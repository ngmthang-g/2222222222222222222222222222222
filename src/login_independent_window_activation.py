"""S189 independent Login: user-click foreground of freshly launched HWND.

Original C03/S78 activation is IsIconic -> ShowWindow(SW_RESTORE/SW_SHOW)
-> SetForegroundWindow with real HWND/PID checks, no game key/mouse input.
Only the live Popen handle from the SAME independent tool launch may request
activation; PID number alone, cached title, stale HWND or game-looking window
are not enough. OS foreground policy may refuse and must be reported.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Protocol

from start_windows import NativeWin32Backend, is_game_candidate


@dataclass(frozen=True)
class IndependentActivationResult:
    code: str
    pid: int | None = None
    hwnd: int | None = None


class LaunchedProcess(Protocol):
    pid: int
    def poll(self) -> int | None: ...


class ForegroundBackend(Protocol):
    def source_matches(self, hwnd: int, pid: int) -> bool: ...
    def activate_source(self, hwnd: int) -> bool: ...


def activate_verified_launched_game(
    process: LaunchedProcess,
    hwnd: int,
    *,
    native=None,
    activator: ForegroundBackend | None = None,
) -> IndependentActivationResult:
    """Only explicit user interaction. Does not infer in-game authentication.

    No window enumeration occurs if the retained created process is already
    exited. The native checks are repeated immediately before and after a
    foreground request; a stale/reused HWND never falls back to another.
    """
    if (os.name != "nt" or process is None
            or type(hwnd) is not int or hwnd <= 0
            or type(getattr(process, "pid", None)) is not int
            or process.pid <= 0):
        return IndependentActivationResult("INVALID_LAUNCH_SESSION")
    pid = process.pid
    try:
        if process.poll() is not None:
            return IndependentActivationResult("LAUNCHED_PROCESS_EXITED", pid)
    except (OSError, ValueError, RuntimeError):
        return IndependentActivationResult("LAUNCHED_PROCESS_UNVERIFIED", pid)
    try:
        native = native if native is not None else NativeWin32Backend()
        tops = tuple(native.enumerate_top_level())
        if (tops.count(hwnd) != 1 or not native.is_window(hwnd)
                or not native.is_visible(hwnd)
                or native.process_id(hwnd) != pid
                or not is_game_candidate(
                    native.process_executable(pid),
                    native.window_class(hwnd),
                    native.title_with_timeout(hwnd, 150))):
            return IndependentActivationResult("WINDOW_NOT_CURRENT_GAME", pid, hwnd)
        # S78 is the existing original-backed native foreground helper.
        if activator is None:
            from dwm_preview import NativeDwmBackend
            activator = NativeDwmBackend()
        if not activator.source_matches(hwnd, pid):
            return IndependentActivationResult("WINDOW_NOT_CURRENT_GAME", pid, hwnd)
        if process.poll() is not None:
            return IndependentActivationResult("LAUNCHED_PROCESS_EXITED", pid, hwnd)
        attempted = activator.activate_source(hwnd) is True
        # Win32 SetForegroundWindow success can be rejected by OS policy;
        # never call this proof of game login or full client readiness.
        if (process.poll() is not None or not native.is_window(hwnd)
                or native.process_id(hwnd) != pid):
            return IndependentActivationResult("WINDOW_CHANGED_AFTER_ACTIVATE", pid, hwnd)
        return IndependentActivationResult(
            "OS_FOREGROUND_ACCEPTED_NOT_LOGIN" if attempted
            else "OS_FOREGROUND_REFUSED", pid, hwnd)
    except (OSError, ValueError, RuntimeError, TypeError, AttributeError):
        return IndependentActivationResult("WINDOW_ACTIVATION_FAILED", pid, hwnd)
