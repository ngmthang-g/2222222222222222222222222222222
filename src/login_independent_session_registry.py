"""S191: F05 serialized independent launch: preserve each genuine PID/HWND.

This owner-scoped local session registry is NOT game account identity and
does not infer a RoleName, HP or Login success from a window title. Each row
requires the actual Popen instance created by S188 and a window verified
by S156 while that process is alive. Retained handles prevent mistaken PID
reuse. One independent S190 size monitor per live owned window.

The original maximum account-count licensing and F05 injected profile
mechanisms are intentionally NOT reproduced. Only one launch worker may
create processes at once; no arbitrary synthetic session/count cap.
"""
from __future__ import annotations

from dataclasses import dataclass
import threading

from start_windows import NativeWin32Backend, is_game_candidate, TITLE_TIMEOUT_MS

from login_independent_resize_monitor import (
    OwnedLoginWindowSizeMonitor, OwnedWindowSizeEvent,
)
from login_independent_window_activation import (
    IndependentActivationResult, activate_verified_launched_game,
)


@dataclass(frozen=True)
class OwnedGameWindow:
    pid: int
    hwnd: int
    size_monitor_active: bool


@dataclass
class _Session:
    process: object
    hwnd: int
    monitor: OwnedLoginWindowSizeMonitor


class OwnedLaunchedGameRegistry:
    """All and only real game processes launched by this independent tool.

    Never terminate or detach Windows native processes by PID. Window
    mutation remains restricted to each retained process and HWND pair.
    """

    def __init__(self, *, native_backend_factory=NativeWin32Backend):
        if not callable(native_backend_factory):
            raise ValueError("INVALID_NATIVE_GAME_WINDOW_VALIDATOR")
        self._native_backend_factory = native_backend_factory
        self._lock = threading.Lock()
        self._sessions: dict[int, _Session] = {}
        self._closed = False

    def _native_owned_game(self, process, hwnd: int) -> bool:
        """S08 live Win32 proof, never any PID-owned dialog/fallback window.

        F05/S156 PID lookup may select a visible fallback if the game
        Unity HWND is not ready. Only a true game candidate may be registered.
        This runs in the background *launch* worker, not in Tk's UI thread.
        """
        if not self._running(process) or type(hwnd) is not int or hwnd <= 0:
            return False
        try:
            reader = self._native_backend_factory()
            all_windows = tuple(reader.enumerate_top_level())
            if (all_windows.count(hwnd) != 1
                    or not reader.is_window(hwnd)
                    or not reader.is_visible(hwnd)
                    or reader.process_id(hwnd) != process.pid):
                return False
            exe = reader.process_executable(process.pid)
            cls = reader.window_class(hwnd)
            title = reader.title_with_timeout(hwnd, TITLE_TIMEOUT_MS)
            return (is_game_candidate(exe, cls, title)
                    and reader.is_window(hwnd)
                    and reader.is_visible(hwnd)
                    and reader.process_id(hwnd) == process.pid
                    and self._running(process))
        except (OSError, RuntimeError, ValueError, TypeError, AttributeError):
            return False

    @staticmethod
    def _running(process) -> bool:
        if process is None or type(getattr(process, "pid", None)) is not int:
            return False
        if process.pid <= 0:
            return False
        try:
            return process.poll() is None
        except (OSError, RuntimeError, ValueError):
            return False

    def register(self, process, hwnd: int) -> bool:
        """Add genuine launched Popen and PID-owned hwnd; never PID alone."""
        if not self._native_owned_game(process, hwnd):
            return False
        with self._lock:
            if self._closed or not self._running(process):
                return False
            # Never trust an overwritten PID: a dead entry is not a new
            # game. A live same-PID second record is ambiguous; reject it.
            old = self._sessions.get(process.pid)
            if old is not None:
                if self._running(old.process):
                    return False
                old.monitor.shutdown()
                del self._sessions[process.pid]
            if any(s.hwnd == hwnd for s in self._sessions.values()):
                return False
            monitor = OwnedLoginWindowSizeMonitor()
            self._sessions[process.pid] = _Session(process, hwnd, monitor)
            # A failed monitor spawn does not fabricate a failed launch:
            # the genuine window remains selectable, size status stays off.
            monitor.start(process, hwnd)
            return True

    def prune_exited(self) -> tuple[int, ...]:
        """Read-only Popen poll; revoke prior tool ownership of exited games."""
        with self._lock:
            if self._closed:
                return ()
            ended = tuple(pid for pid, session in self._sessions.items()
                          if not self._running(session.process))
            for pid in ended:
                old = self._sessions.pop(pid)
                old.monitor.shutdown()
            return ended

    def list_windows(self) -> tuple[OwnedGameWindow, ...]:
        self.prune_exited()
        with self._lock:
            if self._closed:
                return ()
            return tuple(
                OwnedGameWindow(pid, s.hwnd, s.monitor.active)
                for pid, s in self._sessions.items()
                if self._running(s.process))

    def latest_live(self) -> OwnedGameWindow | None:
        rows = self.list_windows()
        return rows[-1] if rows else None

    def activate(self, pid: int) -> IndependentActivationResult:
        """Explicit UI request; native helper revalidates HWND/PID/exe."""
        if type(pid) is not int or pid <= 0:
            return IndependentActivationResult("INVALID_SELECTED_OWNED_PID")
        with self._lock:
            if self._closed:
                return IndependentActivationResult("LAUNCH_REGISTRY_CLOSED")
            record = self._sessions.get(pid)
            if record is None:
                return IndependentActivationResult("PID_NOT_OWN_LAUNCHED")
            process, hwnd = record.process, record.hwnd
        if not self._running(process):
            self.prune_exited()
            return IndependentActivationResult("LAUNCHED_PROCESS_EXITED", pid)
        result = activate_verified_launched_game(process, hwnd)
        if result.code in (
                "LAUNCHED_PROCESS_EXITED", "WINDOW_NOT_CURRENT_GAME",
                "WINDOW_CHANGED_AFTER_ACTIVATE", "LAUNCHED_PROCESS_UNVERIFIED"):
            self.remove_if_same(pid, process, hwnd)
        return result

    def remove_if_same(self, pid: int, process, hwnd: int) -> bool:
        with self._lock:
            current = self._sessions.get(pid)
            if (current is None or current.process is not process
                    or current.hwnd != hwnd):
                return False
            self._sessions.pop(pid).monitor.shutdown()
            return True

    def drain_size_events(self) -> tuple[OwnedWindowSizeEvent, ...]:
        """Drain terminal native failures and revoke only their own HWND.

        A game process may remain alive after its Unity window closes.
        Keeping that missing HWND advertised indefinitely is misleading.
        S190's independent monitor already observes the live native window
        once/second. Reuse that proof rather than doing blocking Win32
        scans from Tk on every status-poll tick.
        """
        self.prune_exited()
        with self._lock:
            if self._closed:
                return ()
            sessions = tuple(self._sessions.values())
        # Revoke only when the game HWND/PID identity has been disproved.
        # Failure to resize, transient native enumeration errors or DPI
        # readback mismatch do NOT prove the window stopped existing.
        terminal_codes = {
            "RESIZE_GAME_WINDOW_LOST",
            "RESIZE_TARGET_NOT_GAME",
            "RESIZE_INVALID_GAME_WINDOW",
            "RESIZE_STALE_OR_REUSED_PID",
        }
        published = []
        for row in sessions:
            for event in row.monitor.drain():
                if not self._running(row.process):
                    continue
                published.append(event)
                if event.code in terminal_codes:
                    # Must be identity-checked because another user-click
                    # may have replaced the same numeric PID concurrently.
                    self.remove_if_same(
                        row.process.pid, row.process, row.hwnd)
        return tuple(published)

    @property
    def has_active_size_monitor(self) -> bool:
        with self._lock:
            return (not self._closed and any(
                s.monitor.active for s in self._sessions.values()))

    def shutdown(self):
        with self._lock:
            if self._closed:
                return
            self._closed = True
            sessions = tuple(self._sessions.values())
            self._sessions.clear()
        for session in sessions:
            session.monitor.shutdown()
        # Never kill/terminate a game process owned by the user.
