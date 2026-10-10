"""S57: C12 original off-screen hide-only Win32 primitive.

Verified source evidence from original TLMTool 2.1.2:
  * C12 hide all game windows to (-2200, -2200)
  * maintain current window sizes; remember GetWindowRect snapshots
  * do not turn window visibility off (Unity must keep rendering)
Restoring original positions vs (0, 0) is CONTRADICTORY in recovered static
docs; no show-side behavior is guessed in this component.

Real backend uses the existing S17 position-only SetWindowPos API.
No mouse, keyboard, injection, network, Proxy or game login activity.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from layout_windows import NativeLayoutBackend
from start_polling import WindowSnapshot
from start_windows import GameWindow, is_game_candidate

HIDE_X = -2200
HIDE_Y = -2200


@dataclass(frozen=True)
class HideResult:
    code: str
    requested: int = 0
    moved: tuple[int, ...] = ()
    unchanged: tuple[int, ...] = ()
    saved_rects: tuple[tuple[int, int, tuple[int, int, int, int]], ...] = ()



@dataclass(frozen=True)
class HiddenResetResult:
    code: str
    checked_hwnds: tuple[int, ...] = ()

class C12HideAll:
    """Hide-only component; unsafe/ambiguous show branch deliberately absent.

    A PARTIAL hide must be reconciled separately using original-proof
    restore semantics. Repeating hide after PARTIAL must not overwrite
    original positions. No UI toggle is exported in this task.
    """

    def __init__(self, backend=None):
        self.backend = backend if backend is not None else NativeLayoutBackend()
        self._state = "VISIBLE"
        self._saved_window_rects: tuple[
            tuple[int, int, tuple[int, int, int, int]], ...] = ()

    @property
    def hidden(self) -> bool:
        return self._state == "HIDDEN"

    @property
    def partial(self) -> bool:
        return self._state == "PARTIAL"

    @property
    def saved_window_rects(self):
        return self._saved_window_rects

    def hide(
        self, snapshot: WindowSnapshot, *, max_windows: int,
        master_hwnd: int | None = None,
        allowed: Callable[[], bool] = lambda: True,
    ) -> HideResult:
        if self._state == "HIDDEN":
            return HideResult("ALREADY_HIDDEN", len(self._saved_window_rects),
                              saved_rects=self._saved_window_rects)
        if self._state == "PARTIAL":
            return HideResult("PARTIAL_HIDE_REQUIRES_RECONCILIATION",
                              len(self._saved_window_rects),
                              saved_rects=self._saved_window_rects)
        if not allowed():
            return HideResult("CANCELLED")
        if type(max_windows) is not int or max_windows <= 0:
            return HideResult("NO_VERIFIED_WINDOW_LIMIT")
        if not isinstance(snapshot, WindowSnapshot) or not snapshot.valid:
            return HideResult("INVALID_CACHE")
        windows = snapshot.windows
        count = len(windows)
        if not count:
            return HideResult("NO_WINDOWS")
        if count > max_windows:
            return HideResult("OVER_VERIFIED_LIMIT", count)
        if (
            any(not isinstance(w, GameWindow) or w.hwnd <= 0 or w.pid <= 0
                or not is_game_candidate(w.process_name, w.class_name, w.title)
                for w in windows)
            or len({w.hwnd for w in windows}) != count
        ):
            return HideResult("INVALID_OR_AMBIGUOUS_CACHE", count)
        if master_hwnd is not None and master_hwnd not in {w.hwnd for w in windows}:
            return HideResult("MASTER_NOT_IN_CACHE", count)

        master = next((w for w in windows if w.hwnd == master_hwnd), windows[0])
        ordered = (master,) + tuple(w for w in windows if w.hwnd != master.hwnd)
        backend = self.backend
        moved: list[int] = []
        unchanged: list[int] = []
        saved: list[tuple[int, int, tuple[int, int, int, int]]] = []

        def finish(code: str) -> HideResult:
            if moved or unchanged:
                # S60: a successful native call alone is not verified movement.
                completed = code == "HIDDEN" and len(moved) + len(unchanged) == count
                self._state = "HIDDEN" if completed else "PARTIAL"
                self._saved_window_rects = tuple(saved)
                if not completed:
                    code += "_PARTIAL"
            return HideResult(code, count, tuple(moved), tuple(unchanged),
                              self._saved_window_rects if self._state != "VISIBLE" else ())

        try:
            live_top_level = set(backend.enumerate_top_level())
            rects: dict[int, tuple[int, int, int, int]] = {}
            # All-or-nothing prevalidation before first native move.
            for w in ordered:
                if w.hwnd not in live_top_level or not backend.is_window(w.hwnd):
                    return HideResult("STALE_NOT_TOP_LEVEL", count)
                if not backend.is_visible(w.hwnd) or backend.process_id(w.hwnd) != w.pid:
                    return HideResult("STALE_OR_REUSED_PID", count)
                if not is_game_candidate(
                    backend.process_executable(w.pid),
                    backend.window_class(w.hwnd),
                    backend.title_with_timeout(w.hwnd, 150),
                ):
                    return HideResult("LIVE_NOT_GAME", count)
                rect = backend.window_rect(w.hwnd)
                if len(rect) != 4 or rect[2] <= rect[0] or rect[3] <= rect[1]:
                    return HideResult("INVALID_WINDOW_RECT", count)
                rects[w.hwnd] = tuple(int(x) for x in rect)

            for w in ordered:
                if not allowed():
                    return finish("CANCELLED")
                if not backend.is_window(w.hwnd) or backend.process_id(w.hwnd) != w.pid:
                    return finish("STALE_BEFORE_MOVE")
                rect = rects[w.hwnd]
                if rect[:2] == (HIDE_X, HIDE_Y):
                    unchanged.append(w.hwnd)
                    saved.append((w.hwnd, w.pid, rect))
                elif backend.move_no_resize(w.hwnd, HIDE_X, HIDE_Y):
                    moved.append(w.hwnd)
                    saved.append((w.hwnd, w.pid, rect))
                else:
                    return finish("SETWINDOWPOS_FAILED")
                # S60 local safety check, not a claim about Nuitka source.
                if not backend.is_window(w.hwnd) or backend.process_id(w.hwnd) != w.pid:
                    return finish("STALE_AFTER_MOVE")
                applied = backend.window_rect(w.hwnd)
                if (len(applied) != 4
                        or tuple(applied[:2]) != (HIDE_X, HIDE_Y)
                        or applied[2] - applied[0] != rect[2] - rect[0]
                        or applied[3] - applied[1] != rect[3] - rect[1]):
                    return finish("MOVE_UNVERIFIED")
            return finish("HIDDEN")
        except (OSError, RuntimeError, ValueError, TypeError):
            return finish("NATIVE_VALIDATION_FAILED")

    def reset_after_verified_layout(
        self, snapshot: WindowSnapshot, *, mode: str,
        master_hwnd: int | None = None,
        allowed: Callable[[], bool] = lambda: True,
    ) -> HiddenResetResult:
        """Reconcile original hidden bookkeeping only AFTER actual C10/C11.

        The recovered EXE proves visible re-layout resets the hidden state.
        This read-only verifier requires every saved HWND/PID to be known
        and EVERY observed game window at its original C10/C11 coordinate.
        It never moves/shows/restores a window. This conservative geometry
        check is a local safety fence, not an assertion about original code.
        Serialize after the C10/C11 worker; do not call on Tk if Win32 slow.
        """
        if self._state == "VISIBLE":
            return HiddenResetResult("NOT_HIDDEN")
        if mode not in ("tight", "diagonal"):
            return HiddenResetResult("UNVERIFIED_LAYOUT_MODE")
        if not allowed():
            return HiddenResetResult("CANCELLED")
        if not isinstance(snapshot, WindowSnapshot) or not snapshot.valid:
            return HiddenResetResult("INVALID_CACHE")
        windows = snapshot.windows
        if (not windows
                or any(not isinstance(w, GameWindow)
                       or w.hwnd <= 0 or w.pid <= 0
                       or not is_game_candidate(
                           w.process_name, w.class_name, w.title)
                       for w in windows)
                or len({w.hwnd for w in windows}) != len(windows)):
            return HiddenResetResult("INVALID_OR_AMBIGUOUS_CACHE")
        by_hwnd = {w.hwnd: w for w in windows}
        if any(by_hwnd.get(h) is None or by_hwnd[h].pid != pid
               for h, pid, _rect in self._saved_window_rects):
            return HiddenResetResult("SAVED_HWND_MISSING_OR_REUSED")
        if master_hwnd is not None and master_hwnd not in by_hwnd:
            return HiddenResetResult("MASTER_NOT_IN_CACHE")
        master = next((w for w in windows if w.hwnd == master_hwnd), windows[0])
        ordered = (master,) + tuple(w for w in windows
                                    if w.hwnd != master.hwnd)
        backend = self.backend
        try:
            active_hwnds = set(backend.enumerate_top_level())
            for index, w in enumerate(ordered):
                if not allowed():
                    return HiddenResetResult("CANCELLED")
                if (w.hwnd not in active_hwnds
                        or not backend.is_window(w.hwnd)
                        or not backend.is_visible(w.hwnd)
                        or backend.process_id(w.hwnd) != w.pid):
                    return HiddenResetResult("STALE_OR_REUSED_PID")
                if not is_game_candidate(
                    backend.process_executable(w.pid),
                    backend.window_class(w.hwnd),
                    backend.title_with_timeout(w.hwnd, 150),
                ):
                    return HiddenResetResult("LIVE_NOT_GAME")
                rect = backend.window_rect(w.hwnd)
                expect = (0, 0) if mode == "tight" else (50*index, 50*index)
                if len(rect) != 4 or rect[:2] != expect:
                    return HiddenResetResult(
                        "LAYOUT_NOT_AT_VERIFIED_VISIBLE_COORDINATES")
            if not allowed():
                return HiddenResetResult("CANCELLED")
        except (OSError, RuntimeError, ValueError, TypeError):
            return HiddenResetResult("NATIVE_VALIDATION_FAILED")

        self._state = "VISIBLE"
        self._saved_window_rects = ()
        return HiddenResetResult(
            "VISIBLE_LAYOUT_VERIFIED_STATE_RESET",
            tuple(w.hwnd for w in ordered),
        )
