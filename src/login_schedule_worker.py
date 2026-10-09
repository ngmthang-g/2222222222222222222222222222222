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
import time
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
        # S43: serialize the ENTIRE start/stop lifecycle, including join().
        # start() refuses while stop() is still cleaning up an older worker.
        self._lifecycle_lock = threading.Lock()
        self._cancel = threading.Event()
        self._cancel.set()
        self._stop_requested = threading.Event()  # S47: guard pending stop vs idle
        # S48: each concurrently waiting stop owns a cancellation request.
        # Successful cleanup may clear the fence only after the LAST
        # registered stopper completes; never erase another caller's stop.
        self._stop_request_lock = threading.Lock()
        self._pending_stop_callers = 0
        self._thread: threading.Thread | None = None
        self._clock: LoginScheduleClock | None = None
        self._audit: list[BlockedScheduleOccurrence] = []
        self._status = "IDLE"
        self._closed = False
        self._ticks = 0

    @property
    def status(self) -> str:
        # S43: a stalled clock provider may own _lock. Status is read-only
        # diagnostic data and must not hang behind poll_once().
        return self._status

    @property
    def active(self) -> bool:
        thread = self._thread
        return (thread is not None and thread.is_alive()
                and not self._cancel.is_set() and not self._closed)

    @property
    def thread_alive(self) -> bool:
        thread = self._thread
        return thread is not None and thread.is_alive()

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
        if not self._lifecycle_lock.acquire(blocking=False):
            return False
        try:
            return self._start_locked()
        finally:
            self._lifecycle_lock.release()

    def _start_locked(self) -> bool:
        with self._lock:
            if (self._closed or self._stop_requested.is_set()
                    or (self._thread is not None and self._thread.is_alive())):
                return False
            if not self._settings.preview_available:
                self._status = "BLOCKED_SETTINGS"
                return False
            try:
                clock = LoginScheduleClock(
                    close_hhmm=self._settings.close_hhmm,
                    open_hhmm=self._settings.open_hhmm)
                clock.enable(self._now())
                # S46: an external no-wait shutdown request can arrive while
                # the injected time source is blocked inside clock.enable().
                if self._closed or self._stop_requested.is_set():
                    self._status = "CLOSED" if self._closed else "STOPPING"
                    return False
            except Exception:
                # Do not print exceptions: caller settings may contain secrets.
                self._status = "BLOCKED_CLOCK"
                return False
            self._clock = clock
            self._audit.clear()
            self._ticks = 0
            self._cancel.clear()
            if self._closed or self._stop_requested.is_set():
                self._cancel.set()
                self._clock.disable()
                self._clock = None
                self._status = "CLOSED" if self._closed else "STOPPING"
                return False
            self._status = "EVALUATING_ONLY_NO_ACTIONS"
            worker = threading.Thread(
                target=self._run, name="F09-S42-evaluation-only",
                daemon=True)
            self._thread = worker
            try:
                worker.start()
            except (RuntimeError, OSError):
                # S50: native Thread.start may reject OS resources with
                # OSError (including PermissionError). Treat exactly like
                # Python's RuntimeError: never leave an enabled clock or
                # an unstarted Thread presented as live scheduling.
                self._cancel.set()
                self._clock.disable()
                self._clock = None
                self._thread = None
                self._status = "CLOSED" if self._closed else "BLOCKED_THREAD"
                return False
            if self._closed or self._stop_requested.is_set():
                self._cancel.set()
                self._status = "CLOSED" if self._closed else "STOPPING"
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
                current = self._now()
                # stop() sets Event without acquiring this lock. A source
                # that finally unblocks after cancellation must never yield
                # a new due-event record, even a BLOCKED-only audit record.
                if self._cancel.is_set() or self._closed:
                    return ()
                events = self._clock.poll(current)
                if self._cancel.is_set() or self._closed:
                    return ()
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

    def _register_stop_request(self) -> None:
        """S48: count an in-flight stopper before waiting for lifecycle mutex."""
        with self._stop_request_lock:
            self._pending_stop_callers += 1
            self._stop_requested.set()
            self._cancel.set()

    def _end_stop_request(self, cleaned: bool) -> None:
        """Never let one stopper clear a still-waiting stop request.

        A failed/timed-out stop leaves the cancellation fence set until
        a later explicit successful cleanup. Permanent shutdown never clears.
        """
        with self._stop_request_lock:
            self._pending_stop_callers -= 1
            if cleaned and self._pending_stop_callers == 0 and not self._closed:
                self._stop_requested.clear()
                # S49: request_shutdown() is deliberately lock-free for Tk.
                # It can set the permanent closed latch while this clear is
                # in flight. Reassert the one-way fence if closure won that
                # race; a shutdown after this check sets it independently.
                if self._closed:
                    self._stop_requested.set()

    def stop(self, timeout: float = 2.0) -> bool:
        """Bound mutex plus join; preserve ALL concurrent cancellation intents.

        S47's single Event fence could be cleared by stopper A after join,
        while stopper B had signalled stop but was still awaiting the mutex.
        S48 tracks pending stoppers so no start may slip into that gap.
        """
        if type(timeout) not in (int, float) or not 0 <= timeout <= 30:
            raise ValueError("INVALID_STOP_TIMEOUT")
        deadline = time.monotonic() + timeout
        self._register_stop_request()
        acquired = False
        cleaned = False
        try:
            remaining = max(0.0, deadline - time.monotonic())
            acquired = self._lifecycle_lock.acquire(timeout=remaining)
            if not acquired:
                self._status = "STOPPING"
                return False
            thread = self._thread
            if thread is not None and thread is threading.current_thread():
                raise RuntimeError("CANNOT_JOIN_OWN_F09_WORKER")
            if thread is not None and thread.is_alive():
                thread.join(max(0.0, deadline - time.monotonic()))
            if thread is not None and thread.is_alive():
                self._status = "STOPPING"
                return False
            with self._lock:
                if self._clock is not None:
                    self._clock.disable()
                    self._clock = None
                self._status = "CLOSED" if self._closed else "STOPPED"
                cleaned = True
                return True
        finally:
            # Still inside lifecycle mutex if acquired. Fence belongs to
            # every concurrently registered caller, not the first to join.
            self._end_stop_request(cleaned)
            if acquired:
                self._lifecycle_lock.release()

    def request_shutdown(self) -> None:
        """S46: permanently cancel WITHOUT acquiring locks or joining.

        Safe on the Tk creator thread even if a different caller owns the
        lifecycle lock in stop(). The permanent closed latch is checked by
        start() before/after any external clock/start callback; cancelling
        an existing Event.wait(20) is immediate. This never touches Tk,
        game windows, accounts or OS process actions.
        """
        self._closed = True
        self._stop_requested.set()
        self._cancel.set()

    def shutdown(self, timeout: float = 2.0) -> bool:
        """Permanently refuse start; join separately, not on Tk GUI thread."""
        self.request_shutdown()
        return self.stop(timeout)
