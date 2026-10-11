"""S133: Windows read-only process module/PE attestation for eventual Farm reader.

O01/O02 original TLM 2.1.2 evidence: native HWND/PID -> OpenProcess,
EnumProcessModulesEx + GameAssembly.dll -> VirtualQueryEx ->
ReadProcessMemory, with separate validation before RoleData dereferencing.

This stage ATTESTS the module/header only. It has NO RoleName, MapID, Site10,
Unity offsets, memory write, pointer chase, game command or authentic issuer.
A legitimate Info verifier is still MISSING, so the production entrypoint
remains fail-closed. Only S133 Windows smoke reads its OWN Python process.
Least-privilege read rights here are a reconstruction safety policy, not
claimed to equal the original unknown PROCESS_RIGHTS.
"""
from __future__ import annotations

import ctypes
from dataclasses import dataclass
import os
from pathlib import Path
import sys
from typing import Callable

from permission_guard import PermissionGuard
from start_windows import GameWindow, NativeWin32Backend
from start_polling import StartWindowProducer, WindowSnapshot

PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400
READ_ONLY_RIGHTS = PROCESS_VM_READ | PROCESS_QUERY_INFORMATION
MEM_COMMIT = 0x1000
PAGE_NOACCESS = 0x01
PAGE_GUARD = 0x100
# Protection base values that permit reading. No PAGE_EXECUTE-only reads.
_READABLE = frozenset((0x02, 0x04, 0x08, 0x20, 0x40, 0x80))
LIST_MODULES_ALL = 0x03
MAX_MODULES = 1024
MAX_DOS_HEADER = 0x1000


@dataclass(frozen=True)
class ModuleAttestation:
    status: str
    pid: int | None = None
    name: str = "GameAssembly.dll"
    base: int | None = None
    image_size: int | None = None
    pe_header_verified: bool = False
    original_role_data_verified: bool = False
    game_memory_sample: bool = False
    # No role, map, bag, game command or authorization grant fields.


class _MemoryBasicInformation(ctypes.Structure):
    # 64-bit Windows layout. On 32-bit hosts fail closed before using.
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", ctypes.c_uint32),
        ("PartitionId", ctypes.c_ushort),
        ("RegionSize", ctypes.c_size_t),
        ("State", ctypes.c_uint32),
        ("Protect", ctypes.c_uint32),
        ("Type", ctypes.c_uint32),
    ]


class _ModuleInfo(ctypes.Structure):
    _fields_ = [
        ("lpBaseOfDll", ctypes.c_void_p),
        ("SizeOfImage", ctypes.c_uint32),
        ("EntryPoint", ctypes.c_void_p),
    ]


class NativeReadOnlyModuleInspector:
    """Real Win32 PID/module PE-header read. No guessed game offsets.

    This low-level inspector is also usable on a TEST-OWNED Windows process,
    while the high-level GameAssembly gate REQUIRES verified Info + Start.
    """

    def __init__(self):
        self.supported = (
            os.name == "nt" and sys.maxsize > 2**32
            and ctypes.sizeof(ctypes.c_void_p) == 8)

    def inspect(self, pid: int, module_name: str) -> ModuleAttestation:
        if type(pid) is not int or pid <= 0 or type(module_name) is not str:
            return ModuleAttestation("INVALID_PID_OR_MODULE")
        if (not module_name or len(module_name) > 120
                or "\x00" in module_name or "/" in module_name
                or "\\" in module_name or module_name in (".", "..")):
            return ModuleAttestation("INVALID_PID_OR_MODULE", pid)
        expected = module_name.casefold()
        if not self.supported:
            return ModuleAttestation("WINDOWS_X64_REQUIRED", pid, module_name)
        # Dynamic library load; do not create a Windows kernel handle on import.
        try:
            kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            psapi = ctypes.WinDLL("psapi", use_last_error=True)
            handle_t = ctypes.c_void_p
            dword = ctypes.c_uint32
            size_t = ctypes.c_size_t
            kernel.OpenProcess.argtypes = [dword, ctypes.c_int, dword]
            kernel.OpenProcess.restype = handle_t
            kernel.CloseHandle.argtypes = [handle_t]
            kernel.CloseHandle.restype = ctypes.c_int
            kernel.VirtualQueryEx.argtypes = [
                handle_t, handle_t, ctypes.POINTER(_MemoryBasicInformation),
                size_t]
            kernel.VirtualQueryEx.restype = size_t
            kernel.ReadProcessMemory.argtypes = [
                handle_t, handle_t, handle_t, size_t,
                ctypes.POINTER(size_t)]
            kernel.ReadProcessMemory.restype = ctypes.c_int
            psapi.EnumProcessModulesEx.argtypes = [
                handle_t, handle_t, dword, ctypes.POINTER(dword), dword]
            psapi.EnumProcessModulesEx.restype = ctypes.c_int
            psapi.GetModuleBaseNameW.argtypes = [
                handle_t, handle_t, ctypes.c_wchar_p, dword]
            psapi.GetModuleBaseNameW.restype = dword
            psapi.GetModuleInformation.argtypes = [
                handle_t, handle_t, ctypes.POINTER(_ModuleInfo), dword]
            psapi.GetModuleInformation.restype = ctypes.c_int
        except (AttributeError, OSError):
            return ModuleAttestation("WIN32_READ_APIS_UNAVAILABLE", pid, module_name)
        handle = kernel.OpenProcess(READ_ONLY_RIGHTS, 0, pid)
        if not handle:
            return ModuleAttestation("READ_ONLY_OPEN_PROCESS_FAILED", pid, module_name)
        try:
            modules = (handle_t * MAX_MODULES)()
            required = dword(0)
            ok = psapi.EnumProcessModulesEx(
                handle, ctypes.cast(modules, handle_t),
                ctypes.sizeof(modules), ctypes.byref(required),
                LIST_MODULES_ALL)
            if not ok:
                return ModuleAttestation("MODULE_ENUM_FAILED", pid, module_name)
            if required.value > ctypes.sizeof(modules) or required.value % 8:
                return ModuleAttestation("MODULE_ENUM_TRUNCATED", pid, module_name)
            target = None
            for i in range(required.value // 8):
                entry = modules[i]
                label = ctypes.create_unicode_buffer(260)
                found = psapi.GetModuleBaseNameW(handle, entry, label, len(label))
                if not found:
                    return ModuleAttestation("MODULE_NAME_READ_FAILED", pid, module_name)
                if label.value.casefold() == expected:
                    target = entry
                    break
            if not target:
                return ModuleAttestation("MODULE_NOT_FOUND", pid, module_name)
            info = _ModuleInfo()
            if not psapi.GetModuleInformation(
                handle, target, ctypes.byref(info), ctypes.sizeof(info)):
                return ModuleAttestation("MODULE_INFO_FAILED", pid, module_name)
            base, size = info.lpBaseOfDll, info.SizeOfImage
            if not isinstance(base, int) or base <= 0 or size < 0x100:
                return ModuleAttestation("INVALID_MODULE_RANGE", pid, module_name)
            # Verify region before attempting ANY read. Do not cross page
            # boundary or interpret an uncommitted/noaccess/guarded page.
            def read_exact(address: int, length: int) -> bytes | None:
                if (address < base or length <= 0
                        or address + length > base + size):
                    return None
                region = _MemoryBasicInformation()
                got = kernel.VirtualQueryEx(
                    handle, handle_t(address), ctypes.byref(region),
                    ctypes.sizeof(region))
                if got != ctypes.sizeof(region):
                    return None
                if (region.State != MEM_COMMIT
                        or region.Protect & (PAGE_NOACCESS | PAGE_GUARD)
                        or (region.Protect & 0xFF) not in _READABLE
                        or region.BaseAddress is None
                        or not region.BaseAddress <= address
                        or address + length > region.BaseAddress + region.RegionSize):
                    return None
                buff = (ctypes.c_ubyte * length)()
                num = size_t(0)
                worked = kernel.ReadProcessMemory(
                    handle, handle_t(address), ctypes.cast(buff, handle_t),
                    length, ctypes.byref(num))
                if not worked or num.value != length:
                    return None
                return bytes(buff)
            header = read_exact(base, 0x40)
            if header is None:
                return ModuleAttestation("UNREADABLE_PE_DOS_HEADER", pid, module_name)
            if header[:2] != b"MZ":
                return ModuleAttestation("NOT_PE_MODULE", pid, module_name)
            pe_offset = int.from_bytes(header[0x3C:0x40], "little")
            if not 0x40 <= pe_offset < min(size - 4, MAX_DOS_HEADER):
                return ModuleAttestation("INVALID_PE_OFFSET", pid, module_name)
            signature = read_exact(base + pe_offset, 4)
            if signature != b"PE\x00\x00":
                return ModuleAttestation("INVALID_PE_SIGNATURE", pid, module_name)
            return ModuleAttestation(
                "PE_MODULE_VERIFIED_ONLY", pid, module_name,
                base, size, True, False, False)
        finally:
            kernel.CloseHandle(handle)


class GuardedGameAssemblyProbe:
    """Exact GameAssembly read-only probe AFTER real Info/Start/Win32 fence.

    No default signed Info provider exists: without a valid independently
    produced PermissionGuard this returns INFO_UNVERIFIED without OpenProcess.
    The exact RoleData pointer, RoleName/MapID/bag fields are NOT read.
    """

    def __init__(self, *, permission_guard: PermissionGuard | None,
                 running_count: Callable[[], int] | None,
                 start_producer: StartWindowProducer | None,
                 backend: NativeWin32Backend | None = None,
                 inspector: NativeReadOnlyModuleInspector | None = None):
        self.guard = permission_guard
        self.running_count = running_count
        self.producer = start_producer
        self.backend = backend if backend is not None else NativeWin32Backend()
        self.inspector = inspector if inspector is not None else NativeReadOnlyModuleInspector()

    def _permitted(self) -> bool:
        if (type(self.guard) is not PermissionGuard
                or not callable(self.running_count)
                or not isinstance(self.producer, StartWindowProducer)):
            return False
        try:
            count = self.running_count()
            return (type(count) is int and count > 0
                    and self.guard.snapshot.has_verified_payload
                    and self.guard.has_permission_with_limit("farm_tab", count))
        except Exception:
            return False

    def _identity(self, window: GameWindow):
        try:
            snap = self.producer.read_snapshot()
            if (type(snap) is not WindowSnapshot or not snap.valid
                    or type(snap.revision) is not int or snap.revision <= 0):
                return None
            if (len([w for w in snap.windows
                     if type(w) is GameWindow and
                     w.hwnd == window.hwnd and w.pid == window.pid]) != 1
                    or not self.backend.is_window(window.hwnd)
                    or not self.backend.is_visible(window.hwnd)
                    or self.backend.process_id(window.hwnd) != window.pid):
                return None
            return snap
        except Exception:
            return None

    def inspect(self, window: GameWindow) -> ModuleAttestation:
        if (type(window) is not GameWindow
                or type(window.hwnd) is not int or window.hwnd <= 0
                or type(window.pid) is not int or window.pid <= 0):
            return ModuleAttestation("INVALID_HWND_PID")
        if not self._permitted():
            return ModuleAttestation("INFO_UNVERIFIED_OR_LIMIT", window.pid)
        before = self._identity(window)
        if before is None:
            return ModuleAttestation("START_HWND_PID_NOT_ATTESTED", window.pid)
        result = self.inspector.inspect(window.pid, "GameAssembly.dll")
        if not self._permitted():
            return ModuleAttestation("INFO_REVOKED_DURING_READ", window.pid)
        after = self._identity(window)
        if (after is None or after.revision != before.revision
                or after.windows != before.windows):
            return ModuleAttestation("STALE_START_GENERATION", window.pid)
        return result
