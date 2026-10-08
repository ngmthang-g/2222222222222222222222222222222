"""S02 bounded reconstruction of TLM permission state, NOT a license verifier.

Original permission_guard exposes plan status, account limit, heartbeat and
permission methods (E04/E07 and compiled EXE). Actual token format/signature
is unknown here. A separate, *real* token verifier MUST return VerifiedClaims.
No raw JSON, client strings or caller-supplied booleans grant permissions.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, FrozenSet

# Original feature identifiers are referenced by original EXE. This set
# names registered Notebook slots, not a free/paid entitlement policy.
REGISTERED_KEYS = frozenset({
    'start_tab', 'login_tab', 'party_tab', 'farm_tab', 'trainlsv_tab',
    'emu_farm_tab', 'phoban_tab', 'daily_tab', 'donvang_tab', 'rao_tab',
    'toiuu_tab', 'info_tab', 'proxy_tab', 'debug_tab', 'android_tab',
})
DEVELOPER_KEYS = frozenset({'proxy_tab', 'debug_tab', 'android_tab'})


@dataclass(frozen=True)
class VerifiedClaims:
    """Normalized *verified* token claims delivered by future auth adapter.

    This is an interface contract, not proof that any real server has been
    contacted. No live producer exists yet; tests use explicit fake adapters.
    """
    permissions: FrozenSet[str]
    plan_status: str
    max_windows: int
    developer: bool = False
    version_locked: bool = False
    server_locked: bool = False
    expires: bool = False


@dataclass(frozen=True)
class PermissionSnapshot:
    has_verified_payload: bool = False
    permissions: FrozenSet[str] = frozenset()
    plan_status: str = 'UNKNOWN'
    max_windows: int = 0
    developer: bool = False
    version_locked: bool = False
    server_locked: bool = False
    expired: bool = False

    @property
    def blocked(self) -> bool:
        return (not self.has_verified_payload or self.version_locked
                or self.server_locked or self.expired
                or self.plan_status.strip().lower() in {'ban', 'banned', 'expired', 'over_limit', 'over_device'})

    @property
    def authorized_keys(self) -> FrozenSet[str]:
        if self.blocked:
            return frozenset({'info_tab'})
        value = self.permissions & REGISTERED_KEYS
        if not self.developer:
            value -= DEVELOPER_KEYS
        return frozenset(value | {'info_tab'})


class PermissionGuard:
    """Permission snapshot manager that defaults to deny (Info only).

    Real signature verification, default-free policy, token expiry clock and
    account counting are future tasks: see S02 report. Do not use this class
    as a cryptographic security boundary.
    """

    def __init__(self, on_change: Callable[[PermissionSnapshot], None] | None = None):
        self._snapshot = PermissionSnapshot()
        self._on_change = on_change

    @property
    def snapshot(self) -> PermissionSnapshot:
        return self._snapshot

    def clear(self) -> None:
        self._set(PermissionSnapshot())

    def receive_token(self, token: str, verify_and_decode: Callable[[str], VerifiedClaims]) -> bool:
        """Never accept unverified server JSON or a truthy signature flag.

        The verifier must be the future independently authenticated provider;
        exceptions, invalid claims or omitted evidence reset all privileges.
        """
        if not isinstance(token, str) or not token or not callable(verify_and_decode):
            self.clear()
            return False
        try:
            claims = verify_and_decode(token)
        except Exception:
            self.clear()
            return False
        if (type(claims) is not VerifiedClaims
                or not isinstance(claims.permissions, frozenset)
                or not all(type(key) is str and key in REGISTERED_KEYS for key in claims.permissions)
                or type(claims.plan_status) is not str or not claims.plan_status.strip()
                or type(claims.max_windows) is not int or claims.max_windows < 0
                or any(type(v) is not bool for v in (claims.developer, claims.version_locked,
                                                     claims.server_locked, claims.expires))):
            self.clear()
            return False
        self._set(PermissionSnapshot(
            has_verified_payload=True, permissions=claims.permissions,
            plan_status=claims.plan_status, max_windows=claims.max_windows,
            developer=claims.developer, version_locked=claims.version_locked,
            server_locked=claims.server_locked, expired=claims.expires,
        ))
        return True

    def _set(self, new: PermissionSnapshot) -> None:
        if new != self._snapshot:
            self._snapshot = new
            if self._on_change:
                self._on_change(new)

    def has_permission(self, feature: str) -> bool:
        return feature in self._snapshot.authorized_keys

    def is_version_locked(self) -> bool:
        return self._snapshot.version_locked

    def is_plan_banned(self) -> bool:
        return self._snapshot.plan_status.lower() in {'ban', 'banned'}

    def check_account_limit(self, running: int) -> tuple[bool, int, int, str]:
        """Bounded gate only, no process scan or guessed plan-name count.

        Original process+emulator aggregation must be supplied externally;
        a nonpositive or invalid limit always fails closed in this slice.
        """
        limit = self._snapshot.max_windows
        if type(running) is not int or running < 0:
            return False, 0, limit, 'UNKNOWN_RUNNING_COUNT'
        if self._snapshot.blocked or limit <= 0:
            return False, running, limit, 'UNVERIFIED_OR_BLOCKED'
        if running > limit:
            return False, running, limit, 'OVER_LIMIT'
        return True, running, limit, 'OK'

    def has_permission_with_limit(self, feature: str, running: int) -> bool:
        return self.has_permission(feature) and self.check_account_limit(running)[0]
