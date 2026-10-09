"""S29 E04 exact process-image counts vs *partial* visible game HWND evidence."""
from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))

from login_path import EXE_NAME, GameDirectoryResult
from login_launch_preflight import check_open_game_preflight
from permission_guard import PermissionSnapshot
from running_count_evidence import (
    NativeWin32ProcessBackend, ProcessRecord, RunningCountEvidence,
    find_named_process_pids, observe_running_game_evidence, visible_hwnds_for_pid,
)
from start_windows import GAME_PROCESS, GameWindow


class Processes:
    def __init__(self, *records, error=None):
        self.records=records
        self.error=error
        self.calls=0
    def snapshot_processes(self):
        self.calls+=1
        if self.error:raise self.error
        return self.records


class Windows:
    def __init__(self,*windows,error=None):
        # window tuple hwnd,pid,visible,image_name,class_name,title
        self.data={w[0]:w for w in windows}
        self.order=[w[0] for w in windows]
        self.error=error
        self.process_queries=0
    def enumerate_top_level(self):
        if self.error:raise self.error
        return self.order
    def is_window(self,h):return h in self.data
    def is_visible(self,h):return self.data[h][2]
    def process_id(self,h):return self.data[h][1]
    def process_executable(self,pid):
        self.process_queries+=1
        for w in self.data.values():
            if w[1]==pid:return w[3]
        return ""
    def window_class(self,h):return self.data[h][4]
    def title_with_timeout(self,h,timeout_ms):
        assert timeout_ms==150
        return self.data[h][5]


def claims():
    return PermissionSnapshot(
        has_verified_payload=True,permissions=frozenset({"login_tab"}),
        plan_status="TEST_ONLY",max_windows=5)


class S29Tests(unittest.TestCase):
    def test_two_space_original_name_exact(self):
        self.assertEqual(EXE_NAME,"Thần Long  Mobile.exe")
        self.assertNotEqual(EXE_NAME,"Thần Long Mobile.exe")

    def test_image_count_unique_distinct_pid_includes_hidden_instances(self):
        p=Processes(ProcessRecord(10,EXE_NAME),ProcessRecord(20,EXE_NAME),
                    ProcessRecord(10,EXE_NAME),ProcessRecord(30,"python.exe"))
        self.assertEqual(find_named_process_pids(p,EXE_NAME),(10,20))
        self.assertEqual(p.calls,1)

    def test_process_exe_case_insensitive_not_prefix_or_spacing_normalized(self):
        p=Processes(ProcessRecord(10,EXE_NAME.upper()),
                    ProcessRecord(20,"Thần Long Mobile.exe"),
                    ProcessRecord(30,"Thần Long  Mobile.exe.config"))
        self.assertEqual(find_named_process_pids(p,EXE_NAME),(10,))

    def test_bad_process_name_rejected(self):
        p=Processes()
        for name in ("",None,"C:/Windows/python.exe",r"C:\\python.exe"):
            with self.subTest(name=name),self.assertRaises(ValueError):
                find_named_process_pids(p,name)
        self.assertEqual(p.calls,0)

    def test_malformed_process_entry_refuses_count(self):
        for bad in ("hello",ProcessRecord("33",EXE_NAME),
                    ProcessRecord(42,None)):
            evidence=observe_running_game_evidence(
                processes=Processes(bad),windows=Windows())
            self.assertFalse(evidence.process_scan_valid)
            self.assertIsNone(evidence.game_process_count)
            self.assertTrue(evidence.window_scan_valid)

    def test_valid_no_processes_not_total_zero(self):
        e=observe_running_game_evidence(processes=Processes(),windows=Windows())
        self.assertEqual((e.game_process_count,e.visible_hwnd_count),(0,0))
        self.assertIsNone(e.combined_running_count)
        self.assertIsNone(e.emulator_process_count)
        self.assertFalse(e.is_authoritative_account_total)

    def test_two_game_windows_one_game_pid_one_game_process(self):
        p=Processes(ProcessRecord(23,EXE_NAME))
        w=Windows((100,23,True,EXE_NAME,"UnityWndClass","A"),
                  (101,23,True,EXE_NAME,"UnityWndClass","B"))
        e=observe_running_game_evidence(processes=p,windows=w)
        self.assertEqual(e.game_process_count,1)
        self.assertEqual(e.visible_hwnd_count,2)
        self.assertEqual(e.visible_game_pid_count,1)
        self.assertEqual(e.game_process_pids,(23,))
        self.assertIsNone(e.combined_running_count)

    def test_invisible_game_process_still_process_counted(self):
        p=Processes(ProcessRecord(23,EXE_NAME))
        w=Windows((100,23,False,EXE_NAME,"UnityWndClass","A"))
        e=observe_running_game_evidence(processes=p,windows=w)
        self.assertEqual((e.game_process_count,e.visible_hwnd_count),(1,0))
        self.assertEqual(e.visible_game_pid_count,0)

    def test_no_invented_game_process_when_title_only_python(self):
        p=Processes(ProcessRecord(77,"python.exe"))
        w=Windows((100,77,True,"python.exe","UnityWndClass","Thần Long  Mobile"))
        e=observe_running_game_evidence(processes=p,windows=w)
        self.assertEqual((e.game_process_count,e.visible_hwnd_count),(0,0))

    def test_window_scan_failure_never_becomes_valid_zero(self):
        p=Processes(ProcessRecord(23,EXE_NAME))
        w=Windows(error=OSError("NO_ENUM"))
        e=observe_running_game_evidence(processes=p,windows=w)
        self.assertTrue(e.process_scan_valid)
        self.assertEqual(e.game_process_count,1)
        self.assertFalse(e.window_scan_valid)
        self.assertIsNone(e.visible_hwnd_count)
        self.assertEqual(e.window_error,"OSError")

    def test_process_scan_failure_never_becomes_valid_zero(self):
        p=Processes(error=OSError("TOOLHELP_FAIL"))
        w=Windows((100,23,True,EXE_NAME,"UnityWndClass","A"))
        e=observe_running_game_evidence(processes=p,windows=w)
        self.assertFalse(e.process_scan_valid)
        self.assertIsNone(e.game_process_count)
        self.assertEqual(e.visible_hwnd_count,1)
        self.assertEqual(e.process_error,"OSError")

    def test_both_failed_still_incomplete(self):
        e=observe_running_game_evidence(
            processes=Processes(error=RuntimeError("F")),
            windows=Windows(error=RuntimeError("W")))
        self.assertIsNone(e.game_process_count)
        self.assertIsNone(e.visible_hwnd_count)
        self.assertIsNone(e.combined_running_count)

    def test_unrelated_windows_rejected_and_no_other_pid_leak(self):
        p=Processes(ProcessRecord(10,EXE_NAME))
        w=Windows((200,10,True,EXE_NAME,"UnityWndClass","TL"),
                  (300,90,True,"python.exe","UnityWndClass","TL"))
        e=observe_running_game_evidence(processes=p,windows=w)
        self.assertEqual([(a.hwnd,a.pid) for a in e.game_windows],[(200,10)])

    def test_hwnd_scan_is_not_a_game_claim(self):
        w=Windows((101,50,True,"python.exe","Generic","S29 TEST"),
                  (102,50,True,"python.exe","Generic","Thần Long"),
                  (103,50,False,"python.exe","Generic","hidden"),
                  (104,55,True,"python.exe","Generic","foreign"))
        self.assertEqual(visible_hwnds_for_pid(w,50),(101,102))
        self.assertEqual(visible_hwnds_for_pid(w,55),(104,))
        self.assertEqual(visible_hwnds_for_pid(w,999),())

    def test_duplicate_or_gone_hwnd_safely_ignored(self):
        w=Windows((11,50,True,"python.exe","Generic","S29"))
        w.order=[11,11,777]
        self.assertEqual(visible_hwnds_for_pid(w,50),(11,))

    def test_invalid_pid_for_window_probe_fails_closed(self):
        w=Windows((11,50,True,"python.exe","Generic","S29"))
        for pid in (None,0,-1,True,"50"):
            self.assertEqual(visible_hwnds_for_pid(w,pid),())

    def test_cannot_pass_partial_count_to_s26_launch_guard(self):
        e=observe_running_game_evidence(
            processes=Processes(ProcessRecord(10,EXE_NAME)),windows=Windows())
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/EXE_NAME
            path.write_bytes(b"S29 TEST OWNED PLACEHOLDER")
            game=GameDirectoryResult(Path(td),"")
            for count in (e.combined_running_count,e):
                with self.subTest(count=count):
                    check=check_open_game_preflight(claims(),game,running_windows=count)
                    self.assertFalse(check.allowed)
                    self.assertEqual(check.reason,"RUNNING_WINDOW_COUNT_UNKNOWN")

    def test_cannot_infer_running_total_even_with_two_good_scans(self):
        e=observe_running_game_evidence(
            processes=Processes(ProcessRecord(10,EXE_NAME)),
            windows=Windows((11,10,True,EXE_NAME,"UnityWndClass","S29")))
        self.assertTrue(e.process_scan_valid and e.window_scan_valid)
        self.assertFalse(e.is_authoritative_account_total)
        self.assertIsNone(e.combined_running_count)

    def test_native_requires_windows(self):
        if os.name!="nt":
            with self.assertRaises(OSError):NativeWin32ProcessBackend()
        else:
            self.assertIsInstance(NativeWin32ProcessBackend(),NativeWin32ProcessBackend)


if __name__=="__main__":
    unittest.main()
