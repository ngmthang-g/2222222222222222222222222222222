"""S95 G10 read-only TeamID observation wait; absolutely NO game commands.

Original G10: _wait_team_state(expect_zero=True) requires ALL verified
members outside team; 0 and 0xFFFFFFFF are known outside, None is not.
_wait_group_same_team requires a real non-sentinel leader TeamID and exact
TeamID equality for other members. Cancel is distinct from timeout.
Original TEAMID_POLL/GROUP_JOIN_POLL and timeouts are SYMBOLIC/UNKNOWN:
caller MUST supply bounded numeric timeout/interval values; these are local
test parameters, never claims of original source timing.

Each observation calls S94 fail-closed diagnostic PartyTeamIdentityPreflight,
which rechecks fresh S09 HWND/PID generation, signed gate and live external
reader validity. The only successful result is a DIAGNOSTIC observation; it
DOES NOT authorize team creation, invitation, leaving or other game input.
"""
from __future__ import annotations

from dataclasses import dataclass
import threading
import time

from party_team_identity import (
    PartyTeamIdentityPreflight, PartyTeamPreflightResult,
    NO_TEAM_IDS,
)


@dataclass(frozen=True)
class PartyTeamWaitResult:
    code: str
    mode: str
    attempts: int
    missing_names: tuple[str, ...] = ()
    leader_team_id: int | None = None
    last_preflight_code: str = ""
    # No RoleID, executable action target or game command in output.


def _assess(
    observation: PartyTeamPreflightResult, selected: tuple[str, ...],
    mode: str, leader_name: str | None,
) -> tuple[str, tuple[str, ...], int | None]:
    if observation.code == "TEAMID_UNKNOWN_NOT_OUTSIDE":
        return "PENDING_UNREADABLE_TEAMID", selected, None
    if observation.code == "UNRESOLVED_ONLINE_MEMBERS":
        return "PENDING_OFFLINE", observation.unavailable_names, None
    if observation.code != "DIAGNOSTIC_OBSERVED_NO_GAME_ACTION":
        return "BLOCKED_"+observation.code, (), None

    members = {t.saved_name:t for t in observation.targets}
    if set(selected) != set(members):
        return "BLOCKED_INCOMPLETE_OBSERVATION", (), None
    if mode == "OUTSIDE":
        missing = tuple(name for name in selected
                        if members[name].team_id not in NO_TEAM_IDS)
        return ("OBSERVED_ALL_OUTSIDE" if not missing else "PENDING_IN_TEAM",
                missing, None)

    # SAME_TEAM: comparing no-team IDs or unknown with each other would
    # falsely treat two members outside the team as successfully joined.
    leader = members.get(leader_name)
    if leader is None:
        return "BLOCKED_LEADER_NOT_SELECTED", (), None
    if leader.team_id in NO_TEAM_IDS:
        return "PENDING_LEADER_NO_TEAM", tuple(
            n for n in selected if n != leader_name), None
    missing = tuple(name for name in selected
                    if name != leader_name
                    and members[name].team_id != leader.team_id)
    return ("OBSERVED_SAME_REAL_TEAM" if not missing else "PENDING_NOT_SAME_TEAM",
            missing, leader.team_id)


class PartyTeamReadOnlyWait:
    """Bounded cancel-aware G10 observation helper, NEVER sends packets."""

    def __init__(self, preflight: PartyTeamIdentityPreflight, *,
                 clock=time.monotonic):
        if not isinstance(preflight, PartyTeamIdentityPreflight):
            raise ValueError("Requires S94 read-only PartyTeamIdentityPreflight")
        self.preflight = preflight
        self.clock = clock

    def wait(self, selected: tuple[str, ...], *, mode: str,
             timeout_seconds: float, poll_seconds: float,
             cancel: threading.Event | None = None,
             leader_name: str | None = None) -> PartyTeamWaitResult:
        if mode not in ("OUTSIDE","SAME_TEAM"):
            return PartyTeamWaitResult("INVALID_MODE",str(mode),0)
        if (not isinstance(selected, tuple) or not selected
                or any(type(n) is not str or not n.strip() for n in selected)
                or len(set(selected)) != len(selected)):
            return PartyTeamWaitResult("INVALID_SELECTION",mode,0)
        if (mode == "SAME_TEAM"
                and (len(selected)<2 or type(leader_name) is not str
                     or leader_name not in selected)):
            return PartyTeamWaitResult("INVALID_LEADER",mode,0)
        if (type(timeout_seconds) not in (float,int)
                or type(poll_seconds) not in (float,int)
                or not 0 <= timeout_seconds <= 3600
                or not 0 < poll_seconds <= 3600):
            return PartyTeamWaitResult("INVALID_BOUNDS",mode,0)
        if cancel is not None and not isinstance(cancel, threading.Event):
            return PartyTeamWaitResult("INVALID_CANCEL",mode,0)
        cancelled = cancel if cancel is not None else threading.Event()
        deadline = self.clock()+timeout_seconds
        attempts = 0
        last_reason = "NO_OBSERVATION"
        missing = selected
        leader_team_id = None
        last_preflight = ""
        while True:
            if cancelled.is_set():
                return PartyTeamWaitResult(
                    "CANCELLED",mode,attempts,missing,
                    leader_team_id,last_preflight)
            observation = self.preflight.inspect(selected)
            attempts += 1
            last_preflight = observation.code
            reason, missing, leader_team_id = _assess(
                observation,selected,mode,leader_name)
            last_reason = reason
            if reason in ("OBSERVED_ALL_OUTSIDE","OBSERVED_SAME_REAL_TEAM"):
                # This is read-only proof of externally supplied data,
                # NEVER authorization to trigger a game command.
                return PartyTeamWaitResult(
                    "DIAGNOSTIC_"+reason+"_NO_GAME_ACTION",
                    mode,attempts,(),leader_team_id,last_preflight)
            if reason.startswith("BLOCKED_"):
                return PartyTeamWaitResult(
                    reason,mode,attempts,missing,leader_team_id,last_preflight)
            remaining = deadline-self.clock()
            if remaining <= 0:
                return PartyTeamWaitResult(
                    "TIMEOUT_NOT_CONFIRMED",mode,attempts,
                    missing,leader_team_id,last_preflight)
            cancelled.wait(min(poll_seconds,remaining))
