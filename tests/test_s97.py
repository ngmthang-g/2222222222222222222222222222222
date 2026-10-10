"""S97 G03/G10 member-level POST-S96 diagnostic, test-only backing."""
from __future__ import annotations
from dataclasses import FrozenInstanceError
from pathlib import Path
import sys
import threading
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"tests"))
from test_s94 import Fixture,win,snap
from party_join_report import PartyJoinTwoRoundDiagnostic
from party_team_wait import PartyTeamReadOnlyWait
from party_member_snapshot import (
    PartyMemberReadOnlySnapshot,PartyJoinDetailedDiagnostic,
)


class S97MemberSnapshots(unittest.TestCase):
    def setUp(self):
        self.fx=Fixture()
        self.fx.teams[100]=531
        self.fx.teams[101]=0
        self.s97=PartyJoinDetailedDiagnostic(
            PartyJoinTwoRoundDiagnostic(PartyTeamReadOnlyWait(self.fx.pre())))

    def read(self,names=("Minh","Hoa"),leader="Minh",cancel=None):
        return self.s97.inspect(names,leader_name=leader,
                                timeout_seconds=0,poll_seconds=.01,cancel=cancel)

    def statuses(self,report):
        return {m.name:m.state for m in report.post_snapshot.members}

    def test_01_reuses_actual_s96_with_same_round_provenance(self):
        r=self.read()
        self.assertEqual(len(r.base.rounds),2)
        self.assertEqual(r.base.rounds[0].missing_names,("Hoa",))
        self.assertEqual(r.base.rounds[1].missing_names,("Hoa",))
        self.assertEqual(r.base.potential_resend_names,("Hoa",))
        self.assertEqual(r.invites_sent,0)
        self.assertEqual(r.base.invites_sent,0)
        self.assertEqual(r.post_snapshot.phase,"AFTER_S96_OBSERVATIONS")
        self.assertEqual(self.statuses(r),{"Minh":"LEADER_REAL_TEAM","Hoa":"KNOWN_OUTSIDE"})

    def test_02_all_joined_one_s96_round_and_post_snapshot(self):
        self.fx.teams[101]=531
        r=self.read()
        self.assertEqual(len(r.base.rounds),1)
        self.assertEqual(r.post_snapshot.code,"DIAGNOSTIC_ALL_JOINED_POST_S96_NO_GAME_ACTION")
        self.assertEqual(self.statuses(r)["Hoa"],"JOINED_LEADER_TEAM")

    def test_03_different_real_team_explicit(self):
        self.fx.teams[101]=700
        r=self.read()
        self.assertEqual(self.statuses(r)["Hoa"],"DIFFERENT_REAL_TEAM")
        self.assertEqual(r.post_snapshot.members[1].team_id,700)

    def test_04_both_outside_sentinels_are_never_same_team(self):
        self.fx.teams[100]=0
        self.fx.teams[101]=0xFFFFFFFF
        r=self.read()
        self.assertNotIn("ALL_JOINED",r.base.code)
        self.assertIsNone(r.post_snapshot.leader_team_id)
        self.assertEqual(self.statuses(r),{"Minh":"KNOWN_OUTSIDE","Hoa":"KNOWN_OUTSIDE"})

    def test_05_unknown_teamid_not_outside(self):
        self.fx.teams[101]=None
        r=self.read()
        self.assertEqual(self.statuses(r)["Hoa"],"UNREADABLE_TEAMID")
        self.assertIsNone(r.post_snapshot.members[1].team_id)

    def test_06_team_reader_exception_distinct_from_none(self):
        def reader(hwnd):
            if hwnd==101:raise OSError("no read")
            return self.fx.teams[hwnd]
        pre=self.fx.pre(read_team_id=reader)
        s=PartyMemberReadOnlySnapshot(pre).inspect(("Minh","Hoa"),leader_name="Minh")
        self.assertEqual({r.name:r.state for r in s.members}["Hoa"],"TEAMID_READ_ERROR")

    def test_07_offline_member_name_not_in_live_records(self):
        r=self.read(("Minh","Offline"))
        self.assertEqual(self.statuses(r)["Offline"],"OFFLINE_NAME")
        self.assertEqual(r.post_snapshot.members[1].source_code,"OFFLINE")

    def test_08_name_in_live_records_but_pid_not_in_Start(self):
        self.fx.records[1]=(9999,43,"Hoa",11)
        r=self.read()
        self.assertEqual(self.statuses(r)["Hoa"],"PID_NOT_IN_START_CACHE")

    def test_09_tampered_generation_blocks_snapshot_not_joined(self):
        class Mutable:
            def __init__(self,p):self.p=p
            def read_snapshot(self):
                self.p.counter+=1
                return snap(self.p.counter,*self.p.windows)
        # S97-alone controlled cache mutation; S94 must fail closed.
        self.fx.producer.value=snap(1,*self.fx.snapshot.windows)
        self.fx.backend.mapped[101]=9999
        r=PartyMemberReadOnlySnapshot(self.fx.pre()).inspect(("Minh","Hoa"),leader_name="Minh")
        self.assertEqual(r.code,"BLOCKED_STALE_NATIVE_HWND_PID")
        self.assertEqual(r.members,())

    def test_10_permission_revoked_blocks_member_rows(self):
        self.fx.permission=False
        r=PartyMemberReadOnlySnapshot(self.fx.pre()).inspect(("Minh","Hoa"),leader_name="Minh")
        self.assertEqual(r.code,"BLOCKED_PERMISSION_NOT_VERIFIED")
        self.assertEqual(r.members,())

    def test_11_missing_real_signed_gate_not_assumed(self):
        pre=self.fx.pre(allowed=None)
        r=PartyMemberReadOnlySnapshot(pre).inspect(("Minh","Hoa"),leader_name="Minh")
        self.assertEqual(r.code,"BLOCKED_SIGNED_INFO_GATE_UNAVAILABLE")

    def test_12_S96_block_does_not_produce_later_snapshot(self):
        pre=self.fx.pre(allowed=None)
        d=PartyJoinDetailedDiagnostic(PartyJoinTwoRoundDiagnostic(PartyTeamReadOnlyWait(pre)))
        r=d.inspect(("Minh","Hoa"),leader_name="Minh",timeout_seconds=0,poll_seconds=.01)
        self.assertTrue(r.base.code.startswith("BLOCKED_"))
        self.assertIsNone(r.post_snapshot)

    def test_13_cancel_and_invalid_selection_do_not_probe_later(self):
        cancel=threading.Event();cancel.set()
        self.assertIsNone(self.read(cancel=cancel).post_snapshot)
        self.assertIsNone(self.read(("Minh","Minh")).post_snapshot)

    def test_14_reused_pid_after_observations_blocks_post_snapshot(self):
        count=[0]
        def team(hwnd):
            if hwnd==101:
                count[0]+=1
                if count[0]==3:self.fx.backend.mapped[101]=9999
            return self.fx.teams[hwnd]
        pre=self.fx.pre(read_team_id=team)
        d=PartyJoinDetailedDiagnostic(PartyJoinTwoRoundDiagnostic(PartyTeamReadOnlyWait(pre)))
        r=d.inspect(("Minh","Hoa"),leader_name="Minh",timeout_seconds=0,poll_seconds=.01)
        self.assertEqual(len(r.base.rounds),2)
        self.assertEqual(r.post_snapshot.code,"BLOCKED_STALE_NATIVE_HWND_PID")
        self.assertFalse(r.post_snapshot.members)

    def test_15_two_round_join_provenance_does_not_override_later_leave(self):
        count=[0]
        def team(hwnd):
            if hwnd==101:
                count[0]+=1
                return 0 if count[0] in (1,3,4) else 531
            return 531
        pre=self.fx.pre(read_team_id=team)
        d=PartyJoinDetailedDiagnostic(PartyJoinTwoRoundDiagnostic(PartyTeamReadOnlyWait(pre)))
        r=d.inspect(("Minh","Hoa"),leader_name="Minh",timeout_seconds=0,poll_seconds=.01)
        self.assertEqual(r.base.code,"DIAGNOSTIC_ALL_JOINED_SECOND_OBSERVATION_NO_GAME_ACTION")
        self.assertEqual(r.post_snapshot.members[1].state,"KNOWN_OUTSIDE")

    def test_16_immutable_no_packet_actions_or_roleid(self):
        r=self.read()
        with self.assertRaises(FrozenInstanceError):
            r.invites_sent=2
        source=(ROOT/"src/party_member_snapshot.py").read_text("utf-8")
        for s in ("ReadProcessMemory(", "WriteProcessMemory(", "PostMessage(",
                  "SendMessage(", "memory_items.invite(", "0x6F4030",
                  "create_team(", "leave_team("):
            self.assertNotIn(s,source)

    def test_17_unicode_names_are_not_rewritten(self):
        self.fx.records=[(1000,0,"LãnhĐạo",10),(1001,430,"Hòa",11)]
        r=self.read(("LãnhĐạo","Hòa"),leader="LãnhĐạo")
        self.assertEqual([x.name for x in r.post_snapshot.members],["LãnhĐạo","Hòa"])

    def test_18_bad_selection_returns_no_rows(self):
        for names,leader in ((("Minh",),"Minh"),(("Minh"," Minh"),"Minh"),
                             (("Minh","Hoa"),"Missing")):
            with self.subTest(names=names):
                self.assertTrue(PartyMemberReadOnlySnapshot(self.fx.pre())
                    .inspect(names,leader_name=leader).code.startswith("BLOCKED_"))

    def test_19_delayed_revocation_returns_no_member_success(self):
        counter=[0]
        def permission():
            counter[0]+=1
            return counter[0] < 4
        r=PartyMemberReadOnlySnapshot(self.fx.pre(allowed=permission)).inspect(
            ("Minh","Hoa"),leader_name="Minh")
        self.assertTrue(r.code.startswith("BLOCKED_"))
        self.assertEqual(r.members,())

    def test_20_unmapped_name_does_not_alias_a_game_target(self):
        self.fx.records[1]=(9999,44,"Hoa",11)
        r=PartyMemberReadOnlySnapshot(self.fx.pre()).inspect(
            ("Minh","Hoa"),leader_name="Minh")
        self.assertEqual(r.members[1].state,"PID_NOT_IN_START_CACHE")
        self.assertFalse(hasattr(r.members[1],"role_id"))

if __name__=="__main__":
    unittest.main()
