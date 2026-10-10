"""S94 original Party G03/G10: read-only action identity and TeamID fail-close."""
from __future__ import annotations
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from party_team_identity import (
    NO_TEAM_IDS, PartyTeamIdentityPreflight, classify_team_id)
from start_windows import GameWindow
from start_polling import WindowSnapshot


def win(hwnd,pid):
    return GameWindow(hwnd,pid,"TITLE IS NOT A ROLE", "TEST-ONLY","python.exe")


def snap(rev=1,*windows,valid=True):
    return WindowSnapshot(revision=rev,windows=tuple(windows),valid=valid)


class Producer:
    def __init__(self,snapshot):
        self.value=snapshot
    def read_snapshot(self):
        return self.value


class Backend:
    def __init__(self,snapshot):
        self.mapped={w.hwnd:w.pid for w in snapshot.windows}
        self.calls=0
        self.read_hook=None
    def is_window(self,hwnd):
        self.calls+=1
        if self.read_hook:self.read_hook(self.calls,self)
        return hwnd in self.mapped
    def process_id(self,hwnd):
        return self.mapped[hwnd]


class Fixture:
    def __init__(self):
        self.snapshot=snap(1,win(100,1000),win(101,1001))
        self.producer=Producer(self.snapshot)
        self.backend=Backend(self.snapshot)
        self.records=[(1000,0,"Minh",10),(1001,430,"Hoa",11)]
        self.teams={100:0,101:0xFFFFFFFF}
        self.permission=True
        self.reads=0
        self.allowed_calls=0
    def read_records(self):
        self.reads+=1
        return self.records
    def read_team(self,hwnd):
        return self.teams[hwnd]
    def allow(self):
        self.allowed_calls+=1
        return self.permission
    def pre(self,**overrides):
        args=dict(start_producer=self.producer,backend=self.backend,
                  read_own_ids=self.read_records,read_team_id=self.read_team,
                  allowed=self.allow)
        args.update(overrides)
        return PartyTeamIdentityPreflight(**args)


class S94IdentityUnit(unittest.TestCase):
    def setUp(self):self.fx=Fixture()

    def test_01_no_team_ids_exact_original(self):
        self.assertEqual(NO_TEAM_IDS,{0,0xFFFFFFFF})

    def test_02_0_is_known_outside_not_error(self):
        self.assertEqual(classify_team_id(0),"KNOWN_OUTSIDE_TEAM")

    def test_03_max_unsigned_is_known_outside(self):
        self.assertEqual(classify_team_id(0xFFFFFFFF),"KNOWN_OUTSIDE_TEAM")

    def test_04_none_is_unknown_not_outside(self):
        self.assertEqual(classify_team_id(None),"UNKNOWN_READ_FAILURE")

    def test_05_valid_team_is_known_in_team(self):
        self.assertEqual(classify_team_id(15),"KNOWN_IN_TEAM")

    def test_06_bool_is_not_numeric_team_id(self):
        self.assertEqual(classify_team_id(False),"INVALID_TEAM_ID")

    def test_07_negative_overflow_team_is_invalid(self):
        for n in (-1,0x100000000,"error",3.1):
            self.assertEqual(classify_team_id(n),"INVALID_TEAM_ID")

    def test_08_missing_external_role_provider_blocks_without_reads(self):
        result=self.fx.pre(read_own_ids=None).inspect(("Minh",))
        self.assertEqual(result.code,"LIVE_IDENTITY_PROVIDER_UNAVAILABLE")
        self.assertEqual(self.fx.reads,0)

    def test_09_missing_external_team_provider_blocks(self):
        r=self.fx.pre(read_team_id=None).inspect(("Minh",))
        self.assertEqual(r.code,"LIVE_IDENTITY_PROVIDER_UNAVAILABLE")

    def test_10_missing_signed_gate_blocks_all_reads(self):
        r=self.fx.pre(allowed=None).inspect(("Minh",))
        self.assertEqual(r.code,"SIGNED_INFO_GATE_UNAVAILABLE")
        self.assertEqual(self.fx.reads,0)

    def test_11_denied_permission_blocks_before_memory_reader(self):
        self.fx.permission=False
        r=self.fx.pre().inspect(("Minh",))
        self.assertEqual(r.code,"PERMISSION_NOT_VERIFIED")
        self.assertEqual(self.fx.reads,0)

    def test_12_no_selected_members_short_circuits(self):
        self.assertEqual(self.fx.pre().inspect(()).code,"NO_SELECTED_MEMBERS")

    def test_13_input_bad_duplicates_rejected(self):
        for selection in (("Minh","Minh"),("",),(" ",),["Minh"],(1,),("Minh"," Minh ")):
            self.assertEqual(self.fx.pre().inspect(selection).code,"INVALID_SELECTION")

    def test_14_verified_test_only_roles_but_no_action_enabled(self):
        result=self.fx.pre().inspect(("Minh","Hoa"))
        self.assertEqual(result.code,"DIAGNOSTIC_OBSERVED_NO_GAME_ACTION")
        self.assertEqual([(x.hwnd,x.pid,x.role_id,x.team_id,x.team_state)
                          for x in result.targets],
                         [(100,1000,0,0,"KNOWN_OUTSIDE_TEAM"),
                          (101,1001,430,0xFFFFFFFF,"KNOWN_OUTSIDE_TEAM")])
        self.assertEqual(self.fx.reads,1)
        self.assertGreater(self.fx.allowed_calls,1)

    def test_15_roleid_zero_not_invented_invalid_sentinel(self):
        result=self.fx.pre().inspect(("Minh",))
        self.assertEqual(result.targets[0].role_id,0)

    def test_16_saved_display_name_matches_exact_before_case(self):
        self.fx.records=[(1000,2,"miNH",10),(1001,3,"Minh",11)]
        result=self.fx.pre().inspect(("Minh",))
        self.assertEqual(result.code,"DIAGNOSTIC_OBSERVED_NO_GAME_ACTION")
        self.assertEqual(result.targets[0].pid,1001)

    def test_17_lowercase_fallback_is_original_rule(self):
        result=self.fx.pre().inspect(("MINH",))
        self.assertEqual(result.code,"DIAGNOSTIC_OBSERVED_NO_GAME_ACTION")
        self.assertEqual(result.targets[0].role_id,0)

    def test_18_ambiguous_lowercase_blocks_not_arbitrary_first(self):
        self.fx.records=[(1000,1,"name",1),(1001,2,"NAME",2)]
        result=self.fx.pre().inspect(("Name",))
        self.assertEqual(result.code,"AMBIGUOUS_LOWERCASE")
        self.assertEqual(result.targets,())

    def test_19_saved_unavailable_never_invents_roleid(self):
        result=self.fx.pre().inspect(("Absent",))
        self.assertEqual(result.code,"UNRESOLVED_ONLINE_MEMBERS")
        self.assertEqual(result.unavailable_names,("Absent",))
        self.assertFalse(result.targets)

    def test_20_pid_outside_current_start_cache_is_unresolved(self):
        self.fx.records=[(9999,42,"Minh",3)]
        result=self.fx.pre().inspect(("Minh",))
        self.assertEqual(result.code,"UNRESOLVED_ONLINE_MEMBERS")
        self.assertEqual(result.targets,())

    def test_21_none_teamid_blocks_no_outside_success(self):
        self.fx.teams[100]=None
        result=self.fx.pre().inspect(("Minh",))
        self.assertEqual(result.code,"TEAMID_UNKNOWN_NOT_OUTSIDE")
        self.assertFalse(result.targets)

    def test_22_stale_pid_at_initial_native_check(self):
        self.fx.backend.mapped[100]=2000
        result=self.fx.pre().inspect(("Minh",))
        self.assertEqual(result.code,"STALE_NATIVE_HWND_PID")

    def test_23_game_window_destroyed_during_team_read(self):
        def destroy(hwnd):
            self.fx.backend.mapped.pop(hwnd,None)
            return 0
        result=self.fx.pre(read_team_id=destroy).inspect(("Minh",))
        self.assertEqual(result.code,"STALE_NATIVE_HWND_PID")

    def test_24_window_reused_during_team_read(self):
        def replace(hwnd):
            self.fx.backend.mapped[hwnd]=9999
            return 0
        result=self.fx.pre(read_team_id=replace).inspect(("Minh",))
        self.assertEqual(result.code,"STALE_NATIVE_HWND_PID")

    def test_25_stale_revision_after_read_rejects_full_result(self):
        def change(_hwnd):
            self.fx.producer.value=snap(2,win(100,1000),win(101,1001))
            return 0
        r=self.fx.pre(read_team_id=change).inspect(("Minh",))
        self.assertEqual(r.code,"STALE_START_REVISION")
        self.assertFalse(r.targets)

    def test_26_signed_gate_revoked_before_publish(self):
        def revoke(hwnd):
            self.fx.permission=False
            return 0
        self.assertEqual(self.fx.pre(read_team_id=revoke).inspect(("Minh",)).code,
                         "PERMISSION_REVOKED")

    def test_27_reader_failure_is_distinct_from_empty_rows(self):
        def fail():raise OSError("no process")
        self.assertEqual(self.fx.pre(read_own_ids=fail).inspect(("Minh",)).code,
                         "ROLEID_READ_ERROR")
        self.assertEqual(self.fx.pre(read_own_ids=lambda:[]).inspect(("Minh",)).code,
                         "UNRESOLVED_ONLINE_MEMBERS")

    def test_28_invalid_roleid_record_not_assumed_online(self):
        for bad in (None,{},[(1000,"42","Minh",2)],[(1000,1,"",2)],
                    [(1000,1,"A",1),(1000,2,"B",1)]):
            self.assertEqual(self.fx.pre(read_own_ids=lambda x=bad:x).inspect(("Minh",)).code,
                             "INVALID_ROLEID_RECORDS")

    def test_29_teamid_read_exception_blocks_with_no_targets(self):
        def fail(hwnd):raise OSError("memory unavailable")
        self.assertEqual(self.fx.pre(read_team_id=fail).inspect(("Minh",)).code,
                         "TEAMID_READ_ERROR")

    def test_30_wrong_teamid_data_rejected(self):
        self.fx.teams[100]=False
        self.assertEqual(self.fx.pre().inspect(("Minh",)).code,"INVALID_TEAMID_DATA")

    def test_31_invalid_start_cache_fails_closed(self):
        self.fx.producer.value=snap(1,win(100,1000),valid=False)
        self.assertEqual(self.fx.pre().inspect(("Minh",)).code,"INVALID_START_CACHE")

    def test_32_empty_cache_reports_no_windows(self):
        self.fx.producer.value=snap(1)
        self.assertEqual(self.fx.pre().inspect(("Minh",)).code,"NO_LIVE_WINDOWS")

    def test_33_duplicate_pid_or_hwnd_in_cache_blocks(self):
        self.fx.producer.value=snap(1,win(100,1000),win(102,1000))
        self.assertEqual(self.fx.pre().inspect(("Minh",)).code,"INVALID_START_CACHE")
        self.fx.producer.value=snap(1,win(100,1000),win(100,1001))
        self.assertEqual(self.fx.pre().inspect(("Minh",)).code,"INVALID_START_CACHE")

    def test_34_record_name_html_not_guessed_from_title(self):
        self.assertEqual(self.fx.pre().inspect(("TITLE IS NOT A ROLE",)).code,
                         "UNRESOLVED_ONLINE_MEMBERS")

    def test_35_zero_packet_game_or_memory_apis_in_source(self):
        source=(ROOT/"src/party_team_identity.py").read_text("utf-8")
        for pattern in ("ReadProcessMemory(", "WriteProcessMemory(",
                        "PostMessage(", "SendMessage(", "0x355B208",
                        "0x6F4030", "create_team(", "leave_team(", "send_invite("):
            self.assertNotIn(pattern,source)

if __name__=="__main__":
    unittest.main()
