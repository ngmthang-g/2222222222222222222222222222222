"""S99 G03/G10 Party _team_snapshot read-only PRESENTATION CONTRACT.

Source evidence: a resolved member is displayed as name=TeamID and unreadable
TeamID as '?'. This adapter adds *separate* explicit diagnostic classifications
for offline/unmapped/read failures. It NEVER claims all observations were
simultaneous: S96 round history, S97 post-round sample and S98 later sequential
sample have distinct provenance. No game action, signed Info or live memory
reader is implemented here. Safe only as TEST/EXTERNAL diagnostic text.

This is not a reconstructed original _team_snapshot function or UI action.
"""
from __future__ import annotations

from dataclasses import dataclass

from party_member_epoch import PartyMemberEpochReport
from party_member_snapshot import PartyMemberDetail, PartyMemberSnapshot
from party_team_identity import NO_TEAM_IDS


_SUCCESS_EPOCH_CODES = frozenset((
    "DIAGNOSTIC_SEQUENTIAL_STABLE_SAME_GENERATION_NO_GAME_ACTION",
    "DIAGNOSTIC_SEQUENTIAL_CHANGE_SAME_GENERATION_NO_GAME_ACTION",
))
_TEAM_STATES = frozenset((
    "LEADER_REAL_TEAM", "JOINED_LEADER_TEAM", "DIFFERENT_REAL_TEAM",
    "KNOWN_OUTSIDE", "REAL_TEAM_LEADER_UNCONFIRMED",
))
_UNKNOWN_STATES = frozenset((
    "UNREADABLE_TEAMID", "TEAMID_READ_ERROR", "OFFLINE_NAME",
    "PID_NOT_IN_START_CACHE", "UNRESOLVED_WINDOW",
    "UNKNOWN_ROLE_RECORDS", "AMBIGUOUS_NAME",
))
_STATES = _TEAM_STATES | _UNKNOWN_STATES
_MAX_TEAMID = 0xFFFFFFFF


def _escaped_name(name: str) -> str:
    """Keep Unicode names but prevent line, separator or control spoofing."""
    result = []
    for c in name:
        if c == "\\":
            result.append("\\\\")
        elif c == "\n":
            result.append("\\n")
        elif c == "\r":
            result.append("\\r")
        elif c == "\t":
            result.append("\\t")
        elif c in ("=", "|"):
            result.append("\\" + c)
        elif ord(c) < 32 or ord(c) == 127:
            result.append("\\u%04x" % ord(c))
        else:
            result.append(c)
    return "".join(result)


@dataclass(frozen=True)
class PartySnapshotPresentationRow:
    name: str
    original_style_field: str
    display_team_id: str
    diagnostic_state: str
    comparison_code: str
    # The original evidence only establishes name=TeamID or '?'.
    # Other statuses are explicitly S97/S98-specific classifications.


@dataclass(frozen=True)
class PartySnapshotPresentation:
    code: str
    rows: tuple[PartySnapshotPresentationRow, ...] = ()
    s96_round_codes: tuple[str, ...] = ()
    s96_round_missing_names: tuple[tuple[str, ...], ...] = ()
    s97_phase: str = ""
    s98_phase: str = ""
    snapshot_revision: int | None = None
    epoch_source_code: str = ""
    sequential_non_atomic: bool = True
    action_authorized: bool = False
    game_parity_verified: bool = False
    invites_sent: int = 0

    def as_lines(self) -> tuple[str, ...]:
        """Diagnostic text; never a command, simulated game log or packet."""
        return tuple(
            row.original_style_field + " [" + row.diagnostic_state
            + "; " + row.comparison_code + "]"
            for row in self.rows
        )


def _valid_row(row: PartyMemberDetail) -> bool:
    if not isinstance(row, PartyMemberDetail) or row.state not in _STATES:
        return False
    if type(row.name) is not str or not row.name or row.name != row.name.strip():
        return False
    if row.state in _TEAM_STATES:
        if type(row.team_id) is not int or not 0 <= row.team_id <= _MAX_TEAMID:
            return False
        if row.state == "KNOWN_OUTSIDE":
            return row.team_id in NO_TEAM_IDS
        return row.team_id not in NO_TEAM_IDS
    return row.team_id is None


def _snapshot_members(snapshot: PartyMemberSnapshot, names: tuple[str, ...]
                      ) -> bool:
    return (
        isinstance(snapshot, PartyMemberSnapshot)
        and snapshot.code.startswith("DIAGNOSTIC_")
        and snapshot.phase == "AFTER_S96_OBSERVATIONS"
        and snapshot.invites_sent == 0
        and type(snapshot.revision) is int
        and snapshot.revision > 0
        and len(snapshot.members) == len(names)
        and tuple(member.name for member in snapshot.members) == names
        and all(_valid_row(member) for member in snapshot.members)
    )


def present_party_team_snapshot(epoch: PartyMemberEpochReport
                                ) -> PartySnapshotPresentation:
    """Fail closed for any blocked/inconsistent epoch, retaining no team rows.

    Treating a diagnostic presentation as successful game team formation
    or action authorization is explicitly unsupported.
    """
    def blocked(code: str) -> PartySnapshotPresentation:
        return PartySnapshotPresentation("BLOCKED_PRESENTATION_" + code)

    if not isinstance(epoch, PartyMemberEpochReport):
        return blocked("INVALID_REPORT_TYPE")
    if epoch.code not in _SUCCESS_EPOCH_CODES:
        return blocked("UNVERIFIED_EPOCH_" + str(epoch.code))
    base = epoch.detailed.base
    original_post = epoch.detailed.post_snapshot
    second = epoch.second_post_snapshot
    if (epoch.atomic is not False or epoch.invites_sent != 0
            or epoch.detailed.invites_sent != 0
            or base.invites_sent != 0):
        return blocked("ACTION_OR_ATOMICITY_INVARIANT")
    if not base.code.startswith("DIAGNOSTIC_"):
        return blocked("S96_NOT_DIAGNOSTIC")
    names = base.selected_names
    if (type(names) is not tuple or len(names) < 2
            or len(set(names)) != len(names)
            or any(type(x) is not str or not x or x != x.strip() for x in names)
            or type(base.leader_name) is not str
            or base.leader_name not in names):
        return blocked("INVALID_MEMBER_SELECTION")
    if (len(base.rounds) not in (1,2)
            or tuple(x.round_number for x in base.rounds)
               != tuple(range(1,len(base.rounds)+1))
            or any(x.code not in (
                "DIAGNOSTIC_OBSERVED_SAME_REAL_TEAM_NO_GAME_ACTION",
                "TIMEOUT_NOT_CONFIRMED") for x in base.rounds)
            or any(any(n not in names for n in x.missing_names)
                   for x in base.rounds)
            or any(n == base.leader_name or n not in names
                   for n in base.potential_resend_names)):
        return blocked("INVALID_S96_PROVENANCE")
    if (not _snapshot_members(original_post,names)
            or not _snapshot_members(second,names)):
        return blocked("INVALID_MEMBER_SAMPLE")
    if (epoch.start_revision != epoch.end_revision
            or epoch.start_revision != original_post.revision
            or epoch.end_revision != second.revision
            or type(epoch.compared_native_windows) is not int
            or epoch.compared_native_windows < 2):
        return blocked("STALE_OR_UNVERIFIED_NATIVE_EPOCH")
    if (len(epoch.changes) != len(names)
            or tuple(change.name for change in epoch.changes) != names):
        return blocked("INVALID_CHANGE_PROVENANCE")

    rows = []
    actual_change = False
    for before,after,change in zip(
            original_post.members,second.members,epoch.changes):
        if (change.from_state != before.state
                or change.to_state != after.state
                or change.from_team_id != before.team_id
                or change.to_team_id != after.team_id
                or change.class_code not in (
                    "OBSERVED_STABLE", "OBSERVED_TEAM_ID_CHANGED",
                    "OBSERVED_READABILITY_CHANGED","OBSERVED_STATE_CHANGED")):
            return blocked("MISMATCHED_S98_COMPARISON")
        if change.class_code == "OBSERVED_STABLE":
            if (before.state != after.state or before.team_id != after.team_id):
                return blocked("FALSE_STABLE_CHANGE")
        else:
            if before.state == after.state and before.team_id == after.team_id:
                return blocked("FALSE_CHANGE")
            actual_change = True
        team = str(after.team_id) if after.team_id is not None else "?"
        rows.append(PartySnapshotPresentationRow(
            after.name, _escaped_name(after.name)+"="+team,
            team,after.state,change.class_code))

    claimed_changed = epoch.code == (
        "DIAGNOSTIC_SEQUENTIAL_CHANGE_SAME_GENERATION_NO_GAME_ACTION")
    if claimed_changed != actual_change:
        return blocked("INCONSISTENT_EPOCH_CHANGE_CODE")
    return PartySnapshotPresentation(
        code="DIAGNOSTIC_PRESENTATION_ONLY_NO_GAME_ACTION",
        rows=tuple(rows),
        s96_round_codes=tuple(r.code for r in base.rounds),
        s96_round_missing_names=tuple(r.missing_names for r in base.rounds),
        s97_phase=original_post.phase,
        s98_phase="SECOND_SEQUENTIAL_POST_S96_OBSERVATION",
        snapshot_revision=epoch.end_revision,
        epoch_source_code=epoch.code,
        sequential_non_atomic=True,
        action_authorized=False,
        game_parity_verified=False,
        invites_sent=0,
    )
