"""S102 G02 TEST/EXTERNAL Party group Combo option provenance at Tk handoff.

The existing S91 PartyReadyConfigEditor already owns Combobox construction,
_saved values_ and earlier-cluster exclusions. This read-only diagnostic
adapter reuses its _refresh_dropdown_values unchanged after the S101 native
HWND/PID-fenced handoff. It labels retained saved/offline selections as
configuration, NEVER verified live character identity or a game action target.

No new widgets, settings save, game reader, packets, auth or original timing.
It is not wired to the original full PartyTab; external names are TEST ONLY.
"""
from __future__ import annotations

from dataclasses import dataclass

from party_group_config import PartySettings
from party_ready_handoff import PartyExternalReadyHandoff, PartyReadyPrepared
from party_ready_list import PartyReadyConfigEditor


@dataclass(frozen=True)
class PartyComboOptionProvenance:
    group_num: int
    slot: int
    name: str
    category: str
    # This is a presentational option, never a sendable RoleID or HWND.


@dataclass(frozen=True)
class PartyComboHandoffReport:
    code: str
    ready_names: tuple[str, ...] = ()
    options: tuple[PartyComboOptionProvenance, ...] = ()
    retained_saved_names: tuple[str, ...] = ()
    source_provenance: str = "TEST_EXTERNAL_UNVERIFIED_NOT_GAME"
    action_authorized: bool = False
    game_role_verified: bool = False
    configuration_modified: bool = False


class PartySavedComboHandoff:
    """Tk-thread-only coordinator; S101 worker collect remains unchanged."""

    def __init__(self, handoff: PartyExternalReadyHandoff):
        if not isinstance(handoff, PartyExternalReadyHandoff):
            raise TypeError("S102 requires the genuine S101 native ready handoff")
        self.handoff = handoff

    def deliver(self, prepared: PartyReadyPrepared, *,
                editor: PartyReadyConfigEditor) -> PartyComboHandoffReport:
        if not isinstance(editor, PartyReadyConfigEditor):
            raise TypeError("S102 requires existing S91 PartyReadyConfigEditor")
        if (not isinstance(editor.state, PartySettings)
                or len(editor.group_inputs) != len(editor.state.groups)
                or any(len(row) > 6 for row in editor.group_inputs)):
            return PartyComboHandoffReport("BLOCKED_INVALID_S91_GROUP_CONFIG")
        saved_state=editor.state

        def refresh() -> bool:
            """Clears stale live options while keeping current saved values."""
            try:
                editor._refresh_ready()
                editor._refresh_dropdown_values()
                return editor.state == saved_state
            except Exception:
                return False

        def reject(code: str) -> PartyComboHandoffReport:
            editor._roster.clear("S102_BLOCKED_"+code)
            if not refresh():
                return PartyComboHandoffReport("BLOCKED_"+code+"_UI_REFRESH_FAILED")
            return PartyComboHandoffReport("BLOCKED_"+code)

        try:
            selected=PartyReadyConfigEditor._selected_names(editor)
            result=self.handoff.deliver(
                prepared,roster=editor._roster,ready_list=editor.ready_list,
                selected=selected)
        except Exception:
            return reject("S101_HANDOFF_ERROR")

        if not result.code.startswith("DIAGNOSTIC_"):
            return reject("S101_"+result.code)
        try:
            # Existing S91 logic: earlier groups reserve their choices,
            # while the current Combo's saved value remains selectable even
            # when no longer online. No configuration is written here.
            editor._refresh_dropdown_values()
        except Exception:
            return reject("S91_COMBO_REFRESH_ERROR")

        # Physical death/Start revision may occur during Combo painting.
        # Recheck via SAME S101 native fence, not stale S90 cache alone.
        if not isinstance(prepared,PartyReadyPrepared) or prepared.revision is None:
            return reject("INVALID_PREPARED_EPOCH")
        code=self.handoff._check(prepared.revision,prepared.pairs)
        if code!="VALID":
            return reject("POST_COMBO_"+code)
        if editor.state!=saved_state:
            return reject("CONFIG_CHANGED_DURING_PRESENTATION")

        live=frozenset(editor._roster.ready_names())
        selected_saved={n for group in saved_state.groups for n in group.members if n}
        provenance=[]
        saved_offline=[]
        try:
            used_before: set[str] = set()
            for group,combos in zip(saved_state.groups,editor.group_inputs):
                for slot,combo in enumerate(combos):
                    current=combo.get()
                    if type(current) is not str:
                        return reject("NONSTRING_COMBO_VALUE")
                    values=tuple(combo["values"])
                    if any(type(n) is not str for n in values):
                        return reject("NONSTRING_COMBO_OPTIONS")
                    if not values or values[0]!="":
                        return reject("MISSING_BLANK_OPTION")
                    if len(set(values))!=len(values):
                        return reject("DUPLICATED_COMBO_OPTIONS")
                    saved=(group.members[slot]
                           if slot<len(group.members) else "")
                    for name in values:
                        if name and name in used_before and name != current:
                            return reject("EARLIER_CLUSTER_SELECTION_OFFERED")
                        if not name:
                            category="EMPTY_OPTION"
                        elif name==current and saved==name and name in used_before:
                            category="SAVED_CURRENT_RESERVED_BY_EARLIER_GROUP"
                        elif name==current and saved==name and name not in live:
                            category="SAVED_SELECTED_OFFLINE_OR_UNVERIFIED"
                            if name not in saved_offline:saved_offline.append(name)
                        elif name==current and saved==name and name in live:
                            category="SAVED_SELECTED_AND_TEST_EXTERNAL_LIVE"
                        elif name==current and saved!=name:
                            category="UNCOMMITTED_WIDGET_VALUE_NOT_VERIFIED"
                        elif name in live and name not in selected_saved:
                            category="TEST_EXTERNAL_LIVE_AVAILABLE"
                        elif name in live and name in selected_saved:
                            category="TEST_EXTERNAL_LIVE_SELECTED_IN_ANOTHER_GROUP"
                        else:
                            # A previously saved/offline name MUST NOT
                            # masquerade as a new verified live choice.
                            return reject("UNEXPLAINED_OFFLINE_NEW_OPTION")
                        provenance.append(PartyComboOptionProvenance(
                            group.num,slot,name,category))
                used_before.update(n for n in group.members if n)
        except Exception:
            return reject("S91_COMBO_INSPECTION_ERROR")

        # Protect against a window dying while reading actual Combo values.
        code=self.handoff._check(prepared.revision,prepared.pairs)
        if code!="VALID":
            return reject("POST_INSPECT_"+code)
        if editor.state!=saved_state:
            return reject("CONFIG_CHANGED_DURING_INSPECTION")
        return PartyComboHandoffReport(
            "DIAGNOSTIC_S102_S91_SAVED_VS_TEST_READY_NO_GAME_ACTION",
            ready_names=tuple(editor.ready_list.names),
            options=tuple(provenance),
            retained_saved_names=tuple(saved_offline))
