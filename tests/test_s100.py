"""S100: externally supplied G03 RoleName, HWND/PID and Start revision safety."""
from __future__ import annotations
from dataclasses import FrozenInstanceError
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"tests"))
from test_s94 import Fixture,snap,win
from auto_role_provenance import RoleReading
from party_roster import PartyRoster,prepare_roster
from party_rolename_source import PartyRoleNameExternalSource


class S100RoleName(unittest.TestCase):
    def setUp(self):
        self.fx=Fixture()
        self.calls=[]
        self.data={100:{"RoleName":"<b>Đội</b> Trưởng"},
                   101:{"RoleName":"Hòa✨"}}

    def reader(self,hwnd):
        self.calls.append(hwnd)
        return self.data[hwnd]

    def source(self,**overrides):
        args=dict(start_producer=self.fx.producer,
                  backend=self.fx.backend,get_character_info=self.reader)
        args.update(overrides)
        return PartyRoleNameExternalSource(**args)

    def test_01_tag_removal_matches_original_G03(self):
        r=self.source().inspect(100,1000)
        self.assertEqual(r.code,"EXTERNAL_DISPLAY_NAME_OBSERVED_NOT_GAME")
        self.assertEqual(r.normalized_name,"Đội Trưởng")
        self.assertEqual(r.reading,RoleReading(100,1000,"<b>Đội</b> Trưởng"))
        self.assertEqual(r.revision,1)

    def test_02_original_Window_fallback_only_prefix_known(self):
        r=self.source(get_character_info=None).inspect(100,1000)
        self.assertEqual(r.fallback_prefix,"Window ")
        self.assertFalse(r.fallback_suffix_known)
        self.assertIsNone(r.reading)
        self.assertIsNone(r.normalized_name)

    def test_03_missing_actual_reader_blocks_before_probing_game(self):
        r=self.source(get_character_info=None).inspect(100,1000)
        self.assertEqual(r.code,"ORIGINAL_CHARACTER_READER_UNAVAILABLE")
        self.assertEqual(self.calls,[])

    def test_04_uses_existing_S90_roster_exactly(self):
        source=self.source()
        r=prepare_roster(self.fx.snapshot,source.read_role)
        self.assertEqual(r.code,"ROLE_NAMES_READ")
        roster=PartyRoster()
        self.assertTrue(roster.apply(r,self.fx.snapshot))
        self.assertEqual(roster.ready_names(),("Đội Trưởng","Hòa✨"))
        self.assertEqual(source.inspect(101,1001).normalized_name,"Hòa✨")

    def test_05_missing_reader_never_offers_ready_names(self):
        source=self.source(get_character_info=None)
        r=prepare_roster(self.fx.snapshot,source.read_role)
        self.assertEqual(r.code,"ROLE_READ_PARTIAL")
        roster=PartyRoster()
        self.assertTrue(roster.apply(r,self.fx.snapshot))
        self.assertEqual(roster.ready_names(),())

    def test_06_wrong_name_key_is_not_fallback_to_title(self):
        self.data[100]={"Name":"wrong"}
        r=self.source().inspect(100,1000)
        self.assertEqual(r.code,"ROLENAME_UNAVAILABLE")
        self.assertIsNone(r.reading)

    def test_07_non_mapping_reader_result_rejected(self):
        self.data[100]="character"
        self.assertEqual(self.source().inspect(100,1000).code,
                         "INVALID_CHARACTER_INFO")

    def test_08_None_name_rejected(self):
        self.data[100]={"RoleName":None}
        self.assertEqual(self.source().inspect(100,1000).code,
                         "ROLENAME_UNAVAILABLE")

    def test_09_boolean_role_value_rejected(self):
        self.data[100]={"RoleName":True}
        self.assertEqual(self.source().inspect(100,1000).code,
                         "ROLENAME_UNAVAILABLE")

    def test_10_tags_only_rejected_and_not_in_roster(self):
        self.data[100]={"RoleName":"<b></b> "}
        r=self.source().inspect(100,1000)
        self.assertEqual(r.code,"ROLENAME_EMPTY_AFTER_TAG_REMOVAL")
        self.assertIsNone(r.reading)
        self.assertEqual(prepare_roster(self.fx.snapshot,self.source().read_role).code,
                         "ROLE_READ_PARTIAL")

    def test_11_whitespace_name_rejected(self):
        self.data[100]={"RoleName":"  \t\n"}
        self.assertEqual(self.source().inspect(100,1000).code,
                         "ROLENAME_EMPTY_AFTER_TAG_REMOVAL")

    def test_12_external_reader_error_fails_closed(self):
        def fail(_hwnd):raise OSError("reader unavailable")
        self.assertEqual(self.source(get_character_info=fail).inspect(100,1000).code,
                         "EXTERNAL_CHARACTER_READER_ERROR")

    def test_13_noncallable_source_fails(self):
        self.assertEqual(self.source(get_character_info=5).inspect(100,1000).code,
                         "ORIGINAL_CHARACTER_READER_UNAVAILABLE")

    def test_14_invalid_hwnd_or_pid_never_calls_reader(self):
        for pair in ((0,1000),(100,0),(-1,1000),(100,-1),
                     ("100",1000),(100,True),(False,1000),(100,1000.)):
            with self.subTest(pair=pair):
                self.assertEqual(self.source().inspect(*pair).code,
                                 "INVALID_HWND_PID")
        self.assertEqual(self.calls,[])

    def test_15_hwnd_pid_pair_missing_from_start_is_not_action_target(self):
        r=self.source().inspect(100,9999)
        self.assertEqual(r.code,"HWND_PID_NOT_IN_START_CACHE")
        self.assertEqual(self.calls,[])

    def test_16_closed_native_window_blocks_before_reader(self):
        self.fx.backend.mapped.pop(100)
        r=self.source().inspect(100,1000)
        self.assertEqual(r.code,"STALE_OR_REUSED_NATIVE_HWND_PID")
        self.assertEqual(self.calls,[])

    def test_17_native_window_reused_for_other_pid_blocks(self):
        self.fx.backend.mapped[100]=2000
        self.assertEqual(self.source().inspect(100,1000).code,
                         "STALE_OR_REUSED_NATIVE_HWND_PID")

    def test_18_reused_pid_during_actual_callback_blocks_after_read(self):
        def replace(_hwnd):
            self.fx.backend.mapped[100]=3333
            return {"RoleName":"Fake"}
        r=self.source(get_character_info=replace).inspect(100,1000)
        self.assertEqual(r.code,"POST_READ_STALE_OR_REUSED_NATIVE_HWND_PID")
        self.assertIsNone(r.reading)

    def test_19_physically_closed_during_callback_fails(self):
        def close(_hwnd):
            self.fx.backend.mapped.pop(100)
            return {"RoleName":"Old"}
        r=self.source(get_character_info=close).inspect(100,1000)
        self.assertEqual(r.code,"POST_READ_STALE_OR_REUSED_NATIVE_HWND_PID")

    def test_20_changed_start_revision_while_reading_blocks(self):
        def change(_hwnd):
            self.fx.producer.value=snap(2,*self.fx.snapshot.windows)
            return {"RoleName":"Stale"}
        r=self.source(get_character_info=change).inspect(100,1000)
        self.assertEqual(r.code,"STALE_START_REVISION_OR_GENERATION")
        self.assertIsNone(r.reading)

    def test_21_changed_other_hwnd_in_cache_during_read_blocks(self):
        def change(_hwnd):
            self.fx.backend.mapped[102]=1002
            self.fx.producer.value=snap(1,win(100,1000),win(102,1002))
            return {"RoleName":"Stale"}
        self.assertEqual(self.source(get_character_info=change).inspect(100,1000).code,
                         "STALE_START_REVISION_OR_GENERATION")

    def test_22_start_cache_invalid_blocks(self):
        self.fx.producer.value=snap(1,win(100,1000),valid=False)
        self.assertEqual(self.source().inspect(100,1000).code,
                         "INVALID_START_CACHE")
        self.assertEqual(self.calls,[])

    def test_23_duplicate_pid_in_start_blocks(self):
        self.fx.producer.value=snap(1,win(100,1000),win(101,1000))
        self.assertEqual(self.source().inspect(100,1000).code,
                         "DUPLICATE_PID_IN_START_CACHE")

    def test_24_native_api_exception_blocks_before_read(self):
        self.fx.backend.read_hook=lambda calls,backend: (_ for _ in ()).throw(
            OSError("native failure"))
        self.assertEqual(self.source().inspect(100,1000).code,
                         "NATIVE_HWND_CHECK_FAILED")
        self.assertEqual(self.calls,[])

    def test_25_start_snapshot_reader_exception_blocks(self):
        class Broken:
            def read_snapshot(self):raise OSError("snapshot")
        self.assertEqual(self.source(start_producer=Broken()).inspect(100,1000).code,
                         "START_CACHE_READ_ERROR")

    def test_26_identity_record_only_exposes_display_no_roleid(self):
        r=self.source().inspect(100,1000)
        self.assertFalse(r.action_authorized)
        self.assertEqual(r.source_provenance,"EXTERNAL_UNVERIFIED_NOT_GAME")
        self.assertFalse(hasattr(r,"role_id"))
        self.assertFalse(hasattr(r,"team_id"))
        self.assertFalse(hasattr(r,"sendable_target"))

    def test_27_immutable_result_cannot_be_modified(self):
        r=self.source().inspect(100,1000)
        with self.assertRaises(FrozenInstanceError):
            r.normalized_name="Fake"

    def test_28_S90_keeps_double_names_out_of_available(self):
        self.data[100]={"RoleName":"Same"}
        self.data[101]={"RoleName":"Same"}
        r=prepare_roster(self.fx.snapshot,self.source().read_role)
        roster=PartyRoster();self.assertTrue(roster.apply(r,self.fx.snapshot))
        self.assertEqual(roster.ready_names(),())

    def test_29_S90_final_revision_change_fences_stale_worker(self):
        r=prepare_roster(self.fx.snapshot,self.source().read_role)
        fresh=snap(2,*self.fx.snapshot.windows)
        roster=PartyRoster()
        self.assertFalse(roster.apply(r,fresh))
        self.assertEqual(roster.ready_names(),())

    def test_30_no_game_execution_or_fake_authorization_in_source(self):
        text=(ROOT/"src/party_rolename_source.py").read_text("utf-8")
        for token in ("ReadProcessMemory(", "WriteProcessMemory(", "PostMessage(",
                      "SendMessage(", "memory_items.invite(", "create_team(",
                      "leave_team(", "ctypes.windll", "0x355B208"):
            self.assertNotIn(token,text)
        self.assertNotIn("from utils import get_character_info",text)

if __name__=="__main__":
    unittest.main()
