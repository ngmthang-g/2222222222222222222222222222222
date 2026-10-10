"""S96 G10 B3 two-round READ-ONLY missing-team report, never an invitation."""
from __future__ import annotations
from pathlib import Path
import sys
import threading
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"tests"))
from test_s94 import Fixture, win, snap
from party_team_identity import PartyTeamIdentityPreflight
from party_team_wait import PartyTeamReadOnlyWait
from party_join_report import PartyJoinTwoRoundDiagnostic


class S96TwoRoundTests(unittest.TestCase):
    def setUp(self):
        self.fx=Fixture()
        self.fx.teams[100]=567
        self.fx.teams[101]=0
        self.diag=PartyJoinTwoRoundDiagnostic(
            PartyTeamReadOnlyWait(self.fx.pre()))

    def inspect(self, names=("Minh","Hoa"),leader="Minh",
                timeout=0,poll=.01,cancel=None):
        return self.diag.inspect(
            names,leader_name=leader,timeout_seconds=timeout,
            poll_seconds=poll,cancel=cancel)

    def test_01_first_observation_all_joined_ends_without_second(self):
        self.fx.teams[101]=567
        r=self.inspect()
        self.assertEqual(r.code,"DIAGNOSTIC_ALL_JOINED_FIRST_OBSERVATION_NO_GAME_ACTION")
        self.assertEqual(len(r.rounds),1)
        self.assertEqual(r.rounds[0].round_number,1)
        self.assertEqual(r.potential_resend_names,())
        self.assertEqual(r.invites_sent,0)
        self.assertEqual(self.fx.reads,1)

    def test_02_missing_first_round_report_and_second_still_missing(self):
        r=self.inspect()
        self.assertEqual(r.code,"DIAGNOSTIC_STILL_MISSING_AFTER_TWO_OBSERVATIONS_NO_GAME_ACTION")
        self.assertEqual([x.round_number for x in r.rounds],[1,2])
        self.assertEqual(r.rounds[0].missing_names,("Hoa",))
        self.assertEqual(r.rounds[1].missing_names,("Hoa",))
        self.assertEqual(r.potential_resend_names,("Hoa",))
        self.assertEqual(r.invites_sent,0)

    def test_03_second_observation_catches_join_without_sending_invite(self):
        reads=[0]
        def callback(hwnd):
            if hwnd==101:
                reads[0]+=1
                if reads[0]>=2:
                    return 567
            return self.fx.teams[hwnd]
        self.diag=PartyJoinTwoRoundDiagnostic(
            PartyTeamReadOnlyWait(self.fx.pre(read_team_id=callback)))
        r=self.inspect()
        self.assertEqual(r.code,"DIAGNOSTIC_ALL_JOINED_SECOND_OBSERVATION_NO_GAME_ACTION")
        self.assertEqual(r.rounds[0].missing_names,("Hoa",))
        self.assertEqual(r.rounds[1].missing_names,())
        self.assertEqual(r.potential_resend_names,("Hoa",))
        self.assertEqual(r.invites_sent,0)

    def test_04_equal_no_team_sentinel_not_a_real_group(self):
        self.fx.teams[100]=0
        self.fx.teams[101]=0
        r=self.inspect()
        self.assertEqual(r.code,"DIAGNOSTIC_STILL_MISSING_AFTER_TWO_OBSERVATIONS_NO_GAME_ACTION")
        self.assertIsNone(r.rounds[0].leader_team_id)
        self.assertEqual(r.potential_resend_names,())

    def test_05_two_different_no_team_sentinels_not_joined(self):
        self.fx.teams[100]=0
        self.fx.teams[101]=0xFFFFFFFF
        self.assertNotIn("ALL_JOINED",self.inspect().code)

    def test_06_both_real_teamids_different_never_match(self):
        self.fx.teams[101]=568
        r=self.inspect()
        self.assertEqual(r.rounds[0].missing_names,("Hoa",))
        self.assertEqual(r.rounds[0].leader_team_id,567)

    def test_07_none_teamid_stays_not_confirmed(self):
        self.fx.teams[101]=None
        r=self.inspect()
        self.assertEqual(r.code,"DIAGNOSTIC_STILL_MISSING_AFTER_TWO_OBSERVATIONS_NO_GAME_ACTION")
        self.assertEqual(r.rounds[0].last_preflight_code,"TEAMID_UNKNOWN_NOT_OUTSIDE")
        self.assertEqual(r.potential_resend_names,())  # no complete, trusted leader observation

    def test_08_none_leader_never_produces_resend_candidate(self):
        self.fx.teams[100]=None
        r=self.inspect()
        self.assertEqual(r.potential_resend_names,())
        self.assertNotIn("ALL_JOINED",r.code)

    def test_09_absent_member_never_counted_as_joined(self):
        r=self.inspect(("Minh","Offline"),timeout=0)
        self.assertEqual(r.code,"DIAGNOSTIC_STILL_MISSING_AFTER_TWO_OBSERVATIONS_NO_GAME_ACTION")
        self.assertTrue(all("Offline" in x.missing_names for x in r.rounds))
        self.assertEqual(r.potential_resend_names,())

    def test_10_after_second_recheck_previously_joined_member_can_leave(self):
        third=win(102,1002)
        self.fx.snapshot=snap(1,*self.fx.snapshot.windows,third)
        self.fx.producer.value=self.fx.snapshot
        self.fx.backend.mapped[102]=1002
        self.fx.records.append((1002,800,"Binh",20))
        self.fx.teams[102]=567
        counts=[0]
        def cb(hwnd):
            if hwnd==102:
                counts[0]+=1
                if counts[0]>=2:return 0
            return self.fx.teams[hwnd]
        self.diag=PartyJoinTwoRoundDiagnostic(
            PartyTeamReadOnlyWait(self.fx.pre(read_team_id=cb)))
        r=self.inspect(("Minh","Hoa","Binh"))
        self.assertEqual(r.rounds[0].missing_names,("Hoa",))
        self.assertEqual(r.rounds[1].missing_names,("Hoa","Binh"))
        self.assertEqual(r.potential_resend_names,("Hoa",))
        self.assertEqual(r.invites_sent,0)

    def test_11_only_first_round_missing_names_are_candidates(self):
        third=win(102,1002)
        self.fx.snapshot=snap(1,*self.fx.snapshot.windows,third)
        self.fx.producer.value=self.fx.snapshot
        self.fx.backend.mapped[102]=1002
        self.fx.records.append((1002,800,"Binh",20))
        self.fx.teams[102]=567
        r=self.inspect(("Minh","Hoa","Binh"))
        self.assertEqual(r.potential_resend_names,("Hoa",))

    def test_12_first_round_permission_missing_halts_immediately(self):
        self.diag=PartyJoinTwoRoundDiagnostic(
            PartyTeamReadOnlyWait(self.fx.pre(allowed=None)))
        r=self.inspect()
        self.assertEqual(r.code,"BLOCKED_FIRST_OBSERVATION_BLOCKED_SIGNED_INFO_GATE_UNAVAILABLE")
        self.assertEqual(len(r.rounds),1)
        self.assertEqual(self.fx.reads,0)

    def test_13_first_round_role_provider_missing_halts(self):
        self.diag=PartyJoinTwoRoundDiagnostic(
            PartyTeamReadOnlyWait(self.fx.pre(read_own_ids=None)))
        r=self.inspect()
        self.assertEqual(r.code,"BLOCKED_FIRST_OBSERVATION_BLOCKED_LIVE_IDENTITY_PROVIDER_UNAVAILABLE")
        self.assertEqual(r.invites_sent,0)

    def test_14_signed_gate_revoked_at_second_round(self):
        count=[0]
        def permission():
            count[0]+=1
            return count[0]<=2
        self.diag=PartyJoinTwoRoundDiagnostic(
            PartyTeamReadOnlyWait(self.fx.pre(allowed=permission)))
        r=self.inspect()
        self.assertEqual(r.code,"BLOCKED_SECOND_OBSERVATION_BLOCKED_PERMISSION_NOT_VERIFIED")
        self.assertEqual(len(r.rounds),2)
        self.assertEqual(r.invites_sent,0)

    def test_15_closed_hwnd_after_first_round_is_blocked_on_second(self):
        counts=[0]
        def team(hwnd):
            if hwnd==101:
                counts[0]+=1
                if counts[0]==1:
                    # S94 preflight sees closed HWND right away.
                    pass
                else:
                    self.fx.backend.mapped.pop(101,None)
            return self.fx.teams[hwnd]
        self.diag=PartyJoinTwoRoundDiagnostic(
            PartyTeamReadOnlyWait(self.fx.pre(read_team_id=team)))
        r=self.inspect()
        self.assertTrue(r.code.startswith("BLOCKED_SECOND_OBSERVATION_BLOCKED_"))
        self.assertFalse(r.rounds[1].code.startswith("DIAGNOSTIC_OBSERVED"))

    def test_16_reused_pid_after_first_round_halts(self):
        calls=[0]
        def team(hwnd):
            if hwnd==101:
                calls[0]+=1
                if calls[0]==2:self.fx.backend.mapped[101]=9999
            return self.fx.teams[hwnd]
        self.diag=PartyJoinTwoRoundDiagnostic(
            PartyTeamReadOnlyWait(self.fx.pre(read_team_id=team)))
        r=self.inspect()
        self.assertEqual(r.code,"BLOCKED_SECOND_OBSERVATION_BLOCKED_STALE_NATIVE_HWND_PID")

    def test_17_revision_after_first_round_halts(self):
        calls=[0]
        def team(hwnd):
            if hwnd==101:
                calls[0]+=1
                if calls[0]==2:
                    self.fx.producer.value=snap(2,*self.fx.snapshot.windows)
            return self.fx.teams[hwnd]
        self.diag=PartyJoinTwoRoundDiagnostic(
            PartyTeamReadOnlyWait(self.fx.pre(read_team_id=team)))
        r=self.inspect()
        self.assertEqual(r.code,"BLOCKED_SECOND_OBSERVATION_BLOCKED_STALE_START_REVISION")

    def test_18_cancel_before_any_observation(self):
        cancel=threading.Event();cancel.set()
        r=self.inspect(cancel=cancel)
        self.assertEqual((r.code,len(r.rounds),self.fx.reads),("CANCELLED",0,0))

    def test_19_cancel_after_first_before_second(self):
        cancel=threading.Event()
        def team(hwnd):
            if hwnd==101:cancel.set()
            return self.fx.teams[hwnd]
        self.diag=PartyJoinTwoRoundDiagnostic(
            PartyTeamReadOnlyWait(self.fx.pre(read_team_id=team)))
        r=self.inspect(cancel=cancel)
        self.assertEqual(r.code,"CANCELLED")
        self.assertEqual(len(r.rounds),1)
        self.assertEqual(self.fx.reads,1)

    def test_20_cancel_during_second_observation(self):
        cancel=threading.Event()
        reads=[0]
        def team(hwnd):
            if hwnd==101:
                reads[0]+=1
                if reads[0]==2:cancel.set()
            return self.fx.teams[hwnd]
        self.diag=PartyJoinTwoRoundDiagnostic(
            PartyTeamReadOnlyWait(self.fx.pre(read_team_id=team)))
        r=self.inspect(cancel=cancel)
        self.assertEqual(r.code,"CANCELLED")
        self.assertEqual(len(r.rounds),2)

    def test_21_bad_selection_none_blocks_no_reads(self):
        for names in ([],(),("Minh",),("Minh","Minh"),("Minh",""),(" Minh","Hoa")):
            with self.subTest(names=names):
                self.assertEqual(self.inspect(names).code,"INVALID_SELECTION")
        self.assertEqual(self.fx.reads,0)

    def test_22_leader_not_selected_blocks(self):
        self.assertEqual(self.inspect(leader="Alien").code,"INVALID_LEADER")
        self.assertEqual(self.fx.reads,0)

    def test_23_invalid_duration_or_interval(self):
        for timeout,poll in ((-1,.001),(0,0),(3601,1),(1,3601),
                             (float("inf"),1),(float("nan"),1),("1",1)):
            with self.subTest(t=timeout,p=poll):
                self.assertEqual(self.inspect(timeout=timeout,poll=poll).code,
                                 "INVALID_BOUNDS")
        self.assertEqual(self.fx.reads,0)

    def test_24_invalid_cancel_object(self):
        self.assertEqual(self.inspect(cancel="stop").code,"INVALID_CANCEL")

    def test_25_real_group_progress_can_succeed_first_round_with_unicode(self):
        self.fx.records=[(1000,100,"Ánh",15),(1001,101,"Bình",13)]
        self.fx.teams[101]=567
        r=self.inspect(("Ánh","Bình"),leader="Ánh")
        self.assertEqual(r.code,"DIAGNOSTIC_ALL_JOINED_FIRST_OBSERVATION_NO_GAME_ACTION")

    def test_26_status_never_claims_packet_invite_or_resend_sent(self):
        r=self.inspect()
        self.assertEqual(r.invites_sent,0)
        self.assertIn("NO_GAME_ACTION",r.code)

    def test_27_result_immutable(self):
        r=self.inspect()
        with self.assertRaises(Exception):r.invites_sent=1
        with self.assertRaises(Exception):r.rounds[0].code="SENT"

    def test_28_round_details_include_test_s95_identity_preflight_code(self):
        self.fx.teams[101]=567
        r=self.inspect()
        self.assertEqual(r.rounds[0].last_preflight_code,
                         "DIAGNOSTIC_OBSERVED_NO_GAME_ACTION")
        self.assertEqual(r.rounds[0].leader_team_id,567)

    def test_29_requires_s95_real_wait_object(self):
        with self.assertRaises(TypeError):
            PartyJoinTwoRoundDiagnostic(object())

    def test_30_no_invalid_game_action_or_token_in_source(self):
        s=(ROOT/"src/party_join_report.py").read_text(encoding="utf-8")
        for t in ("ReadProcessMemory(","WriteProcessMemory(","PostMessage(",
                  "200051","200057","create_team(","invite_team(","send_packet(",
                  "TOKEN_HMAC_SECRET","tk.Button("):
            self.assertNotIn(t,s)

    def test_31_timeout_recovery_second_reads_full_roster(self):
        self.fx.teams[101]=0
        calls=[0]
        def team(hwnd):
            if hwnd==101:
                calls[0]+=1
                if calls[0]==2:return 567
            return self.fx.teams[hwnd]
        self.diag=PartyJoinTwoRoundDiagnostic(
            PartyTeamReadOnlyWait(self.fx.pre(read_team_id=team)))
        r=self.inspect()
        self.assertEqual(r.code,"DIAGNOSTIC_ALL_JOINED_SECOND_OBSERVATION_NO_GAME_ACTION")
        self.assertEqual(self.fx.reads,2)

if __name__=="__main__":
    unittest.main()
