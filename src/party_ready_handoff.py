"""S101 G02/G03 TEST-ONLY S100 RoleName -> S90 roster -> S91 ready handoff.

Verified original: Party reads shared cached HWNDs, external character info
RoleName, removes <[^>]+> tags, and maintains 3 ready names/row. Existing
S90/S91/S100 implement those separate contracts and are NOT modified.

This adapter adds the missing native HWND/PID and Start generation validation
AT the worker->Tk handoff. A cached HWND may still be physically closed even
before the slower Start poll updates its cache. No original reader, live game,
RoleID/TeamID, signed Info, action, widget, timer or command is implemented.
"""
from __future__ import annotations

from dataclasses import dataclass

from party_rolename_source import PartyRoleNameExternalSource
from party_roster import (
    PartyRoster, PartyRosterResult, _valid_snapshot, _identity_set,
    prepare_roster,
)
from party_ready_list import PartyReadyList
from start_polling import WindowSnapshot


@dataclass(frozen=True)
class PartyReadyPrepared:
    code: str
    revision: int | None = None
    pairs: frozenset[tuple[int,int]] = frozenset()
    roster_result: PartyRosterResult | None = None
    # This is EXTERNAL/TEST-only, never signed game RoleName identity.


@dataclass(frozen=True)
class PartyReadyHandoffResult:
    code: str
    displayed_ready_names: tuple[str,...] = ()
    source_provenance: str = "EXTERNAL_UNVERIFIED_NOT_GAME"
    action_authorized: bool = False
    game_role_verified: bool = False


class PartyExternalReadyHandoff:
    """A composable synchronous adapter around existing S90/S91 UI contracts.

    collect() is worker-compatible and never calls Tk; deliver() is Tk owner
    thread only and must be called instead of blindly applying a stale worker
    result. Native checks are performed before/after S91 drawing as best
    effort at this handoff; subsequent window death requires a new refresh.
    """

    def __init__(self, source: PartyRoleNameExternalSource):
        if not isinstance(source, PartyRoleNameExternalSource):
            raise TypeError("S101 requires actual S100 external name source")
        self.source=source

    def _check(self, revision: int, pairs: frozenset[tuple[int,int]]) -> str:
        try:
            snap=self.source.start_producer.read_snapshot()
            if (not _valid_snapshot(snap)
                    or type(snap.revision) is not int or snap.revision < 0):
                return "INVALID_START_CACHE"
            current=_identity_set(snap)
            if (snap.revision != revision or current != pairs
                    or len(current) != len(snap.windows)):
                return "STALE_START_REVISION_OR_PAIR_SET"
            if len({p for _,p in pairs}) != len(pairs):
                return "DUPLICATE_START_PID"
            for hwnd,pid in pairs:
                if (not self.source.backend.is_window(hwnd)
                        or self.source.backend.process_id(hwnd) != pid):
                    return "STALE_NATIVE_HWND_PID"
            return "VALID"
        except Exception:
            return "NATIVE_OR_START_RECHECK_ERROR"

    def collect(self, snapshot: WindowSnapshot) -> PartyReadyPrepared:
        """Read external names using genuine S90 worker model, NO Tk."""
        if not _valid_snapshot(snapshot):
            return PartyReadyPrepared("INVALID_WORKER_START_SNAPSHOT")
        pairs=_identity_set(snapshot)
        if len(pairs)!=len(snapshot.windows) or not pairs:
            return PartyReadyPrepared("EMPTY_OR_AMBIGUOUS_WORKER_SNAPSHOT")
        revision=snapshot.revision
        if type(revision) is not int or revision < 0:
            return PartyReadyPrepared("INVALID_WORKER_REVISION")
        code=self._check(revision,pairs)
        if code!="VALID":
            return PartyReadyPrepared("BLOCKED_BEFORE_ROLE_READ_"+code)
        # If original character provider is not connected, S100 read_role
        # raises and S90 produces only (hwnd,pid,None), not a fake Window name.
        try:
            result=prepare_roster(snapshot,self.source.read_role)
        except Exception:
            return PartyReadyPrepared("BLOCKED_ROLE_WORKER_ERROR")
        code=self._check(revision,pairs)
        if code!="VALID":
            return PartyReadyPrepared("BLOCKED_AFTER_ROLE_READ_"+code)
        if result.revision != revision:
            return PartyReadyPrepared("BLOCKED_WORKER_REVISION")
        return PartyReadyPrepared("EXTERNAL_ROLE_ROSTER_PREPARED_NO_GAME",
                                  revision,pairs,result)

    def deliver(self, prepared: PartyReadyPrepared, *,
                roster: PartyRoster, ready_list: PartyReadyList,
                selected: tuple[str,...] = ()) -> PartyReadyHandoffResult:
        """S90 application + S91 READY DRAW on Tk thread; no team action.

        On any stale HWND/PID/revision, clear S90 and remove all S91 labels.
        Selected group values are CONFIG, not proof of an online ready member.
        """
        if not isinstance(roster, PartyRoster):
            raise TypeError("S101 must deliver into the existing S90 PartyRoster")
        if not isinstance(ready_list, PartyReadyList):
            raise TypeError("S101 must render via the existing S91 PartyReadyList")
        if (type(selected) is not tuple
                or any(type(n) is not str for n in selected)):
            raise TypeError("S101 selected group labels must be a string tuple")

        def reject(code: str) -> PartyReadyHandoffResult:
            roster.clear("HANDOFF_BLOCKED_"+code)
            ready_list.show(roster,selected)
            return PartyReadyHandoffResult("BLOCKED_"+code)

        if (not isinstance(prepared,PartyReadyPrepared)
                or prepared.code!="EXTERNAL_ROLE_ROSTER_PREPARED_NO_GAME"
                or prepared.roster_result is None or prepared.revision is None):
            return reject("NO_VALID_PREPARED_ROLE_READ")
        if (prepared.roster_result.revision!=prepared.revision
                or len(prepared.roster_result.members)!=len(prepared.pairs)
                or frozenset((m.hwnd,m.pid)
                             for m in prepared.roster_result.members)!=prepared.pairs):
            return reject("PREPARED_PAIRS_INCONSISTENT")
        code=self._check(prepared.revision,prepared.pairs)
        if code!="VALID":
            return reject("PRE_DRAW_"+code)
        try:
            latest=self.source.start_producer.read_snapshot()
            if not roster.apply(prepared.roster_result,latest):
                return reject("S90_REJECTED_STALE_WORKER")
            # Recheck immediately before SHOW, including actual native HWND.
            code=self._check(prepared.revision,prepared.pairs)
            if code!="VALID":
                return reject("PRE_DRAW_"+code)
            ready_list.show(roster,selected)
            # A native HWND could close during Tk drawing: clear the display
            # instead of leaving a stale row visible at end of this handoff.
            code=self._check(prepared.revision,prepared.pairs)
            if code!="VALID":
                return reject("DURING_DRAW_"+code)
            return PartyReadyHandoffResult(
                "DIAGNOSTIC_S100_S90_S91_READY_HANDOFF_NO_GAME_ACTION",
                tuple(ready_list.names))
        except Exception:
            # A failed Tk paint may have left a partial row; best effort to
            # clear both; do not report a valid render or action target.
            roster.clear("HANDOFF_RENDER_ERROR")
            try:ready_list.show(roster,selected)
            except Exception:pass
            return PartyReadyHandoffResult("BLOCKED_READY_LIST_RENDER_ERROR")
