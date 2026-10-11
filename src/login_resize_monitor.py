"""S159 F05 — original Login-owned game window size normalizer, real Win32.

Frozen original F05 _login_resize_monitor contract:
- every 1 second inspect visible game window GetWindowRect
- call the shared resize_window ONLY when size differs from 1366x768
- avoid repeated SetWindowPos jitter.

Exact original SWP flags, resize_window outer-vs-client math, initial tick
phase and Login-ownership acquisition are UNKNOWN. This bounded native
reconstruction uses outer GetWindowRect size, SWP_NOMOVE | NOZORDER |
NOACTIVATE (a LOCAL choice), and requires BOTH an external verified Login
ownership predicate and an externally authorized signed Info predicate.
It is NOT hooked to user Login or unverified original game identity.

Reuses existing S08 identity + S17 native GetWindowRect/SetWindowPos,
never interacts with game input/memory/credentials or Proxy.
"""
from __future__ import annotations

from dataclasses import dataclass
import threading
from typing import Callable

from layout_windows import NativeLayoutBackend
from start_polling import WindowSnapshot
from start_windows import GameWindow, TITLE_TIMEOUT_MS, is_game_candidate

F05_LOGIN_RESIZE_INTERVAL_SECONDS = 1.0
F05_LOGIN_TARGET_WIDTH = 1366
F05_LOGIN_TARGET_HEIGHT = 768
F05_RESIZE_FLAGS_PARITY = "UNKNOWN_LOCAL_PRESERVE_POSITION_AND_ZORDER"


@dataclass(frozen=True)
class F05ResizeResult:
    code: str
    resized: tuple[int, ...] = ()
    unchanged: tuple[int, ...] = ()
    skipped: tuple[int, ...] = ()


class NativeF05ResizeBackend(NativeLayoutBackend):
    """Actual already-implemented S17 Win32 SetWindowPos, resize-only."""

    SWP_NOMOVE = 0x0002

    def resize_no_move(self, hwnd: int, width: int, height: int) -> bool:
        return bool(self._move(hwnd, 0, 0, 0, int(width), int(height),
                               self.SWP_NOMOVE | self.SWP_NOZORDER |
                               self.SWP_NOACTIVATE))


class F05LoginResizeMonitor:
    """One non-Tk native pass; caller must prove entitlement AND Login ownership."""

    def __init__(self, backend=None):
        self.backend = backend if backend is not None else NativeF05ResizeBackend()

    @staticmethod
    def _granted(callback: Callable[[], bool] | None) -> bool:
        if not callable(callback):
            return False
        try:
            return callback() is True
        except Exception:
            return False

    @staticmethod
    def _login_owner(callback, item: GameWindow) -> bool:
        if not callable(callback):
            return False
        try:
            return callback(item) is True
        except Exception:
            return False

    def normalize(self, snapshot: WindowSnapshot, *,
                  allowed: Callable[[], bool],
                  login_owned: Callable[[GameWindow], bool]) -> F05ResizeResult:
        if not self._granted(allowed):
            return F05ResizeResult("NOT_AUTHORIZED")
        if not isinstance(snapshot, WindowSnapshot) or not snapshot.valid:
            return F05ResizeResult("INVALID_CACHE")
        if not snapshot.windows:
            return F05ResizeResult("NO_LOGIN_WINDOWS")
        if not callable(login_owned):
            return F05ResizeResult("NO_VERIFIED_LOGIN_OWNER")
        rows = snapshot.windows
        if len({w.hwnd for w in rows if isinstance(w, GameWindow)}) != len(rows):
            return F05ResizeResult("AMBIGUOUS_CACHE")
        backend = self.backend
        resized: list[int] = []
        unchanged: list[int] = []
        skipped: list[int] = []
        try:
            visible_top = set(backend.enumerate_top_level())
        except (OSError, ValueError, RuntimeError, TypeError):
            return F05ResizeResult("NATIVE_ENUM_FAILED")
        for window in rows:
            if not self._granted(allowed):
                return F05ResizeResult("AUTH_REVOKED", tuple(resized),
                                       tuple(unchanged), tuple(skipped))
            if not isinstance(window, GameWindow) or (type(window.hwnd) is not int
                    or window.hwnd <= 0 or type(window.pid) is not int
                    or window.pid <= 0):
                return F05ResizeResult("INVALID_GAME_WINDOW",
                                       tuple(resized), tuple(unchanged), tuple(skipped))
            if not self._login_owner(login_owned, window):
                skipped.append(window.hwnd)
                continue
            try:
                hwnd = window.hwnd
                if (hwnd not in visible_top or not backend.is_window(hwnd)
                        or not backend.is_visible(hwnd)
                        or backend.process_id(hwnd) != window.pid):
                    skipped.append(hwnd)
                    continue
                actual_exe = backend.process_executable(window.pid)
                actual_cls = backend.window_class(hwnd)
                actual_title = backend.title_with_timeout(hwnd, TITLE_TIMEOUT_MS)
                # Stronger than a fake cache title alone: Win32 live executable
                # and native class/title must match source-backed game identity.
                if not is_game_candidate(actual_exe, actual_cls, actual_title):
                    skipped.append(hwnd)
                    continue
                rect = backend.window_rect(hwnd)
                if rect[2] <= rect[0] or rect[3] <= rect[1]:
                    skipped.append(hwnd)
                    continue
                width, height = rect[2] - rect[0], rect[3] - rect[1]
                if (width, height) == (F05_LOGIN_TARGET_WIDTH,
                                        F05_LOGIN_TARGET_HEIGHT):
                    unchanged.append(hwnd)
                    continue
                if not self._granted(allowed):
                    return F05ResizeResult("AUTH_REVOKED", tuple(resized),
                                           tuple(unchanged), tuple(skipped))
                if not self._login_owner(login_owned, window):
                    skipped.append(hwnd)
                    continue
                # Last-moment PID/HWND and visibility revalidation before the
                # only Win32 mutating call (never reposition or activate).
                if (not backend.is_window(hwnd) or not backend.is_visible(hwnd)
                        or backend.process_id(hwnd) != window.pid):
                    skipped.append(hwnd)
                    continue
                if backend.resize_no_move(hwnd, F05_LOGIN_TARGET_WIDTH,
                                           F05_LOGIN_TARGET_HEIGHT):
                    resized.append(hwnd)
                else:
                    return F05ResizeResult("RESIZE_FAILED", tuple(resized),
                                           tuple(unchanged), tuple(skipped))
            except (OSError, RuntimeError, ValueError, TypeError):
                skipped.append(window.hwnd)
                continue
        return F05ResizeResult("PASS", tuple(resized),
                               tuple(unchanged), tuple(skipped))

    def run_until_stopped(self, read_snapshot: Callable[[], WindowSnapshot],
                          *, allowed: Callable[[], bool],
                          login_owned: Callable[[GameWindow], bool],
                          stop_event: threading.Event) -> None:
        """A worker loop whose next CHECK is 1 second after prior tick.

        Phase/call-thread design is a reconstruction detail, NOT original
        launch/GUI wiring. Exit immediately on explicit stop or lost Info.
        """
        if not callable(read_snapshot) or stop_event is None:
            return
        while not stop_event.wait(F05_LOGIN_RESIZE_INTERVAL_SECONDS):
            if not self._granted(allowed):
                return
            try:
                snapshot = read_snapshot()
            except Exception:
                return
            result = self.normalize(snapshot, allowed=allowed,
                                    login_owned=login_owned)
            if result.code in ("NOT_AUTHORIZED", "AUTH_REVOKED"):
                return
