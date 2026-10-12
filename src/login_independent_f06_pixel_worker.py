"""S203 explicit, cancellable off-Tk original-F06 read-only pixel diagnostics.

Never uses usernames/passwords or sends clicks/WM_CHAR/game packets.
The only observable output is frozen, timestamp-fenced native PrintWindow
F06 state evidence from the original compiled TLMTool pixel_data table.
"""
from __future__ import annotations

from pathlib import Path
from queue import Queue, Empty
import threading

from start_polling import StartWindowProducer
from start_windows import GameWindow
from tlm_original_f06_compiled_pixels import (
    CompiledF06Observation, observe_compiled_original_f06,
)


class IndependentOriginalF06PixelWorker:
    def __init__(self, producer: StartWindowProducer):
        if not isinstance(producer, StartWindowProducer):
            raise ValueError("REAL_START_WINDOW_SOURCE_REQUIRED")
        self._producer = producer
        self._lock = threading.Lock()
        self._serial = 0
        self._closed = False
        self._thread = None
        self._cancel = None
        self._events: Queue[tuple[int, str, CompiledF06Observation]] = Queue(
            maxsize=4)

    @property
    def busy(self) -> bool:
        with self._lock:
            return self._thread is not None and self._thread.is_alive()

    def request(self, window: GameWindow, selected_exe: str | Path,
                stage: str) -> bool:
        if (type(window) is not GameWindow
                or not isinstance(selected_exe, (str, Path))
                or stage not in ("form", "update", "enter_game", "active")):
            return False
        with self._lock:
            if (self._closed or
                    (self._thread is not None and self._thread.is_alive())):
                return False
            self._serial += 1
            generation = self._serial
            cancel = threading.Event()
            self._cancel = cancel
            chosen = str(selected_exe)
            thread = threading.Thread(
                target=self._run,
                args=(generation, cancel, window, chosen, stage),
                name="TLM-S203-ReadOnly-OriginalF06Pixels", daemon=True)
            self._thread = thread
            try:
                thread.start()
            except RuntimeError:
                self._thread = None
                return False
            return True

    def _run(self, serial, cancel, window, exe, stage):
        try:
            snapshot = self._producer.read_snapshot()
            report = observe_compiled_original_f06(
                window, snapshot, exe, stage=stage,
                allowed=lambda: not cancel.is_set())
            if type(report) is not CompiledF06Observation:
                report = CompiledF06Observation(
                    "F06_INVALID_NATIVE_READER_RESULT",
                    window.hwnd, window.pid, stage)
        except (OSError, ValueError, RuntimeError, TypeError,
                AttributeError):
            report = CompiledF06Observation(
                "F06_NATIVE_BACKGROUND_WORKER_FAILED",
                window.hwnd, window.pid, stage)
        with self._lock:
            if self._closed or serial != self._serial or cancel.is_set():
                return
            try:
                self._events.put_nowait((serial, exe, report))
            except Exception:
                try:
                    self._events.get_nowait()
                    self._events.put_nowait((serial, exe, report))
                except Empty:
                    pass

    def drain(self) -> tuple[tuple[str, CompiledF06Observation], ...]:
        found = []
        try:
            while True:
                serial, exe, value = self._events.get_nowait()
                with self._lock:
                    if serial == self._serial and not self._closed:
                        found.append((exe, value))
        except Empty:
            return tuple(found)

    def invalidate(self) -> None:
        with self._lock:
            self._serial += 1
            if self._cancel is not None:
                self._cancel.set()
        self.drain()

    def shutdown(self) -> None:
        with self._lock:
            self._closed = True
            self._serial += 1
            if self._cancel is not None:
                self._cancel.set()
        # Native capture may block; it runs on a daemon. Never hang Tk.
