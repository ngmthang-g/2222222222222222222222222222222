"""S205 — read-only original TLMTool pixel point/rect/paired-region recognition.

Authentic source: 65 source-verified entries in S204 frozen Nuitka
PIXEL_DATA (owner's TLMTool 2.1.2), ORIGINAL stored CLIENT coords/RGB.
Native capture: source-backed PrintWindow(flag=2) FULL WINDOW + client-
origin offset from actual Win32 HWND geometry, protected by S09 real
HWND/PID, the selected F04 executable and TWO frozen client SHA256s.

Single point (region length 2), rectangle scan (4), paired-region scan
(6 with original companion offset RGB). NEVER auto-correct malformed
colors, unknown tolerance, or use ROI as a game click coordinate.
All results are image evidence only: no item drop, Train, Login, Party,
Phó Bản, Dồn, keyboard input, injected DLL, token or game packet.
Original color_compare exact rounding still not source-proven: reuse the
S203 conservative local per-channel percentage comparison.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math
import time

from login_frozen_client_fingerprint import inspect_installed_frozen_client
from login_printwindow_pixels import CapturedBgra, NativePrintWindowFrame
from start_polling import WindowSnapshot
from start_windows import GameWindow, NativeWin32Backend
from tlm_original_f06_compiled_pixels import (
    _native_target_current,
    _per_channel_percent_close,
    win32_client_to_full_window_offset,
)
from tlm_original_pixel_catalog import original_pixel_spec

MAX_CANDIDATE_PIXELS_LOCAL = 220000
MAX_NATIVE_IMAGE_WIDTH = 2560
MAX_NATIVE_IMAGE_HEIGHT = 1600
MAX_S09_AGE_SECONDS = 7.0


@dataclass(frozen=True)
class OriginalPixelRegionObservation:
    code: str
    section: str
    key: str
    pid: int | None = None
    hwnd: int | None = None
    scanned_candidates: int = 0
    found_client_xy: tuple[int, int] | None = None
    # A matching pixel is NOT proof of the gameplay/action state.
    native_game_state_verified: bool = False
    account_authenticated: bool = False
    action_sent: bool = False


def _read_rgb(frame: CapturedBgra, x: int, y: int):
    if not 0 <= x < frame.width or not 0 <= y < frame.height:
        return None
    idx = (y * frame.width + x) * 4
    b, g, r = frame.bgra[idx:idx+3]
    return r, g, b


def _color_ok(observed, expected, tolerance) -> bool:
    return (observed is not None and len(observed) == 3
            and all(_per_channel_percent_close(actual, source, tolerance)
                    for actual, source in zip(observed, expected)))


def inspect_original_pixel_region(
    window: GameWindow, snapshot: WindowSnapshot,
    selected_executable: str | Path, section: str, key: str,
    *, backend=None, provider=None,
    offset_reader=win32_client_to_full_window_offset,
    clock=time.monotonic, allowed=lambda: False,
) -> OriginalPixelRegionObservation:
    """One off-Tk screen capture of an original source-backed pixel spec."""
    def out(code, examined=0, found=None):
        return OriginalPixelRegionObservation(
            code, section, key,
            window.pid if type(window) is GameWindow else None,
            window.hwnd if type(window) is GameWindow else None,
            examined, found)
    spec = original_pixel_spec(section, key)
    if spec is None:
        return out("ORIGINAL_PIXEL_KEY_NOT_IN_FROZEN_CATALOG")
    if spec.reader_kind not in (
            "SINGLE_CLIENT_PIXEL_READONLY",
            "RECTANGLE_SCAN_SEPARATE_EVIDENCE_REQUIRED",
            "MULTI_PIXEL_SCAN_SEPARATE_EVIDENCE_REQUIRED"):
        return out("ORIGINAL_PIXEL_UNSUPPORTED_" + spec.reader_kind)
    if (type(window) is not GameWindow
            or type(window.hwnd) is not int or window.hwnd <= 0
            or type(window.pid) is not int or window.pid <= 0
            or type(snapshot) is not WindowSnapshot or not snapshot.valid
            or type(snapshot.windows) is not tuple
            or sum(w.hwnd == window.hwnd and w.pid == window.pid
                   for w in snapshot.windows) != 1
            or not isinstance(snapshot.captured_at, (int, float))
            or not math.isfinite(snapshot.captured_at)):
        return out("ORIGINAL_PIXEL_CURRENT_START_WINDOW_REQUIRED")
    if (not isinstance(selected_executable, (str, Path))
            or not callable(allowed) or not callable(offset_reader)
            or not callable(clock)):
        return out("ORIGINAL_PIXEL_CLIENT_AND_CANCEL_BOUNDARY_REQUIRED")

    region = spec.region
    if len(region) == 2:
        x1, y1 = region
        x2, y2 = x1, y1
    else:
        x1, y1, x2, y2 = region[:4]
    if (not all(type(n) is int for n in (x1, y1, x2, y2))
            or x1 < 0 or y1 < 0 or x2 < x1 or y2 < y1):
        return out("ORIGINAL_PIXEL_INVALID_REGION_GEOMETRY")
    scan_count = (x2 - x1 + 1) * (y2 - y1 + 1)
    if scan_count > MAX_CANDIDATE_PIXELS_LOCAL:
        return out("ORIGINAL_PIXEL_ROI_EXCEEDS_LOCAL_CPU_BUDGET")
    try:
        if (allowed() is not True
                or not 0 <= clock() - snapshot.captured_at <= MAX_S09_AGE_SECONDS):
            return out("ORIGINAL_PIXEL_CANCELLED_OR_START_STALE")
        selected = Path(selected_executable)
        if not inspect_installed_frozen_client(selected).known_static_files:
            return out("ORIGINAL_PIXEL_SELECTED_GAME_VERSION_NOT_PROVEN")
        native = backend if backend is not None else NativeWin32Backend()
        if not _native_target_current(window, selected, native):
            return out("ORIGINAL_PIXEL_GAME_HWND_PID_EXE_NOT_VERIFIED")
        before = offset_reader(window.hwnd)
        if before is None or len(before) != 2:
            return out("ORIGINAL_PIXEL_NONCLIENT_OFFSET_UNAVAILABLE")
        bitmap = (provider if provider is not None
                  else NativePrintWindowFrame(printwindow_flags=2)).capture(
                      window.hwnd)
        if (type(bitmap) is not CapturedBgra
                or type(bitmap.width) is not int
                or type(bitmap.height) is not int
                or not 1 <= bitmap.width <= MAX_NATIVE_IMAGE_WIDTH
                or not 1 <= bitmap.height <= MAX_NATIVE_IMAGE_HEIGHT
                or type(bitmap.bgra) is not bytes
                or len(bitmap.bgra) != bitmap.width * bitmap.height * 4):
            return out("ORIGINAL_PIXEL_INVALID_NATIVE_CAPTURE")
        if (offset_reader(window.hwnd) != before
                or not _native_target_current(window, selected, native)
                or allowed() is not True):
            return out("ORIGINAL_PIXEL_NATIVE_GAME_OR_GEOMETRY_CHANGED")
        if (x2 + before[0] >= bitmap.width
                or y2 + before[1] >= bitmap.height
                or not all(type(v) is int and 0 <= v <= 200 for v in before)):
            return out("ORIGINAL_PIXEL_CLIENT_ROI_OUTSIDE_CAPTURE")
        if len(region) == 6:
            dx, dy = region[4:]
            if (not all(type(n) is int and -1000 <= n <= 1000
                        for n in (dx, dy)) or spec.offset is None
                    or len(spec.offset) != 3
                    or not all(type(n) is int and 0 <= n <= 255
                               for n in spec.offset)):
                return out("ORIGINAL_PIXEL_COMPANION_RGB_UNSAFE")
        else:
            dx, dy = 0, 0
        checked = 0
        for y in range(y1, y2 + 1):
            if allowed() is not True:
                return out("ORIGINAL_PIXEL_CANCELLED_DURING_SCAN", checked)
            for x in range(x1, x2 + 1):
                checked += 1
                first = _read_rgb(
                    bitmap, x + before[0], y + before[1])
                if not _color_ok(first, spec.color, spec.tolerance):
                    continue
                if len(region) == 6:
                    companion = _read_rgb(
                        bitmap, x + dx + before[0], y + dy + before[1])
                    if not _color_ok(companion, spec.offset, spec.tolerance):
                        continue
                if (not _native_target_current(window, selected, native)
                        or offset_reader(window.hwnd) != before):
                    return out("ORIGINAL_PIXEL_TARGET_CHANGED_ON_MATCH", checked)
                return out("ORIGINAL_PIXEL_CANDIDATE_FOUND_NOT_GAME_ACTION",
                           checked, (x, y))
        if not _native_target_current(window, selected, native):
            return out("ORIGINAL_PIXEL_TARGET_CHANGED_AFTER_SCAN", checked)
        return out("ORIGINAL_PIXEL_CANDIDATE_NOT_FOUND", checked)
    except (OSError, ValueError, TypeError, OverflowError, RuntimeError,
            AttributeError):
        return out("ORIGINAL_PIXEL_NATIVE_ROI_SCAN_FAILED")
