"""C16: source-backed WM_CLOSE game window requests and Unity crash cleanup.

The original frozen EXE proves PostMessage(WM_CLOSE) followed by taskkill
/f /t /im UnityCrashHandler64.exe in shared utils.close_all_game_windows.
This taskkill image-match is GLOBAL and destructive (also affects unrelated
same-name processes); only trigger after at least one real verified game
WM_CLOSE post from the explicitly invoked authorized Start 'Đóng hết'.

The original exact error handling/confirmation/cache-refresh is UNKNOWN.
Never force-terminate Thần Long game processes or use a shell.
"""
from __future__ import annotations

import os
import subprocess
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


CRASH_HANDLER_EXE = "UnityCrashHandler64.exe"
CRASH_HANDLER_TASKKILL_ARGS = ("taskkill", "/f", "/t", "/im", CRASH_HANDLER_EXE)
CRASH_HANDLER_TIMEOUT_SECONDS = 5


class NativeCrashHandlerCleaner:
    """C16's EXACT original image-based taskkill, never any game PID killer.

    Caller must independently verify a genuine game WM_CLOSE was posted.
    This action is global for the image name; Windows /im cannot associate
    it with only one game parent. This side effect is original-backed.
    """

    def run(self) -> str:
        if os.name != "nt":
            return "WINDOWS_ONLY_NOT_RUN"
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            result = subprocess.run(
                list(CRASH_HANDLER_TASKKILL_ARGS),
                shell=False, stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                timeout=CRASH_HANDLER_TIMEOUT_SECONDS,
                creationflags=flags, check=False,
            )
        except (OSError, subprocess.TimeoutExpired, ValueError):
            return "TASKKILL_FAILED"
        # taskkill returns nonzero when no image matched, or access denied.
        # Do not treat this as successful termination.
        return "TASKKILL_SENT" if result.returncode == 0 else "TASKKILL_FAILED_OR_NO_MATCH"


class C16CloseAll:
    """C16 shared utility service, guarded by original S08 candidate identity.

    The Start UI is responsible for permission/selected-tab validity. This
    service also independently validates every cached snapshot target against
    a fresh native top-level HWND/PID/process/class/title before posting.
    """

    def __init__(self, backend: CloseBackend | None = None,
                 poster: ClosePoster | None = None, *,
                 crash_cleanup=None):
        # Only a genuine native Start service obtains automatic original C16
        # taskkill; injected test backends never trigger global process kill.
        native_mode = backend is None and poster is None and os.name == "nt"
        self.backend = backend if backend is not None else NativeWin32Backend()
        self.poster = poster if poster is not None else NativeWmClosePoster()
        self.crash_cleanup = (crash_cleanup if crash_cleanup is not None
                              else NativeCrashHandlerCleaner() if native_mode else None)
        self.last_crash_cleanup = "NOT_RUN"

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

        # Original C16 shared close utility follows normal WM_CLOSE with
        # taskkill /f /t /im UnityCrashHandler64.exe. Its process name
        # matching is GLOBAL; never execute unless at least one legitimate
        # game HWND passed all live-identity checks and accepted WM_CLOSE.
        # An external failure must not turn POSTED into CLOSED.
        self.last_crash_cleanup = "NOT_RUN"
        if posted and self.crash_cleanup is not None:
            try:
                value = self.crash_cleanup.run()
                self.last_crash_cleanup = (
                    value if value in ("TASKKILL_SENT", "TASKKILL_FAILED",
                                       "TASKKILL_FAILED_OR_NO_MATCH",
                                       "WINDOWS_ONLY_NOT_RUN")
                    else "TASKKILL_RESULT_UNVERIFIED")
            except Exception:
                self.last_crash_cleanup = "TASKKILL_FAILED"
        code = ("WM_CLOSE_POSTED" if posted and not skipped else
                "PARTIAL_WM_CLOSE_POSTED" if posted else "NO_VALID_TARGETS")
        return CloseResult(code, len(cached), tuple(posted), tuple(skipped))
