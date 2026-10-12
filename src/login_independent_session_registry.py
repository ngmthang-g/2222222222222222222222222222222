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

    def __init__(self):
        self._lock = threading.Lock()
        self._sessions: dict[int, _Session] = {}
        self._closed = False

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
        if not self._running(process) or type(hwnd) is not int or hwnd <= 0:
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
        self.prune_exited()
        with self._lock:
            if self._closed:
                return ()
            sessions = tuple(self._sessions.values())
        # All events identify their original process PID/HWND, not a reused
        # shared "last opened window" or account title.
        return tuple(
            event
            for row in sessions
            for event in row.monitor.drain()
            if self._running(row.process)
        )

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
