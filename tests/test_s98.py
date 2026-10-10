"""S98 deterministic read epoch safety, inherits actual S94-S97 diagnostics."""
from __future__ import annotations
from dataclasses import FrozenInstanceError
from pathlib import Path
import sys, threading, unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"tests"))
from test_s94 import Fixture,snap
from party_team_wait import PartyTeamReadOnlyWait
from party_join_report import PartyJoinTwoRoundDiagnostic
from party_member_snapshot import PartyJoinDetailedDiagnostic
from party_member_epoch import PartyJoinReadEpochDiagnostic


class S98Epoch(unittest.TestCase):
    def setUp(self):
        self.fx=Fixture()
        self.fx.teams[100]=531
        self.fx.teams[101]=0
        self.diag=self.make(self.fx.pre())

    def make(self,pre):
        return PartyJoinReadEpochDiagnostic(
            PartyJoinDetailedDiagnostic(
                PartyJoinTwoRoundDiagnostic(
                    PartyTeamReadOnlyWait(pre))))

    def inspect(self,diag=None,names=("Minh","Hoa"),leader="Minh",cancel=None):
        return (diag or self.diag).inspect(
            names,leader_name=leader,timeout_seconds=0,poll_seconds=.01,
            cancel=cancel)

    def member(self,r,name="Hoa"):
        return next(x for x in r.changes if x.name==name)

    def test_01_unchanged_has_stable_epoch_two_windows(self):
        r=self.inspect()
        self.assertEqual(r.code,"DIAGNOSTIC_SEQUENTIAL_STABLE_SAME_GENERATION_NO_GAME_ACTION")
        self.assertEqual(r.compared_native_windows,2)
        self.assertEqual((r.start_revision,r.end_revision),(1,1))
        self.assertTrue(all(x.class_code=="OBSERVED_STABLE" for x in r.changes))
        self.assertFalse(r.atomic)
        self.assertEqual(r.invites_sent,0)

    def test_02_team_member_joined_later_with_same_pid(self):
        count=[0]
        def reader(hwnd):
            if hwnd==101:
                count[0]+=1
                return 0 if count[0]<=3 else 531
            return 531
        r=self.inspect(self.make(self.fx.pre(read_team_id=reader)))
        self.assertEqual(self.member(r).class_code,"OBSERVED_TEAM_ID_CHANGED")
        self.assertEqual(self.member(r).from_team_id,0)
        self.assertEqual(self.member(r).to_team_id,531)
        self.assertEqual(r.start_revision,r.end_revision)

    def test_03_real_teamid_switch_inside_stable_epoch(self):
        count=[0]
        def reader(hwnd):
            if hwnd==101:
                count[0]+=1
                return 531 if count[0]<=2 else 545
            return 531
        r=self.inspect(self.make(self.fx.pre(read_team_id=reader)))
        self.assertEqual(r.detailed.base.code,"DIAGNOSTIC_ALL_JOINED_FIRST_OBSERVATION_NO_GAME_ACTION")
        self.assertEqual(r.detailed.post_snapshot.members[1].state,"JOINED_LEADER_TEAM")
        self.assertEqual(self.member(r).to_state,"DIFFERENT_REAL_TEAM")

    def test_04_readable_becomes_none_not_outside(self):
        count=[0]
        def reader(hwnd):
            if hwnd==101:
                count[0]+=1
                return 0 if count[0]<=3 else None
            return 531
        r=self.inspect(self.make(self.fx.pre(read_team_id=reader)))
        self.assertEqual(self.member(r).class_code,"OBSERVED_READABILITY_CHANGED")
        self.assertIsNone(self.member(r).to_team_id)

    def test_05_none_recovers_to_known_outside(self):
        count=[0]
        def reader(hwnd):
            if hwnd==101:
                count[0]+=1
                return None if count[0]<=3 else 0xFFFFFFFF
            return 531
        r=self.inspect(self.make(self.fx.pre(read_team_id=reader)))
        self.assertEqual(self.member(r).class_code,"OBSERVED_READABILITY_CHANGED")
        self.assertEqual(self.member(r).to_state,"KNOWN_OUTSIDE")

    def test_06_outside_sentinels_never_real_leader(self):
        self.fx.teams[100]=0
        self.fx.teams[101]=0xFFFFFFFF
        r=self.inspect()
        self.assertEqual(r.detailed.post_snapshot.leader_team_id,None)
        self.assertEqual(self.member(r).to_state,"KNOWN_OUTSIDE")
        self.assertNotIn("ALL_JOINED",r.detailed.base.code)

    def test_07_new_native_pid_at_second_observation_failclosed(self):
        count=[0]
        def reader(hwnd):
            if hwnd==101:
                count[0]+=1
                if count[0]==4:self.fx.backend.mapped[101]=9999
            return self.fx.teams[hwnd]
        r=self.inspect(self.make(self.fx.pre(read_team_id=reader)))
        self.assertIn("BLOCKED_",r.code)
        self.assertEqual(r.changes,())
        self.assertFalse(r.atomic)

    def test_08_second_observation_Start_revision_changes_blocks(self):
        count=[0]
        def reader(hwnd):
            if hwnd==101:
                count[0]+=1
                if count[0]==4:
                    self.fx.producer.value=snap(2,*self.fx.snapshot.windows)
            return self.fx.teams[hwnd]
        r=self.inspect(self.make(self.fx.pre(read_team_id=reader)))
        self.assertTrue(r.code.startswith("BLOCKED_"),r)
        self.assertEqual(r.changes,())

    def test_09_revoked_permission_during_second_read_blocks(self):
        count=[0]
        def reader(hwnd):
            if hwnd==101:
                count[0]+=1
                if count[0]==4:self.fx.permission=False
            return self.fx.teams[hwnd]
        r=self.inspect(self.make(self.fx.pre(read_team_id=reader)))
        self.assertTrue(r.code.startswith("BLOCKED_"))
        self.assertEqual(r.changes,())

    def test_10_missing_gate_never_yields_epoch_snapshot(self):
        r=self.inspect(self.make(self.fx.pre(allowed=None)))
        self.assertIn("SIGNED_INFO_GATE_UNAVAILABLE",r.code)
        self.assertIsNone(r.second_post_snapshot)

    def test_11_missing_live_role_reader_blocks(self):
        r=self.inspect(self.make(self.fx.pre(read_own_ids=None)))
        self.assertIn("LIVE_IDENTITY_PROVIDER_UNAVAILABLE",r.code)
        self.assertEqual(r.compared_native_windows,0)

    def test_12_no_start_windows_cannot_compare(self):
        self.fx.producer.value=snap(1)
        r=self.inspect()
        self.assertTrue(r.code.startswith("BLOCKED_"))

    def test_13_cancel_before_start_has_no_second(self):
        c=threading.Event();c.set()
        r=self.inspect(cancel=c)
        self.assertEqual(r.code,"CANCELLED")
        self.assertIsNone(r.second_post_snapshot)

    def test_14_bad_member_selection_remains_blocked(self):
        r=self.inspect(names=("Minh","Minh"))
        self.assertEqual(r.second_post_snapshot,None)
        self.assertEqual(r.changes,())

    def test_15_offline_name_remains_unresolved_not_game_parity(self):
        r=self.inspect(names=("Minh","Offline"))
        self.assertEqual(r.detailed.post_snapshot.members[1].state,"OFFLINE_NAME")
        self.assertEqual(r.second_post_snapshot.members[1].state,"OFFLINE_NAME")
        self.assertEqual(self.member(r,"Offline").class_code,"OBSERVED_STABLE")

    def test_16_original_two_round_history_preserved(self):
        r=self.inspect()
        self.assertEqual(len(r.detailed.base.rounds),2)
        self.assertEqual(r.detailed.base.rounds[0].missing_names,("Hoa",))
        self.assertEqual(r.detailed.base.rounds[1].missing_names,("Hoa",))
        self.assertEqual(r.detailed.base.potential_resend_names,("Hoa",))
        self.assertEqual(r.detailed.base.invites_sent,0)

    def test_17_all_joined_fast_path_preserves_one_round(self):
        self.fx.teams[101]=531
        r=self.inspect()
        self.assertEqual(len(r.detailed.base.rounds),1)
        self.assertEqual(r.code,"DIAGNOSTIC_SEQUENTIAL_STABLE_SAME_GENERATION_NO_GAME_ACTION")

    def test_18_immutable_records_and_non_atomic_flag(self):
        r=self.inspect()
        with self.assertRaises(FrozenInstanceError):
            r.atomic=True
        with self.assertRaises(FrozenInstanceError):
            r.changes[0].from_team_id=123

    def test_19_zero_sendable_actions_in_source(self):
        t=(ROOT/"src/party_member_epoch.py").read_text("utf-8")
        for x in ("ReadProcessMemory(", "WriteProcessMemory(", "PostMessage(",
                  "SendMessage(", "create_team(", "leave_team(",
                  "memory_items.invite(", "0x6F4030"):
            self.assertNotIn(x,t)

    def test_20_unicode_member_order_and_native_generation(self):
        self.fx.records=[(1000,1,"ĐộiTrưởng",10),(1001,2,"Hoa✨",10)]
        r=self.inspect(names=("ĐộiTrưởng","Hoa✨"),leader="ĐộiTrưởng")
        self.assertEqual([x.name for x in r.changes],["ĐộiTrưởng","Hoa✨"])
        self.assertEqual(r.compared_native_windows,2)

if __name__=="__main__":
    unittest.main()
