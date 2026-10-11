"""S161 E04/F05 source-backed per-serial ADB pidof emulator game count."""
from __future__ import annotations
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from login_emulator_game_capacity import (
    ORIGINAL_ANDROID_GAME_PACKAGE,ORIGINAL_EMU_COUNT_METHOD,
    ORIGINAL_EMU_COUNT_RULE,ADB_TRANSPORT_PARITY,AdbCommandRunner,
    count_adb_emulator_games,check_open_game_with_adb_process_count,
)
from login_path import GameDirectoryResult,EXE_NAME
from permission_guard import PermissionSnapshot


DEVICES="List of devices attached\nemulator-5554\tdevice product:LDPlayer model:TEST\nemulator-5556\tdevice\n\n"
class AdbFake:
    def __init__(self):
        self.calls=[]
        self.devices=DEVICES
        self.present={"emulator-5554":"123 124","emulator-5556":None}
        self.override={}
    def __call__(self,args):
        args=tuple(args)
        self.calls.append(args)
        if args in self.override:return self.override[args]
        if args==("devices","-l"):return (0,self.devices,"")
        if (len(args)==5 and args[0]=="-s" and args[2:]==(
            "shell","pidof",ORIGINAL_ANDROID_GAME_PACKAGE)):
            result=self.present.get(args[1])
            return (0,result+"\n","") if result is not None else (1,"","")
        raise AssertionError(f"unexpected TEST_ONLY ADB command {args}")

class WindowsBackend:
    def __init__(self,rows=()):self.rows=rows;self.calls=0
    def process_images(self):self.calls+=1;return self.rows

def info(limit=5):
    return PermissionSnapshot(True,frozenset({"login_tab"}),"active",limit)


class S161PerSerialPidof(unittest.TestCase):
    def setUp(self):
        from tempfile import TemporaryDirectory
        tmp=TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        directory=Path(tmp.name)
        (directory/EXE_NAME).write_bytes(b"NOT_A_GAME_TEST_ONLY")
        self.game=GameDirectoryResult(directory,"")

    def test_01_original_binary_proven_api_rule_and_game_package(self):
        self.assertEqual(ORIGINAL_ANDROID_GAME_PACKAGE,"com.fgstudio.thanlongmobile")
        self.assertEqual(ORIGINAL_EMU_COUNT_METHOD,"emu_reader.emu_game_count")
        self.assertEqual(ORIGINAL_EMU_COUNT_RULE,"ONE_RUNNING_GAME_VM_COUNTS_AS_ONE_WINDOW")
        self.assertIn("UNKNOWN",ADB_TRANSPORT_PARITY)

    def test_02_two_pids_within_same_emulator_count_once(self):
        a=AdbFake()
        got=count_adb_emulator_games(a)
        self.assertEqual(got.code,"ADB_GAME_PIDOF_CONFIRMED")
        self.assertEqual(got.count,1)
        self.assertEqual(got.game_serials,("emulator-5554",))
        self.assertEqual(len(a.calls),4)

    def test_03_two_emulator_serials_with_game_count_two(self):
        a=AdbFake();a.present["emulator-5556"]="92"
        self.assertEqual(count_adb_emulator_games(a).count,2)

    def test_04_authorized_empty_device_listing_returns_grounded_zero(self):
        a=AdbFake();a.devices="List of devices attached\n\n"
        x=count_adb_emulator_games(a)
        self.assertEqual(x.code,"ADB_GAME_PIDOF_CONFIRMED")
        self.assertEqual(x.count,0)

    def test_05_unknown_provider_not_assumed_zero(self):
        x=count_adb_emulator_games(None)
        self.assertEqual(x.code,"ADB_PROVIDER_NOT_CONFIGURED")
        self.assertIsNone(x.count)

    def test_06_offline_unauthorized_duplicate_or_broken_device_fails_closed(self):
        for value in (
          "List of devices attached\nemulator-5554\toffline\n",
          "List of devices attached\nemulator-5554\tunauthorized\n",
          "List of devices attached\nemulator-5554\tdevice\nemulator-5554\tdevice\n",
          "emulator-5554\tdevice\n",
          "List of devices attached\nevil id\tdevice\n",
          "List of devices attached\nemulator-5554\t???\n",
        ):
            a=AdbFake();a.devices=value
            self.assertEqual(count_adb_emulator_games(a).code,
                             "ADB_FLEET_UNVERIFIED")

    def test_07_pidof_non_numeric_or_nonzero_error_fails_closed(self):
        cmd=("-s","emulator-5554","shell","pidof",ORIGINAL_ANDROID_GAME_PACKAGE)
        for data in ((0,"NaN\n",""),(0,"",""),(1,"999\n",""),
                     (2,"","error"),(1,"","device offline"),
                     (0,"0",""),(0,"-8","")):
            a=AdbFake();a.override[cmd]=data
            self.assertEqual(count_adb_emulator_games(a).code,
                             "ADB_PIDOF_UNVERIFIED")

    def test_08_fleet_changed_after_sample_cannot_grant_capacity(self):
        a=AdbFake();initial=[0]
        def unstable(args):
            if tuple(args)==("devices","-l"):
                initial[0]+=1
                if initial[0]>1:
                    return (0,DEVICES.replace("emulator-5556","emulator-5558"),"")
            return a(args)
        x=count_adb_emulator_games(unstable)
        self.assertEqual(x.code,"ADB_FLEET_CHANGED")

    def test_09_adb_timeout_or_exception_never_assumed_zero(self):
        def fails(_):raise OSError("TEST_READ_FAIL")
        self.assertEqual(count_adb_emulator_games(fails).code,"ADB_READ_FAILED")

    def test_10_signed_Info_denied_before_adb_and_windows_scan(self):
        a=AdbFake();b=WindowsBackend()
        pre,emu=check_open_game_with_adb_process_count(
            PermissionSnapshot(),self.game,adb_run=a,windows_backend=b)
        self.assertEqual(pre.reason,"UNVERIFIED_INFO")
        self.assertEqual(emu.code,"INFO_OR_PLAN_DENIED")
        self.assertEqual(a.calls,[])
        self.assertEqual(b.calls,0)

    def test_11_real_capacity_inherited_from_s160_s26_no_new_formula(self):
        a=AdbFake();a.present["emulator-5556"]="44"
        b=WindowsBackend(((888,EXE_NAME),))
        pre,emu=check_open_game_with_adb_process_count(
            info(limit=3),self.game,adb_run=a,windows_backend=b)
        self.assertEqual(emu.count,2)
        self.assertEqual(pre.reason,"ACCOUNT_LIMIT_EXTRA_ONE")
        self.assertEqual(b.calls,1)

    def test_12_combined_windows_one_emulator_one_plus_one_at_limit_three(self):
        a=AdbFake()
        b=WindowsBackend(((888,EXE_NAME),))
        pre,emu=check_open_game_with_adb_process_count(
            info(limit=3),self.game,adb_run=a,windows_backend=b)
        self.assertEqual(emu.count,1)
        self.assertEqual(pre.reason,"PREFLIGHT_ONLY_NOT_LAUNCHED")
        self.assertTrue(pre.allowed)
        self.assertEqual(pre.running,2)

    def test_13_unknown_adb_status_never_reaches_S26_as_fake_zero(self):
        a=AdbFake()
        a.devices="bad ADB reply"
        b=WindowsBackend()
        pre,emu=check_open_game_with_adb_process_count(
            info(),self.game,adb_run=a,windows_backend=b)
        self.assertEqual(emu.code,"ADB_FLEET_UNVERIFIED")
        self.assertEqual(pre.reason,"RUNNING_WINDOW_COUNT_UNKNOWN")
        self.assertEqual(b.calls,0)

    def test_14_game_exe_selected_still_required_by_original_s26(self):
        a=AdbFake()
        pre,emu=check_open_game_with_adb_process_count(
            info(),GameDirectoryResult(None,""),adb_run=a,
            windows_backend=WindowsBackend())
        self.assertEqual(pre.reason,"GAME_DIRECTORY_NOT_SELECTED")
        self.assertEqual(emu.count,1)

    def test_15_client_does_not_guess_adb_path(self):
        with self.assertRaises((ValueError,TypeError)):
            AdbCommandRunner("./adb.exe")

    def test_16_no_frida_proxy_game_mutation_or_local_auth_issuer(self):
        source=(ROOT/"src/login_emulator_game_capacity.py").read_text("utf-8")
        for fragment in ("shell=True","CREATE_SUSPENDED","CreateRemoteThread(",
                         "SendInput(","TLM_PROXY_","frida.attach(",
                         "grant_permission(","adb connect","input tap"):
            self.assertNotIn(fragment,source)
        self.assertIn('"pidof",ORIGINAL_ANDROID_GAME_PACKAGE',source)

    def test_17_no_login_or_emulator_provider_autowiring(self):
        from source_backed_tab_builders import source_backed_tab_builders
        self.assertTrue(callable(source_backed_tab_builders))
        self.assertEqual(count_adb_emulator_games(None).code,
                         "ADB_PROVIDER_NOT_CONFIGURED")

if __name__=="__main__":unittest.main()
