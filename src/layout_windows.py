"""S17 narrow C18 window-layout synchronization on real Win32 HWNDs.

PROVEN: C18 is a repeatable window-layout toggle consuming S09 worker cache;
C06 master index 0; default grid 3x4; SetWindowPos is used by the tool.
UNKNOWN: original exact grid arithmetic, original worker cadence, exact limit
boundary, initial on-state and mode/input-sync interaction.

This S17 SAFE LOCAL POLICY is move-only: preserve original window sizes, use
the first observed current window as master, cell pitch=master size+8 px, no
off-screen moves. Re-apply only when actual positions differ; updates occur
on existing Start cache-maintenance callbacks, NOT a claimed C18 timer.
Must have an independently verified positive max_windows value.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Callable

from start_polling import WindowSnapshot
from start_windows import GameWindow, NativeWin32Backend, is_game_candidate

GRID_COLS_DEFAULT = 3
GRID_ROWS_DEFAULT = 4
LOCAL_CELL_GAP_PX = 8
ORIGINAL_GRID_FORMULA = "UNKNOWN_S17_MOVE_ONLY_LOCAL_POLICY"
ORIGINAL_LAYOUT_CADENCE = "UNKNOWN_USES_EXISTING_C04_CACHE_MAINTENANCE"
ORIGINAL_LIMIT_COMPARATOR = "UNKNOWN_S17_STRICT_GREATER_THAN"
ORIGINAL_INITIAL_LAYOUT_STATE = "UNKNOWN_S17_FAIL_CLOSED_OFF"


@dataclass(frozen=True)
class LayoutResult:
    code: str
    requested: int = 0
    moved: tuple[int, ...] = ()
    unchanged: tuple[int, ...] = ()


class NativeLayoutBackend:
    """Win32 resize-free movement, with native S08 read-only identity backend."""

    SWP_NOSIZE = 0x0001
    SWP_NOZORDER = 0x0004
    SWP_NOACTIVATE = 0x0010

    def __init__(self):
        if os.name != "nt":
            raise OSError("Windows required")
        import ctypes
        from ctypes import wintypes
        self.w = wintypes
        self.user32 = ctypes.WinDLL("user32", use_last_error=True)
        self.observer = NativeWin32Backend()
        self._rect = self.user32.GetWindowRect
        self._rect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
        self._rect.restype = wintypes.BOOL
        self._move = self.user32.SetWindowPos
        self._move.argtypes = [
            wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, wintypes.UINT]
        self._move.restype = wintypes.BOOL
        self._screen = self.user32.GetSystemMetrics
        self._screen.argtypes = [ctypes.c_int]
        self._screen.restype = ctypes.c_int
        self.ctypes = ctypes

    def __getattr__(self, name):
        return getattr(self.observer, name)

    def screen_size(self) -> tuple[int, int]:
        return int(self._screen(0)), int(self._screen(1))

    def window_rect(self, hwnd: int) -> tuple[int, int, int, int]:
        result = self.w.RECT()
        if not self._rect(hwnd, self.ctypes.byref(result)):
            raise OSError("GetWindowRect failed")
        return int(result.left), int(result.top), int(result.right), int(result.bottom)

    def move_no_resize(self, hwnd: int, x: int, y: int) -> bool:
        return bool(self._move(hwnd, 0, int(x), int(y), 0, 0,
                               self.SWP_NOSIZE | self.SWP_NOZORDER |
                               self.SWP_NOACTIVATE))


class C18LayoutSync:
    """Conservative native C18 slice. No input events, no license inference."""

    def __init__(self, backend=None):
        self.backend = backend if backend is not None else NativeLayoutBackend()

    @staticmethod
    def _valid_limit(value) -> bool:
        return type(value) is int and value > 0

    def arrange(self, snapshot: WindowSnapshot, *, max_windows: int,
                cols: int = GRID_COLS_DEFAULT, rows: int = GRID_ROWS_DEFAULT,
                master_hwnd: int | None = None,
                allowed: Callable[[], bool] = lambda: True) -> LayoutResult:
        # Caller revocation is polled by the native worker immediately
        # before each mutation; a late worker cannot keep rearranging.
        if not allowed():
            return LayoutResult("CANCELLED")
        if not self._valid_limit(max_windows):
            return LayoutResult("NO_VERIFIED_WINDOW_LIMIT")
        if not isinstance(snapshot, WindowSnapshot) or not snapshot.valid:
            return LayoutResult("INVALID_CACHE")
        if type(cols) is not int or type(rows) is not int or cols <= 0 or rows <= 0:
            return LayoutResult("INVALID_GRID")
        candidates = snapshot.windows
        n = len(candidates)
        if n == 0:
            return LayoutResult("NO_WINDOWS")
        if n > max_windows:
            return LayoutResult("OVER_VERIFIED_LIMIT", n)
        if n > cols * rows:
            return LayoutResult("GRID_CAPACITY_EXCEEDED", n)
        if (any(not isinstance(w, GameWindow) or w.hwnd <= 0 or w.pid <= 0
                or not is_game_candidate(w.process_name, w.class_name, w.title)
                for w in candidates)
                or len({w.hwnd for w in candidates}) != n):
            return LayoutResult("INVALID_OR_AMBIGUOUS_CACHE", n)

        if master_hwnd is not None and master_hwnd not in {w.hwnd for w in candidates}:
            return LayoutResult("MASTER_NOT_IN_CACHE", n)
        master = next(
            (w for w in candidates if w.hwnd == master_hwnd), candidates[0])
        ordered = (master,) + tuple(w for w in candidates if w.hwnd != master.hwnd)
        backend = self.backend
        try:
            top_level = set(backend.enumerate_top_level())
            sw, sh = backend.screen_size()
            if min(sw, sh) <= 0:
                return LayoutResult("INVALID_SCREEN", n)
            rects = {}
            # Validation is full batch before any window movement. This
            # protects against partial action when one HWND is already stale.
            for w in ordered:
                if w.hwnd not in top_level or not backend.is_window(w.hwnd):
                    return LayoutResult("STALE_NOT_TOP_LEVEL", n)
                if not backend.is_visible(w.hwnd) or backend.process_id(w.hwnd) != w.pid:
                    return LayoutResult("STALE_OR_REUSED_PID", n)
                if not is_game_candidate(
                        backend.process_executable(w.pid),
                        backend.window_class(w.hwnd),
                        backend.title_with_timeout(w.hwnd, 150)):
                    return LayoutResult("LIVE_NOT_GAME", n)
                rect = backend.window_rect(w.hwnd)
                if rect[2] <= rect[0] or rect[3] <= rect[1]:
                    return LayoutResult("INVALID_WINDOW_RECT", n)
                rects[w.hwnd] = rect
            # S17 explicit LOCAL move-only grid arithmetic, not original
            # C06's unknown ww/wh formula (or its unproven 450/40 meaning).
            m = rects[master.hwnd]
            step_x = m[2] - m[0] + LOCAL_CELL_GAP_PX
            step_y = m[3] - m[1] + LOCAL_CELL_GAP_PX
            slots = []
            for i, w in enumerate(ordered):
                x, y = (i % cols) * step_x, (i // cols) * step_y
                r = rects[w.hwnd]
                # Refuse off-screen geometry, do not hide windows or resize.
                if x + r[2] - r[0] > sw or y + r[3] - r[1] > sh:
                    return LayoutResult("LOCAL_GRID_DOES_NOT_FIT_SCREEN", n)
                slots.append((w, x, y))
            moved, unchanged = [], []
            for w, x, y in slots:
                if not allowed():
                    return LayoutResult("CANCELLED", n, tuple(moved), tuple(unchanged))
                # Single last-moment HWND/PID fence before window mutation.
                if not backend.is_window(w.hwnd) or backend.process_id(w.hwnd) != w.pid:
                    return LayoutResult("STALE_BEFORE_MOVE", n,
                                        tuple(moved), tuple(unchanged))
                if rects[w.hwnd][:2] == (x, y):
                    unchanged.append(w.hwnd)
                elif backend.move_no_resize(w.hwnd, x, y):
                    moved.append(w.hwnd)
                else:
                    return LayoutResult("SETWINDOWPOS_FAILED", n,
                                        tuple(moved), tuple(unchanged))
            return LayoutResult("GRID_APPLIED", n, tuple(moved), tuple(unchanged))
        except (OSError, RuntimeError, ValueError):
            return LayoutResult("NATIVE_VALIDATION_FAILED", n)
