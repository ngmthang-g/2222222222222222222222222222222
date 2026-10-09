"""S08 — read-only Windows game-window discovery for the original Start subsystem.

Original C01 contracts: EnumWindows, visible top-level HWNDs, timed
SendMessageTimeoutW title (150 ms), process/class/title, HWND/PID identity.
C01 cannot prove exact original Boolean grouping, so the conservative gate
below is an EXPLICIT S08 adaptation, not recovered Python source.

No mouse events, process memory reads, DLL/injection, game control,
developer entitlement or license-service integration.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol, Sequence


GAME_PROCESS = "thần long mobile.exe"
UNITY_WINDOW_CLASS = "UnityWndClass"
GAME_TITLE = "Thần Long  Mobile"
TITLE_TIMEOUT_MS = 150
MAX_TITLE_CHARS = 512


def _compact(value: str) -> str:
    """Use Unicode casefold and collapse whitespace (exact original unknown)."""
    return " ".join(value.split()).casefold()


def is_game_candidate(process_name: str, class_name: str, title: str) -> bool:
    """Fail-closed reconstructed predicate; NOT proven original Boolean formula.

    Require actual executable identity AND a supported class or exact title;
    never match Lineage W / an arbitrary Unity window by title alone.
    """
    executable = os.path.basename(process_name.replace("\\", "/"))
    return (_compact(executable) == _compact(GAME_PROCESS)
            and (class_name == UNITY_WINDOW_CLASS
                 or _compact(title) == _compact(GAME_TITLE)))


@dataclass(frozen=True)
class GameWindow:
    hwnd: int
    pid: int
    title: str
    class_name: str
    process_name: str


class WindowBackend(Protocol):
    """Read-only adapter, replaceable in tests. Native uses Win32 ctypes."""
    def enumerate_top_level(self) -> Sequence[int]: ...
    def is_visible(self, hwnd: int) -> bool: ...
    def title_with_timeout(self, hwnd: int, timeout_ms: int) -> str: ...
    def window_class(self, hwnd: int) -> str: ...
    def process_id(self, hwnd: int) -> int: ...
    def process_executable(self, pid: int) -> str: ...
    def is_window(self, hwnd: int) -> bool: ...


def discover_game_windows(backend: WindowBackend) -> tuple[GameWindow, ...]:
    """One bounded, READ-ONLY enumeration; no synthetic/debug accounts.

    The original Start background 3-second producer and Tk 2-second consumer
    are separate later tasks; this API is a single on-demand snapshot.
    """
    accepted: list[GameWindow] = []
    seen: set[int] = set()
    for possible in backend.enumerate_top_level():
        hwnd = int(possible)
        if hwnd <= 0 or hwnd in seen:
            continue
        seen.add(hwnd)
        try:
            if not backend.is_window(hwnd) or not backend.is_visible(hwnd):
                continue
            pid = int(backend.process_id(hwnd))
            if pid <= 0:
                continue
            # Process check first: do not spend 150 ms on every non-game title.
            process_name = backend.process_executable(pid)
            if _compact(os.path.basename(process_name.replace("\\", "/"))) != _compact(GAME_PROCESS):
                continue
            class_name = backend.window_class(hwnd)
            title = backend.title_with_timeout(hwnd, TITLE_TIMEOUT_MS)
            if not is_game_candidate(process_name, class_name, title):
                continue
            # Recheck HWND→PID after potentially timed title operation:
            # refuse HWND values reused while the snapshot was being built.
            if not backend.is_window(hwnd) or backend.process_id(hwnd) != pid:
                continue
            accepted.append(GameWindow(hwnd, pid, title, class_name, process_name))
        except (OSError, RuntimeError, ValueError):
            # Closed/racy/unreadable candidate is skipped, never guessed.
            continue
    return tuple(accepted)


@dataclass(frozen=True)
class WindowDelta:
    added: tuple[GameWindow, ...]
    removed: tuple[GameWindow, ...]
    reused: tuple[tuple[GameWindow, GameWindow], ...]


class WindowRegistry:
    """C02 HWND+PID reconciliation; never silently reuse an old game's row."""
    def __init__(self) -> None:
        self._live: dict[int, GameWindow] = {}

    @property
    def current(self) -> tuple[GameWindow, ...]:
        return tuple(self._live.values())

    def update(self, observed: Sequence[GameWindow]) -> WindowDelta:
        new: dict[int, GameWindow] = {}
        for candidate in observed:
            if candidate.hwnd in new and new[candidate.hwnd].pid != candidate.pid:
                raise ValueError("Ambiguous repeated HWND with changed PID")
            new[candidate.hwnd] = candidate
        old = self._live
        replaced = tuple((old[hwnd], current) for hwnd, current in new.items()
                         if hwnd in old and old[hwnd].pid != current.pid)
        removed = tuple(original for hwnd, original in old.items() if hwnd not in new)
        added = tuple(current for hwnd, current in new.items() if hwnd not in old)
        self._live = new
        return WindowDelta(added=added, removed=removed, reused=replaced)

    def identity_matches(self, hwnd: int, pid: int) -> bool:
        known = self._live.get(hwnd)
        return known is not None and known.pid == pid


class NativeWin32Backend:
    """Win32-only safe API. Does not OpenProcess for memory/injection/VM_WRITE."""

    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    WM_GETTEXT = 0x000D
    WM_GETTEXTLENGTH = 0x000E
    SMTO_BLOCK = 0x0001
    SMTO_ABORTIFHUNG = 0x0002

    def __init__(self):
        if os.name != "nt":
            raise OSError("NativeWin32Backend requires Windows")
        import ctypes
        from ctypes import wintypes
        self.ctypes = ctypes
        self.wintypes = wintypes
        self.user32 = ctypes.WinDLL("user32", use_last_error=True)
        self.kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self.callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

        self._enum = self.user32.EnumWindows
        self._enum.argtypes = [self.callback_type, wintypes.LPARAM]
        self._enum.restype = wintypes.BOOL
        for name in ("IsWindow", "IsWindowVisible"):
            fn = getattr(self.user32, name)
            fn.argtypes = [wintypes.HWND]
            fn.restype = wintypes.BOOL

        self._pid = self.user32.GetWindowThreadProcessId
        self._pid.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
        self._pid.restype = wintypes.DWORD
        self._cls = self.user32.GetClassNameW
        self._cls.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
        self._cls.restype = ctypes.c_int

        self._send = self.user32.SendMessageTimeoutW
        self._send.argtypes = [
            wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM,
            wintypes.UINT, wintypes.UINT, ctypes.POINTER(ctypes.c_size_t),
        ]
        self._send.restype = wintypes.LPARAM

        self._open = self.kernel32.OpenProcess
        self._open.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        self._open.restype = wintypes.HANDLE
        self._query = self.kernel32.QueryFullProcessImageNameW
        self._query.argtypes = [
            wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR,
            ctypes.POINTER(wintypes.DWORD),
        ]
        self._query.restype = wintypes.BOOL
        self._close = self.kernel32.CloseHandle
        self._close.argtypes = [wintypes.HANDLE]
        self._close.restype = wintypes.BOOL

    def enumerate_top_level(self) -> tuple[int, ...]:
        found: list[int] = []

        @self.callback_type
        def collect(hwnd, _):
            found.append(int(hwnd))
            return True

        if not self._enum(collect, 0):
            raise OSError("EnumWindows failed")
        return tuple(found)

    def is_window(self, hwnd: int) -> bool:
        return bool(self.user32.IsWindow(hwnd))

    def is_visible(self, hwnd: int) -> bool:
        return bool(self.user32.IsWindowVisible(hwnd))

    def process_id(self, hwnd: int) -> int:
        pid = self.wintypes.DWORD(0)
        self._pid(hwnd, self.ctypes.byref(pid))
        return int(pid.value)

    def process_executable(self, pid: int) -> str:
        hproc = self._open(self.PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not hproc:
            return ""
        try:
            buf = self.ctypes.create_unicode_buffer(1024)
            length = self.wintypes.DWORD(len(buf))
            if self._query(hproc, 0, buf, self.ctypes.byref(length)):
                return buf.value
            return ""
        finally:
            self._close(hproc)

    def window_class(self, hwnd: int) -> str:
        buf = self.ctypes.create_unicode_buffer(256)
        return buf.value if self._cls(hwnd, buf, len(buf)) > 0 else ""

    def _send_timed(self, hwnd: int, message: int, wparam: int, lparam: int,
                    timeout_ms: int) -> int | None:
        result = self.ctypes.c_size_t(0)
        flags = self.SMTO_BLOCK | self.SMTO_ABORTIFHUNG
        ok = self._send(hwnd, message, wparam, lparam, flags,
                        timeout_ms, self.ctypes.byref(result))
        return int(result.value) if ok else None

    def title_with_timeout(self, hwnd: int, timeout_ms: int = TITLE_TIMEOUT_MS) -> str:
        # Reject unbounded timeout or huge buffers. Every synchronous
        # cross-process WM_GETTEXT request uses SendMessageTimeoutW.
        if timeout_ms < 1 or timeout_ms > 150:
            raise ValueError("Original title timeout is at most 150 ms")
        length = self._send_timed(hwnd, self.WM_GETTEXTLENGTH, 0, 0, timeout_ms)
        if length is None:
            return ""
        count = min(max(0, length), MAX_TITLE_CHARS - 1) + 1
        buf = self.ctypes.create_unicode_buffer(count)
        address = self.ctypes.cast(buf, self.ctypes.c_void_p).value
        received = self._send_timed(hwnd, self.WM_GETTEXT, count, address,
                                    timeout_ms)
        return buf.value if received is not None else ""
