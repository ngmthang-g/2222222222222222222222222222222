"""S124 real H12 Farm authorization: verified Info snapshot, account limit, live HWND/PID.

No raw Boolean callback, local token, game memory access or Proxy may grant.
The real signed Info verifier is STILL absent; production fails closed.
"""
from __future__ import annotations

from permission_guard import PermissionGuard
from start_windows import GameWindow, NativeWin32Backend


class TrainRowPermissionGate:
    """H12 _hwnd_alive(expected_pid) + farm_tab + running account limit."""

    def __init__(self, guard=None, running_count=None, backend_factory=None):
        self.guard = guard
        self.running_count = running_count
        self.backend_factory = (
            backend_factory if backend_factory is not None else NativeWin32Backend)

    def permitted(self, window):
        if (type(window) is not GameWindow
                or type(window.hwnd) is not int or window.hwnd <= 0
                or type(window.pid) is not int or window.pid <= 0
                or not isinstance(self.guard, PermissionGuard)
                or not callable(self.running_count)):
            return False
        snap = self.guard.snapshot
        if not snap.has_verified_payload or snap.blocked:
            return False
        try:
            running = self.running_count()
            if type(running) is not int or running <= 0:
                return False
            if not self.guard.has_permission_with_limit("farm_tab", running):
                return False
            backend = self.backend_factory()
            if not backend.is_window(window.hwnd):
                return False
            if not backend.is_visible(window.hwnd):
                return False
            pid = backend.process_id(window.hwnd)
            return type(pid) is int and pid == window.pid
        except Exception:
            return False
