"""S95 G10 read-only team state wait, TEST-ONLY external identity/team records."""
from __future__ import annotations
from pathlib import Path
import sys
import threading
import time
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"tests"))
from test_s94 import Fixture
from party_team_wait import PartyTeamReadOnlyWait, PartyTeamWaitResult


class S95ReadOnlyTeamWaitTests(unittest.TestCase):
    def setUp(self):
        self.fx=Fixture()
        self.wait=PartyTeamReadOnlyWait(self.fx.pre())

    def call(self,selected=("Minh","Hoa"),*,mode="OUTSIDE",timeout=.03,
             interval=.005,leader="Minh",cancel=None):
        return self.wait.wait(
            selected,mode=mode,timeout_seconds=timeout,
            poll_seconds=interval,leader_name=leader,cancel=cancel)

    def test_01_outside_all_two_original_sentinels_is_true_diagnostic(self):
        r=self.call()
        self.assertEqual(r.code,"DIAGNOSTIC_OBSERVED_ALL_OUTSIDE_NO_GAME_ACTION")
        self.assertEqual(r.attempts,1)
        self.assertEqual(r.missing_names,())

    def test_02_unknown_none_does_not_confirm_outside(self):
        self.fx.teams[100]=None
        r=self.call()
        self.assertEqual(r.code,"TIMEOUT_NOT_CONFIRMED")
        self.assertEqual(r.last_preflight_code,"TEAMID_UNKNOWN_NOT_OUTSIDE")

    def test_03_one_member_in_team_missing_not_success(self):
        self.fx.teams[101]=123
        r=self.call()
        self.assertEqual(r.code,"TIMEOUT_NOT_CONFIRMED")
        self.assertEqual(r.missing_names,("Hoa",))

    def test_04_transient_read_error_recovers_success(self):
        self.fx.teams[100]=None
        calls=[0]
        def team(hwnd):
            calls[0]+=1
            if calls[0]>=3:self.fx.teams[100]=0
            return self.fx.teams[hwnd]
        self.wait=PartyTeamReadOnlyWait(self.fx.pre(read_team_id=team))
        r=self.call()
        self.assertEqual(r.code,"DIAGNOSTIC_OBSERVED_ALL_OUTSIDE_NO_GAME_ACTION")
        self.assertGreater(r.attempts,1)

    def test_05_team_stays_unknown_timeout_count_bounded(self):
        self.fx.teams[100]=None
        r=self.call(timeout=.015)
        self.assertLess(r.attempts,20)
        self.assertGreater(r.attempts,0)

    def test_06_same_real_team_success(self):
        self.fx.teams[100]=445
        self.fx.teams[101]=445
        r=self.call(mode="SAME_TEAM")
        self.assertEqual(r.code,"DIAGNOSTIC_OBSERVED_SAME_REAL_TEAM_NO_GAME_ACTION")
        self.assertEqual(r.leader_team_id,445)
        self.assertEqual(r.missing_names,())

    def test_07_both_outside_same_sentinel_not_a_party(self):
        self.fx.teams[100]=0
        self.fx.teams[101]=0
        r=self.call(mode="SAME_TEAM")
        self.assertEqual(r.code,"TIMEOUT_NOT_CONFIRMED")
        self.assertEqual(r.missing_names,("Hoa",))
        self.assertIsNone(r.leader_team_id)

    def test_08_both_outside_different_sentinels_not_a_party(self):
        r=self.call(mode="SAME_TEAM")
        self.assertEqual(r.code,"TIMEOUT_NOT_CONFIRMED")

    def test_09_different_real_team_ids_not_joined(self):
        self.fx.teams[100]=333
        self.fx.teams[101]=334
        r=self.call(mode="SAME_TEAM")
        self.assertEqual(r.code,"TIMEOUT_NOT_CONFIRMED")
        self.assertEqual(r.leader_team_id,333)
        self.assertEqual(r.missing_names,("Hoa",))

    def test_10_leader_in_team_member_outside_waits(self):
        self.fx.teams[100]=444
        self.fx.teams[101]=0xFFFFFFFF
        r=self.call(mode="SAME_TEAM")
        self.assertEqual(r.code,"TIMEOUT_NOT_CONFIRMED")
        self.assertEqual(r.missing_names,("Hoa",))

    def test_11_member_joins_on_later_poll(self):
        self.fx.teams[100]=444
        self.fx.teams[101]=0
        attempts=[0]
        def team(hwnd):
            if hwnd==101:
                attempts[0]+=1
                if attempts[0]>=2:self.fx.teams[101]=444
            return self.fx.teams[hwnd]
        self.wait=PartyTeamReadOnlyWait(self.fx.pre(read_team_id=team))
        r=self.call(mode="SAME_TEAM")
        self.assertEqual(r.code,"DIAGNOSTIC_OBSERVED_SAME_REAL_TEAM_NO_GAME_ACTION")
        self.assertGreaterEqual(r.attempts,2)

    def test_12_cancel_before_first_read_performs_no_calls(self):
        evt=threading.Event();evt.set()
        r=self.call(cancel=evt)
        self.assertEqual(r.code,"CANCELLED")
        self.assertEqual(r.attempts,0)
        self.assertEqual(self.fx.reads,0)

    def test_13_cancel_during_wait_interrupts_poll(self):
        self.fx.teams[100]=555
        evt=threading.Event()
        t=threading.Thread(target=lambda:(time.sleep(.025),evt.set()))
        t.start()
        start=time.monotonic()
        r=self.call(timeout=2,interval=1,cancel=evt)
        t.join()
        self.assertEqual(r.code,"CANCELLED")
        self.assertLess(time.monotonic()-start,.3)

    def test_14_no_external_providers_blocks_before_poll(self):
        self.wait=PartyTeamReadOnlyWait(self.fx.pre(read_own_ids=None))
        r=self.call()
        self.assertEqual(r.code,"BLOCKED_LIVE_IDENTITY_PROVIDER_UNAVAILABLE")
        self.assertEqual(r.attempts,1)

    def test_15_unsigned_permission_blocks_wait(self):
        self.wait=PartyTeamReadOnlyWait(self.fx.pre(allowed=None))
        self.assertEqual(self.call().code,"BLOCKED_SIGNED_INFO_GATE_UNAVAILABLE")

    def test_16_permission_revocation_aborts_wait(self):
        self.fx.teams[100]=500
        events=[0]
        def allow():
            events[0]+=1
            return events[0]<=2
        self.wait=PartyTeamReadOnlyWait(self.fx.pre(allowed=allow))
        self.assertEqual(self.call().code,"BLOCKED_PERMISSION_NOT_VERIFIED")

    def test_17_closed_hwnd_fails_not_outside_success(self):
        self.fx.backend.mapped.pop(100)
        self.assertEqual(self.call().code,"BLOCKED_STALE_NATIVE_HWND_PID")

    def test_18_changed_pid_fails_not_same_team_success(self):
        self.fx.teams[100]=200
        self.fx.teams[101]=200
        self.fx.backend.mapped[100]=9999
        self.assertEqual(self.call(mode="SAME_TEAM").code,
                         "BLOCKED_STALE_NATIVE_HWND_PID")

    def test_19_changed_start_cache_revision_blocks(self):
        def change(_hwnd):
            self.fx.producer.value=type(self.fx.snapshot)(
                revision=3,windows=self.fx.snapshot.windows,valid=True)
            return 0
        self.wait=PartyTeamReadOnlyWait(self.fx.pre(read_team_id=change))
        self.assertEqual(self.call().code,"BLOCKED_STALE_START_REVISION")

    def test_20_offline_member_never_imputed_joined(self):
        r=self.call(("Minh","Offline"))
        self.assertEqual(r.code,"TIMEOUT_NOT_CONFIRMED")
        self.assertEqual(r.missing_names,("Offline",))

    def test_21_no_team_read_error_stays_unconfirmed(self):
        self.wait=PartyTeamReadOnlyWait(self.fx.pre(read_team_id=lambda h:None))
        self.assertEqual(self.call().code,"TIMEOUT_NOT_CONFIRMED")

    def test_22_bad_mode(self):
        self.assertEqual(self.call(mode="CREATE").code,"INVALID_MODE")

    def test_23_bad_selected(self):
        self.assertEqual(self.call(selected=()).code,"INVALID_SELECTION")
        self.assertEqual(self.call(selected=["Minh"]).code,"INVALID_SELECTION")

    def test_24_same_team_requires_actual_selected_leader(self):
        self.assertEqual(self.call(mode="SAME_TEAM",leader="Offline").code,"INVALID_LEADER")
        self.assertEqual(self.call(("Minh",),mode="SAME_TEAM").code,"INVALID_LEADER")

    def test_25_unknown_bound_numerics_fail(self):
        for timeout,poll in ((-1,.01),(0,0),(1,-.2),(3601,1),(1,3601),("4",.01),(1,float("nan"))):
            self.assertEqual(self.call(timeout=timeout,interval=poll).code,"INVALID_BOUNDS")

    def test_26_invalid_cancel_type_fails(self):
        self.assertEqual(self.call(cancel="yes").code,"INVALID_CANCEL")

    def test_27_zero_timeout_only_one_observation(self):
        self.fx.teams[100]=3
        r=self.call(timeout=0)
        self.assertEqual(r.attempts,1)
        self.assertEqual(r.code,"TIMEOUT_NOT_CONFIRMED")

    def test_28_same_team_explicit_missing_member_diagnostic(self):
        self.fx.teams[100]=200
        self.fx.teams[101]=333
        r=self.call(mode="SAME_TEAM")
        self.assertEqual(r.missing_names,("Hoa",))

    def test_29_no_fake_packet_write_or_auth_issuer(self):
        source=(ROOT/"src/party_team_wait.py").read_text("utf-8")
        for term in ("ReadProcessMemory(", "WriteProcessMemory(", "PostMessage(",
                     "200051", "200057", "TOKEN_HMAC_SECRET", "create_team(",
                     "leave_team(", "socket.send(", "tk.Button("):
            self.assertNotIn(term,source)

if __name__=="__main__":
    unittest.main()
