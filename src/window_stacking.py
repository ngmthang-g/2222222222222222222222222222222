"""S55/S66/S67: C06 source-backed four-mode window stacking + Win32 readback.

The original binary documents C06 move-only commands:
C10: (0,0), C11: (50*index,50*index), Xếp ngang: (50*index,0),
Xếp dọc: (0,50*index); master first and window dimensions unchanged.
This module implements their shared positioning *engine* from the existing
S09 HWND cache and S17 NativeLayoutBackend. It does NOT invent an Auto UI,
mock signed Info privileges, reset a hidden-state tracker that does not yet
exist, or recreate the still-UNKNOWN interaction with the 1s Auto tiler.

No physical mouse input, game login, memory injection or Proxy implementation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from layout_windows import NativeLayoutBackend
from start_polling import WindowSnapshot
from start_windows import GameWindow, is_game_candidate

@dataclass(frozen=True)
class StackResult:
    code: str
    requested: int = 0
    moved: tuple[int,...] = ()
    unchanged: tuple[int,...] = ()

class C10C11WindowStacker:
    """Verifiable shared C06 _move_windows_offset geometry and HWND/PID fencing.

    A caller must supply an already-verified positive max_windows and an
    externally revocable allowed() callback. The real Auto frame/button
    integration is a separate source-backed UI parity task.
    """
    def __init__(self, backend=None):
        self.backend = backend if backend is not None else NativeLayoutBackend()

    def apply(self, snapshot: WindowSnapshot, *, mode: str,
              max_windows: int, master_hwnd: int | None = None,
              allowed: Callable[[], bool] = lambda: True) -> StackResult:
        if mode not in ("tight", "diagonal", "horizontal", "vertical"):
            return StackResult("UNKNOWN_STACK_MODE")
        if not allowed():
            return StackResult("CANCELLED")
        if type(max_windows) is not int or max_windows <= 0:
            return StackResult("NO_VERIFIED_WINDOW_LIMIT")
        if not isinstance(snapshot, WindowSnapshot) or not snapshot.valid:
            return StackResult("INVALID_CACHE")
        windows = snapshot.windows
        count = len(windows)
        if not count:
            return StackResult("NO_WINDOWS")
        if count > max_windows:
            return StackResult("OVER_VERIFIED_LIMIT", count)
        if (any(not isinstance(w, GameWindow) or w.hwnd <= 0 or w.pid <= 0
                or not is_game_candidate(w.process_name, w.class_name, w.title)
                for w in windows)
                or len({w.hwnd for w in windows}) != count):
            return StackResult("INVALID_OR_AMBIGUOUS_CACHE", count)
        if master_hwnd is not None and master_hwnd not in {w.hwnd for w in windows}:
            return StackResult("MASTER_NOT_IN_CACHE", count)

        master = next((w for w in windows if w.hwnd == master_hwnd), windows[0])
        ordered = (master,) + tuple(w for w in windows if w.hwnd != master.hwnd)
        backend = self.backend
        try:
            top_level = set(backend.enumerate_top_level())
            original_rects = {}
            # Validate THE ENTIRE batch before changing any HWND; a stale
            # secondary window must not cause an avoidable partial movement.
            for w in ordered:
                if w.hwnd not in top_level or not backend.is_window(w.hwnd):
                    return StackResult("STALE_NOT_TOP_LEVEL", count)
                if (not backend.is_visible(w.hwnd)
                        or backend.process_id(w.hwnd) != w.pid):
                    return StackResult("STALE_OR_REUSED_PID", count)
                if not is_game_candidate(
                        backend.process_executable(w.pid),
                        backend.window_class(w.hwnd),
                        backend.title_with_timeout(w.hwnd, 150)):
                    return StackResult("LIVE_NOT_GAME", count)
                rect=backend.window_rect(w.hwnd)
                if len(rect) != 4 or rect[2] <= rect[0] or rect[3] <= rect[1]:
                    return StackResult("INVALID_WINDOW_RECT", count)
                original_rects[w.hwnd] = rect

            moved, unchanged = [], []
            for index, w in enumerate(ordered):
                if not allowed():
                    return StackResult("CANCELLED", count, tuple(moved), tuple(unchanged))
                # Original C06 master-first, move-only; no invented resize,
                # tile arithmetic or screen-fit comparison.
                if mode == "tight":
                    target = (0, 0)
                elif mode == "diagonal":
                    target = (50*index, 50*index)
                elif mode == "horizontal":
                    target = (50*index, 0)
                else:
                    target = (0, 50*index)
                if (not backend.is_window(w.hwnd)
                        or backend.process_id(w.hwnd) != w.pid):
                    return StackResult("STALE_BEFORE_MOVE", count,
                                       tuple(moved), tuple(unchanged))
                if original_rects[w.hwnd][:2] == target:
                    unchanged.append(w.hwnd)
                elif backend.move_no_resize(w.hwnd, *target):
                    moved.append(w.hwnd)
                else:
                    return StackResult("SETWINDOWPOS_FAILED", count,
                                       tuple(moved), tuple(unchanged))
                # S67 LOCAL SAFETY: SetWindowPos success is not proof that
                # Win32 actually applied the requested position or kept size.
                # This post-check applies to BOTH moved and already-at-target
                # HWNDs, including the last window in the batch.
                if (not backend.is_window(w.hwnd)
                        or backend.process_id(w.hwnd) != w.pid):
                    return StackResult("STALE_AFTER_MOVE_PARTIAL", count,
                                       tuple(moved), tuple(unchanged))
                applied = backend.window_rect(w.hwnd)
                original = original_rects[w.hwnd]
                if (len(applied) != 4
                        or tuple(applied[:2]) != target
                        or applied[2] - applied[0] != original[2] - original[0]
                        or applied[3] - applied[1] != original[3] - original[1]):
                    return StackResult("MOVE_UNVERIFIED_PARTIAL", count,
                                       tuple(moved), tuple(unchanged))
            code = {
                "tight": "STACK_TIGHT_APPLIED",
                "diagonal": "STACK_DIAGONAL_APPLIED",
                "horizontal": "STACK_HORIZONTAL_APPLIED",
                "vertical": "STACK_VERTICAL_APPLIED",
            }[mode]
            return StackResult(code, count, tuple(moved), tuple(unchanged))
        except (OSError, RuntimeError, ValueError, TypeError):
            return StackResult("NATIVE_VALIDATION_FAILED", count)
