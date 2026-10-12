"""S190 independent F05 Login window-size normalization, original-backed.

Frozen F05: 1s inspection of visible Login-owned game HWNDs, target
1366×768, no SetWindowPos when already correct. The independent launcher
can currently attest ONLY its most recently Popen-created PID/HWND, so this
loop normalizes *that* window and never silently acts on arbitrary clients.

Reuses S159 real F05LoginResizeMonitor and S08/S17 Win32 backends; does
not require or imitate the original signed Info entitlement. The independent
local ownership predicate must stay live/revocable and process-bound.
"""
from __future__ import annotations

from dataclasses import dataclass
from queue import Empty, Queue
import threading
from typing import Callable, Protocol

from login_resize_monitor import (
    F05LoginResizeMonitor,
    F05_LOGIN_RESIZE_INTERVAL_SECONDS,
    F05_LOGIN_TARGET_WIDTH,
    F05_LOGIN_TARGET_HEIGHT,
    NativeF05ResizeBackend,
)
from start_polling import WindowSnapshot
from start_windows import GameWindow, TITLE_TIMEOUT_MS, is_game_candidate


class CreatedGameProcess(Protocol):
    pid: int
    def poll(self) -> int | None: ...


@dataclass(frozen=True)
class OwnedWindowSizeEvent:
    code: str
    pid: int
    hwnd: int


class OwnedLoginWindowSizeMonitor:
    """Background 1-second F05 loop. NEVER reads or writes Tk widgets.

    On new user launch, the old monitor's unique stop Event is set before
    a new worker is installed. The same Popen handle and native PID/HWND
    are checked immediately before EVERY Win32 SetWindowPos via S159.
    """

    def __init__(
        self,
        *,
        backend_factory: Callable[[], NativeF05ResizeBackend] = NativeF05ResizeBackend,
    ):
        if not callable(backend_factory):
            raise ValueError("F05_WIN32_BACKEND_REQUIRED")
        self._backend_factory = backend_factory
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._stop: threading.Event | None = None
        self._session: tuple[CreatedGameProcess, int] | None = None
        self._closed = False
        self._events: Queue[OwnedWindowSizeEvent] = Queue(maxsize=12)

    def start(self, process: CreatedGameProcess, hwnd: int) -> bool:
        if (process is None or type(getattr(process, "pid", None)) is not int
                or process.pid <= 0 or type(hwnd) is not int or hwnd <= 0):
            return False
        try:
            if process.poll() is not None:
                return False
        except (OSError, RuntimeError, ValueError):
            return False
        with self._lock:
            if self._closed:
                return False
            if self._stop is not None:
                self._stop.set()
            stop = threading.Event()
            session = (process, hwnd)
            self._stop = stop
            self._session = session
            worker = threading.Thread(
                name="TLM-Independent-F05-Resize-1366x768",
                target=self._run, args=(session, stop),
                daemon=True,
            )
            self._thread = worker
            try:
                worker.start()
            except (RuntimeError, OSError):
                self._stop = None
                self._session = None
                self._thread = None
                return False
            return True

    def _owns(self, session: tuple[CreatedGameProcess, int],
              stop: threading.Event) -> bool:
        if stop.is_set():
            return False
        with self._lock:
            if self._closed or self._session is not session or self._stop is not stop:
                return False
        try:
            return session[0].poll() is None
        except (OSError, RuntimeError, ValueError):
            return False

    def _emit(self, session, stop, code: str) -> None:
        if not self._owns(session, stop):
            return
        proc, hwnd = session
        item = OwnedWindowSizeEvent(code, proc.pid, hwnd)
        try:
            self._events.put_nowait(item)
        except Exception:
            try:
                self._events.get_nowait()
                self._events.put_nowait(item)
            except Empty:
                pass

    def _run(self, session: tuple[CreatedGameProcess, int],
             stop: threading.Event):
        proc, hwnd = session
        try:
            backend = self._backend_factory()
            normalizer = F05LoginResizeMonitor(backend)
        except (OSError, RuntimeError, ValueError, TypeError):
            self._emit(session, stop, "RESIZE_NATIVE_BACKEND_UNAVAILABLE")
            return
        first = True
        while not stop.wait(F05_LOGIN_RESIZE_INTERVAL_SECONDS):
            if not self._owns(session, stop):
                return
            try:
                # This is a FRESH native enumeration, not a fabricated
                # window source from the original Start cached UI.
                windows = tuple(backend.enumerate_top_level())
                if (windows.count(hwnd) != 1 or not backend.is_window(hwnd)
                        or not backend.is_visible(hwnd)
                        or backend.process_id(hwnd) != proc.pid):
                    self._emit(session, stop, "RESIZE_GAME_WINDOW_LOST")
                    return
                exe = backend.process_executable(proc.pid)
                cls = backend.window_class(hwnd)
                title = backend.title_with_timeout(hwnd, TITLE_TIMEOUT_MS)
                if (not is_game_candidate(exe, cls, title)
                        or not backend.is_window(hwnd)
                        or backend.process_id(hwnd) != proc.pid):
                    self._emit(session, stop, "RESIZE_TARGET_NOT_GAME")
                    return
                window = GameWindow(hwnd, proc.pid, title, cls, exe)
                real_observation = WindowSnapshot(
                    windows=(window,), valid=True)
                native = normalizer.normalize(
                    real_observation,
                    allowed=lambda: self._owns(session, stop),
                    login_owned=lambda w: (
                        w.hwnd == hwnd and w.pid == proc.pid
                        and self._owns(session, stop)),
                )
                if native.code != "PASS":
                    self._emit(session, stop, "RESIZE_"+native.code)
                    return
                if hwnd in native.resized:
                    # S159 originally has no post-SetWindowPos verification.
                    # S190 conservatively validates the exact requested
                    # outer size after mutation; never claims game readiness.
                    if not self._owns(session, stop):
                        return
                    rect = backend.window_rect(hwnd)
                    if (rect[2]-rect[0], rect[3]-rect[1]) != (
                            F05_LOGIN_TARGET_WIDTH, F05_LOGIN_TARGET_HEIGHT):
                        self._emit(session, stop, "RESIZE_READBACK_MISMATCH")
                        return
                    self._emit(session, stop, "RESIZED_TO_1366X768")
                elif first and hwnd in native.unchanged:
                    self._emit(session, stop, "ALREADY_1366X768")
                first = False
            except (OSError, RuntimeError, ValueError, TypeError, IndexError):
                self._emit(session, stop, "RESIZE_NATIVE_READ_FAILED")
                return

    @property
    def active(self) -> bool:
        with self._lock:
            return (not self._closed and self._thread is not None
                    and self._thread.is_alive()
                    and self._stop is not None
                    and not self._stop.is_set())

    def drain(self) -> tuple[OwnedWindowSizeEvent, ...]:
        result = []
        try:
            while True:
                result.append(self._events.get_nowait())
        except Empty:
            return tuple(result)

    def stop(self):
        with self._lock:
            if self._stop is not None:
                self._stop.set()
            self._session = None
        # The background native worker is a daemon. No join on Tk main thread.

    def shutdown(self):
        with self._lock:
            self._closed = True
            if self._stop is not None:
                self._stop.set()
            self._session = None
        # NEVER terminate the underlying user's game process.
