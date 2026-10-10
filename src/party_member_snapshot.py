"""S97 G03/G10 per-member POST-S96 snapshot (read-only, never a game action).

Original _team_snapshot prints name=TeamID, '?' for unreadable data.
S96 round history is retained unchanged. This separate snapshot is taken
AFTER those rounds; it is NOT a fabricated per-member history of prior polls.
S94 independently validates permission + physical HWND/PID + Start revision
for every read. All injected sources are TEST/EXTERNAL diagnostics only.
"""
from __future__ import annotations

from dataclasses import dataclass
import threading

from party_join_report import PartyJoinTwoRoundDiagnostic, PartyJoinTwoRoundReport
from party_team_identity import (
    NO_TEAM_IDS, PartyTeamIdentityPreflight,
    _match_record, _parse_live_records, _snapshot_pairs,
)


@dataclass(frozen=True)
class PartyMemberDetail:
    name: str
    state: str
    team_id: int | None = None
    source_code: str = ""
    # No RoleID, packet payload or sendable target is exposed.


@dataclass(frozen=True)
class PartyMemberSnapshot:
    code: str
    phase: str = "AFTER_S96_OBSERVATIONS"
    revision: int | None = None
    leader_team_id: int | None = None
    members: tuple[PartyMemberDetail, ...] = ()
    invites_sent: int = 0


@dataclass(frozen=True)
class PartyDetailedJoinReport:
    base: PartyJoinTwoRoundReport
    post_snapshot: PartyMemberSnapshot | None = None
    invites_sent: int = 0


_BLOCKING = frozenset((
    "SIGNED_INFO_GATE_UNAVAILABLE", "PERMISSION_NOT_VERIFIED",
    "PERMISSION_READ_ERROR", "PERMISSION_REVOKED",
    "LIVE_IDENTITY_PROVIDER_UNAVAILABLE", "INVALID_START_CACHE",
    "START_CACHE_READ_ERROR", "NO_LIVE_WINDOWS",
    "STALE_NATIVE_HWND_PID", "NATIVE_WINDOW_CHECK_FAILED",
    "STALE_START_REVISION", "FINAL_REVALIDATION_FAILED",
    "ROLEID_READ_ERROR", "INVALID_ROLEID_RECORDS",
    "DUPLICATE_ACTION_TARGET", "AMBIGUOUS_EXACT",
    "AMBIGUOUS_LOWERCASE",
))


class PartyMemberReadOnlySnapshot:
    def __init__(self, preflight: PartyTeamIdentityPreflight) -> None:
        if not isinstance(preflight, PartyTeamIdentityPreflight):
            raise TypeError("S97 requires the existing S94 identity preflight")
        self.preflight = preflight

    def _unresolved(self, name: str, pairs: frozenset[tuple[int, int]]
                    ) -> PartyMemberDetail:
        """Never assume 'offline' merely because the PID is not in Start."""
        try:
            records = _parse_live_records(self.preflight.read_own_ids())
            if records is None:
                return PartyMemberDetail(name, "UNKNOWN_ROLE_RECORDS", None,
                                         "INVALID_ROLEID_RECORDS")
            record, match = _match_record(name, records)
            if match in ("AMBIGUOUS_EXACT", "AMBIGUOUS_LOWERCASE"):
                return PartyMemberDetail(name, "AMBIGUOUS_NAME", None, match)
            if record is None:
                return PartyMemberDetail(name, "OFFLINE_NAME", None, "OFFLINE")
            if not any(pid == record.pid for _, pid in pairs):
                return PartyMemberDetail(name, "PID_NOT_IN_START_CACHE", None,
                                         "UNMAPPED_PID")
            return PartyMemberDetail(name, "UNRESOLVED_WINDOW", None,
                                     "UNRESOLVED_ONLINE_MEMBERS")
        except Exception:
            return PartyMemberDetail(name, "UNKNOWN_ROLE_RECORDS", None,
                                     "ROLEID_READ_ERROR")

    def inspect(self, selected_names: tuple[str, ...], *,
                leader_name: str) -> PartyMemberSnapshot:
        def failure(code: str) -> PartyMemberSnapshot:
            return PartyMemberSnapshot("BLOCKED_"+code)
        if (type(selected_names) is not tuple or len(selected_names) < 2
                or any(type(name) is not str or not name.strip()
                       or name != name.strip() for name in selected_names)
                or len(set(selected_names)) != len(selected_names)):
            return failure("INVALID_SELECTION")
        if type(leader_name) is not str or leader_name not in selected_names:
            return failure("INVALID_LEADER")

        # The first S94 read verifies the external gate and native HWND/PID.
        leader = self.preflight.inspect((leader_name,))
        if leader.code in _BLOCKING:
            return failure(leader.code)
        try:
            initial = self.preflight.start_producer.read_snapshot()
            pairs = _snapshot_pairs(initial)
            if pairs is None or not pairs:
                return failure("INVALID_START_CACHE")
            revision = initial.revision
        except Exception:
            return failure("START_CACHE_READ_ERROR")
        readings = {leader_name: leader}
        for name in selected_names:
            if name == leader_name:
                continue
            r = self.preflight.inspect((name,))
            if r.code in _BLOCKING:
                return failure(r.code)
            readings[name] = r
            if r.observed_revision and r.observed_revision != revision:
                return failure("STALE_START_REVISION")

        leader_id = None
        if leader.code == "DIAGNOSTIC_OBSERVED_NO_GAME_ACTION":
            if leader.observed_revision != revision or len(leader.targets) != 1:
                return failure("STALE_START_REVISION")
            team_id = leader.targets[0].team_id
            if team_id not in NO_TEAM_IDS:
                leader_id = team_id

        details: list[PartyMemberDetail] = []
        for name in selected_names:
            r = readings[name]
            if r.code == "UNRESOLVED_ONLINE_MEMBERS":
                details.append(self._unresolved(name, pairs))
                continue
            if r.code == "TEAMID_UNKNOWN_NOT_OUTSIDE":
                details.append(PartyMemberDetail(name,"UNREADABLE_TEAMID",None,r.code))
                continue
            if r.code in ("TEAMID_READ_ERROR", "INVALID_TEAMID_DATA"):
                details.append(PartyMemberDetail(name,"TEAMID_READ_ERROR",None,r.code))
                continue
            if r.code != "DIAGNOSTIC_OBSERVED_NO_GAME_ACTION" or len(r.targets) != 1:
                return failure("UNHANDLED_"+r.code)
            if r.observed_revision != revision:
                return failure("STALE_START_REVISION")
            tid = r.targets[0].team_id
            if tid in NO_TEAM_IDS:
                status = "KNOWN_OUTSIDE"
            elif leader_id is None:
                status = "REAL_TEAM_LEADER_UNCONFIRMED"
            elif tid == leader_id:
                status = "LEADER_REAL_TEAM" if name == leader_name else "JOINED_LEADER_TEAM"
            else:
                status = "DIFFERENT_REAL_TEAM"
            details.append(PartyMemberDetail(name,status,tid,r.code))

        # Final generation and gate fence: reject *all* rows on mutation.
        try:
            final = self.preflight.start_producer.read_snapshot()
            if final.revision != revision or _snapshot_pairs(final) != pairs:
                return failure("STALE_START_REVISION")
            for hwnd,pid in pairs:
                if (not self.preflight.backend.is_window(hwnd)
                        or self.preflight.backend.process_id(hwnd) != pid):
                    return failure("STALE_NATIVE_HWND_PID")
            if self.preflight.allowed() is not True:
                return failure("PERMISSION_REVOKED")
            # A changing leader TeamID invalidates comparisons made above.
            confirm = self.preflight.inspect((leader_name,))
            if (confirm.code != leader.code
                    or (confirm.code == "DIAGNOSTIC_OBSERVED_NO_GAME_ACTION"
                        and (len(confirm.targets) != 1
                             or confirm.targets[0].team_id != leader.targets[0].team_id))
                    or (confirm.observed_revision and confirm.observed_revision != revision)):
                return failure("LEADER_CHANGED_DURING_SNAPSHOT")
        except Exception:
            return failure("FINAL_REVALIDATION_FAILED")

        joined = all(x.state in ("LEADER_REAL_TEAM","JOINED_LEADER_TEAM")
                     for x in details)
        return PartyMemberSnapshot(
            "DIAGNOSTIC_ALL_JOINED_POST_S96_NO_GAME_ACTION" if joined
            else "DIAGNOSTIC_MEMBER_STATES_INCOMPLETE_NO_GAME_ACTION",
            revision=revision,leader_team_id=leader_id,members=tuple(details))


class PartyJoinDetailedDiagnostic:
    """Preserve S96 two-round provenance + ADD a fresh post-round G03 snapshot."""

    def __init__(self, two_round: PartyJoinTwoRoundDiagnostic) -> None:
        if not isinstance(two_round, PartyJoinTwoRoundDiagnostic):
            raise TypeError("S97 must reuse S96, not reimplement B3")
        self.two_round = two_round
        self.snapshot = PartyMemberReadOnlySnapshot(two_round.waiter.preflight)

    def inspect(self, selected_names: tuple[str, ...], *,
                leader_name: str, timeout_seconds: float, poll_seconds: float,
                cancel: threading.Event | None = None) -> PartyDetailedJoinReport:
        base = self.two_round.inspect(
            selected_names,leader_name=leader_name,
            timeout_seconds=timeout_seconds,poll_seconds=poll_seconds,
            cancel=cancel)
        # S96 block/cancel/invalid results must not be overridden by an
        # apparently healthy later snapshot.
        if (base.code.startswith("BLOCKED_") or base.code.startswith("INVALID_")
                or base.code == "CANCELLED"
                or (cancel is not None and cancel.is_set())):
            return PartyDetailedJoinReport(base)
        post = self.snapshot.inspect(selected_names,leader_name=leader_name)
        if cancel is not None and cancel.is_set():
            return PartyDetailedJoinReport(base)
        return PartyDetailedJoinReport(base,post)
