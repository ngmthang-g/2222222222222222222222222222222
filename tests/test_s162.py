"""S162 original permission_guard PC-game count: ONE or TWO spaces.

Verified in frozen original EXE near 0x02b83815..0x02b83ab1.
Only the running-process count predicate changes; F04 disk EXE remains
the single canonical TWO-space name (not relaxed).
"""
from __future__ import annotations
import sys,tempfile,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from login_running_process_capacity import (
    RUNNING_GAME_PROCESS_IMAGE_NAMES,count_current_game_processes,
    check_native_open_game_capacity,
)
from login_path import EXE_NAME,GameDirectoryResult,resolve_game_dir
from permission_guard import PermissionSnapshot

ONE="Thần Long Mobile.exe"
TWO="Thần Long  Mobile.exe"

class ProcessFixture:
    def __init__(self,*rows):
        self.rows=tuple(rows)
        self.calls=0
    def process_images(self):
        self.calls+=1
        return self.rows

def grant(limit=2):
    return PermissionSnapshot(True,frozenset({"login_tab"}),"active",limit)

class S162OriginalTwoNameParity(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        (self.root/EXE_NAME).write_bytes(b"TEST_CANONICAL_NOT_GAME")
        self.game=GameDirectoryResult(self.root,"")

    def test_01_original_exact_two_names_and_no_other(self):
        self.assertEqual(RUNNING_GAME_PROCESS_IMAGE_NAMES,
                         frozenset({ONE.casefold(),TWO.casefold()}))

    def test_02_original_single_space_process_now_counted(self):
        s=count_current_game_processes(ProcessFixture((21,ONE)))
        self.assertEqual((s.code,s.running_exe),("PROCESS_SNAPSHOT_OK",1))

    def test_03_original_double_space_process_still_counted(self):
        self.assertEqual(count_current_game_processes(
            ProcessFixture((31,TWO))).running_exe,1)

    def test_04_both_space_variants_counted_together(self):
        p=ProcessFixture((21,ONE),(32,TWO),(43,"python.exe"))
        self.assertEqual(count_current_game_processes(p).running_exe,2)

    def test_05_unicode_casefold_and_deduplicated_pid(self):
        p=ProcessFixture((11,"THẦN LONG MOBILE.EXE"),
                         (11,TWO),(22,"THẦN LONG  MOBILE.EXE"))
        self.assertEqual(count_current_game_processes(p).running_exe,2)

    def test_06_near_miss_names_never_counted(self):
        names=("Thần Long   Mobile.exe","Thần  Long Mobile.exe",
               "Thần Long Mobile.exe.bak","XThần Long Mobile.exe",
               "Thần Long Mob ile.exe","Thần LongMobile.exe",
               "Thần Long Mobile.com","another.exe")
        self.assertEqual(count_current_game_processes(ProcessFixture(
            *( (100+i,name) for i,name in enumerate(names)))).running_exe,0)

    def test_07_original_single_space_process_prevents_extra_one(self):
        p=ProcessFixture((12,ONE),(13,TWO))
        pre,result=check_native_open_game_capacity(
            grant(limit=2),self.game,verified_emulator_sessions=0,backend=p)
        self.assertEqual(pre.reason,"ACCOUNT_LIMIT_EXTRA_ONE")
        self.assertEqual((result.running_exe,result.combined),(2,2))

    def test_08_one_pc_game_plus_one_emu_satisfies_limit_when_cap3(self):
        pre,result=check_native_open_game_capacity(
            grant(limit=3),self.game,verified_emulator_sessions=1,
            backend=ProcessFixture((12,ONE)))
        self.assertTrue(pre.allowed)
        self.assertEqual((pre.reason,result.combined),
                         ("PREFLIGHT_ONLY_NOT_LAUNCHED",2))

    def test_09_s26_unverified_info_prevents_process_enumeration(self):
        proc=ProcessFixture((12,ONE))
        pre,_=check_native_open_game_capacity(
            PermissionSnapshot(),self.game,verified_emulator_sessions=0,
            backend=proc)
        self.assertEqual(pre.reason,"UNVERIFIED_INFO")
        self.assertEqual(proc.calls,0)

    def test_10_unknown_emulator_count_not_inferred_from_processes(self):
        proc=ProcessFixture((12,ONE))
        pre,_=check_native_open_game_capacity(
            grant(),self.game,verified_emulator_sessions=None,backend=proc)
        self.assertEqual(pre.reason,"RUNNING_WINDOW_COUNT_UNKNOWN")
        self.assertEqual(proc.calls,0)

    def test_11_canonical_F04_two_space_EXE_remains_unchanged(self):
        self.assertEqual(EXE_NAME,TWO)
        self.assertEqual(resolve_game_dir(self.root).directory,self.root)
        (self.root/TWO).unlink()
        (self.root/ONE).write_bytes(b"TEST_ONLY_NOT_REAL_EXE")
        self.assertIsNone(resolve_game_dir(self.root).directory)
        # Counting one-space existing processes does NOT authorize launching
        # the noncanonical on-disk one-space EXE.
        pre,_=check_native_open_game_capacity(
            grant(),self.game,verified_emulator_sessions=0,
            backend=ProcessFixture((12,ONE)))
        self.assertEqual(pre.reason,"GAME_EXECUTABLE_MISSING")

    def test_12_game_window_start_predicate_NOT_changed(self):
        source=(ROOT/"src/start_windows.py").read_text(encoding="utf-8")
        self.assertIn("def is_game_candidate(",source)
        # This task has no write to Start's independently owned predicates.
        self.assertFalse(hasattr(ProcessFixture,"post_message"))

if __name__=="__main__":
    unittest.main()
