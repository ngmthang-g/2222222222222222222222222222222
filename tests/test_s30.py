"""S30 E04 emulator-count blocker and read-only observation provenance."""
from __future__ import annotations
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from login_path import EXE_NAME, GameDirectoryResult
from login_launch_preflight import check_open_game_preflight
from permission_guard import PermissionSnapshot
from running_count_provenance import (
    DEFAULT_DIAGNOSTIC_MAX_AGE_SECONDS,
    RunningSnapshotProvenance, observe_running_provenance,
)
from running_count_evidence import ProcessRecord


class ProcessFixture:
    def __init__(self, *snapshots):
        self.snapshots=list(snapshots)
        self.calls=0
    def snapshot_processes(self):
        i=min(self.calls,len(self.snapshots)-1)
        self.calls+=1
        item=self.snapshots[i]
        if isinstance(item,Exception):
            raise item
        return tuple(ProcessRecord(pid,image) for pid,image in item)


class WindowFixture:
    def __init__(self, *windows, error=None):
        self.data={w[0]:w for w in windows}
        self.error=error
    def enumerate_top_level(self):
        if self.error:raise self.error
        return tuple(self.data)
    def is_window(self,h):return h in self.data
    def is_visible(self,h):return self.data[h][2]
    def process_id(self,h):return self.data[h][1]
    def process_executable(self,pid):
        for v in self.data.values():
            if v[1]==pid:return v[3]
        return ""
    def window_class(self,h):return self.data[h][4]
    def title_with_timeout(self,h,ms):
        assert ms==150
        return self.data[h][5]


class Clock:
    def __init__(self,values=(0.,.05)):
        self.values=iter(values)
    def __call__(self):return next(self.values)


def game(pid):
    return (pid,EXE_NAME)


def game_window(hwnd,pid):
    return (hwnd,pid,True,EXE_NAME,"UnityWndClass","Thần Long")


class S30Tests(unittest.TestCase):
    def test_consistent_double_process_sample_and_visible_hwnd(self):
        p=ProcessFixture((game(10),), (game(10),))
        s=observe_running_provenance(
            processes=p,windows=WindowFixture(game_window(111,10)),
            clock=Clock())
        self.assertEqual(s.status,"OBSERVATION_CONSISTENT")
        self.assertEqual(s.process_pids_before,(10,))
        self.assertEqual(s.process_pids_after,(10,))
        self.assertEqual(s.game_process_count,1)
        self.assertEqual(s.visible_game_hwnd_count,1)
        self.assertEqual(s.visible_game_pid_count,1)
        self.assertEqual(p.calls,2)

    def test_changed_process_set_rejected_no_count(self):
        p=ProcessFixture((game(10),),(game(10),game(20)))
        s=observe_running_provenance(processes=p,windows=WindowFixture(),
                                     clock=Clock())
        self.assertEqual(s.status,"GAME_PROCESS_SET_CHANGED")
        self.assertIsNone(s.game_process_count)

    def test_same_number_different_pid_rejected(self):
        p=ProcessFixture((game(10),),(game(20),))
        s=observe_running_provenance(processes=p,windows=WindowFixture(),
                                     clock=Clock())
        self.assertEqual(s.status,"GAME_PROCESS_SET_CHANGED")
        self.assertEqual(len(s.process_pids_before),len(s.process_pids_after))

    def test_hwnd_pid_absent_from_process_list(self):
        p=ProcessFixture((game(10),),(game(10),))
        s=observe_running_provenance(processes=p,windows=WindowFixture(game_window(50,99)),
                                     clock=Clock())
        self.assertEqual(s.status,"HWND_PID_ABSENT_FROM_PROCESS_SNAPSHOT")
        self.assertIsNone(s.game_process_count)

    def test_hidden_process_with_no_visible_hwnd_stays_valid_diagnostic(self):
        p=ProcessFixture((game(10),),(game(10),))
        s=observe_running_provenance(processes=p,windows=WindowFixture(),
                                     clock=Clock())
        self.assertEqual(s.game_process_count,1)
        self.assertEqual(s.visible_game_hwnd_count,0)
        self.assertIsNone(s.combined_running_count)

    def test_two_hwnds_one_pid_not_two_processes(self):
        p=ProcessFixture((game(10),),(game(10),))
        s=observe_running_provenance(processes=p,windows=WindowFixture(
            game_window(50,10),game_window(60,10)),clock=Clock())
        self.assertEqual(s.game_process_count,1)
        self.assertEqual(s.visible_game_hwnd_count,2)
        self.assertEqual(s.visible_game_pid_count,1)

    def test_unchanged_zero_does_not_mean_zero_emulators(self):
        s=observe_running_provenance(processes=ProcessFixture((),()),
                                     windows=WindowFixture(),clock=Clock())
        self.assertEqual(s.game_process_count,0)
        self.assertIsNone(s.emulator_count)
        self.assertIsNone(s.combined_running_count)
        self.assertFalse(s.is_authoritative_account_total)

    def test_first_process_scan_failure_not_zero(self):
        s=observe_running_provenance(
            processes=ProcessFixture(OSError("bad"),(game(10),)),
            windows=WindowFixture(),clock=Clock())
        self.assertEqual((s.status,s.error_stage),("SCAN_FAILED","PROCESS_BEFORE"))
        self.assertIsNone(s.process_pids_before)
        self.assertIsNone(s.game_process_count)

    def test_second_process_scan_failure_not_zero(self):
        s=observe_running_provenance(
            processes=ProcessFixture((game(10),),OSError("bad")),
            windows=WindowFixture(),clock=Clock())
        self.assertEqual((s.status,s.error_stage),("SCAN_FAILED","PROCESS_AFTER"))
        self.assertIsNone(s.process_pids_after)
        self.assertIsNone(s.game_process_count)

    def test_hwnd_scan_failure_not_zero(self):
        s=observe_running_provenance(
            processes=ProcessFixture((),()),
            windows=WindowFixture(error=OSError("bad")),clock=Clock())
        self.assertEqual((s.status,s.error_stage),("SCAN_FAILED","WINDOWS"))
        self.assertIsNone(s.visible_game_hwnd_count)

    def test_consistent_freshness_is_only_diagnostic(self):
        s=observe_running_provenance(processes=ProcessFixture((),()),
                                     windows=WindowFixture(),clock=Clock())
        self.assertEqual(s.diagnostic_freshness(.1),"FRESH_DIAGNOSTIC_ONLY")
        self.assertFalse(s.is_authoritative_account_total)
        self.assertEqual(DEFAULT_DIAGNOSTIC_MAX_AGE_SECONDS,2.0)

    def test_old_observation_is_stale(self):
        s=observe_running_provenance(processes=ProcessFixture((),()),
                                     windows=WindowFixture(),clock=Clock())
        self.assertEqual(s.diagnostic_freshness(2.06),"STALE_DIAGNOSTIC")

    def test_nonatomic_span_too_wide(self):
        s=observe_running_provenance(processes=ProcessFixture((),()),
                                     windows=WindowFixture(),
                                     clock=Clock((0.,3.0)))
        self.assertEqual(s.diagnostic_freshness(3.01),"OBSERVATION_SPAN_TOO_WIDE")

    def test_clock_regression_does_not_count(self):
        s=observe_running_provenance(processes=ProcessFixture((game(10),),(game(10),)),
                                     windows=WindowFixture(),clock=Clock((2.,1.)))
        self.assertEqual(s.status,"CLOCK_INVALID_OR_REGRESSED")
        self.assertIsNone(s.game_process_count)
        self.assertEqual(s.diagnostic_freshness(3.),"CLOCK_INVALID_OR_REGRESSED")

    def test_future_timestamp_rejected(self):
        s=observe_running_provenance(processes=ProcessFixture((),()),
                                     windows=WindowFixture(),clock=Clock())
        self.assertEqual(s.diagnostic_freshness(.01),"CLOCK_INVALID_OR_REGRESSED")

    def test_incomplete_has_no_fresh_grant(self):
        s=observe_running_provenance(processes=ProcessFixture((),(game(3),)),
                                     windows=WindowFixture(),clock=Clock())
        self.assertEqual(s.diagnostic_freshness(.1),"INCOMPLETE_OR_CHANGING")

    def test_invalid_ttl_and_now_types_rejected(self):
        s=observe_running_provenance(processes=ProcessFixture((),()),
                                     windows=WindowFixture(),clock=Clock())
        for now,age,span in ((True,2,2),(float("nan"),2,2),
                             (1,-1,2),(1,2,float("inf")),(1,2,True)):
            with self.assertRaises(ValueError):
                s.diagnostic_freshness(now,max_age_seconds=age,
                                       max_span_seconds=span)

    def test_preflight_unchanged_missing_aggregate_blocks(self):
        s=observe_running_provenance(processes=ProcessFixture((),()),
                                     windows=WindowFixture(),clock=Clock())
        with tempfile.TemporaryDirectory() as td:
            d=Path(td);(d/EXE_NAME).write_bytes(b"S30 NOT A GAME EXE")
            snap=PermissionSnapshot(
                has_verified_payload=True,permissions=frozenset({"login_tab"}),
                max_windows=3,plan_status="TEST_ONLY")
            r=check_open_game_preflight(snap,GameDirectoryResult(d,""),
                                        running_windows=s.combined_running_count)
            self.assertEqual(r.reason,"RUNNING_WINDOW_COUNT_UNKNOWN")
            self.assertFalse(r.allowed)

    def test_fake_title_python_image_not_consistent_game(self):
        s=observe_running_provenance(
            processes=ProcessFixture((),()),
            windows=WindowFixture((9,10,True,"python.exe",
                                   "UnityWndClass","Thần Long")),
            clock=Clock())
        self.assertEqual(s.visible_game_hwnd_count,0)
        self.assertEqual(s.status,"OBSERVATION_CONSISTENT")


if __name__=="__main__":
    unittest.main()
