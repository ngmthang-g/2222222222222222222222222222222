"""S42 F09 real 20-second cancellable background event *evaluation* ONLY.

A genuine worker uses threading.Event.wait(20), S39 daily event deadlines,
and S40 strictly read-only settings. No game action dispatch is available:
all due occurrences are in-memory BLOCKED_ACTION_UNAVAILABLE audit records.
Never attach a fake scheduler checkbox or use opaque persisted boolean flags
to auto-run. No F05/F06 launcher, HWND close-all, shutdown, Proxy or INI write.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import threading
from typing import Callable

from login_schedule_clock import LoginScheduleClock, WORKER_CHECK_SECONDS
from login_schedule_settings import ReadOnlyScheduleSettings

BLOCKED_ACTION = "BLOCKED_ACTION_UNAVAILABLE"
AUDIT_CAP = 64


@dataclass(frozen=True)
class BlockedScheduleOccurrence:
    """Safe audit only: no usernames, raw INI fields or executable actions."""
    kind: str
    planned_time: datetime
    status: str = BLOCKED_ACTION


class F09ScheduleEvaluationWorker:
    """Real Event.wait(20) loop, explicitly started, never action-dispatching.

    Not the complete original worker: due open/close actions are BLOCKED
    until authenticated production F05/F06 + close-all handlers exist.
    This controller is not installed in the product Login tab.

    poll_once() exists for deterministic, independently testable due-event
    evaluation; the background worker calls the exact same method.
    """
    def __init__(self, settings: ReadOnlyScheduleSettings,
                 *, now: Callable[[], datetime] | None = None):
        if not isinstance(settings, ReadOnlyScheduleSettings):
            raise TypeError("S42_READONLY_SETTINGS_REQUIRED")
        if now is not None and not callable(now):
            raise TypeError("S42_CLOCK_SOURCE_REQUIRED")
        self._settings = settings
        self._now = now or datetime.now
        self._lock = threading.RLock()
        self._cancel = threading.Event()
        self._cancel.set()
        self._thread: threading.Thread | None = None
        self._clock: LoginScheduleClock | None = None
        self._audit: list[BlockedScheduleOccurrence] = []
        self._status = "IDLE"
        self._closed = False
        self._ticks = 0

    @property
    def status(self) -> str:
        with self._lock:
            return self._status

    @property
    def active(self) -> bool:
        with self._lock:
            return (self._thread is not None and self._thread.is_alive()
                    and not self._cancel.is_set())

    @property
    def thread_alive(self) -> bool:
        with self._lock:
            return self._thread is not None and self._thread.is_alive()

    @property
    def ticks(self) -> int:
        with self._lock:
            return self._ticks

    def blocked_occurrences(self) -> tuple[BlockedScheduleOccurrence, ...]:
        """Immutable snapshot; never exposes credential-bearing Settings."""
        with self._lock:
            return tuple(self._audit)

    def start(self) -> bool:
        """Explicit ONLY; no auto-resume from unknown persisted schedule_on.

        Repeated start while active is a no-op. First due evaluation occurs
        after Event.wait(20), not immediately upon starting.
        """
        with self._lock:
            if self._closed or (self._thread is not None and self._thread.is_alive()):
                return False
            if not self._settings.preview_available:
                self._status = "BLOCKED_SETTINGS"
                return False
            try:
                clock = LoginScheduleClock(
                    close_hhmm=self._settings.close_hhmm,
                    open_hhmm=self._settings.open_hhmm)
                clock.enable(self._now())
            except Exception:
                # Do not print exceptions: caller settings may contain secrets.
                self._status = "BLOCKED_CLOCK"
                return False
            self._clock = clock
            self._audit.clear()
            self._ticks = 0
            self._cancel.clear()
            self._status = "EVALUATING_ONLY_NO_ACTIONS"
            worker = threading.Thread(
                target=self._run, name="F09-S42-evaluation-only",
                daemon=True)
            self._thread = worker
            try:
                worker.start()
            except RuntimeError:
                self._cancel.set()
                self._clock.disable()
                self._clock = None
                self._thread = None
                self._status = "BLOCKED_THREAD"
                return False
            return True

    def _run(self) -> None:
        """F09 documented worker 20s check cadence, cancellable immediately."""
        try:
            while not self._cancel.wait(WORKER_CHECK_SECONDS):
                self.poll_once()
        except Exception:
            # NEVER promote errors to game actions or print settings contents.
            self._cancel.set()
            with self._lock:
                self._status = "BLOCKED_WORKER"
        # Avoid clearing shared clock here; stop() owns join and cleanup.

    def poll_once(self) -> tuple[BlockedScheduleOccurrence, ...]:
        """Read-only evaluation of due events, no callback or action dispatch.

        A concurrent stop takes precedence once the lock is acquired.
        S39 independently suppresses repeated due occurrences.
        """
        with self._lock:
            if self._cancel.is_set() or self._clock is None or self._closed:
                return ()
            try:
                events = self._clock.poll(self._now())
                self._ticks += 1
            except Exception:
                self._cancel.set()
                self._status = "BLOCKED_CLOCK"
                return ()
            blocked = tuple(
                BlockedScheduleOccurrence(event.kind, event.planned_time)
                for event in events
            )
            if blocked:
                self._audit.extend(blocked)
                del self._audit[:-AUDIT_CAP]
            return blocked

    def stop(self, timeout: float = 2.0) -> bool:
        """Cancel + join before permitting restart. Never kill game windows.

        Returns False if worker hasn't exited; start() then refuses a second
        thread until it exits. timeout bounds wait even for a hung clock
        provider. No Event.wait() runaway loop survives normal cancellation.
        """
        if type(timeout) not in (int, float) or not 0 <= timeout <= 30:
            raise ValueError("INVALID_STOP_TIMEOUT")
        with self._lock:
            self._cancel.set()
            thread = self._thread
        if thread is not None and thread is threading.current_thread():
            raise RuntimeError("CANNOT_JOIN_OWN_F09_WORKER")
        if thread is not None and thread.is_alive():
            thread.join(timeout)
        with self._lock:
            if thread is not None and thread.is_alive():
                self._status = "STOPPING"
                return False
            if self._clock is not None:
                self._clock.disable()
                self._clock = None
            self._status = "CLOSED" if self._closed else "STOPPED"
            return True

    def shutdown(self, timeout: float = 2.0) -> bool:
        """Permanently refuse start after requesting cancellation."""
        with self._lock:
            self._closed = True
        return self.stop(timeout)
