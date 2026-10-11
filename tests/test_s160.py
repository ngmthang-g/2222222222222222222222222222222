"""S160: real game EXE count from process snapshot + original S26 F05 guard.

Mocks only the *backend process listing*, never a permission issuer.
Actual Windows Toolhelp native proof lives in S160 smoke.
"""
from __future__ import annotations
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from login_running_process_capacity import (
    PROCESS_SNAPSHOT_KIND, NativeWindowsProcessImages,
    count_current_game_processes, check_native_open_game_capacity,
)
from login_path import EXE_NAME, GameDirectoryResult
from permission_guard import PermissionSnapshot


class Proc:
    def __init__(self,*rows):self.rows=tuple(rows);self.calls=0
    def process_images(self):self.calls+=1;return self.rows


def test_snapshot(limit=2,active=True):
    return PermissionSnapshot(
        has_verified_payload=active,
        permissions=frozenset({"login_tab"}),
        plan_status="active",max_windows=limit)


class S160F05ActualProcessCap(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        folder=Path(self.tmp.name)
        (folder/EXE_NAME).write_bytes(b"TEST_ONLY_NOT_EXECUTABLE")
        self.game=GameDirectoryResult(folder,"")

    def test_01_original_exact_image_and_new_external_count_not_HWND(self):
        self.assertEqual(EXE_NAME,"Thần Long  Mobile.exe")
        self.assertIn("LOCAL_WIN32",PROCESS_SNAPSHOT_KIND)

    def test_02_distinct_PID_images_count_even_without_any_HWND(self):
        p=Proc((11,EXE_NAME),(22,EXE_NAME),(11,EXE_NAME),
               (99,"python.exe"))
        n=count_current_game_processes(p)
        self.assertEqual((n.code,n.running_exe),("PROCESS_SNAPSHOT_OK",2))

    def test_03_windows_unicode_casefold_exact_filename_only(self):
        p=Proc((11,"THẦN LONG  MOBILE.EXE"),(12,"Thần Long Mobile.exe"),
               (13,EXE_NAME))
        self.assertEqual(count_current_game_processes(p).running_exe,2)

    def test_04_combined_running_Exe_plus_emulator_and_extra_one_blocks(self):
        p=Proc((1,EXE_NAME),(2,EXE_NAME))
        pre,count=check_native_open_game_capacity(test_snapshot(limit=3),
            self.game,verified_emulator_sessions=1,backend=p)
        self.assertEqual(pre.reason,"ACCOUNT_LIMIT_EXTRA_ONE")
        self.assertEqual((count.running_exe,count.running_emulators,count.combined),
                         (2,1,3))
        self.assertEqual(p.calls,1)

    def test_05_exact_boundary_count_plus_one_allowed_but_NO_LAUNCH(self):
        p=Proc((11,EXE_NAME),(44,"random.exe"))
        pre,n=check_native_open_game_capacity(test_snapshot(limit=3),
            self.game,verified_emulator_sessions=1,backend=p)
        self.assertTrue(pre.allowed)
        self.assertEqual(pre.reason,"PREFLIGHT_ONLY_NOT_LAUNCHED")
        self.assertEqual((pre.running,n.combined),(2,2))
        self.assertTrue(pre.executable.is_file())

    def test_06_unknown_emulator_count_never_assumed_zero(self):
        p=Proc()
        for count in (None,False,0.0,"0",-1):
            with self.subTest(count=count):
                pre,result=check_native_open_game_capacity(
                    test_snapshot(),self.game,
                    verified_emulator_sessions=count,backend=p)
                self.assertEqual(pre.reason,"RUNNING_WINDOW_COUNT_UNKNOWN")
                self.assertEqual(result.code,"EMULATOR_SESSIONS_UNVERIFIED")
        self.assertEqual(p.calls,0)

    def test_07_no_signed_Info_never_enumerates_native_processes(self):
        p=Proc((22,EXE_NAME))
        pre,result=check_native_open_game_capacity(
            PermissionSnapshot(),self.game,verified_emulator_sessions=0,backend=p)
        self.assertFalse(pre.allowed)
        self.assertEqual(pre.reason,"UNVERIFIED_INFO")
        self.assertEqual(result.code,"NOT_AUTHORIZED_OR_INVALID_LIMIT")
        self.assertEqual(p.calls,0)

    def test_08_blocked_plan_and_no_login_permission_never_enumerate(self):
        p=Proc((22,EXE_NAME))
        for snap in (
                PermissionSnapshot(True,frozenset({"login_tab"}),"banned",2),
                PermissionSnapshot(True,frozenset({"start_tab"}),"active",2),
                test_snapshot(limit=0)):
            pre,result=check_native_open_game_capacity(
                snap,self.game,verified_emulator_sessions=0,backend=p)
            self.assertFalse(pre.allowed)
            self.assertEqual(result.code,"NOT_AUTHORIZED_OR_INVALID_LIMIT")
        self.assertEqual(p.calls,0)

    def test_09_unknown_or_broken_native_process_scan_fails_closed(self):
        class Broken:
            def process_images(self):raise OSError("TEST_ONLY_FAILED_WIN32")
        pre,n=check_native_open_game_capacity(test_snapshot(),self.game,
                verified_emulator_sessions=0,backend=Broken())
        self.assertEqual(pre.reason,"RUNNING_WINDOW_COUNT_UNKNOWN")
        self.assertEqual(n.code,"PROCESS_SNAPSHOT_UNAVAILABLE")

    def test_10_malformed_process_snapshot_cannot_under_count(self):
        for proc in (Proc((0,EXE_NAME)),Proc((-1,EXE_NAME)),
                     Proc(("11",EXE_NAME)),Proc((1,None))):
            self.assertEqual(count_current_game_processes(proc).code,
                             "UNVERIFIED_PROCESS_SNAPSHOT")

    def test_11_exe_removed_after_config_accepted_blocks_real_preflight(self):
        (self.game.directory/EXE_NAME).unlink()
        pre,n=check_native_open_game_capacity(test_snapshot(),self.game,
                   verified_emulator_sessions=0,backend=Proc())
        self.assertEqual(pre.reason,"GAME_EXECUTABLE_MISSING")
        self.assertEqual(n.combined,0)

    def test_12_game_dir_unselected_blocks_after_count(self):
        pre,n=check_native_open_game_capacity(test_snapshot(),GameDirectoryResult(None,""),
                   verified_emulator_sessions=0,backend=Proc())
        self.assertEqual(pre.reason,"GAME_DIRECTORY_NOT_SELECTED")
        self.assertEqual(n.combined,0)

    def test_13_no_exe_launch_hidden_click_inject_proxy_or_mutation(self):
        source=(ROOT/"src/login_running_process_capacity.py").read_text("utf-8")
        for forbidden in ("subprocess.Popen(","CreateRemoteThread(","TerminateProcess(",
                          "ReadProcessMemory(","SetWindowPos(","TLM_PROXY_HOST",
                          "SendInput(","os.system("):
            self.assertNotIn(forbidden,source)
        self.assertIn("check_open_game_preflight(",source)

    def test_14_exact_S26_existing_guard_not_duplicated(self):
        from login_launch_preflight import check_open_game_preflight
        f=check_open_game_preflight(test_snapshot(limit=1),self.game,running_windows=1)
        self.assertEqual(f.reason,"ACCOUNT_LIMIT_EXTRA_ONE")

if __name__=="__main__":
    unittest.main()
