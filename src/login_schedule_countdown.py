"""S41 F09 genuine Tk main-thread countdown preview, with cancellation.

Only a real Tk Label and Tk.after are used. S39 supplies daily dates and
S40 supplies read-only, verified HH:MM settings. This module NEVER launches
or closes game windows, spawns scheduler workers, decodes F09 persisted
Boolean tokens, writes settings, or invokes shutdown.

A TEST-owned or future properly authorized caller may request a PREVIEW.
This is not the original schedule_on worker or a working Login action.
"""
from __future__ import annotations

from datetime import datetime
import threading
from typing import Callable

from login_schedule_clock import COUNTDOWN_REFRESH_SECONDS, LoginScheduleClock
from login_schedule_settings import ReadOnlyScheduleSettings

REFRESH_MS = COUNTDOWN_REFRESH_SECONDS * 1000


class TkScheduleCountdownPreview:
    """An actually functioning cancellable Tk Label renderer, never a worker.

    All methods which touch Tk must be called on the creator/Tk thread.
    `preview_start` is an explicitly read-only display action. No persisted
    ON or PC-shutdown flags are interpreted or used as an action command.
    """

    def __init__(self, label, *, now: Callable[[], datetime] | None = None):
        import tkinter as tk

        if not isinstance(label, tk.Label):
            raise TypeError("S41 requires a real Tk Label")
        if now is not None and not callable(now):
            raise TypeError("S41 now provider must be callable")
        self._label = label
        self._now = now or datetime.now
        self._owner_thread = threading.get_ident()
        self._cancel = threading.Event()
        self._cancel.set()
        self._after_id: str | None = None
        self._clock: LoginScheduleClock | None = None
        self._epoch = 0
        self._active = False
        self._closed = False
        self._status = "IDLE"
        self._last_text = ""
        # S44: Tk may destroy Label before the next 1-second after callback.
        # Subscribe on the real widget so active timers are invalidated now.
        self._destroy_binding = self._label.bind(
            "<Destroy>", self._on_label_destroy, add="+")

    def _on_label_destroy(self, event) -> None:
        # Tk sends Destroy for descendants/ancestors during teardown; only
        # the actual owned label may terminate this preview.
        if getattr(event, "widget", None) is self._label:
            self.shutdown()

    def _live(self, epoch: int) -> bool:
        return not self._closed and self.active and epoch == self._epoch

    @property
    def active(self) -> bool:
        return self._active and not self._cancel.is_set()

    @property
    def status(self) -> str:
        return self._status

    @property
    def last_text(self) -> str:
        return self._last_text

    @property
    def has_pending_refresh(self) -> bool:
        return self._after_id is not None

    def _main_thread_only(self) -> None:
        if threading.get_ident() != self._owner_thread:
            raise RuntimeError("TK_MAIN_THREAD_REQUIRED")

    def preview_start(self, settings: ReadOnlyScheduleSettings) -> bool:
        """Start genuine Tk countdown preview (NOT a scheduled game action).

        A second start never schedules a second callback chain. Old persisted
        schedule_on is deliberately ignored, even when it looks truthy.
        """
        self._main_thread_only()
        if self._closed or self.active:
            return False
        if (not isinstance(settings, ReadOnlyScheduleSettings)
                or not settings.preview_available):
            self._status = "BLOCKED_SETTINGS"
            return False
        try:
            if not self._label.winfo_exists():
                self._status = "BLOCKED_TK_LABEL"
                return False
            clock = LoginScheduleClock(
                close_hhmm=settings.close_hhmm,
                open_hhmm=settings.open_hhmm)
            before_now = self._epoch
            clock.enable(self._now())
            # A caller-supplied time provider may re-enter stop()/shutdown.
            if self._closed or self._epoch != before_now:
                return False
            self._clock = clock
            self._epoch += 1
            self._cancel.clear()
            self._active = True
            self._status = "PREVIEW_ONLY"
            self._refresh(self._epoch)
            return self.active
        except Exception:
            # Tk, clock and caller-provided now() failures are not logged.
            # Re-entrant shutdown must NOT be downgraded to BLOCKED_PREVIEW.
            if not self._closed:
                self._stop_internal("BLOCKED_PREVIEW")
            return False

    def _refresh(self, epoch: int) -> None:
        """Run on Tk thread; stale or cancelled callbacks are no-ops."""
        if not self._live(epoch):
            return
        try:
            self._main_thread_only()
            now = self._now()
            if not self._live(epoch):
                return
            if not isinstance(now, datetime):
                raise TypeError("INVALID_PREVIEW_CLOCK")
            # Pure daily rollover only. Drop any returned due events; no
            # F05/F06 callback exists and NONE is implicitly authorized.
            self._clock.poll(now)
            if not self._live(epoch):
                return
            rendered = self._clock.countdown(now)
            self._label.configure(text=rendered)
            if not self._live(epoch):
                return
            self._last_text = rendered
            new_id = self._label.after(
                REFRESH_MS, lambda: self._scheduled_refresh(epoch))
            # Even if an injected callback re-entered stop() from .after(),
            # do not orphan a timer that did not exist when stop() ran.
            if not self._live(epoch):
                try:
                    self._label.after_cancel(new_id)
                except Exception:
                    pass
                return
            self._after_id = new_id
        except Exception:
            if self._live(epoch):
                self._stop_internal("BLOCKED_PREVIEW")

    def _scheduled_refresh(self, epoch: int) -> None:
        # The timer executing now no longer has a pending Tcl after id.
        if epoch != self._epoch or not self.active:
            return
        self._after_id = None
        self._refresh(epoch)

    def _stop_internal(self, status: str) -> None:
        self._epoch += 1
        self._cancel.set()
        self._active = False
        pending = self._after_id
        self._after_id = None
        if self._clock is not None:
            self._clock.disable()
            self._clock = None
        if pending is not None:
            try:
                self._label.after_cancel(pending)
            except Exception:
                pass  # Widget may have been destroyed.
        try:
            if self._label.winfo_exists():
                self._label.configure(text="")
        except Exception:
            pass
        self._last_text = ""
        self._status = status

    def stop(self) -> None:
        """Cooperative Tk preview cancellation, leaves game windows alone."""
        self._main_thread_only()
        if self._closed:
            return
        self._stop_internal("STOPPED")

    def shutdown(self) -> None:
        """Idempotently release after callbacks before owner destroys Label."""
        self._main_thread_only()
        if self._closed:
            return
        self._stop_internal("CLOSED")
        self._closed = True
