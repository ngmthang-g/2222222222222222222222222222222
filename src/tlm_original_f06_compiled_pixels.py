"""S203 original F06 PIXEL_DATA from exact owner TLMTool.exe, READ ONLY.

Static proof: original inner TLMTool.exe SHA256
15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22,
compiled Nuitka .pixel_data D7 serialized dict begins at EXE 0x2B97B3E,
ends at 0x2B98EC5. ORIGINAL values include client-relative coordinates,
RGB color, percentage tolerance, and configured timeout.

Original .pixel docs: one full-window PrintWindow(flag=2) frame, translated
by ClientToScreen(0,0) minus GetWindowRect top-left for CLIENT pixels.
Original color_compare uses per-channel PERCENT tolerance; exact rounding
ABI is still unverified so comparison is a local conservative policy.
Screen observation != logged-in account, credentials, mouse or game action.
"""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from pathlib import Path
from tlm_original_pixel_catalog import original_pixel_spec
import ctypes
from ctypes import wintypes
import math
import os
import time

from login_frozen_client_fingerprint import inspect_installed_frozen_client
from login_printwindow_pixels import CapturedBgra, NativePrintWindowFrame
from start_polling import WindowSnapshot
from start_windows import GameWindow, NativeWin32Backend, is_game_candidate, TITLE_TIMEOUT_MS

# One source of truth: all original TLM Nuitka PIXEL_DATA was decoded
# into S204's immutable seven-section catalog. F06 uses these FIVE
# source-verified point entries and no separately typed/guesstimated RGB.
_F06_KEYS = {
    "login.login1": ("login", "login1"),
    "login.login2": ("login", "login2"),
    "login.update": ("login", "update"),
    "login.vaoTroChoi": ("login", "vaoTroChoi"),
    "common.active": ("common", "active"),
}


def _real_original_f06_points():
    result = {}
    for label, (section, key) in _F06_KEYS.items():
        source = original_pixel_spec(section, key)
        if (source is None or
                source.reader_kind != "SINGLE_CLIENT_PIXEL_READONLY"):
            raise RuntimeError("FROZEN_ORIGINAL_F06_POINT_NOT_VALID")
        x, y = source.region
        r, g, b = source.color
        result[label] = (
            x, y, r, g, b, source.tolerance, source.timeout)
    return MappingProxyType(result)


ORIGINAL_F06_PIXELS = _real_original_f06_points()
F06_STAGE_KEYS = {
    "form": ("login.login1", "login.login2"),
    "update": ("login.update",),
    "enter_game": ("login.vaoTroChoi",),
    "active": ("common.active",),
}
MAX_SNAPSHOT_AGE_SECONDS = 7.0


@dataclass(frozen=True)
class CompiledF06Observation:
    code: str
    hwnd: int | None = None
    pid: int | None = None
    stage: str | None = None
    matched_keys: tuple[str, ...] = ()
    screen_observed: bool = False
    # No screen color match can certify server-side session/account login.
    credentials_sent: bool = False
    logged_in: bool = False
    game_actions_authorized: bool = False


def win32_client_to_full_window_offset(hwnd: int) -> tuple[int, int] | None:
    if os.name != "nt" or type(hwnd) is not int or hwnd <= 0:
        return None
    user = ctypes.WinDLL("user32", use_last_error=True)
    get_rect = user.GetWindowRect
    get_rect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    get_rect.restype = wintypes.BOOL
    to_screen = user.ClientToScreen
    to_screen.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.POINT)]
    to_screen.restype = wintypes.BOOL
    rect = wintypes.RECT()
    origin = wintypes.POINT()
    if (not get_rect(hwnd, ctypes.byref(rect))
            or not to_screen(hwnd, ctypes.byref(origin))):
        return None
    offset = (origin.x - rect.left, origin.y - rect.top)
    if not all(type(n) is int and 0 <= n <= 200 for n in offset):
        return None
    return offset


def _per_channel_percent_close(actual: int, expected: int, percent: int) -> bool:
    """Original percentage semantics, local bounded rounding policy."""
    return abs(actual - expected) * 100 <= percent * max(1, actual, expected)


def match_compiled_f06_pixel(
    frame: CapturedBgra, key: str, offset: tuple[int, int],
) -> bool:
    if (type(frame) is not CapturedBgra
            or key not in ORIGINAL_F06_PIXELS
            or type(offset) is not tuple or len(offset) != 2
            or not all(type(v) is int for v in offset)
            or type(frame.bgra) is not bytes
            or type(frame.width) is not int or type(frame.height) is not int
            or not 1 <= frame.width <= 2560
            or not 1 <= frame.height <= 1600
            or len(frame.bgra) != frame.width * frame.height * 4):
        return False
    x, y, r, g, b, percent, _ = ORIGINAL_F06_PIXELS[key]
    x += offset[0]
    y += offset[1]
    if not 0 <= x < frame.width or not 0 <= y < frame.height:
        return False
    try:
        actual = frame.rgb_at(x, y)
    except (ValueError, IndexError, TypeError):
        return False
    return all(_per_channel_percent_close(a, e, percent)
               for a, e in zip(actual, (r, g, b)))


def _native_target_current(window: GameWindow, selected: Path, native) -> bool:
    try:
        exe = native.process_executable(window.pid)
        return (tuple(native.enumerate_top_level()).count(window.hwnd) == 1
                and native.is_window(window.hwnd)
                and native.is_visible(window.hwnd)
                and native.process_id(window.hwnd) == window.pid
                and isinstance(exe, str)
                and os.path.normcase(os.path.normpath(exe)) ==
                    os.path.normcase(os.path.normpath(str(selected)))
                and is_game_candidate(
                    exe, native.window_class(window.hwnd),
                    native.title_with_timeout(window.hwnd, TITLE_TIMEOUT_MS))
                and native.is_window(window.hwnd)
                and native.process_id(window.hwnd) == window.pid)
    except (OSError, ValueError, TypeError, AttributeError, RuntimeError):
        return False


def observe_compiled_original_f06(
    window: GameWindow, snapshot: WindowSnapshot,
    selected_executable: str | Path,
    *, stage: str = "form", backend=None, provider=None,
    offset_reader=win32_client_to_full_window_offset,
    clock=time.monotonic, allowed=lambda: False,
) -> CompiledF06Observation:
    """One bounded background PrintWindow capture with actual original RGB.

    This NEVER enters credentials/clicks or claims account is authenticated.
    The caller must run off Tk (hashing and PrintWindow can block).
    """
    def out(code, matched=(), observed=False):
        return CompiledF06Observation(
            code, window.hwnd if type(window) is GameWindow else None,
            window.pid if type(window) is GameWindow else None, stage,
            tuple(matched), observed)
    if (type(window) is not GameWindow
            or type(window.hwnd) is not int or window.hwnd <= 0
            or type(window.pid) is not int or window.pid <= 0
            or stage not in F06_STAGE_KEYS):
        return out("F06_INVALID_NATIVE_TARGET_OR_STAGE")
    if (type(snapshot) is not WindowSnapshot or not snapshot.valid
            or type(snapshot.windows) is not tuple
            or not isinstance(snapshot.captured_at, (int, float))
            or not math.isfinite(snapshot.captured_at)
            or sum(w.hwnd == window.hwnd and w.pid == window.pid
                   for w in snapshot.windows) != 1):
        return out("F06_REAL_START_SOURCE_REQUIRED")
    try:
        if not 0 <= clock() - snapshot.captured_at <= MAX_SNAPSHOT_AGE_SECONDS:
            return out("F06_START_WINDOW_SNAPSHOT_EXPIRED")
        if (not callable(allowed) or allowed() is not True
                or not callable(offset_reader)):
            return out("F06_OWNER_CANCELLED")
        if not isinstance(selected_executable, (str, Path)):
            return out("F06_SELECTED_GAME_REQUIRED")
        selected = Path(selected_executable)
        if not inspect_installed_frozen_client(selected).known_static_files:
            return out("F06_ORIGINAL_CLIENT_HASH_MISMATCH")
        native = backend if backend is not None else NativeWin32Backend()
        if not _native_target_current(window, selected, native):
            return out("F06_HWND_PID_GAME_EXE_MISMATCH")
        before = offset_reader(window.hwnd)
        if before is None:
            return out("F06_CLIENT_WINDOW_OFFSET_UNKNOWN")
        provider = provider if provider is not None else NativePrintWindowFrame(
            printwindow_flags=2)
        frame = provider.capture(window.hwnd)
        after = offset_reader(window.hwnd)
        if (before != after or not _native_target_current(window, selected, native)
                or allowed() is not True):
            return out("F06_WINDOW_CHANGED_DURING_CAPTURE")
        wanted = F06_STAGE_KEYS[stage]
        found = tuple(k for k in wanted if match_compiled_f06_pixel(
            frame, k, before))
        if len(found) == len(wanted):
            return out("F06_ORIGINAL_PIXEL_STAGE_OBSERVED_NOT_LOGIN", found, True)
        if found:
            return out("F06_ORIGINAL_PIXEL_STAGE_PARTIAL", found)
        return out("F06_ORIGINAL_PIXEL_STAGE_NOT_OBSERVED")
    except (OSError, ValueError, RuntimeError, OverflowError,
            AttributeError, TypeError):
        return out("F06_ORIGINAL_NATIVE_CAPTURE_UNAVAILABLE")
