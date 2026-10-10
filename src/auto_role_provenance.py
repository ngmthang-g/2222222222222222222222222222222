"""S64 C02/C05/C07 original-backed RoleName/HWND/PID identity preflight.

ORIGINAL PROVEN: character info obtains RoleName through PID-keyed Reader,
current rows use HWND+PID identity, C07 Auto tile sorts by RoleName and
forces the master first. UNKNOWN: exact original _sort_key, name fallback,
Unicode collation and x/y/w/h tiling. S09 currently does NOT read RoleName.
No real character-reader implementation is supplied in this module.

This read-only prerequisite NEVER silently sorts followers, guesses labels,
moves HWNDs, touches game memory or offers nonfunctional UI. Caller-supplied
test/worker RoleName readings are not proof of authentic game memory.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from start_polling import WindowSnapshot
from start_windows import GameWindow, NativeWin32Backend, is_game_candidate


@dataclass(frozen=True)
class RoleReading:
    hwnd: int
    pid: int
    role_name: str


@dataclass(frozen=True)
class RolePreflightResult:
    code: str
    requested: int = 0
    verified: tuple[RoleReading, ...] = ()
    ordered: tuple[GameWindow, ...] = ()


class C07RolePreflight:
    """Read-only verified-identity intake; not a reconstructed Reader/sort."""

    def __init__(self, backend=None):
        self.backend = backend if backend is not None else NativeWin32Backend()

    def prepare(
        self, snapshot: WindowSnapshot, *, max_windows: int,
        master_hwnd: int | None, read_role: Callable[[int, int], RoleReading] | None,
        allowed: Callable[[], bool] = lambda: True,
    ) -> RolePreflightResult:
        if not allowed():
            return RolePreflightResult("CANCELLED")
        if type(max_windows) is not int or max_windows <= 0:
            return RolePreflightResult("NO_VERIFIED_WINDOW_LIMIT")
        if not isinstance(snapshot, WindowSnapshot) or not snapshot.valid:
            return RolePreflightResult("INVALID_CACHE")
        windows = snapshot.windows
        count = len(windows)
        if count == 0:
            return RolePreflightResult("NO_WINDOWS")
        if count > max_windows:
            return RolePreflightResult("OVER_VERIFIED_LIMIT", count)
        if (any(not isinstance(w, GameWindow) or type(w.hwnd) is not int
                or type(w.pid) is not int or w.hwnd <= 0 or w.pid <= 0
                or not is_game_candidate(w.process_name, w.class_name, w.title)
                for w in windows)
                or len({w.hwnd for w in windows}) != count):
            return RolePreflightResult("INVALID_OR_AMBIGUOUS_CACHE", count)
        if (type(master_hwnd) is not int
                or master_hwnd not in {w.hwnd for w in windows}):
            return RolePreflightResult("MASTER_NOT_VERIFIED", count)
        if not callable(read_role):
            # Production S09 has no RoleName source yet. No title fallback!
            return RolePreflightResult("ROLE_READER_UNAVAILABLE", count)

        backend = self.backend
        try:
            top_level = set(backend.enumerate_top_level())
            for w in windows:
                if w.hwnd not in top_level or not backend.is_window(w.hwnd):
                    return RolePreflightResult("STALE_NOT_TOP_LEVEL", count)
                if (not backend.is_visible(w.hwnd)
                        or backend.process_id(w.hwnd) != w.pid):
                    return RolePreflightResult("STALE_OR_REUSED_PID", count)
                if not is_game_candidate(
                    backend.process_executable(w.pid),
                    backend.window_class(w.hwnd),
                    backend.title_with_timeout(w.hwnd, 150),
                ):
                    return RolePreflightResult("LIVE_NOT_GAME", count)
        except (OSError, RuntimeError, ValueError, TypeError, AttributeError):
            return RolePreflightResult("NATIVE_VALIDATION_FAILED", count)

        readings: list[RoleReading] = []
        for w in windows:
            if not allowed():
                return RolePreflightResult("CANCELLED", count)
            try:
                if not backend.is_window(w.hwnd) or backend.process_id(w.hwnd) != w.pid:
                    return RolePreflightResult("STALE_BEFORE_READ", count)
                reading = read_role(w.hwnd, w.pid)
                # A caller is never allowed to reuse data from a prior PID.
                if not backend.is_window(w.hwnd) or backend.process_id(w.hwnd) != w.pid:
                    return RolePreflightResult("STALE_AFTER_READ", count)
            except Exception:
                return RolePreflightResult("ROLE_READER_ERROR", count)
            if (not isinstance(reading, RoleReading)
                    or type(reading.hwnd) is not int
                    or type(reading.pid) is not int
                    or reading.hwnd != w.hwnd or reading.pid != w.pid):
                return RolePreflightResult("ROLE_IDENTITY_MISMATCH", count)
            # Keep exact received Unicode; neither infer nor normalize case,
            # accent, HTML processing or fallback from the window title.
            if (not isinstance(reading.role_name, str)
                    or not reading.role_name.strip()):
                return RolePreflightResult("ROLE_NAME_MISSING", count)
            readings.append(reading)

        if not allowed():
            return RolePreflightResult("CANCELLED", count)
        # Verified original: the selected master must lead. With <=1
        # follower the sort comparator is irrelevant; with >=2 followers
        # original _sort_key must be recovered before publishing an order.
        if count <= 2:
            master = next(w for w in windows if w.hwnd == master_hwnd)
            return RolePreflightResult(
                "MASTER_FIRST_WITHOUT_SORT", count, tuple(readings),
                (master,) + tuple(w for w in windows if w.hwnd != master_hwnd))
        return RolePreflightResult(
            "ORIGINAL_SORT_KEY_UNKNOWN", count, tuple(readings))
