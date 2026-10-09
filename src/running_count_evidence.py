"""S29: read-only Windows EXE-process vs visible-HWND count evidence.

E04 says account-limit usage combines running game EXEs and emulators. S08
discovers *visible* game HWNDs only, which is NOT a process count. S29 adds
a separate read-only Toolhelp32 process snapshot, reuses S08 discovery, and
NEVER supplies a combined count or issues an entitlement/launch grant.

No game process creation, injection, Proxy, DLL loading or tool login.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol, Sequence

from login_path import EXE_NAME
from start_windows import GameWindow, NativeWin32Backend, WindowBackend, discover_game_windows


@dataclass(frozen=True)
class ProcessRecord:
    pid: int
    image_name: str


class ProcessSnapshotBackend(Protocol):
    def snapshot_processes(self) -> Sequence[ProcessRecord]: ...


class NativeWin32ProcessBackend:
    """Read-only Toolhelp32 process-list enumerator, *not* OpenProcess VM access."""

    def __init__(self) -> None:
        if os.name != "nt":
            raise OSError("Windows process snapshot requires Windows")
        import ctypes
        from ctypes import wintypes

        class PROCESSENTRY32W(ctypes.Structure):
            _fields_ = [
                ("dwSize", wintypes.DWORD),
                ("cntUsage", wintypes.DWORD),
                ("th32ProcessID", wintypes.DWORD),
                ("th32DefaultHeapID", ctypes.c_size_t),
                ("th32ModuleID", wintypes.DWORD),
                ("cntThreads", wintypes.DWORD),
                ("th32ParentProcessID", wintypes.DWORD),
                ("pcPriClassBase", ctypes.c_long),
                ("dwFlags", wintypes.DWORD),
                ("szExeFile", wintypes.WCHAR * 260),
            ]

        self._ctypes = ctypes
        self._record_type = PROCESSENTRY32W
        self._kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self._snapshot = self._kernel32.CreateToolhelp32Snapshot
        self._snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
        self._snapshot.restype = wintypes.HANDLE
        self._first = self._kernel32.Process32FirstW
        self._next = self._kernel32.Process32NextW
        for fn in (self._first, self._next):
            fn.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
            fn.restype = wintypes.BOOL
        self._close = self._kernel32.CloseHandle
        self._close.argtypes = [wintypes.HANDLE]
        self._close.restype = wintypes.BOOL

    def snapshot_processes(self) -> tuple[ProcessRecord, ...]:
        handle = self._snapshot(0x00000002, 0)  # TH32CS_SNAPPROCESS
        if not handle or int(handle) == self._ctypes.c_void_p(-1).value:
            raise OSError("CreateToolhelp32Snapshot failed")
        try:
            entry = self._record_type()
            entry.dwSize = self._ctypes.sizeof(entry)
            if not self._first(handle, self._ctypes.byref(entry)):
                raise OSError("Process32FirstW failed")
            found: list[ProcessRecord] = []
            while True:
                found.append(ProcessRecord(int(entry.th32ProcessID),
                                           str(entry.szExeFile)))
                if not self._next(handle, self._ctypes.byref(entry)):
                    # ERROR_NO_MORE_FILES is the success end-of-enumeration
                    # condition, not proof that no processes were running.
                    if self._ctypes.get_last_error() != 18:
                        raise OSError("Process32NextW failed")
                    break
            return tuple(found)
        finally:
            self._close(handle)


def find_named_process_pids(
    backend: ProcessSnapshotBackend, image_name: str,
) -> tuple[int, ...]:
    """Case-insensitive Windows image basename match, 1 PID counted once.

    Generic helper allows TEST-ONLY matching of the CI python.exe host.
    In production observe_running_game_evidence binds the exact F04 EXE.
    An image name match is not a cryptographically verified binary identity.
    """
    if type(image_name) is not str or not image_name or "/" in image_name or "\\" in image_name:
        raise ValueError("Windows image basename required")
    pids: set[int] = set()
    for record in backend.snapshot_processes():
        if (type(record) is not ProcessRecord or type(record.pid) is not int
                or type(record.image_name) is not str):
            raise ValueError("Corrupt process snapshot")
        if record.pid > 0 and record.image_name.casefold() == image_name.casefold():
            pids.add(record.pid)
    return tuple(sorted(pids))


@dataclass(frozen=True)
class RunningCountEvidence:
    game_process_pids: tuple[int, ...]
    game_windows: tuple[GameWindow, ...]
    process_scan_valid: bool
    window_scan_valid: bool
    process_error: str | None = None
    window_error: str | None = None

    @property
    def game_process_count(self) -> int | None:
        return len(self.game_process_pids) if self.process_scan_valid else None

    @property
    def visible_hwnd_count(self) -> int | None:
        return len(self.game_windows) if self.window_scan_valid else None

    @property
    def visible_game_pid_count(self) -> int | None:
        return (len({w.pid for w in self.game_windows})
                if self.window_scan_valid else None)

    @property
    def emulator_process_count(self) -> None:
        # E04 requires an independently recovered emulator counting contract.
        return None

    @property
    def combined_running_count(self) -> None:
        # Deliberately NOT int even when both scans succeed or see zero.
        # E04 combined = running EXE + emulator; emulator is UNKNOWN.
        return None

    @property
    def is_authoritative_account_total(self) -> bool:
        return False


def observe_running_game_evidence(
    *,
    processes: ProcessSnapshotBackend | None = None,
    windows: WindowBackend | None = None,
) -> RunningCountEvidence:
    """Observe two independent, non-atomic read-only snapshots.

    The Win32 process list reports an image-name count including invisible
    instances. S08 observes matched visible game HWNDs only; an individual
    game process can own multiple windows and an invisible process none.
    Any failed scan is UNKNOWN, never silently reported as zero.
    """
    process_pids: tuple[int, ...] = ()
    game_windows: tuple[GameWindow, ...] = ()
    process_ok = window_ok = False
    process_error = window_error = None
    try:
        process_backend = processes if processes is not None else NativeWin32ProcessBackend()
        process_pids = find_named_process_pids(process_backend, EXE_NAME)
        process_ok = True
    except (OSError, RuntimeError, ValueError, TypeError) as exc:
        process_error = type(exc).__name__
    try:
        window_backend = windows if windows is not None else NativeWin32Backend()
        game_windows = discover_game_windows(window_backend)
        window_ok = True
    except (OSError, RuntimeError, ValueError, TypeError) as exc:
        window_error = type(exc).__name__
    return RunningCountEvidence(process_pids, game_windows, process_ok,
                                window_ok, process_error, window_error)


def visible_hwnds_for_pid(
    backend: WindowBackend, pid: int,
) -> tuple[int, ...]:
    """Read-only PID-scoped *HWND evidence* for test/diagnostic use only.

    Unlike S08's discover_game_windows, this never calls a window 'game':
    Windows test-owned Tk top levels are python.exe, not Thần Long.
    PID and visibility are checked twice; stale/reused handles are omitted.
    """
    if type(pid) is not int or pid <= 0:
        return ()
    handles: list[int] = []
    seen: set[int] = set()
    for item in backend.enumerate_top_level():
        try:
            hwnd = int(item)
            if hwnd <= 0 or hwnd in seen:
                continue
            seen.add(hwnd)
            if not backend.is_window(hwnd) or not backend.is_visible(hwnd):
                continue
            if backend.process_id(hwnd) != pid:
                continue
            if backend.is_window(hwnd) and backend.is_visible(hwnd) and backend.process_id(hwnd) == pid:
                handles.append(hwnd)
        except (OSError, RuntimeError, ValueError, TypeError):
            continue
    return tuple(handles)
