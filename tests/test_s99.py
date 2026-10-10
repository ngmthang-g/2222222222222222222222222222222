"""S99 G03/G10 original name=TeamID, '?' UI-neutral diagnostic contract."""
from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
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
from party_snapshot_presentation import present_party_team_snapshot


class S99Presentation(unittest.TestCase):
    def setUp(self):
        self.fx=Fixture()
        self.fx.teams[100]=531
        self.fx.teams[101]=0

    def diag(self,pre=None):
        return PartyJoinReadEpochDiagnostic(
            PartyJoinDetailedDiagnostic(
                PartyJoinTwoRoundDiagnostic(PartyTeamReadOnlyWait(
                    pre or self.fx.pre()))))

    def epoch(self,names=("Minh","Hoa"),leader="Minh",pre=None,cancel=None):
        return self.diag(pre).inspect(
            names,leader_name=leader,
            timeout_seconds=0,poll_seconds=.01,cancel=cancel)

    def view(self,**kwargs):
        return present_party_team_snapshot(self.epoch(**kwargs))

    def test_01_source_original_style_name_equals_decimal_teamid(self):
        r=self.view()
        self.assertEqual([x.original_style_field for x in r.rows],
                         ["Minh=531","Hoa=0"])
        self.assertEqual([x.display_team_id for x in r.rows],["531","0"])
        self.assertEqual(r.rows[1].diagnostic_state,"KNOWN_OUTSIDE")

    def test_02_second_post_read_is_explicit_non_atomic(self):
        r=self.view()
        self.assertEqual(r.code,"DIAGNOSTIC_PRESENTATION_ONLY_NO_GAME_ACTION")
        self.assertEqual(r.s97_phase,"AFTER_S96_OBSERVATIONS")
        self.assertEqual(r.s98_phase,"SECOND_SEQUENTIAL_POST_S96_OBSERVATION")
        self.assertTrue(r.sequential_non_atomic)
        self.assertFalse(r.game_parity_verified)
        self.assertFalse(r.action_authorized)
        self.assertEqual(r.invites_sent,0)

    def test_03_s96_both_rounds_missing_provenance_not_fabricated(self):
        r=self.view()
        self.assertEqual(len(r.s96_round_codes),2)
        self.assertEqual(r.s96_round_missing_names,(("Hoa",),("Hoa",)))

    def test_04_one_round_s96_complete_is_preserved(self):
        self.fx.teams[101]=531
        r=self.view()
        self.assertEqual(len(r.s96_round_codes),1)
        self.assertEqual(r.rows[1].original_style_field,"Hoa=531")
        self.assertEqual(r.rows[1].diagnostic_state,"JOINED_LEADER_TEAM")

    def test_05_mismatched_real_team_is_diagnostic_not_joined(self):
        self.fx.teams[101]=981
        r=self.view()
        self.assertEqual(r.rows[1].diagnostic_state,"DIFFERENT_REAL_TEAM")
        self.assertEqual(r.rows[1].original_style_field,"Hoa=981")
        self.assertFalse(r.action_authorized)

    def test_06_0_and_ffffffff_both_known_outside(self):
        self.fx.teams[100]=0
        self.fx.teams[101]=0xFFFFFFFF
        r=self.view()
        self.assertEqual(r.rows[0].original_style_field,"Minh=0")
        self.assertEqual(r.rows[1].original_style_field,"Hoa=4294967295")
        self.assertTrue(all(x.diagnostic_state=="KNOWN_OUTSIDE" for x in r.rows))

    def test_07_none_teamid_is_question_mark_not_zero(self):
        self.fx.teams[101]=None
        r=self.view()
        self.assertEqual(r.rows[1].original_style_field,"Hoa=?")
        self.assertEqual(r.rows[1].diagnostic_state,"UNREADABLE_TEAMID")

    def test_08_offline_name_question_mark_is_classified_separately(self):
        r=self.view(names=("Minh","Offline"))
        self.assertEqual(r.rows[1].original_style_field,"Offline=?")
        self.assertEqual(r.rows[1].diagnostic_state,"OFFLINE_NAME")

    def test_09_role_record_pid_not_present_in_start_is_not_offline(self):
        self.fx.records[1]=(9999,430,"Hoa",10)
        r=self.view()
        self.assertEqual(r.rows[1].original_style_field,"Hoa=?")
        self.assertEqual(r.rows[1].diagnostic_state,"PID_NOT_IN_START_CACHE")

    def test_10_read_exception_post_round_shows_unknown_and_detail(self):
        reads=[0]
        def team(hwnd):
            if hwnd==101:
                reads[0]+=1
                if reads[0] >= 2:
                    raise OSError("test reader unavailable")
            return 531
        v=self.view(pre=self.fx.pre(read_team_id=team))
        self.assertEqual(v.rows[1].original_style_field,"Hoa=?")
        self.assertEqual(v.rows[1].diagnostic_state,"TEAMID_READ_ERROR")

    def test_11_stale_pid_blocks_entire_presentation(self):
        self.fx.backend.mapped[101]=9999
        v=self.view()
        self.assertTrue(v.code.startswith("BLOCKED_PRESENTATION_"))
        self.assertEqual(v.rows,())

    def test_12_stale_start_revision_blocks_entire_report(self):
        reads=[0]
        def team(hwnd):
            if hwnd==101:
                reads[0]+=1
                if reads[0]==4:
                    self.fx.producer.value=snap(2,*self.fx.snapshot.windows)
            return self.fx.teams[hwnd]
        v=self.view(pre=self.fx.pre(read_team_id=team))
        self.assertTrue(v.code.startswith("BLOCKED_PRESENTATION_"))
        self.assertFalse(v.rows)

    def test_13_unsigned_info_gate_missing_blocks(self):
        v=self.view(pre=self.fx.pre(allowed=None))
        self.assertTrue(v.code.startswith("BLOCKED_PRESENTATION_"))
        self.assertEqual(v.rows,())

    def test_14_cancel_before_begin_never_renders_success(self):
        e=threading.Event();e.set()
        v=self.view(cancel=e)
        self.assertTrue(v.code.startswith("BLOCKED_PRESENTATION_"))
        self.assertEqual(v.rows,())

    def test_15_two_sequential_teamids_keep_later_snapshot(self):
        reads=[0]
        def team(hwnd):
            if hwnd==101:
                reads[0]+=1
                return 0 if reads[0]<=3 else 531
            return 531
        v=self.view(pre=self.fx.pre(read_team_id=team))
        self.assertEqual(v.rows[1].original_style_field,"Hoa=531")
        self.assertEqual(v.rows[1].comparison_code,"OBSERVED_TEAM_ID_CHANGED")
        self.assertEqual(len(v.s96_round_codes),2)

    def test_16_s99_never_claims_original_s97_round_data_atomic(self):
        v=self.view()
        self.assertEqual(v.snapshot_revision,1)
        self.assertIn("DIAGNOSTIC_SEQUENTIAL_",v.epoch_source_code)
        self.assertTrue(v.sequential_non_atomic)

    def test_17_unicode_original_names_retained(self):
        self.fx.records=[(1000,1,"ĐộiTrưởng",10),(1001,2,"Hòa✨",11)]
        v=self.view(names=("ĐộiTrưởng","Hòa✨"),leader="ĐộiTrưởng")
        self.assertEqual(v.rows[0].original_style_field,"ĐộiTrưởng=531")
        self.assertEqual(v.rows[1].original_style_field,"Hòa✨=0")

    def test_18_escaping_metadata_delimiters_is_not_game_behavior_claim(self):
        self.fx.records=[(1000,1,"Mi=nh",10),(1001,2,"Ho|a",11)]
        v=self.view(names=("Mi=nh","Ho|a"),leader="Mi=nh")
        self.assertEqual(v.rows[0].original_style_field,r"Mi\=nh=531")
        self.assertEqual(v.rows[1].original_style_field,r"Ho\|a=0")

    def test_19_newline_in_external_name_does_not_inject_log_line(self):
        name="Dòng\nMới"
        self.fx.records[1]=(1001,3,name,11)
        # S94 accepts nonempty exact names; display escapes newline.
        v=self.view(names=("Minh",name))
        self.assertNotIn("\n",v.rows[1].original_style_field)
        self.assertIn(r"\n",v.rows[1].original_style_field)

    def test_20_structured_rows_immutable(self):
        v=self.view()
        with self.assertRaises(FrozenInstanceError):
            v.action_authorized=True
        with self.assertRaises(FrozenInstanceError):
            v.rows[0].display_team_id="bad"

    def test_21_epoch_claims_atomic_true_rejected(self):
        e=replace(self.epoch(),atomic=True)
        v=present_party_team_snapshot(e)
        self.assertIn("ACTION_OR_ATOMICITY_INVARIANT",v.code)
        self.assertFalse(v.rows)

    def test_22_any_nonzero_invites_sent_rejected(self):
        e=replace(self.epoch(),invites_sent=1)
        self.assertEqual(present_party_team_snapshot(e).rows,())
        e=self.epoch()
        b=replace(e.detailed.base,invites_sent=1)
        e=replace(e,detailed=replace(e.detailed,base=b))
        self.assertEqual(present_party_team_snapshot(e).rows,())

    def test_23_changed_revision_rejected_even_with_claimed_success(self):
        e=replace(self.epoch(),end_revision=44)
        v=present_party_team_snapshot(e)
        self.assertIn("STALE_OR_UNVERIFIED_NATIVE_EPOCH",v.code)
        self.assertEqual(v.rows,())

    def test_24_fake_comparison_rejected_without_gameside_actions(self):
        e=self.epoch()
        changed=replace(e.changes[1],class_code="OBSERVED_TEAM_ID_CHANGED")
        e=replace(e,changes=(e.changes[0],changed))
        self.assertEqual(present_party_team_snapshot(e).rows,())

    def test_25_fake_round_provenance_rejected(self):
        e=self.epoch()
        b=replace(e.detailed.base,rounds=tuple(replace(x,round_number=9)
                                                for x in e.detailed.base.rounds))
        e=replace(e,detailed=replace(e.detailed,base=b))
        self.assertIn("INVALID_S96_PROVENANCE",present_party_team_snapshot(e).code)

    def test_26_forged_invalid_team_state_rejected(self):
        e=self.epoch()
        m=replace(e.second_post_snapshot.members[1],state="INVITED_OK")
        e=replace(e,second_post_snapshot=replace(
            e.second_post_snapshot,members=(e.second_post_snapshot.members[0],m)))
        self.assertEqual(present_party_team_snapshot(e).rows,())

    def test_27_invalid_nonreport_type_never_renders(self):
        self.assertEqual(present_party_team_snapshot(None).rows,())
        self.assertEqual(present_party_team_snapshot({}).rows,())

    def test_28_diagnostic_lines_separate_status_from_original_field(self):
        v=self.view()
        self.assertEqual(v.as_lines()[0],"Minh=531 [LEADER_REAL_TEAM; OBSERVED_STABLE]")
        self.assertEqual(v.as_lines()[1],"Hoa=0 [KNOWN_OUTSIDE; OBSERVED_STABLE]")

    def test_29_missing_second_snapshot_has_no_display(self):
        e=replace(self.epoch(),second_post_snapshot=None)
        self.assertFalse(present_party_team_snapshot(e).rows)

    def test_30_source_does_not_contain_game_input(self):
        txt=(ROOT/"src/party_snapshot_presentation.py").read_text("utf-8")
        for token in ("ReadProcessMemory(", "WriteProcessMemory(",
                      "PostMessage(", "SendMessage(", "create_team(",
                      "leave_team(", "send_invite(", "memory_items.invite(",
                      "0x6F4030", "0x355B208"):
            self.assertNotIn(token,txt)
        self.assertFalse(self.view().action_authorized)

if __name__=="__main__":
    unittest.main()
