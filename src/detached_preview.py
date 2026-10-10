"""S68 C14 read-only detached DWM preview region/session.

ORIGINAL-C14 PROVED: the detached overlay region begins at (0, 768),
width = screen_width - 450 and extends to the screen bottom. It owns distinct
DWM thumbnail destination HWNDs, not the embedded Start preview slots.
Source HWND/PID identity and cleanup are inherited from verified S11/S12.

NOT RECOVERED: exact detached tile spacing/order, automatic open/close timing,
the `Tách rời`/ `Hủy tách`/ `Đóng xem` embedded-visibility state transition.
Therefore callers MUST supply genuine already-placed tile rectangles within an
independently verified host region. This module does not invent UI, cursor
events, game memory reads or auto-open behavior. All Win32 calls belong on
the Tk OWNER thread; do not run on the S09 background producer thread.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

from dwm_preview import (
    NativeDwmBackend, PreviewPlacement, ReadOnlyDwmPreviews,
)
from layout_windows import NativeLayoutBackend
from start_polling import WindowSnapshot
from start_windows import GameWindow, is_game_candidate

DETACHED_TOP = 768
DETACHED_RIGHT_RESERVED = 450


@dataclass(frozen=True)
class DetachedRegion:
    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class DetachedResult:
    code: str
    rendered: tuple[int, ...] = ()
    errors: tuple[tuple[int, str], ...] = ()


def verified_detached_region(screen_width: int, screen_height: int) -> DetachedRegion | None:
    """No guessed screen height or clamp; C14 has no usable region <=768px."""
    if (type(screen_width) is not int or type(screen_height) is not int
            or screen_width <= DETACHED_RIGHT_RESERVED
            or screen_height <= DETACHED_TOP):
        return None
    return DetachedRegion(
        0, DETACHED_TOP, screen_width - DETACHED_RIGHT_RESERVED,
        screen_height - DETACHED_TOP)


class C14DetachedDwmSession:
    """Independent DWM slots for an existing, verified detached HWND host.

    Does NOT create fake Tách rời controls/tiles. Source placement comes from
    a separately measured owner-thread native layout. Entire batch validates
    before changing DWM registrations; any failure clears detached slots.
    The main Start embedded controller is NEVER accessed or closed here.
    """

    def __init__(self, dwm_backend=None, windows_backend=None):
        self._previews = ReadOnlyDwmPreviews(
            dwm_backend if dwm_backend is not None else NativeDwmBackend())
        self._windows = windows_backend if windows_backend is not None else NativeLayoutBackend()
        self._closed = False

    @property
    def active_hwnds(self) -> tuple[int, ...]:
        return self._previews.active_hwnds

    def clear(self) -> None:
        self._previews.clear()

    def shutdown(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._previews.shutdown()

    def _deny(self, code: str) -> DetachedResult:
        self.clear()
        return DetachedResult(code)

    def update(
        self, snapshot: WindowSnapshot, *,
        owner_hwnd: int, owner_pid: int,
        screen_width: int, screen_height: int,
        max_windows: int, placements: Sequence[PreviewPlacement],
        allowed: Callable[[], bool] = lambda: True,
    ) -> DetachedResult:
        if self._closed:
            return DetachedResult("CLOSED")
        if not allowed():
            return self._deny("CANCELLED")
        if type(max_windows) is not int or max_windows <= 0:
            return self._deny("NO_VERIFIED_WINDOW_LIMIT")
        if not isinstance(snapshot, WindowSnapshot) or not snapshot.valid:
            return self._deny("INVALID_CACHE")
        region = verified_detached_region(screen_width, screen_height)
        if region is None:
            return self._deny("NO_USABLE_SCREEN_REGION")
        if (type(owner_hwnd) is not int or type(owner_pid) is not int
                or owner_hwnd <= 0 or owner_pid <= 0):
            return self._deny("INVALID_OWNER")
        windows = snapshot.windows
        count = len(windows)
        if not count:
            return self._deny("NO_WINDOWS")
        if count > max_windows:
            return self._deny("OVER_VERIFIED_LIMIT")
        if (any(not isinstance(w, GameWindow) or type(w.hwnd) is not int
                or type(w.pid) is not int or w.hwnd <= 0 or w.pid <= 0
                or w.hwnd == owner_hwnd
                or not is_game_candidate(w.process_name, w.class_name, w.title)
                for w in windows)
                or len({w.hwnd for w in windows}) != count):
            return self._deny("INVALID_OR_AMBIGUOUS_CACHE")
        if len(placements) != count:
            return self._deny("INCOMPLETE_PLACEMENTS")
        mapping = {w.hwnd: w for w in windows}
        seen: set[int] = set()
        for place in placements:
            if (not isinstance(place, PreviewPlacement)
                    or place.hwnd in seen
                    or place.hwnd not in mapping
                    or place.pid != mapping[place.hwnd].pid
                    or place.owner_hwnd != owner_hwnd
                    or type(place.x) is not int or type(place.y) is not int
                    or type(place.width) is not int or type(place.height) is not int
                    or place.width <= 0 or place.height <= 0
                    or place.x < region.x or place.y < region.y
                    or place.x + place.width > region.x + region.width
                    or place.y + place.height > region.y + region.height):
                return self._deny("INVALID_OR_OUTSIDE_REGION")
            seen.add(place.hwnd)

        b = self._windows
        try:
            tops = set(b.enumerate_top_level())
            if (owner_hwnd not in tops or not b.is_window(owner_hwnd)
                    or not b.is_visible(owner_hwnd)
                    or b.process_id(owner_hwnd) != owner_pid):
                return self._deny("STALE_OR_HIDDEN_OWNER")
            rect = b.window_rect(owner_hwnd)
            if (len(rect) != 4
                    or (rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1])
                    != (region.x, region.y, region.width, region.height)):
                return self._deny("OWNER_REGION_MISMATCH")
            for w in windows:
                if (w.hwnd not in tops or not b.is_window(w.hwnd)
                        or not b.is_visible(w.hwnd)
                        or b.process_id(w.hwnd) != w.pid):
                    return self._deny("STALE_SOURCE_HWND_PID")
                if not is_game_candidate(
                        b.process_executable(w.pid), b.window_class(w.hwnd),
                        b.title_with_timeout(w.hwnd, 150)):
                    return self._deny("LIVE_SOURCE_NOT_GAME")
        except (OSError, ValueError, TypeError, RuntimeError, AttributeError):
            return self._deny("NATIVE_VALIDATION_FAILED")
        if not allowed():
            return self._deny("CANCELLED")
        try:
            result = self._previews.sync(placements)
        except (OSError, ValueError, TypeError, RuntimeError) as exc:
            return self._deny("DWM_REGISTRATION_FAILED_" + type(exc).__name__)
        if result.errors or len(result.rendered) != count:
            self.clear()
            return DetachedResult("DWM_INCOMPLETE", errors=result.errors)
        return DetachedResult("DETACHED_DWM_VISIBLE", result.rendered)
