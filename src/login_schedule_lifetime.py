"""S45 test-owned F09 Tk preview + blocked-only worker lifetime coordinator.

F09 proves Tk countdown ~1s, worker schedule checks every 20s and
cooperative cancellation. S41/S44 preview and S42/S43 worker were separately
correct but a destroyed tab did not own the independent worker lifetime.

This coordinator is NOT installed in the Login product: authentic Info/F05/F06
launch and close-all handlers are unavailable. It NEVER dispatches game actions,
interprets persisted schedule_on booleans, saves account data or shuts down PC.
"""
from __future__ import annotations

from datetime import datetime
import threading
from typing import Callable

from login_schedule_countdown import TkScheduleCountdownPreview
from login_schedule_settings import ReadOnlyScheduleSettings
from login_schedule_worker import F09ScheduleEvaluationWorker


class F09ReadOnlyTabLifetime:
    """Tie real Tk Label destruction to cancellation of both F09 models.

    Every method affecting Tk is creator-thread-only. close() must never
    join a potentially stalled worker on the Tk GUI thread. The separate
    finish_close() only joins an already-cancelled thread and never touches Tk.
    start() is explicitly TEST-owned, not inferred from raw schedule_on.
    """

    def __init__(self, label, settings: ReadOnlyScheduleSettings,
                 *, now: Callable[[], datetime] | None = None,
                 worker_now: Callable[[], datetime] | None = None):
        if not isinstance(settings, ReadOnlyScheduleSettings):
            raise TypeError("S45_VERIFIED_READONLY_SETTINGS_REQUIRED")
        self._owner_thread = threading.get_ident()
        self._preview = TkScheduleCountdownPreview(label, now=now)
        self._worker = F09ScheduleEvaluationWorker(
            settings, now=worker_now if worker_now is not None else now)
        self._settings = settings
        self._closed = False
        self._status = "IDLE"
        self._label = label
        # S44 preview's own <Destroy> callback is registered first. add='+'
        # retains that owner and any other application-bound handlers.
        self._destroy_binding = label.bind(
            "<Destroy>", self._on_label_destroy, add="+")

    @property
    def preview(self) -> TkScheduleCountdownPreview:
        return self._preview

    @property
    def worker(self) -> F09ScheduleEvaluationWorker:
        return self._worker

    @property
    def status(self) -> str:
        if self._closed and self._status == "CLOSING_WORKER":
            if not self._worker.thread_alive:
                return "CLOSED_PENDING_JOIN"
        return self._status

    @property
    def closed(self) -> bool:
        return self._closed

    def _tk_thread_only(self) -> None:
        if threading.get_ident() != self._owner_thread:
            raise RuntimeError("TK_MAIN_THREAD_REQUIRED")

    def start_preview_and_evaluation(self) -> bool:
        """Explicitly start real preview and read-only due evaluation.

        No product scheduler checkbox, no original persisted boolean decode.
        A partial start rolls back immediately; no worker stays enabled on
        failed Label preview or blocked settings.
        """
        self._tk_thread_only()
        if self._closed or self._status != "IDLE":
            return False
        if not self._settings.preview_available:
            self._status = "BLOCKED_SETTINGS"
            return False
        if not self._preview.preview_start(self._settings):
            self._status = "BLOCKED_PREVIEW"
            return False
        # Reentrant Label callbacks may destroy this widget during start.
        if self._closed or not self._preview.active:
            return False
        if not self._worker.start():
            self._preview.stop()
            if not self._closed:
                self._status = "BLOCKED_WORKER"
            return False
        if self._closed or not self._preview.active:
            # Handles a test-injected worker.start side effect that destroys
            # the Label; real worker is cancelled without blocking Tk.
            self.close()
            return False
        self._status = "READONLY_PREVIEW_AND_BLOCKED_EVALUATION"
        return True

    def _on_label_destroy(self, event) -> None:
        if getattr(event, "widget", None) is self._label:
            self.close()

    def close(self) -> bool:
        """Signal both components once; never wait for stuck worker on Tk.

        The original F09 cooperative cancellation requires stopping the
        worker when scheduling is disabled. Native Tk destruction is a
        lifetime boundary, not permission for open/close/shutdown actions.
        """
        self._tk_thread_only()
        if self._closed:
            return not self._worker.thread_alive
        self._closed = True  # one-way gate BEFORE any reentrant callbacks
        self._preview.shutdown()
        completed = self._worker.shutdown(timeout=0)
        self._status = "CLOSED" if completed else "CLOSING_WORKER"
        return completed

    def finish_close(self, timeout: float = 2.0) -> bool:
        """Join an already-cancelled worker; no Tk calls.

        Can be called after the event loop has been destroyed. Never starts
        scheduling again, even if close() returned while a source was hung.
        """
        if not self._closed:
            raise RuntimeError("S45_CLOSE_MUST_BE_REQUESTED_FIRST")
        finished = self._worker.shutdown(timeout=timeout)
        self._status = "CLOSED" if finished else "CLOSING_WORKER"
        return finished
