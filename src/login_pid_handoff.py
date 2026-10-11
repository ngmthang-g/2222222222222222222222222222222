"""S158 F05 -- serialize a caller's launch operation until its PID-owned HWND appears.

FROZEN ORIGINAL SOURCE-BACKED CONTRACT (docs/tasks/F05.md):
 _launch_one_window uses _launch_lock; returns hwnd or None; waits up to
 25 seconds to find a HWND belonging to the returned PID; only after
 the launch+wait completes does the next game launch start. Multi-account
 LAUNCH TUAN TU + LOGIN SONG SONG. A further window-stabilization phase
 exists, but the exact duration/criteria remain UNKNOWN and are NOT implemented.

This helper NEVER launches a process itself and NEVER calls original injected
payload / CREATE_SUSPENDED. It merely serializes an externally authorized,
caller-provided spawn callback and then uses existing S156 REAL Win32
find_main_window_by_pid. The callback must only be supplied by an external
authorized launcher. The original sleep/poll cadence is UNKNOWN; the 250ms
wait quantum is explicitly a local cancel-responsive reconstruction choice.
An HWND arrival is NOT evidence that a game login, injection or stabilization
succeeded. The signed Info product remains blocked.
"""
from __future__ import annotations

from dataclasses import dataclass
import threading
import time
from typing import Callable

from login_pid_window import find_main_window_by_pid

F05_HWND_TIMEOUT_SECONDS = 25
F05_LOCAL_POLL_SECONDS = 0.25
_SHARED_F05_LAUNCH_LOCK = threading.Lock()


@dataclass(frozen=True)
class F05HandoffResult:
    code: str
    pid: int | None = None
    hwnd: int | None = None
    polls: int = 0


class F05SerializedHandoff:
    """Lock spans callback spawn and HWND arrival, never just the lookup."""

    def __init__(
        self, *,
        launch_lock=None,
        find_hwnd: Callable[[int], int | None] = find_main_window_by_pid,
        monotonic: Callable[[], float] = time.monotonic,
        wait: Callable[[float], object] = time.sleep,
    ):
        self._lock = launch_lock if launch_lock is not None else _SHARED_F05_LAUNCH_LOCK
        self._find_hwnd = find_hwnd
        self._clock = monotonic
        self._wait = wait

    @staticmethod
    def _approved(callback: Callable[[], bool]) -> bool:
        if not callable(callback):
            return False
        try:
            return callback() is True
        except Exception:
            return False

    @staticmethod
    def _cancelled(callback: Callable[[], bool] | None) -> bool:
        if callback is None:
            return False
        if not callable(callback):
            return True
        try:
            return callback() is True
        except Exception:
            return True

    def launch_and_wait(
        self, spawn_pid: Callable[[], int], *,
        allowed: Callable[[], bool],
        cancelled: Callable[[], bool] | None = None,
    ) -> F05HandoffResult:
        if not callable(spawn_pid):
            return F05HandoffResult("INVALID_LAUNCH_CALLBACK")
        if not self._approved(allowed):
            return F05HandoffResult("NOT_AUTHORIZED")
        if self._cancelled(cancelled):
            return F05HandoffResult("CANCELLED")
        # The original F05 launch lock serializes the whole one-window
        # launch+find sequence; never allow two callbacks to overlap.
        with self._lock:
            if not self._approved(allowed):
                return F05HandoffResult("NOT_AUTHORIZED")
            if self._cancelled(cancelled):
                return F05HandoffResult("CANCELLED")
            try:
                pid = spawn_pid()
            except Exception:
                return F05HandoffResult("LAUNCH_CALLBACK_FAILED")
            if type(pid) is not int or not 0 < pid <= 0xFFFFFFFF:
                return F05HandoffResult("INVALID_SPAWN_PID")
            start = self._clock()
            polls = 0
            while True:
                if not self._approved(allowed):
                    return F05HandoffResult("AUTH_REVOKED", pid, polls=polls)
                if self._cancelled(cancelled):
                    return F05HandoffResult("CANCELLED", pid, polls=polls)
                # Do not inspect window title or assume RoleName here; the
                # previously proven S156 selector verifies live PID/HWND.
                if self._clock() - start >= F05_HWND_TIMEOUT_SECONDS:
                    return F05HandoffResult("TIMEOUT_NO_PID_WINDOW", pid, polls=polls)
                try:
                    hwnd = self._find_hwnd(pid)
                except Exception:
                    hwnd = None
                polls += 1
                if type(hwnd) is int and hwnd > 0:
                    if not self._approved(allowed):
                        return F05HandoffResult("AUTH_REVOKED", pid, polls=polls)
                    if self._cancelled(cancelled):
                        return F05HandoffResult("CANCELLED", pid, polls=polls)
                    return F05HandoffResult("PID_HWND_FOUND", pid, hwnd, polls)
                remaining = F05_HWND_TIMEOUT_SECONDS - (self._clock() - start)
                if remaining <= 0:
                    return F05HandoffResult("TIMEOUT_NO_PID_WINDOW", pid, polls=polls)
                try:
                    self._wait(min(F05_LOCAL_POLL_SECONDS, remaining))
                except Exception:
                    return F05HandoffResult("WAIT_INTERRUPTED", pid, polls=polls)
