"""S61 original-backed C07 Auto transition reset Win32 primitive.

PROVEN by original TLM 2.1.2 C07: each game HWND returns to (0,0),
1366x768 when entering Auto. C06 resize_window uses GetWindowPlacement,
ShowWindow(SW_SHOWNORMAL), then SetWindowPos with SWP_NOMOVE, NOZORDER,
NOACTIVATE; the separate native move primitive is already S17.
UNKNOWN: original exact call ordering and 1-second tile x/y/w/h math.
This is an independently verifiable worker-only engine, NOT Auto mode UI.

No input sync, game launch, Proxy, memory reads or forged license grants.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

from layout_windows import NativeLayoutBackend
from start_polling import WindowSnapshot
from start_windows import GameWindow, is_game_candidate

AUTO_X = 0
AUTO_Y = 0
AUTO_WIDTH = 1366
AUTO_HEIGHT = 768


class NativeC07Backend(NativeLayoutBackend):
    """Use the original SetWindowPos resize-no-move API family."""

    SWP_NOMOVE = 0x0002
    SW_SHOWNORMAL = 1

    def __init__(self):
        super().__init__()
        from ctypes import wintypes
        class WINDOWPLACEMENT(self.ctypes.Structure):
            _fields_ = [
                ("length", wintypes.UINT),
                ("flags", wintypes.UINT),
                ("showCmd", wintypes.UINT),
                ("ptMinPosition", wintypes.POINT),
                ("ptMaxPosition", wintypes.POINT),
                ("rcNormalPosition", wintypes.RECT),
            ]
        self.WINDOWPLACEMENT = WINDOWPLACEMENT
        self._placement = self.user32.GetWindowPlacement
        self._placement.argtypes = [
            wintypes.HWND, self.ctypes.POINTER(WINDOWPLACEMENT)]
        self._placement.restype = wintypes.BOOL
        self._show = self.user32.ShowWindow
        self._show.argtypes = [wintypes.HWND, self.ctypes.c_int]
        self._show.restype = wintypes.BOOL

    def resize_no_move(self, hwnd: int, width: int, height: int) -> bool:
        state = self.WINDOWPLACEMENT()
        state.length = self.ctypes.sizeof(self.WINDOWPLACEMENT)
        if not self._placement(hwnd, self.ctypes.byref(state)):
            raise OSError("GetWindowPlacement failed")
        if int(state.showCmd) in (2, 6, 7, 11):
            # Original C06: normalize a minimized window before resize.
            # ShowWindow return value is previous visibility, not success.
            self._show(hwnd, self.SW_SHOWNORMAL)
        return bool(self._move(hwnd, 0, 0, 0, int(width), int(height),
                               self.SWP_NOMOVE | self.SWP_NOZORDER |
                               self.SWP_NOACTIVATE))


@dataclass(frozen=True)
class AutoResetResult:
    code: str
    requested: int = 0
    resized: tuple[int, ...] = ()
    moved: tuple[int, ...] = ()
    unchanged: tuple[int, ...] = ()
    saved_rects: tuple[tuple[int, int, tuple[int,int,int,int]], ...] = ()


class C07AutoReset:
    """Verified exact final geometry only; does not implement 1s auto tiling.

    Caller supplies authoritative current cache/limit and revocation gate.
    Call only on a native worker, never directly from the Tk UI callback.
    """
    def __init__(self, backend=None):
        self.backend = backend if backend is not None else NativeC07Backend()

    def apply(
        self, snapshot: WindowSnapshot, *, max_windows: int,
        master_hwnd: int | None = None,
        allowed: Callable[[], bool] = lambda: True,
    ) -> AutoResetResult:
        if not allowed():
            return AutoResetResult("CANCELLED")
        if type(max_windows) is not int or max_windows <= 0:
            return AutoResetResult("NO_VERIFIED_WINDOW_LIMIT")
        if not isinstance(snapshot, WindowSnapshot) or not snapshot.valid:
            return AutoResetResult("INVALID_CACHE")
        windows = snapshot.windows
        n = len(windows)
        if n == 0:
            return AutoResetResult("NO_WINDOWS")
        if n > max_windows:
            return AutoResetResult("OVER_VERIFIED_LIMIT", n)
        if (any(not isinstance(w, GameWindow) or w.hwnd <= 0 or w.pid <= 0
                or not is_game_candidate(w.process_name, w.class_name, w.title)
                for w in windows)
                or len({w.hwnd for w in windows}) != n):
            return AutoResetResult("INVALID_OR_AMBIGUOUS_CACHE", n)
        if master_hwnd is not None and master_hwnd not in {w.hwnd for w in windows}:
            return AutoResetResult("MASTER_NOT_IN_CACHE", n)

        master = next((w for w in windows if w.hwnd == master_hwnd), windows[0])
        ordered = (master,) + tuple(w for w in windows if w.hwnd != master.hwnd)
        native = self.backend
        resized, moved, unchanged = [], [], []
        saved = []

        def finish(code: str) -> AutoResetResult:
            if code != "AUTO_RESET_APPLIED" and (resized or moved or unchanged):
                code += "_PARTIAL"
            return AutoResetResult(
                code, n, tuple(resized), tuple(moved), tuple(unchanged),
                tuple(saved))

        try:
            active = set(native.enumerate_top_level())
            for w in ordered:
                if w.hwnd not in active or not native.is_window(w.hwnd):
                    return AutoResetResult("STALE_NOT_TOP_LEVEL", n)
                if not native.is_visible(w.hwnd) or native.process_id(w.hwnd) != w.pid:
                    return AutoResetResult("STALE_OR_REUSED_PID", n)
                if not is_game_candidate(
                        native.process_executable(w.pid), native.window_class(w.hwnd),
                        native.title_with_timeout(w.hwnd, 150)):
                    return AutoResetResult("LIVE_NOT_GAME", n)
                rect = native.window_rect(w.hwnd)
                if len(rect) != 4 or rect[2] <= rect[0] or rect[3] <= rect[1]:
                    return AutoResetResult("INVALID_WINDOW_RECT", n)
                saved.append((w.hwnd, w.pid, tuple(rect)))

            for w in ordered:
                if not allowed():
                    return finish("CANCELLED")
                if not native.is_window(w.hwnd) or native.process_id(w.hwnd) != w.pid:
                    return finish("STALE_BEFORE_RESET")
                prior = next(rect for h, pid, rect in saved if h == w.hwnd)
                if prior == (AUTO_X, AUTO_Y, AUTO_WIDTH, AUTO_HEIGHT):
                    unchanged.append(w.hwnd)
                    continue
                if (prior[2] - prior[0], prior[3] - prior[1]) != (AUTO_WIDTH, AUTO_HEIGHT):
                    if not native.resize_no_move(w.hwnd, AUTO_WIDTH, AUTO_HEIGHT):
                        return finish("RESIZE_FAILED")
                    resized.append(w.hwnd)
                    if not allowed():
                        return finish("CANCELLED")
                    if not native.is_window(w.hwnd) or native.process_id(w.hwnd) != w.pid:
                        return finish("STALE_AFTER_RESIZE")
                    intermediate = native.window_rect(w.hwnd)
                    if (len(intermediate) != 4 or
                        intermediate[2]-intermediate[0] != AUTO_WIDTH or
                        intermediate[3]-intermediate[1] != AUTO_HEIGHT):
                        return finish("RESIZE_UNVERIFIED")
                current = native.window_rect(w.hwnd)
                if tuple(current[:2]) != (AUTO_X, AUTO_Y):
                    if not native.move_no_resize(w.hwnd, AUTO_X, AUTO_Y):
                        return finish("MOVE_FAILED")
                    moved.append(w.hwnd)
                if not native.is_window(w.hwnd) or native.process_id(w.hwnd) != w.pid:
                    return finish("STALE_AFTER_RESET")
                final = native.window_rect(w.hwnd)
                if tuple(final) != (AUTO_X, AUTO_Y, AUTO_WIDTH, AUTO_HEIGHT):
                    return finish("FINAL_GEOMETRY_UNVERIFIED")
            return finish("AUTO_RESET_APPLIED")
        except (OSError, RuntimeError, ValueError, TypeError, AttributeError):
            return finish("NATIVE_VALIDATION_FAILED")
