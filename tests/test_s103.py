"""S103 read-only G03 Party saved Combo ↔ S94 external OWN record provenance."""
from __future__ import annotations

from dataclasses import FrozenInstanceError,replace
from pathlib import Path
import sys,unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"tests")]
from test_s94 import Fixture,snap,win
from test_s91 import FakeLabel
from test_s102 import new_editor
from party_rolename_source import PartyRoleNameExternalSource
from party_ready_handoff import PartyExternalReadyHandoff
from party_combo_provenance import PartySavedComboHandoff
from party_saved_role_identity import PartySavedRoleIdentityDiagnostic
from party_ready_list import PartyReadyConfigEditor


class S103SavedRoleIdentityTests(unittest.TestCase):
    def setUp(self):
        self.fx=Fixture()
        self.fx.records=[(1000,0,"Đội Trưởng",10),(1001,430,"Hòa✨",11)]
        self.names={100:{"RoleName":"<b>Đội</b> Trưởng"},
                    101:{"RoleName":"Hòa✨"}}
        self.editor=new_editor((("Đội Trưởng","Offline"),("Hòa✨",)))
        p=patch("party_ready_list.ttk.Label",FakeLabel)
        p.start();self.addCleanup(p.stop)

    def chain(self,*,pre=None,read=None,editor=None):
        source=PartyRoleNameExternalSource(
            start_producer=self.fx.producer,backend=self.fx.backend,
            get_character_info=read if read is not None else
                (lambda hwnd:self.names[hwnd]))
        combo=PartySavedComboHandoff(PartyExternalReadyHandoff(source))
        prepared=combo.handoff.collect(self.fx.snapshot)
        prior=combo.deliver(prepared,editor=editor or self.editor)
        obj=PartySavedRoleIdentityDiagnostic(combo,pre or self.fx.pre())
        return obj,prepared,prior

    def perform(self,**kwargs):
        diag,batch,prior=self.chain(**kwargs)
        return diag.inspect(prior,batch,editor=kwargs.get("editor") or self.editor)

    def row(self,report,name):
        return next(x for x in report.observations if x.saved_name==name)

    def test_01_two_fresh_external_own_records_match_display_pid(self):
        r=self.perform()
        self.assertEqual(r.code,"DIAGNOSTIC_S103_TEST_OWN_ROLE_PROVENANCE_NO_GAME_ACTION")
        self.assertEqual(len(r.observations),3)
        for name in ("Đội Trưởng","Hòa✨"):
            x=self.row(r,name)
            self.assertEqual(x.role_identity_class,"S94_TEST_OWN_ROLEID_MATCHED_S100_DISPLAY_PID")
            self.assertEqual(x.s94_read_code,"DIAGNOSTIC_OBSERVED_NO_GAME_ACTION")

    def test_02_saved_offline_is_unresolved_not_online_assertion(self):
        r=self.perform()
        x=self.row(r,"Offline")
        self.assertEqual(x.displayed_as,"SAVED_SELECTED_OFFLINE_OR_UNVERIFIED")
        self.assertEqual(x.role_identity_class,"SAVED_NOT_RESOLVED_BY_EXTERNAL_OWN_IDS")
        self.assertEqual(x.s94_read_code,"UNRESOLVED_ONLINE_MEMBERS")

    def test_03_roleid_zero_not_assumed_invalid_sentinel(self):
        r=self.perform()
        self.assertEqual(self.row(r,"Đội Trưởng").role_identity_class,
                         "S94_TEST_OWN_ROLEID_MATCHED_S100_DISPLAY_PID")
        self.assertEqual(self.fx.records[0][1],0)

    def test_04_none_and_ffffffff_team_are_original_not_role_id_sentinel(self):
        self.fx.teams[100]=0xFFFFFFFF
        r=self.perform()
        self.assertEqual(self.row(r,"Đội Trưởng").s94_read_code,
                         "DIAGNOSTIC_OBSERVED_NO_GAME_ACTION")

    def test_05_no_game_authorization_even_when_two_names_match(self):
        r=self.perform()
        self.assertTrue(r.external_source_only)
        self.assertFalse(r.game_identity_verified)
        self.assertFalse(r.action_authorized)
        self.assertEqual(r.packets_sent,0)
        self.assertFalse(r.signed_info_issuer_implemented)

    def test_06_s94_different_pid_for_same_role_name_is_not_verified(self):
        self.fx.records=[(1000,1,"Hòa✨",10),(1001,2,"Đội Trưởng",10)]
        r=self.perform()
        self.assertEqual(self.row(r,"Đội Trưởng").role_identity_class,
                         "S100_DISPLAY_VS_S94_OWN_PID_MISMATCH")
        self.assertEqual(self.row(r,"Hòa✨").role_identity_class,
                         "S100_DISPLAY_VS_S94_OWN_PID_MISMATCH")

    def test_07_display_visible_but_missing_external_own_role_record(self):
        self.fx.records=[(1000,1,"Đội Trưởng",10)]
        r=self.perform()
        self.assertEqual(self.row(r,"Hòa✨").role_identity_class,
                         "S100_DISPLAY_SEEN_BUT_S94_OWN_ROLEID_UNRESOLVED")

    def test_08_external_own_record_but_display_role_source_missing(self):
        self.names[101]={"RoleName":None}
        r=self.perform()
        self.assertEqual(self.row(r,"Hòa✨").role_identity_class,
                         "S94_OWN_RECORD_OBSERVED_S100_DISPLAY_UNVERIFIED")

    def test_09_s100_wrong_role_name_does_not_prove_current_roleid(self):
        self.names[100]={"RoleName":"Another"}
        r=self.perform()
        self.assertEqual(self.row(r,"Đội Trưởng").role_identity_class,
                         "S94_OWN_RECORD_OBSERVED_S100_DISPLAY_UNVERIFIED")

    def test_10_s94_record_pid_outside_start_cache_unresolved(self):
        self.fx.records=[(1000,1,"Đội Trưởng",10),
                         (9999,2,"Hòa✨",10)]
        r=self.perform()
        self.assertEqual(self.row(r,"Hòa✨").role_identity_class,
                         "S100_DISPLAY_SEEN_BUT_S94_OWN_ROLEID_UNRESOLVED")

    def test_11_original_lowercase_fallback_allowed_when_unambiguous(self):
        self.fx.records=[(1000,1,"đội trưởng",10),(1001,2,"Hòa✨",10)]
        r=self.perform()
        self.assertEqual(self.row(r,"Đội Trưởng").role_identity_class,
                         "S94_TEST_OWN_ROLEID_MATCHED_S100_DISPLAY_PID")

    def test_12_ambiguous_roleid_lowercase_blocks_no_rows(self):
        self.editor=new_editor((("Name",),))
        self.fx.records=[(1000,1,"name",1),(1001,2,"NAME",1)]
        self.names={100:{"RoleName":"Name"},101:{"RoleName":"Other"}}
        r=self.perform()
        self.assertIn("AMBIGUOUS_LOWERCASE",r.code)
        self.assertEqual(r.observations,())

    def test_13_duplicate_saved_names_across_groups_blocks(self):
        self.editor=new_editor((("Đội Trưởng",),("Đội Trưởng",)))
        r=self.perform()
        self.assertEqual(r.code,"BLOCKED_SAVED_NAME_DUPLICATE_NO_ACTION")

    def test_14_absent_signed_info_gate_blocks_all_records(self):
        r=self.perform(pre=self.fx.pre(allowed=None))
        self.assertEqual(r.code,"BLOCKED_S94_SIGNED_INFO_GATE_UNAVAILABLE")
        self.assertEqual(r.observations,())

    def test_15_permission_denied_blocks_all_records(self):
        self.fx.permission=False
        r=self.perform()
        self.assertEqual(r.code,"BLOCKED_S94_PERMISSION_NOT_VERIFIED")
        self.assertEqual(r.observations,())

    def test_16_no_external_own_role_reader_blocks(self):
        r=self.perform(pre=self.fx.pre(read_own_ids=None))
        self.assertEqual(r.code,"BLOCKED_S94_LIVE_IDENTITY_PROVIDER_UNAVAILABLE")

    def test_17_no_external_team_reader_blocks(self):
        r=self.perform(pre=self.fx.pre(read_team_id=None))
        self.assertEqual(r.code,"BLOCKED_S94_LIVE_IDENTITY_PROVIDER_UNAVAILABLE")

    def test_18_stale_start_revision_after_S102_before_S103_blocks(self):
        obj,batch,prior=self.chain()
        self.fx.producer.value=snap(2,*self.fx.snapshot.windows)
        r=obj.inspect(prior,batch,editor=self.editor)
        self.assertIn("STALE_BEFORE_S94_STALE_START_REVISION",r.code)

    def test_19_closed_native_hwnd_after_s102_blocks(self):
        obj,batch,prior=self.chain()
        self.fx.backend.mapped.pop(101)
        r=obj.inspect(prior,batch,editor=self.editor)
        self.assertEqual(r.observations,())
        self.assertIn("STALE_BEFORE_S94_STALE_NATIVE_HWND_PID",r.code)

    def test_20_reused_pid_after_S102_blocks(self):
        obj,batch,prior=self.chain()
        self.fx.backend.mapped[101]=4444
        self.assertIn("STALE_BEFORE_S94_STALE_NATIVE_HWND_PID",
                      obj.inspect(prior,batch,editor=self.editor).code)

    def test_21_revoked_permission_during_S94_blocks_partial(self):
        obj,batch,prior=self.chain()
        def revoke(hwnd):
            self.fx.permission=False
            return self.fx.teams[hwnd]
        obj.preflight.read_team_id=revoke
        result=obj.inspect(prior,batch,editor=self.editor)
        self.assertIn("S94_PERMISSION_REVOKED",result.code)
        self.assertEqual(result.observations,())

    def test_22_stale_epoch_during_roleid_callback_blocks(self):
        obj,batch,prior=self.chain()
        def modify():
            self.fx.producer.value=snap(2,*self.fx.snapshot.windows)
            return self.fx.records
        obj.preflight.read_own_ids=modify
        result=obj.inspect(prior,batch,editor=self.editor)
        self.assertTrue(result.code.startswith("BLOCKED_S94_STALE_START_REVISION"))
        self.assertFalse(result.observations)

    def test_23_s94_native_data_sources_must_be_same_S101_source(self):
        another=Fixture()
        r=self.perform(pre=another.pre())
        self.assertEqual(r.code,"BLOCKED_S94_S101_NATIVE_SOURCES_DIFFER")

    def test_24_blocked_or_forged_s102_report_rejected(self):
        obj,batch,prior=self.chain()
        wrong=replace(prior,code="BLOCKED_S102")
        r=obj.inspect(wrong,batch,editor=self.editor)
        self.assertEqual(r.code,"BLOCKED_NO_VERIFIED_S102_PRESENTATION")
        wrong=replace(prior,action_authorized=True)
        self.assertEqual(obj.inspect(wrong,batch,editor=self.editor).observations,())

    def test_25_changing_combobox_current_saved_name_blocks(self):
        obj,batch,prior=self.chain()
        self.editor.group_inputs[0][0].name="NotSaved"
        r=obj.inspect(prior,batch,editor=self.editor)
        self.assertIn("CHANGED_COMBO_SELECTION",r.code)

    def test_26_s102_wrong_per_slot_category_blocks(self):
        obj,batch,prior=self.chain()
        first=next(i for i,x in enumerate(prior.options)
                   if x.group_num==1 and x.slot==0 and x.name=="Đội Trưởng")
        opts=list(prior.options)
        opts[first]=replace(opts[first],category="TEST_EXTERNAL_LIVE_AVAILABLE")
        r=obj.inspect(replace(prior,options=tuple(opts)),batch,editor=self.editor)
        self.assertIn("S102_SELECTED_PROVENANCE_MISSING",r.code)

    def test_27_immutable_presentation_no_targets_or_runtime_ids(self):
        r=self.perform()
        with self.assertRaises(FrozenInstanceError):
            r.action_authorized=True
        with self.assertRaises(FrozenInstanceError):
            r.observations[0].saved_name="Fake"
        for x in (r,r.observations[0]):
            self.assertFalse(hasattr(x,"role_id"))
            self.assertFalse(hasattr(x,"team_id"))
            self.assertFalse(hasattr(x,"hwnd"))
            self.assertFalse(hasattr(x,"pid"))

    def test_28_no_saved_names_is_not_identity_verified(self):
        editor=new_editor((("",),))
        r=self.perform(editor=editor)
        self.assertEqual(r.code,"DIAGNOSTIC_NO_SAVED_MEMBERS_NO_GAME_ACTION")
        self.assertFalse(r.game_identity_verified)
        self.assertEqual(r.observations,())

    def test_29_none_teamid_preflight_error_never_promotes_identity(self):
        self.fx.teams[101]=None
        r=self.perform()
        self.assertIn("S94_TEAMID_UNKNOWN_NOT_OUTSIDE",r.code)
        self.assertEqual(r.observations,())

    def test_30_no_game_packet_click_memory_or_auth_provisioning(self):
        source=(ROOT/"src/party_saved_role_identity.py").read_text("utf-8")
        for keyword in ("ReadProcessMemory(", "WriteProcessMemory(",
                        "SendMessage(", "PostMessage(", "200051", "200057",
                        "create_team(", "leave_team(", "memory_items.invite(",
                        "TOKEN_HMAC_SECRET", "ctypes.windll"):
            self.assertNotIn(keyword,source)
        self.assertFalse(self.perform().action_authorized)

if __name__=="__main__":
    unittest.main()
