"""S02 InfoTab's verified-token handoff; no invented HTTP endpoint.

The original TLMInfoTab owns device data, token decode/verify, startup API,
heartbeat and UI. S02 reconstructs only the testable in-memory state bridge.
The UI and live network remain UNVERIFIED and are not pretended here.
"""
from __future__ import annotations
from typing import Callable

from permission_guard import PermissionGuard, PermissionSnapshot, VerifiedClaims


class InfoState:
    CURRENT_VERSION = '2.1.2'  # B12 / original info_tab constant

    def __init__(self, on_update: Callable[[PermissionSnapshot], None] | None = None):
        self.permission_guard = PermissionGuard(on_change=on_update)
        self.server_last_result = 'NOT_VERIFIED'
        self._heartbeat_running = False

    def receive_server_token(self, token: str,
                             real_verify_and_decode: Callable[[str], VerifiedClaims]) -> bool:
        result = self.permission_guard.receive_token(token, real_verify_and_decode)
        self.server_last_result = 'VERIFIED_CLAIMS_RECEIVED' if result else 'TOKEN_INVALID_OR_UNVERIFIED'
        return result

    def on_server_error(self) -> None:
        # Conservative S02 behavior. Exact original heartbeat grace is UNKNOWN.
        self.permission_guard.clear()
        self.server_last_result = 'SERVER_UNAVAILABLE'

    def stop_heartbeat(self) -> None:
        # No remote scheduler exists yet: this only clears placeholder state.
        self._heartbeat_running = False
