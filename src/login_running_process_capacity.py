"""S160 F05/E04: count actual Windows game EXE processes before F05 preflight.

Original E04 permission_guard combines RUNNING GAME EXE and emulator sessions,
then check_account_limit(login, extra=1) gates any launch. S26 already
implements permission -> combined count+one -> F04 verified executable path.
This module supplies the MISSING real read-only EXE process count, rather
than rebuilding S26, guessing that hidden games have zero HWNDs, or assuming
an unknown emulator count is zero.

Original exact game process counting API is UNKNOWN. This native reader uses
the standard Windows Toolhelp32Snapshot PROCESSENTRY32W API as an explicit
reconstruction implementation choice. It never launches/stops processes,
changes original Info claims or adds the (unverified) F05 Mở game button.

A caller must separately authenticate PermissionSnapshot via original signed
Info and supply an independently counted emulator session integer; no
automatically trusted emulator count or real signed issuer exists yet.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from login_launch_preflight import LaunchPreflight, check_open_game_preflight
from login_path import EXE_NAME, GameDirectoryResult
from permission_guard import PermissionSnapshot

PROCESS_SNAPSHOT_KIND = "LOCAL_WIN32_TOOLHELP_READONLY_NOT_ORIGINAL_API_PROOF"
TH32CS_SNAPPROCESS = 0x00000002
ERROR_NO_MORE_FILES = 18


class ProcessSnapshotBackend(Protocol):
    def process_images(self) -> tuple[tuple[int, str], ...]: ...


class NativeWindowsProcessImages:
    """Windows-only read-only list of (PID, image basename), no cmd execution."""

    def process_images(self) -> tuple[tuple[int, str], ...]:
        import ctypes
        import os
        from ctypes import wintypes

        if os.name != "nt":
            raise OSError("WIN32_REQUIRED")
        class PROCESSENTRY32W(ctypes.Structure):
            _fields_ = [
                ("dwSize", wintypes.DWORD),
                ("cntUsage", wintypes.DWORD),
                ("th32ProcessID", wintypes.DWORD),
                ("th32DefaultHeapID", ctypes.c_size_t),
                ("th32ModuleID", wintypes.DWORD),
                ("cntThreads", wintypes.DWORD),
                ("th32ParentProcessID", wintypes.DWORD),
                ("pcPriClassBase", wintypes.LONG),
                ("dwFlags", wintypes.DWORD),
                ("szExeFile", wintypes.WCHAR * 260),
            ]
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        create = kernel.CreateToolhelp32Snapshot
        create.argtypes = [wintypes.DWORD, wintypes.DWORD]
        create.restype = wintypes.HANDLE
        first = kernel.Process32FirstW
        next_one = kernel.Process32NextW
        first.argtypes = next_one.argtypes = [
            wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
        first.restype = next_one.restype = wintypes.BOOL
        close = kernel.CloseHandle
        close.argtypes = [wintypes.HANDLE]
        close.restype = wintypes.BOOL

        handle = create(TH32CS_SNAPPROCESS, 0)
        if not handle or handle == ctypes.c_void_p(-1).value:
            raise OSError("PROCESS_SNAPSHOT_OPEN_FAILED")
        rows: list[tuple[int, str]] = []
        try:
            entry = PROCESSENTRY32W()
            entry.dwSize = ctypes.sizeof(entry)
            if not first(handle, ctypes.byref(entry)):
                if ctypes.get_last_error() != ERROR_NO_MORE_FILES:
                    raise OSError("PROCESS_SNAPSHOT_FIRST_FAILED")
                return ()
            while True:
                if entry.th32ProcessID > 0 and entry.szExeFile:
                    rows.append((int(entry.th32ProcessID), str(entry.szExeFile)))
                entry.dwSize = ctypes.sizeof(entry)
                if not next_one(handle, ctypes.byref(entry)):
                    if ctypes.get_last_error() != ERROR_NO_MORE_FILES:
                        raise OSError("PROCESS_SNAPSHOT_NEXT_FAILED")
                    break
            return tuple(rows)
        finally:
            if not close(handle):
                raise OSError("PROCESS_SNAPSHOT_CLOSE_FAILED")


@dataclass(frozen=True)
class S160RunningCount:
    code: str
    running_exe: int | None = None
    running_emulators: int | None = None
    combined: int | None = None


def count_current_game_processes(
    backend: ProcessSnapshotBackend | None = None,
) -> S160RunningCount:
    """Count distinct real PIDs by exact original EXE basename, not HWND."""
    backend = backend if backend is not None else NativeWindowsProcessImages()
    try:
        rows = backend.process_images()
        if type(rows) is not tuple:
            return S160RunningCount("UNVERIFIED_PROCESS_SNAPSHOT")
        seen_pids: set[int] = set()
        for pid, image in rows:
            if (type(pid) is not int or pid <= 0
                    or type(image) is not str or not image):
                return S160RunningCount("UNVERIFIED_PROCESS_SNAPSHOT")
            if image.casefold() == EXE_NAME.casefold():
                seen_pids.add(pid)
        return S160RunningCount("PROCESS_SNAPSHOT_OK",running_exe=len(seen_pids))
    except (OSError, RuntimeError, TypeError, ValueError):
        return S160RunningCount("PROCESS_SNAPSHOT_UNAVAILABLE")


def check_native_open_game_capacity(
    snapshot: PermissionSnapshot, game: GameDirectoryResult, *,
    verified_emulator_sessions: int | None,
    backend: ProcessSnapshotBackend | None = None,
) -> tuple[LaunchPreflight, S160RunningCount]:
    """Always run pre-existing S26 guard; report native count separately.

    Explicit emulator sessions MUST come from independent, presently unknown
    real emulator provider. No license, game, Proxy or emulator population is
    inferred from a client-supplied 0. No process may be spawned here.
    """
    # Deny BEFORE native enumeration when Info is missing/blocked. S26's
    # own permission order remains authority; this method adds no grants.
    prior = check_open_game_preflight(snapshot, game, running_windows=None)
    if prior.reason not in ("RUNNING_WINDOW_COUNT_UNKNOWN",):
        return prior, S160RunningCount("NOT_AUTHORIZED_OR_INVALID_LIMIT")
    if type(verified_emulator_sessions) is not int or verified_emulator_sessions < 0:
        return prior, S160RunningCount("EMULATOR_SESSIONS_UNVERIFIED")
    observed = count_current_game_processes(backend)
    if observed.code != "PROCESS_SNAPSHOT_OK" or observed.running_exe is None:
        return prior, observed
    total = observed.running_exe + verified_emulator_sessions
    result = check_open_game_preflight(snapshot, game, running_windows=total)
    return result, S160RunningCount(
        "COMBINED_EXE_PLUS_EMULATOR_COUNT", observed.running_exe,
        verified_emulator_sessions, total)
