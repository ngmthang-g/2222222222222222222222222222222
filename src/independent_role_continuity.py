"""S201: continuity evidence for *unverified* original-TLM memory readings.

Original Reader static reconstruction may recover a plausible RoleName,
RoleID and HP from native process memory. One plausible publication is NOT
proof of game login nor even exact runtime ABI. This finite-state ledger
records whether two or more SEPARATE read-only publications refer to the
same underlying HWND/PID/RoleID/RoleName. HP/MapID may legitimately change
during gameplay; they are never used to define identity continuity.

A change in the original game HWND/PID, RoleID or RoleName, an intervening
failed native read, a selected game folder change, window disappearance or
elapsed evidence gap revokes continuity. It NEVER authorizes account
authentication, a Party-ready name, or gameplay controls.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import unicodedata

MAX_TRACKED_IDENTITIES = 48
MAX_GAP_BETWEEN_ACTUAL_READS_SECONDS = 210.0  # local evidence retention
MAX_ROLE_NAME_CHARS = 80
MAX_INDEPENDENT_OBSERVATIONS = 3


@dataclass(frozen=True)
class IndependentRoleContinuity:
    hwnd: int
    pid: int
    role_id: int
    role_name: str
    process_creation_filetime: int
    first_monotonic: float
    last_monotonic: float
    independent_read_count: int = 1
    # A plausible 2x/3x matching memory read is not game account proof.
    live_game_runtime_verified: bool = False
    party_ready: bool = False
    game_actions_authorized: bool = False


def _valid_name(name):
    return (type(name) is str
            and 1 <= len(name) <= MAX_ROLE_NAME_CHARS
            and bool(name.strip())
            and not any(unicodedata.category(ch) in ("Cc", "Cs", "Cf")
                        for ch in name))


def _valid_stamp(value):
    return (type(value) in (int, float) and math.isfinite(value)
            and 0 <= value)


class OriginalRoleContinuityLedger:
    """Worker-thread-only, bounded continuation history, no Win32 calls."""

    def __init__(self):
        self._by_native_identity: dict[tuple[int, int], IndependentRoleContinuity] = {}

    def reset(self):
        self._by_native_identity.clear()

    def retain_current(self, identities) -> None:
        """Remove all windows absent/reused in the CURRENT native Start set."""
        present = set(identities)
        self._by_native_identity = {
            key: value for key, value in self._by_native_identity.items()
            if key in present}

    def failed(self, hwnd: int, pid: int) -> None:
        self._by_native_identity.pop((hwnd, pid), None)

    def accept(
        self, hwnd: int, pid: int, role_id: int, role_name: str,
        observed_monotonic: float, process_creation_filetime: int,
    ) -> IndependentRoleContinuity | None:
        """One independently completed source-memory read, not a UI tick."""
        if (any(type(n) is not int or n <= 0 for n in
                (hwnd, pid, role_id, process_creation_filetime))
                or not _valid_name(role_name)
                or not _valid_stamp(observed_monotonic)):
            self.failed(hwnd, pid)
            return None
        key = (hwnd, pid)
        previous = self._by_native_identity.get(key)
        if (previous is not None
                and previous.role_id == role_id
                and previous.role_name == role_name
                and previous.process_creation_filetime == process_creation_filetime
                and 0 < observed_monotonic - previous.last_monotonic
                <= MAX_GAP_BETWEEN_ACTUAL_READS_SECONDS):
            result = IndependentRoleContinuity(
                hwnd, pid, role_id, role_name, process_creation_filetime,
                previous.first_monotonic, observed_monotonic,
                min(MAX_INDEPENDENT_OBSERVATIONS,
                    previous.independent_read_count + 1))
        else:
            result = IndependentRoleContinuity(
                hwnd, pid, role_id, role_name, process_creation_filetime,
                observed_monotonic, observed_monotonic)
        self._by_native_identity[key] = result
        if len(self._by_native_identity) > MAX_TRACKED_IDENTITIES:
            # Keep only the most recent actual readings; never synthesize
            # an account limit or carry stale data across a source epoch.
            oldest = min(
                self._by_native_identity,
                key=lambda k: self._by_native_identity[k].last_monotonic)
            del self._by_native_identity[oldest]
        return result
