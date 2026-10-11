"""S144: original F06 background printable text via real Windows WM_CHAR.

Original F06/keyboard.py confirms WM_CHAR text into target HWND without using
the DLL-key sync protocol; first/last char synchronous. This reconstruction
sends each BMP printable char synchronously with a BOUNDED timeout (a safer
LOCAL ordering choice, NOT claimed to match every Nuitka instruction).
No actual input sender is attached to Login without authentic signed Info,
F05 launch and real game pixel/HWND evidence.

No physical mouse, keyboard global hooks, Ctrl/Enter, injection or Proxy.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Callable, Protocol

from start_polling import WindowSnapshot
from start_windows import (
    GameWindow, NativeWin32Backend, is_game_candidate,
)

WM_CHAR = 0x0102
SMTO_ABORTIFHUNG = 0x0002
WM_CHAR_TIMEOUT_MS = 150  # S144 local timeout, NOT original timing
MAX_PRINTABLE_TEXT_UNITS = 256  # S144 local bound, NOT original account limit


@dataclass(frozen=True)
class TextDeliveryResult:
    code: str
    sent: int = 0
    total: int = 0


class NativeCharPoster:
    """Real Win32 direct HWND WM_CHAR. No SendInput or cursor movement."""

    def __init__(self) -> None:
        if os.name != "nt":
            raise OSError("S144_WINDOWS_REQUIRED")
        import ctypes
        from ctypes import wintypes
        self._ctypes = ctypes
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        self._send = user32.SendMessageTimeoutW
        self._send.argtypes = [
            wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM,
            wintypes.UINT, wintypes.UINT, ctypes.POINTER(ctypes.c_size_t),
        ]
        self._send.restype = wintypes.LPARAM

    def send_bmp_char(self, hwnd: int, scalar: int) -> bool:
        if (type(hwnd) is not int or hwnd <= 0 or
                type(scalar) is not int or not 0x20 <= scalar <= 0xFFFF or
                0xD800 <= scalar <= 0xDFFF):
            return False
        out = self._ctypes.c_size_t()
        return bool(self._send(
            hwnd, WM_CHAR, scalar, 1, SMTO_ABORTIFHUNG,
            WM_CHAR_TIMEOUT_MS, self._ctypes.byref(out)))


class CharPoster(Protocol):
    def send_bmp_char(self, hwnd: int, scalar: int) -> bool: ...


def _safe_printable(text: str) -> bool:
    # Login user/pass is untrusted. No CR/Enter or control instruction is
    # inferred from plaintext. Separate special-key helper remains unbuilt.
    return (type(text) is str and 1 <= len(text) <= MAX_PRINTABLE_TEXT_UNITS
            and all(c.isprintable() and ord(c) <= 0xFFFF and
                    not 0xD800 <= ord(c) <= 0xDFFF for c in text))


def guarded_send_login_text(
    window: GameWindow,
    text: str,
    *,
    snapshot: WindowSnapshot,
    max_windows: int,
    allowed: Callable[[], bool],
    backend=None,
    poster: CharPoster | None = None,
) -> TextDeliveryResult:
    """Send ONLY to a fresh, identified original S08 game HWND+PID.

    Snapshot + independently verified max_windows and separately signed
    allowed() callback are required. Native identity is revalidated before
    EVERY WM_CHAR and immediately after it, so no fallback/recycled HWND.
    The actual Win32 sender is not wired to the unverified product entry.
    A partial native write cannot be rolled back; return PARTIAL, no retries.
    """
    if not _safe_printable(text):
        return TextDeliveryResult("UNSUPPORTED_OR_EMPTY_TEXT")
    count = len(text)
    if (not isinstance(window, GameWindow) or
            not isinstance(snapshot, WindowSnapshot) or not snapshot.valid
            or type(max_windows) is not int or max_windows <= 0
            or len(snapshot.windows) > max_windows
            or window not in snapshot.windows
            or not is_game_candidate(
                window.process_name, window.class_name, window.title)
            or not callable(allowed)):
        return TextDeliveryResult("UNVERIFIED_TARGET", total=count)
    try:
        if allowed() is not True:
            return TextDeliveryResult("PERMISSION_DENIED", total=count)
    except Exception:
        return TextDeliveryResult("PERMISSION_DENIED", total=count)

    backend = backend if backend is not None else NativeWin32Backend()
    poster = poster if poster is not None else NativeCharPoster()

    def fresh() -> bool:
        try:
            if allowed() is not True:
                return False
            # The live list must still contain exactly this HWND.
            tops = tuple(backend.enumerate_top_level())
            if tops.count(window.hwnd) != 1:
                return False
            if not backend.is_window(window.hwnd) or not backend.is_visible(window.hwnd):
                return False
            if backend.process_id(window.hwnd) != window.pid:
                return False
            return is_game_candidate(
                backend.process_executable(window.pid),
                backend.window_class(window.hwnd),
                backend.title_with_timeout(window.hwnd, 150),
            ) and backend.is_window(window.hwnd) and (
                backend.process_id(window.hwnd) == window.pid
            )
        except Exception:
            return False

    sent = 0
    for ch in text:
        if not fresh():
            return TextDeliveryResult(
                "STALE_OR_PERMISSION_REVOKED" if not sent
                else "PARTIAL_STALE_OR_PERMISSION_REVOKED", sent, count)
        try:
            success = poster.send_bmp_char(window.hwnd, ord(ch)) is True
        except Exception:
            success = False
        if not success:
            return TextDeliveryResult(
                "NATIVE_WM_CHAR_FAILED" if not sent
                else "PARTIAL_NATIVE_WM_CHAR_FAILED", sent, count)
        sent += 1
        if not fresh():
            return TextDeliveryResult(
                "PARTIAL_STALE_OR_PERMISSION_REVOKED", sent, count)
    return TextDeliveryResult("WIN32_WM_CHAR_SENT_NOT_GAME_LOGIN", sent, count)
