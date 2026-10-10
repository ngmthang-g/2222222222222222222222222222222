"""S73 C14 detached independent single-shot read-only HWND/PID discovery.

Original _detached_update_loop is independent of Start-tab visibility; its
EXACT interval and scheduling transitions remain UNKNOWN. This is a useful
INTERNAL one-shot worker boundary, not a claimed original periodic loop.
An external verified owner requests each scan explicitly; there is no timer.

S08 discovery validates native HWND/PID/title/class/executable. A revocation
invalidates a late scan; no old result is republished. No Tk, DWM, login,
game-control, Proxy or synthetic production HWNDs are created here.
"""
from __future__ import annotations

from dataclasses import dataclass
import threading
import time
from typing import Callable

from start_polling import WindowSnapshot
from start_windows import NativeWin32Backend, WindowBackend, discover_game_windows


@dataclass(frozen=True)
class DetachedScanState:
    code: str
    snapshot: WindowSnapshot


class C14DetachedOneShotScanner:
    """Separate owner-controlled worker, never borrowed from Start poller.

    A successful request scans exactly ONCE. On-window-unmap of Start has no
    effect because this object does not own / attach a TkStartCachePoller.
    Only the independent detached owner may request/revoke/shutdown.
    """

    def __init__(self,
                 backend_factory: Callable[[], WindowBackend] = NativeWin32Backend,
                 clock: Callable[[], float] = time.monotonic):
        if not callable(backend_factory) or not callable(clock):
            raise TypeError("backend_factory and clock must be callables")
        self._backend_factory = backend_factory
        self._clock = clock
        self._guard = threading.Lock()
        self._epoch = 0
        self._revision = 0
        self._closed = False
        self._thread: threading.Thread | None = None
        self._state = DetachedScanState("IDLE", WindowSnapshot())

    def read(self) -> DetachedScanState:
        """O(1) thread-safe cache snapshot; no native I/O or Tk wait."""
        with self._guard:
            return self._state

    def request(self, *, max_windows: int,
                allowed: Callable[[], bool]) -> str:
        if not callable(allowed):
            return "PERMISSION_NOT_VERIFIED"
        try:
            if not allowed():
                self.revoke()
                return "PERMISSION_REVOKED"
        except Exception:
            self.revoke()
            return "PERMISSION_NOT_VERIFIED"
        if type(max_windows) is not int or max_windows <= 0:
            self.revoke()
            return "NO_VERIFIED_WINDOW_LIMIT"
        with self._guard:
            if self._closed:
                return "CLOSED"
            if self._thread is not None and self._thread.is_alive():
                return "SCAN_BUSY"
            self._epoch += 1
            self._revision += 1
            epoch, revision = self._epoch, self._revision
            self._state = DetachedScanState(
                "SCANNING", WindowSnapshot(revision=revision))
            worker = threading.Thread(
                target=self._scan,
                args=(epoch, revision, max_windows),
                name="TLM-C14-Detached-OneShot-ReadOnly",
                daemon=True)
            self._thread = worker
            try:
                worker.start()
            except (OSError, RuntimeError):
                self._epoch += 1
                self._state = DetachedScanState(
                    "THREAD_START_FAILED",
                    WindowSnapshot(revision=self._revision,
                                   error="THREAD_START_FAILED"))
                return "THREAD_START_FAILED"
        return "SCAN_STARTED"

    def _scan(self, epoch: int, revision: int, max_windows: int) -> None:
        error = None
        windows = ()
        try:
            # Construct native ctypes backend INSIDE the worker thread.
            backend = self._backend_factory()
            windows = discover_game_windows(backend)
            if len(windows) > max_windows:
                error = "OVER_VERIFIED_LIMIT"
                windows = ()
        except Exception as exc:
            error = "SCAN_ERROR_" + type(exc).__name__
        with self._guard:
            if self._closed or epoch != self._epoch:
                return
            try:
                captured = self._clock()
            except Exception:
                captured = None
                error = "CLOCK_ERROR"
                windows = ()
            self._state = DetachedScanState(
                "READY" if error is None else error,
                WindowSnapshot(revision, tuple(windows), error is None,
                               captured_at=captured, error=error))

    def revoke(self) -> None:
        """Nonblocking. Previously running native scan may exit asynchronously."""
        with self._guard:
            if self._closed:
                return
            self._epoch += 1
            self._revision += 1
            self._state = DetachedScanState(
                "REVOKED", WindowSnapshot(revision=self._revision,
                                           error="REVOKED"))

    def shutdown(self) -> None:
        """Permanent nonblocking close; no join on Tk owner thread."""
        with self._guard:
            if self._closed:
                return
            self._closed = True
            self._epoch += 1
            self._revision += 1
            self._state = DetachedScanState(
                "CLOSED", WindowSnapshot(revision=self._revision,
                                          error="CLOSED"))
