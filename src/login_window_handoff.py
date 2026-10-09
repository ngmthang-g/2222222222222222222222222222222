"""S27: bounded F05 PID -> visible HWND handoff after an EXTERNAL real PID.

No game launch, DLL injection, login, Proxy or guessed stabilization delay.
F05 proves a 25-second no-window ceiling; the polling interval and precise
lock acquisition rules are S27 local safeguards, NOT original micro-timing.
Reuse S26 PID/HWND selector and the existing S08 native Win32 backend.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import threading
import time
from typing import Callable

from login_launch_preflight import PidWindowBackend, find_main_window_by_pid
from start_windows import NativeWin32Backend

MAX_WAIT_SECONDS = 25.0
# S27 local polling choice; F05 original poll frequency was NOT recovered.
DEFAULT_POLL_SECONDS = 0.1
_LOCK_POLL_SECONDS = 0.05


@dataclass(frozen=True)
class WindowHandoffResult:
    pid: int
    hwnd: int | None
    code: str
    elapsed_seconds: float
    scans: int

    @property
    def found(self) -> bool:
        return self.code == "FOUND" and self.hwnd is not None


def _validate_timing(timeout_seconds: float, poll_seconds: float) -> None:
    for name, value in (("timeout_seconds", timeout_seconds),
                        ("poll_seconds", poll_seconds)):
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError(name + " must be a finite non-boolean number")
    if not 0 <= timeout_seconds <= MAX_WAIT_SECONDS:
        raise ValueError("F05 handoff timeout must be between 0 and 25 seconds")
    if poll_seconds <= 0:
        raise ValueError("poll_seconds must be positive")


def wait_for_pid_window(
    pid: int,
    *,
    backend: PidWindowBackend | None = None,
    cancel: threading.Event | None = None,
    timeout_seconds: float = MAX_WAIT_SECONDS,
    poll_seconds: float = DEFAULT_POLL_SECONDS,
    clock: Callable[[], float] = time.monotonic,
    pause: Callable[[float], object] | None = None,
) -> WindowHandoffResult:
    """One worker-side, bounded handoff. Do not run blocking wait on Tk UI.

    Returns a reason, never a synthetic HWND. Cancel is observed before and
    after each real Win32 scan and during Event.wait (if a cancel is supplied).
    A single native scan may overrun the absolute deadline if Windows itself
    is slow; late discoveries are rejected rather than misreported as ready.
    timeout_seconds=0 explicitly means one immediate snapshot only.
    """
    _validate_timing(timeout_seconds, poll_seconds)
    start = clock()
    def result(code: str, hwnd: int | None, scans: int) -> WindowHandoffResult:
        return WindowHandoffResult(pid, hwnd, code,
                                   max(0.0, float(clock() - start)), scans)
    if type(pid) is not int or pid <= 0:
        return result("INVALID_PID", None, 0)
    if cancel is not None and cancel.is_set():
        return result("CANCELLED", None, 0)
    deadline = start + timeout_seconds
    try:
        reader = backend if backend is not None else NativeWin32Backend()
    except (OSError, RuntimeError, ValueError):
        return result("BACKEND_UNAVAILABLE", None, 0)
    scans = 0
    while True:
        if cancel is not None and cancel.is_set():
            return result("CANCELLED", None, scans)
        if scans and clock() >= deadline:
            return result("TIMEOUT", None, scans)
        try:
            hwnd = find_main_window_by_pid(pid, reader)
        except (OSError, RuntimeError, ValueError):
            return result("ENUMERATION_FAILED", None, scans + 1)
        scans += 1
        if cancel is not None and cancel.is_set():
            return result("CANCELLED", None, scans)
        # A zero-time probe may accept a window from its first snapshot; a
        # positive deadline must not accept an HWND found AFTER the ceiling.
        if timeout_seconds > 0 and clock() > deadline:
            return result("TIMEOUT", None, scans)
        if hwnd is not None:
            # S26 already rechecks before returning; S27 checks once more at
            # the handoff boundary to reject HWND close/reuse during polling.
            try:
                if (reader.is_window(hwnd) and reader.is_visible(hwnd)
                        and reader.process_id(hwnd) == pid):
                    if cancel is not None and cancel.is_set():
                        return result("CANCELLED", None, scans)
                    if timeout_seconds > 0 and clock() > deadline:
                        return result("TIMEOUT", None, scans)
                    return result("FOUND", hwnd, scans)
            except (OSError, RuntimeError, ValueError):
                pass
        remaining = deadline - clock()
        if remaining <= 0:
            return result("TIMEOUT", None, scans)
        wait_time = min(poll_seconds, remaining)
        if pause is not None:
            pause(wait_time)
        elif cancel is not None:
            cancel.wait(wait_time)
        else:
            time.sleep(wait_time)


class SerializedPidWindowHandoff:
    """Coordinate F05 one-by-one HWND readiness *without* launching a game.

    Shared lock serializes waits. Each caller's 25s budget includes lock
    queue time, so an occupied lock cannot cause an unbounded backlog.
    Caller cancellation also works while waiting for another PID to finish.
    This does not claim to recreate the missing _launch_lock/spawn sequence.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()

    def wait(
        self, pid: int, *, backend: PidWindowBackend | None = None,
        cancel: threading.Event | None = None,
        timeout_seconds: float = MAX_WAIT_SECONDS,
        poll_seconds: float = DEFAULT_POLL_SECONDS,
        clock: Callable[[], float] = time.monotonic,
        pause: Callable[[float], object] | None = None,
    ) -> WindowHandoffResult:
        _validate_timing(timeout_seconds, poll_seconds)
        started = clock()
        deadline = started + timeout_seconds

        def waiting(code: str) -> WindowHandoffResult:
            return WindowHandoffResult(
                pid, None, code, max(0.0, float(clock()-started)), 0)

        if type(pid) is not int or pid <= 0:
            return waiting("INVALID_PID")
        acquired = False
        while not acquired:
            if cancel is not None and cancel.is_set():
                return waiting("CANCELLED")
            remaining = deadline - clock()
            if timeout_seconds == 0 or remaining <= 0:
                acquired = self._lock.acquire(blocking=False)
                if not acquired:
                    return waiting("TIMEOUT")
            else:
                acquired = self._lock.acquire(timeout=min(_LOCK_POLL_SECONDS, remaining))
                if not acquired and clock() >= deadline:
                    return waiting("TIMEOUT")
        try:
            if cancel is not None and cancel.is_set():
                return waiting("CANCELLED")
            # Total deadline starts BEFORE waiting for the shared lock.
            remaining = max(0.0, deadline-clock())
            result = wait_for_pid_window(
                pid, backend=backend, cancel=cancel,
                timeout_seconds=remaining, poll_seconds=poll_seconds,
                clock=clock, pause=pause)
            return WindowHandoffResult(result.pid, result.hwnd, result.code,
                                       max(0.0, clock()-started), result.scans)
        finally:
            self._lock.release()
