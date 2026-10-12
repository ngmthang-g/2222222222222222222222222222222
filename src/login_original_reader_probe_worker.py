"""S196 background-only diagnostic of original compiled TLM Reader.

Never touches Tk or sends game actions. One explicit user click -> one
native read-only diagnostic against a window OWN-LAUNCHED by this tool,
after exact frozen client SHA256 check. Results are only diagnostic codes.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from queue import Empty, Queue
import threading

from tlm_original_memory_reader_native import TlmOriginalReadProbe


@dataclass(frozen=True)
class OriginalReaderWorkerResult:
    pid: int
    status: str
    probe: TlmOriginalReadProbe


class OriginalReaderWorker:
    def __init__(self, inspect_owned):
        if not callable(inspect_owned):
            raise ValueError("ORIGINAL_READER_CALLBACK_REQUIRED")
        self._inspect_owned = inspect_owned
        self._lock = threading.Lock()
        self._generation = 0
        self._closed = False
        self._worker = None
        self._events: Queue[tuple[int, OriginalReaderWorkerResult]] = Queue(maxsize=4)

    @property
    def busy(self):
        with self._lock:
            return self._worker is not None and self._worker.is_alive()

    def request(self, pid: int, game_exe: str | Path) -> bool:
        if type(pid) is not int or pid <= 0 or not isinstance(game_exe, (str, Path)):
            return False
        with self._lock:
            if (self._closed or
                    (self._worker is not None and self._worker.is_alive())):
                return False
            self._generation += 1
            generation = self._generation
            thread = threading.Thread(
                target=self._run, args=(generation, pid, str(game_exe)),
                name="TLM-S196-OriginalReader-ReadOnly", daemon=True)
            self._worker = thread
            try:
                thread.start()
            except RuntimeError:
                self._worker = None
                return False
            return True

    def _run(self, generation: int, pid: int, game_exe: str):
        try:
            probe = self._inspect_owned(pid, game_exe)
            if type(probe) is not TlmOriginalReadProbe:
                probe = TlmOriginalReadProbe("ORIGINAL_READER_INVALID_RESULT", pid)
        except (OSError, ValueError, RuntimeError, TypeError):
            probe = TlmOriginalReadProbe("ORIGINAL_READER_BACKGROUND_FAILURE", pid)
        result = OriginalReaderWorkerResult(pid, probe.status, probe)
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

    def drain(self) -> tuple[OriginalReaderWorkerResult, ...]:
        results = []
        try:
            while True:
                generation, item = self._events.get_nowait()
                with self._lock:
                    if not self._closed and generation == self._generation:
                        results.append(item)
        except Empty:
            return tuple(results)

    def invalidate(self):
        with self._lock:
            self._generation += 1
        self.drain()

    def shutdown(self):
        with self._lock:
            self._closed = True
            self._generation += 1
        # A pending Windows-native read may finish, but cannot publish to UI.
        # NEVER kill or suspend a game process.
