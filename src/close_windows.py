"""S16: C16 verified WM_CLOSE for genuine, live S08/S09 game HWNDs only.

Original C16 uses PostMessage(WM_CLOSE), not force-kill of the main client.
Fail closed on invalid cache, wrong executable/class/title, stale/reused PID,
missing top-level HWND or failing native APIs. No arbitrary HWND close from UI.

Separate UnityCrashHandler process-tree cleanup is original-backed but not
implemented in S16: unsafe without its exact targeting and lifecycle proof.
The original immediate preview refresh and close confirmation are UNKNOWN.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol

from start_polling import WindowSnapshot
from start_windows import GameWindow, NativeWin32Backend, is_game_candidate

WM_CLOSE = 0x0010


@dataclass(frozen=True)
class CloseResult:
    code: str
    requested: int = 0
    posted: tuple[int, ...] = ()
    skipped: tuple[tuple[int, str], ...] = ()


class CloseBackend(Protocol):
    def enumerate_top_level(self) -> tuple[int, ...]: ...
    def is_window(self, hwnd: int) -> bool: ...
    def is_visible(self, hwnd: int) -> bool: ...
    def process_id(self, hwnd: int) -> int: ...
    def process_executable(self, pid: int) -> str: ...
    def window_class(self, hwnd: int) -> str: ...
    def title_with_timeout(self, hwnd: int, timeout_ms: int) -> str: ...


class ClosePoster(Protocol):
    def post_close(self, hwnd: int) -> bool: ...


class NativeWmClosePoster:
    """Only normal, asynchronous Win32 WM_CLOSE; no termination privilege."""

    def __init__(self) -> None:
        if os.name != "nt":
            raise OSError("Native WM_CLOSE requires Windows")
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        self._post = user32.PostMessageW
        self._post.argtypes = [
            wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
        self._post.restype = wintypes.BOOL

    def post_close(self, hwnd: int) -> bool:
        return bool(self._post(hwnd, WM_CLOSE, 0, 0))


class C16CloseAll:
    """C16 shared utility service, guarded by original S08 candidate identity.

    The Start UI is responsible for permission/selected-tab validity. This
    service also independently validates every cached snapshot target against
    a fresh native top-level HWND/PID/process/class/title before posting.
    """

    def __init__(self, backend: CloseBackend | None = None,
                 poster: ClosePoster | None = None):
        self.backend = backend if backend is not None else NativeWin32Backend()
        self.poster = poster if poster is not None else NativeWmClosePoster()

    def _check(self, item: GameWindow, top_level: frozenset[int]) -> str | None:
        hwnd, pid = item.hwnd, item.pid
        if hwnd <= 0 or pid <= 0 or hwnd not in top_level:
            return "NOT_LIVE_TOP_LEVEL"
        if not is_game_candidate(item.process_name, item.class_name, item.title):
            return "UNVERIFIED_CACHE_GAME_IDENTITY"
        try:
            backend = self.backend
            if not backend.is_window(hwnd) or not backend.is_visible(hwnd):
                return "CLOSED_OR_HIDDEN"
            if backend.process_id(hwnd) != pid:
                return "PID_REUSED"
            path = backend.process_executable(pid)
            cls = backend.window_class(hwnd)
            title = backend.title_with_timeout(hwnd, 150)
            if not is_game_candidate(path, cls, title):
                return "LIVE_GAME_IDENTITY_MISMATCH"
            # Source may have disappeared during the 150ms timed title read.
            if not backend.is_window(hwnd) or backend.process_id(hwnd) != pid:
                return "PID_CHANGED_BEFORE_CLOSE"
            return None
        except Exception:
            return "LIVE_VALIDATION_ERROR"

    def close_all_game_windows(self, snapshot: WindowSnapshot) -> CloseResult:
        if not isinstance(snapshot, WindowSnapshot) or not snapshot.valid:
            return CloseResult("INVALID_CACHE")
        if any(not isinstance(item, GameWindow) for item in snapshot.windows):
            return CloseResult("INVALID_ROW")
        if not snapshot.windows:
            return CloseResult("NO_GAME_WINDOWS")
        cached = snapshot.windows
        # Ambiguous cache must never send even the first destructive message.
        if len({item.hwnd for item in cached}) != len(cached):
            return CloseResult("AMBIGUOUS_HWND", requested=len(cached))
        try:
            live = frozenset(int(h) for h in self.backend.enumerate_top_level())
        except Exception:
            return CloseResult("ENUMERATION_FAILED", requested=len(cached))

        posted: list[int] = []
        skipped: list[tuple[int, str]] = []
        for item in cached:
            reason = self._check(item, live)
            if reason is not None:
                skipped.append((item.hwnd, reason))
                continue
            try:
                # C02 freshness fence immediately before the irreversible post.
                if not self.backend.is_window(item.hwnd):
                    skipped.append((item.hwnd, "CLOSED_BEFORE_POST"))
                elif self.backend.process_id(item.hwnd) != item.pid:
                    skipped.append((item.hwnd, "PID_CHANGED_BEFORE_POST"))
                elif self.poster.post_close(item.hwnd):
                    posted.append(item.hwnd)
                else:
                    skipped.append((item.hwnd, "POSTMESSAGE_FAILED"))
            except Exception:
                skipped.append((item.hwnd, "POSTMESSAGE_ERROR"))

        code = ("WM_CLOSE_POSTED" if posted and not skipped else
                "PARTIAL_WM_CLOSE_POSTED" if posted else "NO_VALID_TARGETS")
        return CloseResult(code, len(cached), tuple(posted), tuple(skipped))
