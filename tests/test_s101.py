"""S101 external G03 RoleName to existing S90/S91 READY handoff tests."""
from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"tests"))
from test_s94 import Fixture, snap, win
from test_s91 import FakeLabel,fake_view
from party_rolename_source import PartyRoleNameExternalSource
from party_ready_handoff import PartyExternalReadyHandoff
from party_roster import PartyRoster, PartyRosterResult, PartyMember
from party_ready_list import PartyReadyList


class S101ReadyHandoff(unittest.TestCase):
    def setUp(self):
        self.fx=Fixture()
        self.data={100:{"RoleName":"<b>Đội</b> Trưởng"},
                   101:{"RoleName":"Hòa✨"}}
        self.roster=PartyRoster()
        self.view=fake_view()
        patcher=patch("party_ready_list.ttk.Label",FakeLabel)
        patcher.start()
        self.addCleanup(patcher.stop)

    def hand(self,read=None):
        source=PartyRoleNameExternalSource(
            start_producer=self.fx.producer,backend=self.fx.backend,
            get_character_info=(lambda hwnd:self.data[hwnd]) if read is None else read)
        return PartyExternalReadyHandoff(source)

    def do(self, hand=None, selected=()):
        hand=hand or self.hand()
        b=hand.collect(self.fx.snapshot)
        return hand.deliver(b,roster=self.roster,
                            ready_list=self.view,selected=selected)

    def test_01_normal_s100_s90_s91_chain_displays_unicode(self):
        r=self.do()
        self.assertEqual(r.code,"DIAGNOSTIC_S100_S90_S91_READY_HANDOFF_NO_GAME_ACTION")
        self.assertEqual(r.displayed_ready_names,("Đội Trưởng","Hòa✨"))
        self.assertEqual(self.view.names,r.displayed_ready_names)
        self.assertEqual([(x.row,x.column) for x in self.view.labels],[(0,0),(0,1)])

    def test_02_selected_member_hidden_from_ready_ui(self):
        r=self.do(selected=("Đội Trưởng",))
        self.assertEqual(r.displayed_ready_names,("Hòa✨",))

    def test_03_missing_original_reader_has_no_fabricated_name(self):
        h=self.hand(read=lambda _:{"Name":"window title not RoleName"})
        r=self.do(h)
        self.assertEqual(r.displayed_ready_names,())
        self.assertEqual(self.view.labels,[])

    def test_04_none_reader_halts_ready_names(self):
        h=PartyExternalReadyHandoff(PartyRoleNameExternalSource(
            start_producer=self.fx.producer,backend=self.fx.backend,
            get_character_info=None))
        r=self.do(h)
        self.assertEqual(r.displayed_ready_names,())
        self.assertEqual(self.roster.ready_names(),())

    def test_05_one_invalid_role_is_excluded_not_invented(self):
        self.data[101]={"RoleName":None}
        r=self.do()
        self.assertEqual(r.displayed_ready_names,("Đội Trưởng",))

    def test_06_original_window_fallback_not_conjured(self):
        self.data[100]={"RoleName":"<p></p>"}
        self.data[101]={"RoleName":""}
        self.assertEqual(self.do().displayed_ready_names,())
        self.assertNotIn("Window ",str(self.view.names))

    def test_07_stale_cache_before_worker_blocks(self):
        self.fx.producer.value=snap(2,*self.fx.snapshot.windows)
        batch=self.hand().collect(self.fx.snapshot)
        self.assertTrue(batch.code.startswith("BLOCKED_BEFORE_ROLE_READ_"))
        self.assertIsNone(batch.roster_result)

    def test_08_native_hwnd_closed_before_worker_blocks(self):
        self.fx.backend.mapped.pop(101)
        batch=self.hand().collect(self.fx.snapshot)
        self.assertIn("STALE_NATIVE_HWND_PID",batch.code)

    def test_09_native_hwnd_reused_before_worker_blocks(self):
        self.fx.backend.mapped[101]=9999
        self.assertIn("STALE_NATIVE_HWND_PID",
                      self.hand().collect(self.fx.snapshot).code)

    def test_10_native_hwnd_closed_after_worker_before_draw_blocks(self):
        h=self.hand();b=h.collect(self.fx.snapshot)
        self.fx.backend.mapped.pop(101)
        r=h.deliver(b,roster=self.roster,ready_list=self.view)
        self.assertIn("PRE_DRAW_STALE_NATIVE_HWND_PID",r.code)
        self.assertEqual(self.view.names,())

    def test_11_native_hwnd_reused_after_worker_before_draw_blocks(self):
        h=self.hand();b=h.collect(self.fx.snapshot)
        self.fx.backend.mapped[100]=9999
        r=h.deliver(b,roster=self.roster,ready_list=self.view)
        self.assertIn("PRE_DRAW_STALE_NATIVE_HWND_PID",r.code)
        self.assertEqual(self.view.names,())

    def test_12_start_cache_revision_change_before_draw_blocks(self):
        h=self.hand();b=h.collect(self.fx.snapshot)
        self.fx.producer.value=snap(2,*self.fx.snapshot.windows)
        r=h.deliver(b,roster=self.roster,ready_list=self.view)
        self.assertIn("PRE_DRAW_STALE_START_REVISION_OR_PAIR_SET",r.code)
        self.assertEqual(self.roster.ready_names(),())

    def test_13_start_cache_changed_pid_before_draw_blocks(self):
        h=self.hand();b=h.collect(self.fx.snapshot)
        self.fx.backend.mapped[101]=7777
        self.fx.producer.value=snap(2,win(100,1000),win(101,7777))
        self.assertEqual(h.deliver(b,roster=self.roster,ready_list=self.view).displayed_ready_names,())

    def test_14_neighbor_window_replaced_same_revision_blocks(self):
        h=self.hand();b=h.collect(self.fx.snapshot)
        self.fx.backend.mapped[102]=1002
        self.fx.producer.value=snap(1,win(100,1000),win(102,1002))
        r=h.deliver(b,roster=self.roster,ready_list=self.view)
        self.assertTrue(r.code.startswith("BLOCKED_PRE_DRAW_STALE_"))

    def test_15_window_closed_during_external_role_read_blocks_worker(self):
        def reader(hwnd):
            if hwnd==101:self.fx.backend.mapped.pop(100)
            return self.data[hwnd]
        b=self.hand(reader).collect(self.fx.snapshot)
        self.assertTrue(b.code.startswith("BLOCKED_AFTER_ROLE_READ_") or
                        b.roster_result is None)
        self.assertIsNone(b.roster_result)

    def test_16_worker_does_not_mutate_tk_view_before_deliver(self):
        b=self.hand().collect(self.fx.snapshot)
        self.assertEqual(self.view.names,())
        self.assertEqual(self.view.labels,[])
        self.assertEqual(b.code,"EXTERNAL_ROLE_ROSTER_PREPARED_NO_GAME")

    def test_17_duplicate_role_names_not_offered(self):
        self.data[101]={"RoleName":"Đội Trưởng"}
        self.assertEqual(self.do().displayed_ready_names,())

    def test_18_fail_closing_existing_ready_names_removes_old_labels(self):
        h=self.hand()
        self.assertEqual(self.do(h).displayed_ready_names,("Đội Trưởng","Hòa✨"))
        existing=tuple(self.view.labels)
        b=h.collect(self.fx.snapshot)
        self.fx.backend.mapped.pop(101)
        r=h.deliver(b,roster=self.roster,ready_list=self.view)
        self.assertTrue(r.code.startswith("BLOCKED_"))
        self.assertEqual(self.view.labels,[])
        self.assertEqual(self.view.names,())
        self.assertTrue(all(x.destroyed for x in existing))

    def test_19_old_batch_after_second_generation_success_cannot_publish(self):
        h=self.hand();old=h.collect(self.fx.snapshot)
        self.fx.producer.value=snap(2,*self.fx.snapshot.windows)
        latest=h.collect(self.fx.producer.value)
        self.assertEqual(h.deliver(latest,roster=self.roster,ready_list=self.view).displayed_ready_names,
                         ("Đội Trưởng","Hòa✨"))
        self.assertFalse(h.deliver(old,roster=self.roster,ready_list=self.view).displayed_ready_names)

    def test_20_drawing_time_native_death_clears_rows(self):
        h=self.hand();b=h.collect(self.fx.snapshot)
        class DeathOnLabel(FakeLabel):
            def __init__(nested,parent,*,text):
                super().__init__(parent,text=text)
                self.fx.backend.mapped.pop(101,None)
        with patch("party_ready_list.ttk.Label",DeathOnLabel):
            r=h.deliver(b,roster=self.roster,ready_list=self.view)
        self.assertIn("DURING_DRAW_STALE_NATIVE_HWND_PID",r.code)
        self.assertEqual(self.view.names,())

    def test_21_native_exception_after_worker_blocks_publish(self):
        h=self.hand();b=h.collect(self.fx.snapshot)
        self.fx.backend.read_hook=lambda *_:(_ for _ in ()).throw(OSError("failed"))
        r=h.deliver(b,roster=self.roster,ready_list=self.view)
        self.assertEqual(r.displayed_ready_names,())
        self.assertIn("NATIVE_OR_START_RECHECK_ERROR",r.code)

    def test_22_start_cache_exception_after_worker_blocks(self):
        h=self.hand();b=h.collect(self.fx.snapshot)
        self.fx.producer.read_snapshot=lambda:(_ for _ in ()).throw(OSError("error"))
        r=h.deliver(b,roster=self.roster,ready_list=self.view)
        self.assertTrue(r.code.startswith("BLOCKED_PRE_DRAW_"))
        self.assertEqual(r.displayed_ready_names,())

    def test_23_reject_forged_member_pair_data(self):
        h=self.hand();b=h.collect(self.fx.snapshot)
        fake=replace(b.roster_result,members=(
            PartyMember(100,1000,"Cũ"),
            PartyMember(101,9999,"Sai"),
        ))
        bad=replace(b,roster_result=fake)
        r=h.deliver(bad,roster=self.roster,ready_list=self.view)
        self.assertIn("PREPARED_PAIRS_INCONSISTENT",r.code)

    def test_24_reject_forged_revision(self):
        h=self.hand();b=h.collect(self.fx.snapshot)
        altered=replace(b,revision=77)
        self.assertIn("PREPARED_PAIRS_INCONSISTENT",
                      h.deliver(altered,roster=self.roster,ready_list=self.view).code)

    def test_25_no_valid_batch_clears_preexisting_labels(self):
        self.do()
        h=self.hand()
        r=h.deliver(None,roster=self.roster,ready_list=self.view)
        self.assertEqual(r.code,"BLOCKED_NO_VALID_PREPARED_ROLE_READ")
        self.assertEqual(self.view.names,())

    def test_26_invalid_selected_rejected_without_config_mutation(self):
        h=self.hand();b=h.collect(self.fx.snapshot)
        with self.assertRaises(TypeError):
            h.deliver(b,roster=self.roster,ready_list=self.view,selected=["Hòa✨"])

    def test_27_reject_unknown_roster_or_ui_type(self):
        h=self.hand();b=h.collect(self.fx.snapshot)
        with self.assertRaises(TypeError):
            h.deliver(b,roster=[],ready_list=self.view)
        with self.assertRaises(TypeError):
            h.deliver(b,roster=self.roster,ready_list=[])

    def test_28_immutable_reports_and_no_action_bind(self):
        h=self.hand();b=h.collect(self.fx.snapshot)
        with self.assertRaises(FrozenInstanceError):
            b.code="fake"
        r=h.deliver(b,roster=self.roster,ready_list=self.view)
        with self.assertRaises(FrozenInstanceError):
            r.action_authorized=True
        self.assertFalse(r.action_authorized)
        self.assertFalse(r.game_role_verified)
        self.assertFalse(hasattr(r,"role_id"))
        self.assertFalse(hasattr(r,"team_id"))

    def test_29_source_does_not_import_game_reader_or_write_game(self):
        code=(ROOT/"src/party_ready_handoff.py").read_text("utf-8")
        for token in ("ReadProcessMemory(", "WriteProcessMemory(",
                      "SendMessage(", "PostMessage(", "create_team(",
                      "leave_team(", "200051", "200057", "get_character_info("):
            self.assertNotIn(token,code)

    def test_30_reject_missing_or_non_S100_source(self):
        with self.assertRaises(TypeError):
            PartyExternalReadyHandoff(None)
        with self.assertRaises(TypeError):
            PartyExternalReadyHandoff(self.roster)

if __name__=="__main__":
    unittest.main()
