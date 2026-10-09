"""S26: F05 launch preflight and PID-bound *read-only* Win32 HWND handoff.

This module DOES NOT launch or inject a process, grant a license, implement
forwarder/Proxy, or expose the original 'Mở game' control prematurely.
Callers must supply an independently validated PermissionSnapshot and the
actual already-running total. Production has neither real license provider
nor F05 suspend/inject; therefore there is NO production launch entrypoint.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from login_path import GameDirectoryResult, GameDirectoryStore
from permission_guard import PermissionSnapshot
from start_windows import NativeWin32Backend, TITLE_TIMEOUT_MS, UNITY_WINDOW_CLASS


@dataclass(frozen=True)
class LaunchPreflight:
    allowed: bool
    reason: str
    executable: Path | None = None
    running: int | None = None
    max_windows: int = 0


def check_open_game_preflight(
    snapshot: PermissionSnapshot,
    game: GameDirectoryResult,
    *,
    running_windows: int | None,
) -> LaunchPreflight:
    """Original F05 ordering: permission -> limit(extra=1) -> game path.

    This returns verified *preconditions*, never a launch authorization
    independent of a real authenticated Info/token source. Account counts
    MUST be supplied from future actual process+emulator enumeration; an
    unknown count blocks. No guess of a default zero.
    """
    if type(snapshot) is not PermissionSnapshot or not snapshot.has_verified_payload:
        return LaunchPreflight(False, "UNVERIFIED_INFO")
    if snapshot.blocked or "login_tab" not in snapshot.authorized_keys:
        return LaunchPreflight(False, "NO_LOGIN_PERMISSION")
    limit = snapshot.max_windows
    if type(limit) is not int or limit <= 0:
        return LaunchPreflight(False, "INVALID_WINDOW_LIMIT")
    if type(running_windows) is not int or running_windows < 0:
        return LaunchPreflight(False, "RUNNING_WINDOW_COUNT_UNKNOWN",
                               max_windows=limit)
    if running_windows + 1 > limit:
        return LaunchPreflight(False, "ACCOUNT_LIMIT_EXTRA_ONE",
                               running=running_windows, max_windows=limit)
    if not isinstance(game, GameDirectoryResult) or game.directory is None:
        return LaunchPreflight(False, "GAME_DIRECTORY_NOT_SELECTED",
                               running=running_windows, max_windows=limit)
    exe = GameDirectoryStore.get_exe_path(game)
    if exe is None:
        return LaunchPreflight(False, "GAME_EXECUTABLE_MISSING",
                               running=running_windows, max_windows=limit)
    return LaunchPreflight(True, "PREFLIGHT_ONLY_NOT_LAUNCHED", exe,
                           running_windows, limit)


class PidWindowBackend(Protocol):
    """Reuse S08 NativeWin32Backend. No second ctypes/WinAPI implementation."""
    def enumerate_top_level(self): ...
    def is_window(self, hwnd: int) -> bool: ...
    def is_visible(self, hwnd: int) -> bool: ...
    def process_id(self, hwnd: int) -> int: ...
    def window_class(self, hwnd: int) -> str: ...
    def title_with_timeout(self, hwnd: int, timeout_ms: int) -> str: ...


def find_main_window_by_pid(
    pid: int, backend: PidWindowBackend | None = None,
) -> int | None:
    """F05: prefer UnityWndClass, then Thần Long title, then visible PID HWND.

    One read-only snapshot. F05's 25-second launcher polling/stabilization
    is NOT reconstructed here. The PID must be known from a successful real
    launch in future stages. Never infer identity from a game-looking title
    alone. Both each candidate and final choice are PID+HWND revalidated.
    """
    if type(pid) is not int or pid <= 0:
        return None
    if backend is None:
        backend = NativeWin32Backend()
    ranked: list[tuple[int, int, int]] = []
    seen: set[int] = set()
    for candidate in backend.enumerate_top_level():
        try:
            hwnd = int(candidate)
            if hwnd <= 0 or hwnd in seen:
                continue
            seen.add(hwnd)
            if not backend.is_window(hwnd) or not backend.is_visible(hwnd):
                continue
            if backend.process_id(hwnd) != pid:
                continue
            class_name = backend.window_class(hwnd)
            title = backend.title_with_timeout(hwnd, TITLE_TIMEOUT_MS)
            # Race: window can close or HWND be reused while title is read.
            if not backend.is_window(hwnd) or not backend.is_visible(hwnd):
                continue
            if backend.process_id(hwnd) != pid:
                continue
            # Ranking is a bounded S26 interpretation of F05's 'prefer
            # UnityWndClass or title containing Thần Long'; exact tie rule
            # among several visible windows UNKNOWN in original source.
            score = (2 if class_name == UNITY_WINDOW_CLASS else
                     1 if "thần long" in title.casefold() else 0)
            ranked.append((score, len(ranked), hwnd))
        except (OSError, RuntimeError, ValueError):
            continue
    # Preserve native enumeration ordering for equal scores.
    for _, _, hwnd in sorted(ranked, key=lambda x: (-x[0], x[1])):
        try:
            if (backend.is_window(hwnd) and backend.is_visible(hwnd)
                    and backend.process_id(hwnd) == pid):
                return hwnd
        except (OSError, RuntimeError, ValueError):
            pass
    return None
