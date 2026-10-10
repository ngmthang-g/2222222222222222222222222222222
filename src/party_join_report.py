"""S96 G10 B3: TWO observational team-join rounds, NO invitations sent.

Original G10 _invite_burst B3 uses an initial burst + one resend to the
missing targets, with ONE shared _wait_group_same_team after each. The
original resend is an ACTION, not an observation. This module models only
the first/second verification reports, keeps potential resend names for
DIAGNOSTICS, and NEVER claims to have sent or scheduled a resend.

Both rounds re-check ALL group members, not just those missing in round 1:
a previously joined member might leave between observations. Per-round
timeouts/polls are explicit local numeric test parameters; original symbolic
GROUP_JOIN_TIMEOUT and GROUP_JOIN_POLL remain UNKNOWN.

Requires externally provided S95 PartyTeamReadOnlyWait; its S94 preflight
validates HWND/PID generation, live RoleID/TeamID and external permissions
on every read. With missing authentic game reader or signed Info, it fails
closed. Success is only a read-only TEST/EXTERNAL observation, NOT a game
action outcome or legitimate team authorization.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import threading

from party_team_wait import PartyTeamReadOnlyWait, PartyTeamWaitResult


@dataclass(frozen=True)
class PartyJoinObservation:
    round_number: int
    code: str
    attempts: int
    missing_names: tuple[str, ...]
    leader_team_id: int | None
    last_preflight_code: str


@dataclass(frozen=True)
class PartyJoinTwoRoundReport:
    code: str
    leader_name: str
    selected_names: tuple[str, ...]
    rounds: tuple[PartyJoinObservation, ...] = ()
    potential_resend_names: tuple[str, ...] = ()
    invites_sent: int = 0
    # Never include game RoleID/packet/execute adapter.


def _round(number: int, result: PartyTeamWaitResult) -> PartyJoinObservation:
    return PartyJoinObservation(
        round_number=number, code=result.code, attempts=result.attempts,
        missing_names=result.missing_names,
        leader_team_id=result.leader_team_id,
        last_preflight_code=result.last_preflight_code)


class PartyJoinTwoRoundDiagnostic:
    """Source-backed two-stage READ-ONLY B3 diagnostic, not _invite_burst."""

    def __init__(self, waiter: PartyTeamReadOnlyWait) -> None:
        if not isinstance(waiter, PartyTeamReadOnlyWait):
            raise TypeError("S96 requires actual S95 read-only TeamID waiter")
        self.waiter = waiter

    def inspect(self, selected_names: tuple[str, ...], *,
                leader_name: str, timeout_seconds: float,
                poll_seconds: float, cancel: threading.Event | None = None
                ) -> PartyJoinTwoRoundReport:
        selected = selected_names if isinstance(selected_names, tuple) else ()
        leader = leader_name if type(leader_name) is str else ""
        def report(code, rounds=(), candidates=()):
            return PartyJoinTwoRoundReport(
                code, leader, selected, rounds, candidates, 0)

        if (not isinstance(selected_names, tuple)
                or len(selected_names) < 2
                or any(type(n) is not str or not n.strip()
                       or n != n.strip() for n in selected_names)
                or len(set(selected_names)) != len(selected_names)):
            return report("INVALID_SELECTION")
        if type(leader_name) is not str or leader_name not in selected_names:
            return report("INVALID_LEADER")
        if (type(timeout_seconds) not in (float, int)
                or type(poll_seconds) not in (float, int)
                or not math.isfinite(timeout_seconds)
                or not math.isfinite(poll_seconds)
                or not 0 <= timeout_seconds <= 3600
                or not 0 < poll_seconds <= 3600):
            return report("INVALID_BOUNDS")
        if cancel is not None and not isinstance(cancel, threading.Event):
            return report("INVALID_CANCEL")
        if cancel is not None and cancel.is_set():
            return report("CANCELLED")

        def wait():
            return self.waiter.wait(
                selected_names, mode="SAME_TEAM",
                leader_name=leader_name, timeout_seconds=timeout_seconds,
                poll_seconds=poll_seconds, cancel=cancel)

        first = wait()
        first_record = _round(1, first)
        rounds = (first_record,)
        if cancel is not None and cancel.is_set():
            return report("CANCELLED", rounds)
        if first.code == "DIAGNOSTIC_OBSERVED_SAME_REAL_TEAM_NO_GAME_ACTION":
            return report("DIAGNOSTIC_ALL_JOINED_FIRST_OBSERVATION_NO_GAME_ACTION",
                          rounds)
        if first.code == "CANCELLED":
            return report("CANCELLED", rounds)
        if first.code != "TIMEOUT_NOT_CONFIRMED":
            return report("BLOCKED_FIRST_OBSERVATION_"+first.code, rounds)

        # The original might SEND a second invite here, but without G10
        # protocol and legitimate signed Info, we MUST NOT transmit one.
        # This is an OBSERVATION BOUNDARY ONLY. Candidates are not invites.
        others = tuple(n for n in selected_names if n != leader_name)
        candidates = tuple(n for n in others if n in first.missing_names)
        # No verified real leader TeamID means no meaningful resend TARGETS.
        if first.leader_team_id is None:
            candidates = ()
        if cancel is not None and cancel.is_set():
            return report("CANCELLED", rounds, candidates)

        second = wait()  # re-evaluate ALL members; NEVER treat missing as joined
        rounds += (_round(2, second),)
        if cancel is not None and cancel.is_set():
            return report("CANCELLED", rounds, candidates)
        if second.code == "DIAGNOSTIC_OBSERVED_SAME_REAL_TEAM_NO_GAME_ACTION":
            return report("DIAGNOSTIC_ALL_JOINED_SECOND_OBSERVATION_NO_GAME_ACTION",
                          rounds, candidates)
        if second.code == "CANCELLED":
            return report("CANCELLED", rounds, candidates)
        if second.code == "TIMEOUT_NOT_CONFIRMED":
            return report("DIAGNOSTIC_STILL_MISSING_AFTER_TWO_OBSERVATIONS_NO_GAME_ACTION",
                          rounds, candidates)
        return report("BLOCKED_SECOND_OBSERVATION_"+second.code,
                      rounds, candidates)
