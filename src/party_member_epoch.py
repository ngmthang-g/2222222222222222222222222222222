"""S98 G10: sequential read-epoch comparison, not an atomic game snapshot.

Adds a second S97 read-only member snapshot AFTER its post-S96 detail. A
native HWND/PID + Start revision fence surrounds the two S97 samples.
S96 first/second history and S97 first post-observation remain unchanged.
No read proves that all player fields were sampled at the same instant.
All callbacks used by reconstruction tests are TEST-ONLY, never game auth.
"""
from __future__ import annotations

from dataclasses import dataclass
import threading

from party_member_snapshot import (
    PartyJoinDetailedDiagnostic, PartyDetailedJoinReport,
    PartyMemberSnapshot,
)
from party_team_identity import _snapshot_pairs


@dataclass(frozen=True)
class PartyMemberEpochChange:
    name: str
    from_state: str
    to_state: str
    from_team_id: int | None
    to_team_id: int | None
    class_code: str


@dataclass(frozen=True)
class PartyMemberEpochReport:
    code: str
    detailed: PartyDetailedJoinReport
    second_post_snapshot: PartyMemberSnapshot | None = None
    start_revision: int | None = None
    end_revision: int | None = None
    compared_native_windows: int = 0
    changes: tuple[PartyMemberEpochChange, ...] = ()
    atomic: bool = False
    invites_sent: int = 0


class PartyJoinReadEpochDiagnostic:
    """Preserves S96 and S97 exactly; adds only read-only S98 comparison."""

    def __init__(self, detailed: PartyJoinDetailedDiagnostic) -> None:
        if not isinstance(detailed, PartyJoinDetailedDiagnostic):
            raise TypeError("S98 must reuse actual S97/S96 read-only diagnostics")
        self.detailed = detailed
        self.preflight = detailed.snapshot.preflight

    def _generation(self):
        """Read native current HWND/PID fingerprint; never return send targets."""
        try:
            snap = self.preflight.start_producer.read_snapshot()
            pairs = _snapshot_pairs(snap)
            if pairs is None or not pairs:
                return "INVALID_START_CACHE",None,None
            # The individual S94/S97 reads already guard permission. Recheck
            # it before exposing any additional native generation detail.
            if self.preflight.allowed() is not True:
                return "PERMISSION_NOT_VERIFIED",None,None
            for hwnd,pid in pairs:
                if (not self.preflight.backend.is_window(hwnd)
                        or self.preflight.backend.process_id(hwnd) != pid):
                    return "STALE_NATIVE_HWND_PID",None,None
            return "VERIFIED",snap.revision,pairs
        except Exception:
            return "NATIVE_GENERATION_READ_ERROR",None,None

    def inspect(self, selected_names: tuple[str, ...], *,
                leader_name: str, timeout_seconds: float,
                poll_seconds: float, cancel: threading.Event | None = None
                ) -> PartyMemberEpochReport:
        # This maintains S96 two rounds & S97 one fresh post-S96 snapshot.
        detailed = self.detailed.inspect(
            selected_names,leader_name=leader_name,
            timeout_seconds=timeout_seconds,poll_seconds=poll_seconds,
            cancel=cancel)

        def report(code,second=None,start=None,end=None,count=0,changes=()):
            return PartyMemberEpochReport(code,detailed,second,start,end,
                                          count,changes,False,0)

        if cancel is not None and cancel.is_set():
            return report("CANCELLED")
        first = detailed.post_snapshot
        if first is None:
            return report("BLOCKED_NO_S97_POST_SNAPSHOT_"+detailed.base.code)
        if first.code.startswith("BLOCKED_"):
            return report("BLOCKED_S97_"+first.code)
        # The fingerprint is measured after S97, not historically at B3 time.
        c1,rev1,pairs1=self._generation()
        if c1!="VERIFIED":
            return report("BLOCKED_FIRST_GENERATION_"+c1)
        if rev1!=first.revision:
            return report("BLOCKED_FIRST_REVISION_CHANGED",start=rev1)
        if cancel is not None and cancel.is_set():
            return report("CANCELLED",start=rev1)
        second=self.detailed.snapshot.inspect(
            selected_names,leader_name=leader_name)
        if cancel is not None and cancel.is_set():
            return report("CANCELLED",second,start=rev1)
        if second.code.startswith("BLOCKED_"):
            return report("BLOCKED_SECOND_SNAPSHOT_"+second.code,
                          second,start=rev1)
        c2,rev2,pairs2=self._generation()
        if c2!="VERIFIED":
            return report("BLOCKED_SECOND_GENERATION_"+c2,
                          second,rev1)
        if (rev1!=rev2 or first.revision!=second.revision
                or pairs1!=pairs2):
            return report("BLOCKED_EPOCH_GENERATION_CHANGED",second,
                          rev1,rev2)
        before={m.name:m for m in first.members}
        after={m.name:m for m in second.members}
        if (set(before)!=set(selected_names) or set(after)!=set(selected_names)
                or len(before)!=len(selected_names)
                or len(after)!=len(selected_names)):
            return report("BLOCKED_MEMBER_SET_CHANGED",second,rev1,rev2)
        changes=[]
        for name in selected_names:
            a,b=before[name],after[name]
            if a.team_id is not None and b.team_id is not None and a.team_id!=b.team_id:
                kind="OBSERVED_TEAM_ID_CHANGED"
            elif (a.team_id is None)!=(b.team_id is None):
                kind="OBSERVED_READABILITY_CHANGED"
            elif a.state!=b.state:
                kind="OBSERVED_STATE_CHANGED"
            else:
                kind="OBSERVED_STABLE"
            changes.append(PartyMemberEpochChange(
                name,a.state,b.state,a.team_id,b.team_id,kind))
        changed=any(c.class_code!="OBSERVED_STABLE" for c in changes)
        return report(
            "DIAGNOSTIC_SEQUENTIAL_CHANGE_SAME_GENERATION_NO_GAME_ACTION"
            if changed else
            "DIAGNOSTIC_SEQUENTIAL_STABLE_SAME_GENERATION_NO_GAME_ACTION",
            second,rev1,rev2,len(pairs1),tuple(changes))
