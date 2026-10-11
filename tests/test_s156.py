"""S156 original F05 PID-bound main HWND chooser source-backed regressions.

All source candidates are injected test-only records. One distinct Win64
smoke exercises the existing actual Windows EnumWindows/Win32 API.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from login_pid_window import find_main_window_by_pid, ORIGINAL_GAME_TITLE_TOKEN
from start_windows import TITLE_TIMEOUT_MS, UNITY_WINDOW_CLASS


class Fake:
    def __init__(self):
        self.handles=[10,20,30,40]
        self.alive={10,20,30,40}
        self.visible={10,20,30,40}
        self.pids={10:101,20:101,30:101,40:999}
        self.classes={10:"MiscWnd",20:"MiscWnd",30:UNITY_WINDOW_CLASS,40:UNITY_WINDOW_CLASS}
        self.titles={10:"Launcher",20:"Thần Long  Mobile",30:"RoleOne",40:"Thần Long  Mobile"}
        self.title_calls=[]
        self.reuse_at_title={}
        self.kill_at_title=set()
        self.throw_title=set()

    def enumerate_top_level(self):
        return tuple(self.handles)
    def is_window(self,hwnd):
        return hwnd in self.alive
    def is_visible(self,hwnd):
        return hwnd in self.visible
    def process_id(self,hwnd):
        return self.pids.get(hwnd,0)
    def window_class(self,hwnd):
        return self.classes.get(hwnd,"")
    def title_with_timeout(self,hwnd,ms):
        self.title_calls.append((hwnd,ms))
        if hwnd in self.kill_at_title:self.alive.discard(hwnd)
        if hwnd in self.reuse_at_title:self.pids[hwnd]=self.reuse_at_title[hwnd]
        if hwnd in self.throw_title:raise OSError("HUNG_TITLE")
        return self.titles.get(hwnd,"")


class S156F05PidMainHwnd(unittest.TestCase):
    def test_01_original_unity_class_preferred_over_title_and_fallback(self):
        self.assertEqual(find_main_window_by_pid(101,Fake()),30)

    def test_02_original_game_title_preferred_over_launcher(self):
        b=Fake();b.classes[30]="Other"
        self.assertEqual(find_main_window_by_pid(101,b),20)

    def test_03_casefolded_vietnamese_game_title_matches(self):
        b=Fake();b.classes[30]="Other";b.titles[20]="THẦN LONG MOBILE"
        self.assertEqual(find_main_window_by_pid(101,b),20)

    def test_04_first_visible_same_PID_fallback_not_other_pid(self):
        b=Fake();b.classes[30]="Other";b.titles[20]="Other"
        self.assertEqual(find_main_window_by_pid(101,b),10)

    def test_05_only_other_pid_windows_returns_none(self):
        b=Fake();b.pids={h:999 for h in b.handles}
        self.assertIsNone(find_main_window_by_pid(101,b))
        self.assertEqual(b.title_calls,[])

    def test_06_invisible_or_destroyed_windows_not_candidates(self):
        b=Fake();b.visible.discard(30);b.alive.discard(20)
        self.assertEqual(find_main_window_by_pid(101,b),10)
        self.assertEqual(b.title_calls,[(10,TITLE_TIMEOUT_MS)])

    def test_07_PID_generation_reuse_during_title_rejected(self):
        b=Fake();b.reuse_at_title[30]=555;b.reuse_at_title[20]=777
        self.assertEqual(find_main_window_by_pid(101,b),10)

    def test_08_closed_during_title_not_accepted(self):
        b=Fake();b.kill_at_title.add(30)
        self.assertEqual(find_main_window_by_pid(101,b),20)

    def test_09_hung_window_not_selected_and_does_not_block_fallback(self):
        b=Fake();b.throw_title.add(30)
        self.assertEqual(find_main_window_by_pid(101,b),20)

    def test_10_invalid_PID_types_refuse_before_WinAPI(self):
        for v in (0,-1,False,True,1.0,"101",None,0x100000000):
            with self.subTest(value=v):
                self.assertIsNone(find_main_window_by_pid(v,Fake()))

    def test_11_empty_duplicate_nonint_and_bad_handles_never_crash(self):
        b=Fake();b.handles=[None,"20",-4,0,20,20,30,30]
        self.assertEqual(find_main_window_by_pid(101,b),30)
        self.assertEqual(b.title_calls,[(20,TITLE_TIMEOUT_MS),(30,TITLE_TIMEOUT_MS)])

    def test_12_final_PID_recheck_rejects_removed_preferred(self):
        b=Fake();old=b.process_id
        def check(hwnd):
            if hwnd==30 and b.title_calls.count((30,TITLE_TIMEOUT_MS))>0:
                # Reused immediately after original enumeration
                b.pids[30]=900
            return old(hwnd)
        b.process_id=check
        self.assertEqual(find_main_window_by_pid(101,b),20)

    def test_13_exact_original_title_token_and_shared_150ms_safe_WinAPI(self):
        self.assertEqual(ORIGINAL_GAME_TITLE_TOKEN,"Thần Long")
        b=Fake()
        find_main_window_by_pid(101,b)
        self.assertTrue(all(ms==150 for _,ms in b.title_calls))

    def test_14_no_launcher_injection_auth_bypass_or_game_memory(self):
        src=(ROOT/"src/login_pid_window.py").read_text("utf-8")
        for forbidden in ("CreateRemoteThread(", "LoadLibraryW(", "Popen(",
                          "ReadProcessMemory(", "WriteProcessMemory(",
                          "PostMessage(", "TLM_PROXY_", "has_permission = True",
                          "os.kill(", "Game.RoleData"):
            self.assertNotIn(forbidden,src)
        self.assertIn("backend.process_id(hwnd) == pid",src)

    def test_15_only_read_only_top_level_Win32_methods_in_contract(self):
        b=Fake()
        self.assertEqual(find_main_window_by_pid(101,b),30)
        self.assertTrue(all(h!=40 for h,_ in b.title_calls))


if __name__=="__main__":
    unittest.main()
