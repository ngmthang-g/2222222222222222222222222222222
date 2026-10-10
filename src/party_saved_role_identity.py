"""S103 G03: read-only saved Party name vs S94 live-OWN identity provenance.

Original separation: G02/S91 display+saved RoleName is NOT action RoleID.
At action time the original resolves selected names from read_own_ids()
(pid, RoleID, Name, Lv) and hwnd_of_pid. This diagnostic ONLY reuses the
external TEST-only S94 identity preflight. It NEVER returns sendable HWNDs,
RoleIDs or TeamIDs, and never implements game packets, signed Info, or actions.

Important: S102 "saved offline/unverified" is a display classification;
a missing S94 match means NOT RESOLVED, not proof that a player is offline.
Real signed Info, original game memory readers and B04 PartyTab are missing.
"""
from __future__ import annotations

from dataclasses import dataclass

from party_combo_provenance import (
    PartySavedComboHandoff, PartyComboHandoffReport,
)
from party_group_config import PartySettings
from party_ready_handoff import PartyReadyPrepared
from party_ready_list import PartyReadyConfigEditor
from party_team_identity import PartyTeamIdentityPreflight


@dataclass(frozen=True)
class PartySavedIdentityObservation:
    group_num: int
    slot: int
    saved_name: str
    displayed_as: str
    role_identity_class: str
    s94_read_code: str
    # No numeric RoleID, PID, HWND or TeamID may escape to an action handler.


@dataclass(frozen=True)
class PartySavedIdentityReport:
    code: str
    observations: tuple[PartySavedIdentityObservation, ...] = ()
    external_source_only: bool = True
    game_identity_verified: bool = False
    action_authorized: bool = False
    packets_sent: int = 0
    signed_info_issuer_implemented: bool = False


class PartySavedRoleIdentityDiagnostic:
    """Compare actual S102 selected options to S94 TEST-own-role preflight."""

    def __init__(self, combo: PartySavedComboHandoff,
                 preflight: PartyTeamIdentityPreflight):
        if (not isinstance(combo, PartySavedComboHandoff)
                or not isinstance(preflight, PartyTeamIdentityPreflight)):
            raise TypeError("S103 reuses actual S102/S94 diagnostics")
        self.combo=combo
        self.preflight=preflight
        self.handoff=combo.handoff
        self.source=self.handoff.source

    def inspect(self, prior: PartyComboHandoffReport,
                prepared: PartyReadyPrepared, *,
                editor: PartyReadyConfigEditor) -> PartySavedIdentityReport:
        def blocked(code: str) -> PartySavedIdentityReport:
            return PartySavedIdentityReport("BLOCKED_"+code)
        if not isinstance(editor,PartyReadyConfigEditor):
            return blocked("INVALID_S91_EDITOR")
        if (not isinstance(prior,PartyComboHandoffReport)
                or prior.code!="DIAGNOSTIC_S102_S91_SAVED_VS_TEST_READY_NO_GAME_ACTION"
                or prior.action_authorized or prior.game_role_verified
                or prior.configuration_modified):
            return blocked("NO_VERIFIED_S102_PRESENTATION")
        if (not isinstance(prepared,PartyReadyPrepared)
                or prepared.code!="EXTERNAL_ROLE_ROSTER_PREPARED_NO_GAME"
                or type(prepared.revision) is not int
                or prepared.roster_result is None):
            return blocked("NO_VALID_S101_PREPARED_GENERATION")
        if (self.preflight.start_producer is not self.source.start_producer
                or self.preflight.backend is not self.source.backend):
            return blocked("S94_S101_NATIVE_SOURCES_DIFFER")
        try:
            state=editor.state
            if type(state) is not PartySettings:
                return blocked("INVALID_GROUP_SETTINGS")
            selected=[]
            for group in state.groups:
                if len(editor.group_inputs)<group.num:
                    return blocked("MISSING_S91_GROUP_INPUTS")
                for slot,name in enumerate(group.members):
                    if not name:continue
                    if (type(name) is not str or name!=name.strip()
                            or slot>=len(editor.group_inputs[group.num-1])
                            or editor.group_inputs[group.num-1][slot].get()!=name):
                        return blocked("CHANGED_COMBO_SELECTION")
                    options=[o for o in prior.options
                             if (o.group_num,o.slot,o.name)==(group.num,slot,name)]
                    if (len(options)!=1
                            or options[0].category not in (
                                "SAVED_SELECTED_OFFLINE_OR_UNVERIFIED",
                                "SAVED_SELECTED_AND_TEST_EXTERNAL_LIVE",
                                "SAVED_CURRENT_RESERVED_BY_EARLIER_GROUP")):
                        return blocked("S102_SELECTED_PROVENANCE_MISSING")
                    selected.append((group.num,slot,name,options[0].category))
            if len({x[2] for x in selected})!=len(selected):
                return blocked("SAVED_NAME_DUPLICATE_NO_ACTION")
        except Exception:
            return blocked("COMBO_SELECTION_INSPECTION_ERROR")
        if not selected:
            return PartySavedIdentityReport("DIAGNOSTIC_NO_SAVED_MEMBERS_NO_GAME_ACTION")
        if not callable(self.preflight.allowed):
            return blocked("S94_SIGNED_INFO_GATE_UNAVAILABLE")
        if (not callable(self.preflight.read_own_ids)
                or not callable(self.preflight.read_team_id)):
            return blocked("S94_LIVE_IDENTITY_PROVIDER_UNAVAILABLE")
        try:
            if self.preflight.allowed() is not True:
                return blocked("S94_PERMISSION_NOT_VERIFIED")
            first=self.handoff._check(prepared.revision,prepared.pairs)
        except Exception:
            return blocked("S94_PERMISSION_OR_START_READ_ERROR")
        if first!="VALID":
            return blocked("STALE_BEFORE_S94_"+first)

        saved_state=state
        rows=[]
        for group_num,slot,name,category in selected:
            # Never infer game identity from S100 RoleName, S102 Combobox,
            # or saved config. S94 resolves own ID from FRESH external records.
            checked=self.preflight.inspect((name,))
            if checked.code=="DIAGNOSTIC_OBSERVED_NO_GAME_ACTION":
                if (len(checked.targets)!=1
                        or checked.observed_revision!=prepared.revision
                        or checked.targets[0].saved_name!=name):
                    return blocked("S94_TARGET_OR_REVISION_MISMATCH")
                target=checked.targets[0]
                # A matching saved RoleID from ANOTHER PID is not a valid
                # match of the currently displayed ready character!
                display_exact=[m for m in editor._roster.members
                               if m.role_name==name]
                display_matches=display_exact or [
                    m for m in editor._roster.members
                    if m.role_name is not None
                    and m.role_name.lower()==name.lower()]
                if len(display_matches)>1:
                    label="AMBIGUOUS_S100_DISPLAY_IDENTITY"
                elif not display_matches:
                    label="S94_OWN_RECORD_OBSERVED_S100_DISPLAY_UNVERIFIED"
                elif (display_matches[0].hwnd,display_matches[0].pid)!=(
                        target.hwnd,target.pid):
                    label="S100_DISPLAY_VS_S94_OWN_PID_MISMATCH"
                else:
                    label="S94_TEST_OWN_ROLEID_MATCHED_S100_DISPLAY_PID"
            elif checked.code=="UNRESOLVED_ONLINE_MEMBERS":
                label=("S100_DISPLAY_SEEN_BUT_S94_OWN_ROLEID_UNRESOLVED"
                       if category=="SAVED_SELECTED_AND_TEST_EXTERNAL_LIVE"
                       else "SAVED_NOT_RESOLVED_BY_EXTERNAL_OWN_IDS")
            else:
                # S94 observed a stale HWND, revoked gate, invalid TeamID,
                # ambiguous RoleID, reader error, invalid record or no HWND:
                # fail closed for the FULL cross-snapshot report.
                return blocked("S94_"+checked.code)
            rows.append(PartySavedIdentityObservation(
                group_num,slot,name,category,label,checked.code))
            if self.handoff._check(prepared.revision,prepared.pairs)!="VALID":
                return blocked("STALE_DURING_S94_READ")
        try:
            if (editor.state!=saved_state
                    or any(editor.group_inputs[g-1][s].get()!=name
                           for g,s,name,_ in selected)):
                return blocked("CHANGED_SAVED_SELECTION_DURING_S94")
            if self.preflight.allowed() is not True:
                return blocked("S94_PERMISSION_REVOKED")
        except Exception:
            return blocked("FINAL_PERMISSION_OR_SELECTION_ERROR")
        if self.handoff._check(prepared.revision,prepared.pairs)!="VALID":
            return blocked("STALE_FINAL_NATIVE_GENERATION")
        return PartySavedIdentityReport(
            "DIAGNOSTIC_S103_TEST_OWN_ROLE_PROVENANCE_NO_GAME_ACTION",
            observations=tuple(rows))
