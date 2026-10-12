"""S199 non-Tk worker for owner-click pre-existing real game HWND reads.

Runs ExistingGameOriginalReader.inspect on a source-provided genuine
GameWindow, NEVER arbitrary PID, no credentials/game action/remote writes.
The Tk Login UI only drains immutable results after generation fencing.
"""
from __future__ import annotations

from queue import Queue, Empty
import threading

from start_windows import GameWindow
from tlm_existing_game_reader import ExistingTlmGameReaderReport


class ExistingOriginalReaderWorker:
    def __init__(self, inspect_window):
        if not callable(inspect_window):
            raise ValueError("REAL_EXISTING_GAME_READER_REQUIRED")
        self._inspect = inspect_window
        self._lock = threading.Lock()
        self._closed = False
        self._generation = 0
        self._thread = None
        self._events: Queue[tuple[int, ExistingTlmGameReaderReport]] = (
            Queue(maxsize=4))

    @property
    def busy(self):
        with self._lock:
            return self._thread is not None and self._thread.is_alive()

    def request(self, window: GameWindow) -> bool:
        if (type(window) is not GameWindow or type(window.pid) is not int
                or window.pid <= 0 or type(window.hwnd) is not int
                or window.hwnd <= 0):
            return False
        with self._lock:
            if (self._closed or
                    (self._thread is not None and self._thread.is_alive())):
                return False
            self._generation += 1
            generation = self._generation
            self._thread = threading.Thread(
                name="TLM-ExistingOriginalReader-S199",
                target=self._run, args=(generation, window), daemon=True)
            try:
                self._thread.start()
            except RuntimeError:
                self._thread = None
                return False
            return True

    def _run(self, generation, window):
        try:
            result = self._inspect(window)
            if type(result) is not ExistingTlmGameReaderReport:
                result = ExistingTlmGameReaderReport(
                    "INVALID_ORIGINAL_READER_RESULT", window.hwnd, window.pid)
        except (OSError, ValueError, TypeError, RuntimeError):
            result = ExistingTlmGameReaderReport(
                "EXISTING_READER_FAILED", window.hwnd, window.pid)
        with self._lock:
            if self._closed or generation != self._generation:
                return
            try:
                self._events.put_nowait((generation, result))
            except Exception:
                try:
                    self._events.get_nowait()
                    self._events.put_nowait((generation, result))
                except Empty:
                    pass

    def drain(self) -> tuple[ExistingTlmGameReaderReport, ...]:
        items = []
        try:
            while True:
                generation, result = self._events.get_nowait()
                with self._lock:
                    if not self._closed and generation == self._generation:
                        items.append(result)
        except Empty:
            return tuple(items)

    def invalidate(self):
        with self._lock:
            self._generation += 1
        self.drain()

    def shutdown(self):
        with self._lock:
            self._closed = True
            self._generation += 1
