"""S102: Party S91 Combo existing-options and offline-saved provenance tests."""
from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"tests"))

from test_s94 import Fixture,snap,win
from test_s91 import FakeLabel,fake_view
from party_group_config import PartyGroup,PartySettings
from party_rolename_source import PartyRoleNameExternalSource
from party_ready_handoff import PartyExternalReadyHandoff
from party_combo_provenance import PartySavedComboHandoff
from party_ready_list import PartyReadyConfigEditor
from party_roster import PartyRoster


class Combo:
    def __init__(self,name):self.name=name;self.values=()
    def get(self):return self.name
    def configure(self,**kwargs):self.values=kwargs["values"]
    def __getitem__(self,key):
        if key=="values":return self.values
        raise KeyError(key)


def new_editor(groups):
    e=object.__new__(PartyReadyConfigEditor)
    e.state=PartySettings(groups=tuple(
        PartyGroup(i+1,tuple(names)) for i,names in enumerate(groups)))
    e.group_inputs=[[Combo(n) for n in names] for names in groups]
    e._roster=PartyRoster()
    e.ready_list=fake_view()
    return e


class S102GroupCombo(unittest.TestCase):
    def setUp(self):
        self.fx=Fixture()
        self.data={100:{"RoleName":"<b>Đội</b> Trưởng"},
                   101:{"RoleName":"Hòa✨"}}
        self.editor=new_editor((("Đội Trưởng","Offline"),("Hòa✨",)))
        p=patch("party_ready_list.ttk.Label",FakeLabel)
        p.start();self.addCleanup(p.stop)

    def adapter(self,read=None):
        source=PartyRoleNameExternalSource(
            start_producer=self.fx.producer,backend=self.fx.backend,
            get_character_info=(lambda hwnd:self.data[hwnd]) if read is None else read)
        hand=PartyExternalReadyHandoff(source)
        return PartySavedComboHandoff(hand)

    def collect(self,a):
        return a.handoff.collect(self.fx.snapshot)

    def perform(self,a=None,editor=None):
        a=a or self.adapter()
        b=self.collect(a)
        return a.deliver(b,editor=editor or self.editor)

    def values(self,i,j):return self.editor.group_inputs[i][j].values
    def option(self,report,group,slot,name):
        return next(r for r in report.options if r.group_num==group
                    and r.slot==slot and r.name==name)

    def test_01_existing_S91_combobox_refresh_is_reused(self):
        r=self.perform()
        self.assertEqual(r.code,"DIAGNOSTIC_S102_S91_SAVED_VS_TEST_READY_NO_GAME_ACTION")
        self.assertEqual(self.values(0,0),("","Đội Trưởng","Hòa✨"))
        self.assertEqual(self.values(0,1),("","Đội Trưởng","Hòa✨","Offline"))
        self.assertEqual(self.values(1,0),("","Hòa✨"))
        self.assertEqual(r.ready_names,())

    def test_02_saved_offline_preserved_as_current_value(self):
        r=self.perform()
        self.assertIn("Offline",r.retained_saved_names)
        self.assertEqual(self.option(r,1,1,"Offline").category,
                         "SAVED_SELECTED_OFFLINE_OR_UNVERIFIED")
        self.assertEqual(self.editor.group_inputs[0][1].get(),"Offline")

    def test_03_offline_name_not_offered_as_new_option(self):
        self.perform()
        self.assertNotIn("Offline",self.values(0,0))
        self.assertNotIn("Offline",self.values(1,0))

    def test_04_earlier_cluster_selection_excluded_from_later_cluster(self):
        r=self.perform()
        self.assertNotIn("Đội Trưởng",self.values(1,0))
        self.assertEqual(self.option(r,1,0,"Đội Trưởng").category,
                         "SAVED_SELECTED_AND_TEST_EXTERNAL_LIVE")

    def test_05_later_selected_name_may_remain_prior_dropdown_according_to_S91(self):
        r=self.perform()
        self.assertIn("Hòa✨",self.values(0,0))
        self.assertEqual(self.option(r,1,0,"Hòa✨").category,
                         "TEST_EXTERNAL_LIVE_SELECTED_IN_ANOTHER_GROUP")

    def test_06_no_config_mutation_even_as_ready_options_update(self):
        old=self.editor.state
        self.perform()
        self.assertEqual(self.editor.state,old)

    def test_07_unicode_tag_stripping_via_S100_and_existing_S90(self):
        self.editor=new_editor((("Offline",),("",)))
        r=self.perform()
        self.assertEqual(r.ready_names,("Đội Trưởng","Hòa✨"))
        self.assertIn("Hòa✨",self.values(1,0))

    def test_08_no_original_reader_keeps_offline_choice_only(self):
        r=self.perform(self.adapter(read=lambda _:{"FakeName":"No real reader"}))
        self.assertEqual(r.ready_names,())
        self.assertEqual(self.values(0,1),("","Offline"))
        self.assertEqual(self.values(1,0),("","Hòa✨"))
        self.assertFalse(r.game_role_verified)

    def test_09_window_fallback_not_fabricated(self):
        self.data[100]={"RoleName":""}
        self.data[101]={"RoleName":None}
        r=self.perform()
        self.assertEqual(r.ready_names,())
        self.assertNotIn("Window ",repr(r.options))

    def test_10_native_child_closed_after_worker_clears_live_options(self):
        a=self.adapter();b=self.collect(a)
        self.fx.backend.mapped.pop(101)
        r=a.deliver(b,editor=self.editor)
        self.assertTrue(r.code.startswith("BLOCKED_S101_"))
        self.assertEqual(self.values(0,0),("","Đội Trưởng"))
        self.assertEqual(self.values(0,1),("","Offline"))
        self.assertEqual(self.values(1,0),("","Hòa✨"))

    def test_11_window_reused_with_new_pid_after_worker_blocks(self):
        a=self.adapter();b=self.collect(a)
        self.fx.backend.mapped[101]=9999
        self.assertTrue(a.deliver(b,editor=self.editor).code.startswith("BLOCKED_"))
        self.assertEqual(self.values(0,1),("","Offline"))

    def test_12_start_revision_updated_after_worker_blocks(self):
        a=self.adapter();b=self.collect(a)
        self.fx.producer.value=snap(2,*self.fx.snapshot.windows)
        r=a.deliver(b,editor=self.editor)
        self.assertTrue(r.code.startswith("BLOCKED_"))
        self.assertEqual(self.values(0,1),("","Offline"))

    def test_13_native_stale_after_first_S91_combo_paint_blocks(self):
        a=self.adapter();b=self.collect(a)
        first=self.editor.group_inputs[0][0]
        orig=first.configure
        def fail(**kwargs):
            orig(**kwargs)
            self.fx.backend.mapped.pop(101,None)
        first.configure=fail
        r=a.deliver(b,editor=self.editor)
        self.assertTrue(r.code.startswith("BLOCKED_POST_COMBO_STALE_NATIVE_HWND_PID"))
        self.assertEqual(self.values(0,1),("","Offline"))

    def test_14_cache_changed_after_first_combo_paint_blocks(self):
        a=self.adapter();b=self.collect(a)
        first=self.editor.group_inputs[0][0]
        orig=first.configure
        def changed(**kwargs):
            orig(**kwargs)
            self.fx.producer.value=snap(2,*self.fx.snapshot.windows)
        first.configure=changed
        r=a.deliver(b,editor=self.editor)
        self.assertIn("POST_COMBO_STALE_START_REVISION",r.code)
        self.assertEqual(self.values(0,1),("","Offline"))

    def test_15_during_inspection_stale_native_state_blocks(self):
        a=self.adapter();b=self.collect(a)
        c=self.editor.group_inputs[0][0]
        orig=c.__class__.get
        count=[0]
        def get(com):
            count[0]+=1
            if count[0]>=4:self.fx.backend.mapped.pop(101,None)
            return orig(com)
        with patch.object(Combo,"get",get):
            r=a.deliver(b,editor=self.editor)
        self.assertTrue(r.code.startswith("BLOCKED_POST_INSPECT_"),r.code)

    def test_16_source_role_unavailable_preserves_saved_selected(self):
        self.data[100]={"RoleName":None}
        r=self.perform()
        self.assertIn("Đội Trưởng",r.retained_saved_names)
        self.assertEqual(self.values(0,0),("","Đội Trưởng"))

    def test_17_same_role_on_both_PIDs_is_not_new_ready_name(self):
        self.data[100]={"RoleName":"Hòa✨"}
        r=self.perform()
        self.assertEqual(r.ready_names,())
        self.assertEqual(self.values(0,1),("","Offline"))

    def test_18_stale_live_choice_does_not_mutate_saved_settings(self):
        saved=self.editor.state
        a=self.adapter();b=self.collect(a)
        self.fx.backend.mapped.pop(100)
        a.deliver(b,editor=self.editor)
        self.assertIs(saved,self.editor.state)

    def test_19_invalid_prepared_without_prior_render_retains_offline(self):
        a=self.adapter()
        r=a.deliver(None,editor=self.editor)
        self.assertEqual(r.ready_names,())
        self.assertEqual(self.values(0,1),("","Offline"))

    def test_20_existing_ready_list_clears_on_failing_second_batch(self):
        self.editor=new_editor((("Offline",),("",)))
        a=self.adapter()
        self.assertEqual(self.perform(a).ready_names,("Đội Trưởng","Hòa✨"))
        b=self.collect(a)
        self.fx.backend.mapped.pop(101)
        r=a.deliver(b,editor=self.editor)
        self.assertEqual(r.ready_names,())
        self.assertEqual(self.editor.ready_list.names,())
        self.assertEqual(self.values(0,0),("","Offline"))

    def test_21_invalid_editor_type_rejected(self):
        a=self.adapter()
        with self.assertRaises(TypeError):
            a.deliver(None,editor={})

    def test_22_constructor_rejects_non_S101_adapter(self):
        with self.assertRaises(TypeError):
            PartySavedComboHandoff(None)

    def test_23_bad_group_widgets_fail_closed(self):
        a=self.adapter()
        self.editor.group_inputs.append([Combo("bad")])
        r=a.deliver(None,editor=self.editor)
        self.assertEqual(r.code,"BLOCKED_INVALID_S91_GROUP_CONFIG")

    def test_24_test_external_name_is_not_authorized_to_act(self):
        r=self.perform()
        self.assertFalse(r.action_authorized)
        self.assertFalse(r.game_role_verified)
        self.assertEqual(r.source_provenance,"TEST_EXTERNAL_UNVERIFIED_NOT_GAME")
        self.assertFalse(hasattr(r,"role_id"))
        self.assertFalse(hasattr(r,"team_id"))

    def test_25_reports_are_immutable(self):
        r=self.perform()
        with self.assertRaises(FrozenInstanceError):
            r.action_authorized=True
        with self.assertRaises(FrozenInstanceError):
            r.options[0].name="Fake"

    def test_26_uncommitted_widget_value_not_promoted_to_saved_identity(self):
        self.editor.group_inputs[0][0].name="NotSaved"
        r=self.perform()
        self.assertEqual(self.option(r,1,0,"NotSaved").category,
                         "UNCOMMITTED_WIDGET_VALUE_NOT_VERIFIED")
        self.assertEqual(self.editor.state.groups[0].members[0],"Đội Trưởng")

    def test_27_retained_offline_not_assumed_online_on_new_ready_cycle(self):
        r=self.perform()
        self.assertIn("Offline",r.retained_saved_names)
        self.data[101]={"RoleName":"Offline"}
        r2=self.perform()
        self.assertNotIn("Offline",r2.retained_saved_names)
        self.assertEqual(self.option(r2,1,1,"Offline").category,
                         "SAVED_SELECTED_AND_TEST_EXTERNAL_LIVE")

    def test_28_invalid_role_provider_does_not_turn_stale_saved_name_into_new_option(self):
        self.data[100]={"RoleName":"<b></b>"}
        self.data[101]={"RoleName":False}
        r=self.perform()
        self.assertEqual(r.ready_names,())
        self.assertEqual(self.values(1,0),("","Hòa✨"))

    def test_29_adapter_does_not_save_settings_or_invent_GUI(self):
        s=(ROOT/"src/party_combo_provenance.py").read_text("utf-8")
        for token in ("ReadProcessMemory(", "PostMessage(", "SendMessage(",
                      "write_settings(", ".save(", "create_team(",
                      "leave_team(", "200051", "200057", "Tk("):
            self.assertNotIn(token,s)

    def test_30_all_results_say_no_game_action(self):
        a=self.adapter()
        r=self.perform(a)
        self.assertIn("NO_GAME_ACTION",r.code)
        self.assertFalse(r.configuration_modified)
        self.assertEqual(self.editor.ready_list.names,())

if __name__=="__main__":
    unittest.main()
