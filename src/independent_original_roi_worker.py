"""S206: one shared off-Tk, explicit read-only source-backed ROI inspection worker.

User action selects ONE original pixel_catalog section+key and ONE genuine
S09 WindowSnapshot HWND/PID. The worker loads the F04-selected real game
executable outside Tk, checks native identity+original frozen client hashes
through S205 and publishes an immutable diagnostic, not a gameplay state.

This worker DOES NOT perform periodic scans, automatically click at a
matched coordinate, or enable any in-game activity. Shop/Bag are sections
of original pixel evidence, not newly invented application tabs.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import threading
import time

from login_path import GameDirectoryStore
from start_polling import StartWindowProducer, WindowSnapshot
from start_windows import GameWindow
from tlm_original_pixel_catalog import original_pixel_spec
from tlm_original_pixel_region_reader import (
    OriginalPixelRegionObservation, inspect_original_pixel_region,
)

MAX_RESULT_AGE_SECONDS = 20.0
MAX_SOURCE_AGE_SECONDS = 7.0


@dataclass(frozen=True)
class OriginalRoiDiagnosticResult:
    ticket: int
    section: str
    key: str
    hwnd: int
    pid: int
    code: str
    captured_monotonic: float
    scanned_candidates: int = 0
    found_client_xy: tuple[int, int] | None = None
    # A source-pixel observation does NOT authorize gameplay or login.
    source_gameplay_verified: bool = False
    action_sent: bool = False


class IndependentOriginalRoiWorker:
    def __init__(
        self, producer: StartWindowProducer, settings_file: str | Path,
        *, clock=time.monotonic,
    ):
        if (not isinstance(producer, StartWindowProducer)
                or not isinstance(settings_file, (str, Path))
                or not callable(clock)):
            raise ValueError("S206_REAL_S09_SOURCE_SETTINGS_REQUIRED")
        self.producer = producer
        self.store = GameDirectoryStore(settings_file)
        self.clock = clock
        self._guard = threading.Lock()
        self._closed = False
        self._serial = 0
        self._worker = None
        self._cancel = None
        self._latest: OriginalRoiDiagnosticResult | None = None

    @property
    def busy(self) -> bool:
        with self._guard:
            return self._worker is not None and self._worker.is_alive()

    @property
    def closed(self) -> bool:
        with self._guard:
            return self._closed

    def request(self, window: GameWindow, section: str, key: str) -> int | None:
        """Explicit user-click only. Never queues a second overlapping capture."""
        if (type(window) is not GameWindow or type(window.hwnd) is not int
                or type(window.pid) is not int
                or window.hwnd <= 0 or window.pid <= 0):
            return None
        spec = original_pixel_spec(section, key)
        if spec is None:
            return None
        with self._guard:
            if (self._closed or
                    (self._worker is not None and self._worker.is_alive())):
                return None
            self._serial += 1
            ticket = self._serial
            cancel = threading.Event()
            self._cancel = cancel
            self._latest = None
            thread = threading.Thread(
                target=self._run,
                args=(ticket, cancel, window, section, key),
                name="TLM-S206-Original-ReadOnly-ROI",
                daemon=True)
            self._worker = thread
            try:
                thread.start()
            except RuntimeError:
                self._worker = None
                return None
            return ticket

    def _run(self, ticket: int, cancel: threading.Event, window: GameWindow,
             section: str, key: str):
        def publish(code: str, observed=None):
            if type(observed) is OriginalPixelRegionObservation:
                result = OriginalRoiDiagnosticResult(
                    ticket, section, key, window.hwnd, window.pid,
                    code, self.clock(), observed.scanned_candidates,
                    observed.found_client_xy)
            else:
                result = OriginalRoiDiagnosticResult(
                    ticket, section, key, window.hwnd, window.pid,
                    code, self.clock())
            with self._guard:
                if (not self._closed and not cancel.is_set()
                        and ticket == self._serial):
                    self._latest = result

        try:
            if cancel.is_set() or not self.producer.active:
                publish("S206_NATIVE_START_PRODUCER_INACTIVE")
                return
            first = self.producer.read_snapshot()
            if (type(first) is not WindowSnapshot or not first.valid
                    or first.captured_at is None
                    or not 0 <= self.clock()-first.captured_at
                    <= MAX_SOURCE_AGE_SECONDS
                    or sum(w.hwnd == window.hwnd and w.pid == window.pid
                           for w in first.windows) != 1):
                publish("S206_NATIVE_WINDOW_NOT_IN_FRESH_START_CACHE")
                return
            # File-system/settings I/O is deliberately outside Tk.
            selected = self.store.get_exe_path(self.store.load())
            if selected is None:
                publish("S206_F04_SELECTED_GAME_PATH_UNAVAILABLE")
                return
            result = inspect_original_pixel_region(
                window, first, selected, section, key,
                allowed=lambda: not cancel.is_set())
            # Target/path/source must still be real after expensive Win32
            # hashing and PrintWindow. A newer Start revision is okay only
            # when the set of native HWND/PID identities remains identical.
            after = self.producer.read_snapshot()
            latest_path = self.store.get_exe_path(self.store.load())
            if cancel.is_set():
                return
            if (not self.producer.active
                    or type(after) is not WindowSnapshot or not after.valid
                    or after.captured_at is None
                    or not 0 <= self.clock()-after.captured_at
                    <= MAX_SOURCE_AGE_SECONDS
                    or {(w.hwnd, w.pid) for w in after.windows}
                    != {(w.hwnd, w.pid) for w in first.windows}
                    or latest_path != selected):
                publish("S206_NATIVE_WINDOW_SET_OR_GAME_FOLDER_CHANGED")
                return
            publish(result.code, result)
        except (OSError, RuntimeError, ValueError, TypeError,
                AttributeError, OverflowError):
            publish("S206_NATIVE_ROI_READ_UNAVAILABLE_OR_FAILED")

    def read_result(self, ticket: int | None) -> OriginalRoiDiagnosticResult | None:
        if type(ticket) is not int or ticket <= 0:
            return None
        with self._guard:
            result = None if self._closed else self._latest
        if (result is None or result.ticket != ticket
                or not 0 <= self.clock()-result.captured_monotonic
                <= MAX_RESULT_AGE_SECONDS):
            return None
        # Returning an immutable scan result is not a valid claim about
        # a newly changed HWND; consumer must mark it diagnostic only.
        return result

    def invalidate(self):
        with self._guard:
            self._serial += 1
            self._latest = None
            if self._cancel is not None:
                self._cancel.set()

    def shutdown(self):
        with self._guard:
            self._closed = True
            self._serial += 1
            self._latest = None
            if self._cancel is not None:
                self._cancel.set()
        # Native PrintWindow may block. Never join it on Tk, and never
        # terminate a game process to stop a diagnostic.
