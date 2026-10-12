"""S196 — read-only Win64 groundwork for ORIGINAL TLMTool memory_reader.

Frozen O02 evidence: GameAssembly+0x355B208 -> +0xB8 -> +0x88
and SessionData.RoleData at +0x88; the original get_RoleData getter is
at GA+0x6F4030. We do not know exact RoleName/HP/MapID field offsets.
Only verify a version-specific POINTER candidate and a matching session
anchor; no game character data, DLL injection, writes or input commands.

The target is the actual game HWND/PID and the explicitly selected F04
game folder. Both GameAssembly/metadata SHA256 hashes must match the
frozen DATA-2222 client before ANY process attach. Run from a worker,
never synchronously on Tk; no original TLM licensing/Info dependency.
"""
from __future__ import annotations

from dataclasses import dataclass
import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import sys

from login_frozen_client_fingerprint import inspect_installed_frozen_client
from login_path import EXE_NAME
from start_windows import (
    GameWindow, NativeWin32Backend, TITLE_TIMEOUT_MS, is_game_candidate,
)
from train_memory_module_probe import (
    READ_ONLY_RIGHTS, _MemoryBasicInformation, MEM_COMMIT,
    PAGE_GUARD, PAGE_NOACCESS, _READABLE,
    _ModuleInfo, LIST_MODULES_ALL, MAX_MODULES, MAX_DOS_HEADER,
)

O02_STORAGE_RVA = 0x355B208
O02_HOP = 0xB8
O02_ROLE_SLOT = 0x88
O02_GET_ROLE_RVA = 0x6F4030
O02_GETTER_SCAN_BYTES = 64
USER_PTR_MAX = 0x00007FFFFFFFFFFF


@dataclass(frozen=True)
class TlmOriginalReadProbe:
    status: str
    pid: int | None = None
    hwnd: int | None = None
    gameassembly_live_pe: bool = False
    original_role_pointer_observed: bool = False
    original_session_anchor_observed: bool = False
    role_name_read: bool = False
    hp_read: bool = False
    map_id_read: bool = False
    gameplay_authorized: bool = False


def _pointer(v):
    return type(v) is int and 0x10000 <= v <= USER_PTR_MAX and v % 8 == 0


def _same_path(a, b):
    return bool(a and b and os.path.normcase(os.path.normpath(a))
                == os.path.normcase(os.path.normpath(str(b))))


class _Win64ReadProcess:
    """Own a least-privilege OpenProcess handle; never act on PID alone."""

    def __init__(self, pid, selected_exe):
        self.pid, self.exe = pid, selected_exe
        self.handle = None

    def __enter__(self):
        self.kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        self.psapi = ctypes.WinDLL("psapi", use_last_error=True)
        pointer, dword = ctypes.c_void_p, wintypes.DWORD

        def sig(dll, name, argtypes, restype):
            fn = getattr(dll, name)
            fn.argtypes, fn.restype = argtypes, restype
            return fn

        self.open = sig(self.kernel, "OpenProcess",
                        [dword, wintypes.BOOL, dword], pointer)
        self.close = sig(self.kernel, "CloseHandle", [pointer], wintypes.BOOL)
        self.exit_code = sig(self.kernel, "GetExitCodeProcess",
                             [pointer, ctypes.POINTER(dword)], wintypes.BOOL)
        self.exe_path = sig(self.kernel, "QueryFullProcessImageNameW",
                            [pointer, dword, wintypes.LPWSTR,
                             ctypes.POINTER(dword)], wintypes.BOOL)
        self.query = sig(self.kernel, "VirtualQueryEx",
                         [pointer, pointer, ctypes.POINTER(_MemoryBasicInformation),
                          ctypes.c_size_t], ctypes.c_size_t)
        self.read = sig(self.kernel, "ReadProcessMemory",
                        [pointer, pointer, pointer, ctypes.c_size_t,
                         ctypes.POINTER(ctypes.c_size_t)], wintypes.BOOL)
        self.enum = sig(self.psapi, "EnumProcessModulesEx",
                        [pointer, pointer, dword, ctypes.POINTER(dword), dword],
                        wintypes.BOOL)
        self.mod_name = sig(self.psapi, "GetModuleBaseNameW",
                            [pointer, pointer, wintypes.LPWSTR, dword], dword)
        self.mod_path = sig(self.psapi, "GetModuleFileNameExW",
                            [pointer, pointer, wintypes.LPWSTR, dword], dword)
        self.mod_info = sig(self.psapi, "GetModuleInformation",
                            [pointer, pointer, ctypes.POINTER(_ModuleInfo), dword],
                            wintypes.BOOL)
        self.handle = self.open(READ_ONLY_RIGHTS, False, self.pid)
        if not self.handle:
            raise OSError("READ_ONLY_OPEN_PROCESS_FAILED")
        return self

    def __exit__(self, *_):
        if self.handle:
            self.close(self.handle)
            self.handle = None

    def live(self):
        value = wintypes.DWORD(0)
        return (bool(self.handle)
                and bool(self.exit_code(self.handle, ctypes.byref(value)))
                and value.value == 259)

    def selected_image(self):
        if not self.live():
            return False
        buf = ctypes.create_unicode_buffer(32768)
        length = wintypes.DWORD(len(buf))
        return (bool(self.exe_path(self.handle, 0, buf, ctypes.byref(length)))
                and _same_path(buf.value, self.exe))

    def module(self, name):
        if not self.live():
            return None
        arr = (ctypes.c_void_p * MAX_MODULES)()
        needed = wintypes.DWORD(0)
        if not self.enum(self.handle, ctypes.cast(arr, ctypes.c_void_p),
                         ctypes.sizeof(arr), ctypes.byref(needed),
                         LIST_MODULES_ALL):
            return None
        ptr_bytes = ctypes.sizeof(ctypes.c_void_p)
        if (needed.value <= 0 or needed.value > ctypes.sizeof(arr)
                or needed.value % ptr_bytes):
            return None
        matches = []
        for idx in range(needed.value // ptr_bytes):
            module_handle = arr[idx]
            basename = ctypes.create_unicode_buffer(260)
            if not self.mod_name(
                    self.handle, module_handle, basename, len(basename)):
                return None
            if basename.value.casefold() != name.casefold():
                continue
            fullpath = ctypes.create_unicode_buffer(32768)
            if (not self.mod_path(
                    self.handle, module_handle, fullpath, len(fullpath))
                    or not _same_path(fullpath.value, self.exe.parent / name)):
                return None
            info = _ModuleInfo()
            if not self.mod_info(self.handle, module_handle,
                                 ctypes.byref(info), ctypes.sizeof(info)):
                return None
            if not _pointer(info.lpBaseOfDll) or info.SizeOfImage < 0x1000:
                return None
            matches.append((int(info.lpBaseOfDll), int(info.SizeOfImage)))
        return matches[0] if len(matches) == 1 else None

    def bytes(self, address, size):
        if (not _pointer(address) or type(size) is not int
                or not 1 <= size <= 64
                or address > USER_PTR_MAX-size or not self.live()):
            return None
        reg = _MemoryBasicInformation()
        if self.query(self.handle, ctypes.c_void_p(address),
                      ctypes.byref(reg), ctypes.sizeof(reg)) != ctypes.sizeof(reg):
            return None
        if (reg.State != MEM_COMMIT
                or reg.Protect & (PAGE_NOACCESS | PAGE_GUARD)
                or (reg.Protect & 0xFF) not in _READABLE
                or reg.BaseAddress is None or reg.BaseAddress > address
                or address + size > reg.BaseAddress + reg.RegionSize):
            return None
        buff = (ctypes.c_ubyte * size)()
        count = ctypes.c_size_t(0)
        if not self.read(self.handle, ctypes.c_void_p(address),
                         ctypes.cast(buff, ctypes.c_void_p), size,
                         ctypes.byref(count)) or count.value != size:
            return None
        return bytes(buff)

    def qword(self, address):
        data = self.bytes(address, 8)
        return int.from_bytes(data, "little") if data is not None else None

    def pe(self, base, length):
        dos = self.bytes(base, 64)
        if not dos or dos[:2] != b"MZ":
            return False
        off = int.from_bytes(dos[60:64], "little")
        return (0x40 <= off < min(length - 24, MAX_DOS_HEADER)
                and self.bytes(base+off, 4) == b"PE\x00\x00")


def _real_game_window(window, native):
    if (type(window) is not GameWindow or type(window.hwnd) is not int
            or type(window.pid) is not int or window.hwnd <= 0 or window.pid <= 0):
        return False
    try:
        return (tuple(native.enumerate_top_level()).count(window.hwnd) == 1
                and native.is_window(window.hwnd)
                and native.is_visible(window.hwnd)
                and native.process_id(window.hwnd) == window.pid
                and is_game_candidate(
                    native.process_executable(window.pid),
                    native.window_class(window.hwnd),
                    native.title_with_timeout(window.hwnd, TITLE_TIMEOUT_MS)))
    except (OSError, RuntimeError, ValueError, TypeError, AttributeError):
        return False


def _role_pointer(reader, ga_base):
    p1 = reader.qword(ga_base + O02_STORAGE_RVA)
    if not _pointer(p1):
        return None
    p2 = reader.qword(p1 + O02_HOP)
    if not _pointer(p2):
        return None
    role = reader.qword(p2 + O02_ROLE_SLOT)
    if not _pointer(role) or reader.qword(role) is None:
        return None
    return role


def _anchored_session(reader, ga_base, role):
    """Bounded O02 get_RoleData mov rax,[rip+disp32] search (not first-hit).

    Each candidate points to a static qword value; only the candidate
    that equals the separately resolved RoleData pointer may anchor.
    Multiple candidate session blocks => AMBIGUOUS / reject.
    """
    opcodes = reader.bytes(ga_base + O02_GET_ROLE_RVA, O02_GETTER_SCAN_BYTES)
    if opcodes is None:
        return None
    matches = set()
    for i in range(len(opcodes)-6):
        if opcodes[i:i+3] != b"\x48\x8b\x05":
            continue
        displacement = int.from_bytes(
            opcodes[i+3:i+7], "little", signed=True)
        static_slot = ga_base + O02_GET_ROLE_RVA + i + 7 + displacement
        if not _pointer(static_slot) or static_slot < O02_ROLE_SLOT:
            continue
        if reader.qword(static_slot) != role:
            continue
        block = static_slot - O02_ROLE_SLOT
        if _pointer(block) and reader.qword(block + O02_ROLE_SLOT) == role:
            matches.add(block)
    return next(iter(matches)) if len(matches) == 1 else None


def inspect_original_tlm_role_pointer(window, selected_exe, *, backend=None):
    """One real Windows-only diagnostic read; no RoleName or HP publication."""
    if (os.name != "nt" or sys.maxsize <= 2**32
            or ctypes.sizeof(ctypes.c_void_p) != 8):
        return TlmOriginalReadProbe("WINDOWS_X64_REQUIRED")
    if type(window) is not GameWindow or not isinstance(selected_exe, (str, Path)):
        return TlmOriginalReadProbe("INVALID_WINDOW_OR_SELECTED_GAME")
    exe = Path(selected_exe)
    if (exe.name != EXE_NAME or exe.is_symlink() or exe.parent.is_symlink()
            or not exe.is_file()):
        return TlmOriginalReadProbe("SELECTED_GAME_INVALID")
    pid, hwnd = window.pid, window.hwnd

    def report(code, pe=False, chain=False, anchored=False):
        return TlmOriginalReadProbe(code, pid, hwnd, pe, chain, anchored)

    if not inspect_installed_frozen_client(exe).known_static_files:
        return report("SELECTED_CLIENT_NOT_FROZEN_SHA256_MATCH")
    try:
        native = backend if backend is not None else NativeWin32Backend()
        if not _real_game_window(window, native):
            return report("HWND_PID_NOT_CURRENT_GAME")
        with _Win64ReadProcess(pid, exe) as reader:
            if not reader.selected_image():
                return report("ATTACHED_PROCESS_NOT_SELECTED_GAME")
            ga = reader.module("GameAssembly.dll")
            unity = reader.module("UnityPlayer.dll")
            if not ga or not unity:
                return report("GAME_MODULES_NOT_ATTESTED")
            if not reader.pe(*ga) or not reader.pe(*unity):
                return report("GAME_MODULE_PE_NOT_ATTESTED")
            base, size = ga
            if (O02_STORAGE_RVA + 8 > size
                    or O02_GET_ROLE_RVA + O02_GETTER_SCAN_BYTES > size):
                return report("O02_RVA_OUTSIDE_GAMEASSEMBLY", pe=True)
            role = _role_pointer(reader, base)
            if not role:
                return report("ORIGINAL_ROLE_POINTER_UNRESOLVED", pe=True)
            anchor = _anchored_session(reader, base, role)
            if anchor is None:
                return report("SESSION_ROLE_ANCHOR_UNVERIFIED", True, True)
            if not reader.selected_image():
                return report("GAME_PROCESS_CHANGED_DURING_READ", True, True, True)
        if not _real_game_window(window, native):
            return report("HWND_PID_CHANGED_DURING_READ", True, True, True)
        return report("ROLE_POINTER_SESSION_ANCHORED_NO_CHARACTER_FIELDS",
                      True, True, True)
    except (OSError, RuntimeError, ValueError, OverflowError, AttributeError):
        return report("NATIVE_MEMORY_READ_FAILED")
