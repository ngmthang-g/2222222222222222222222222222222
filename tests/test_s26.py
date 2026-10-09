"""S26 F05 original-evidenced preflight + PID-owned HWND selection only."""
from __future__ import annotations
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"src"))

from login_launch_preflight import check_open_game_preflight, find_main_window_by_pid
from login_path import GameDirectoryResult, EXE_NAME
from permission_guard import PermissionSnapshot
from start_windows import TITLE_TIMEOUT_MS, UNITY_WINDOW_CLASS


class WindowsFixture:
    def __init__(self, windows=()):
        # (hwnd, pid, is_visible, class_name, title)
        self.windows={w[0]:w for w in windows}
        self.order=[w[0] for w in windows]
        self.calls=[]
        self.swaps={}
        self.pid_reads={}
    def enumerate_top_level(self):return self.order
    def is_window(self,h):return h in self.windows
    def is_visible(self,h):return self.windows[h][2]
    def window_class(self,h):return self.windows[h][3]
    def title_with_timeout(self,h,t):
        self.calls.append((h,t))
        if h in self.swaps:
            w=self.windows[h]
            self.windows[h]=(w[0],self.swaps[h],w[2],w[3],w[4])
        return self.windows[h][4]
    def process_id(self,h):return self.windows[h][1]


def claims(*, permissions=frozenset({"login_tab"}),limit=3,blocked=False,verified=True):
    return PermissionSnapshot(
        has_verified_payload=verified,permissions=frozenset(permissions),
        plan_status="TEST_ONLY",max_windows=limit,server_locked=blocked)


class S26Tests(unittest.TestCase):
    def with_game(self):
        return tempfile.TemporaryDirectory(prefix="S26_TEST_ONLY_")

    def result(self,directory):
        d=Path(directory);d.mkdir(parents=True,exist_ok=True)
        (d/EXE_NAME).write_bytes(b"S26 TEST OWNED NOT EXECUTABLE")
        return GameDirectoryResult(d,"")

    def test_unverified_token_fail_closed(self):
        with self.with_game() as td:
            game=self.result(td)
            self.assertEqual(check_open_game_preflight(
                PermissionSnapshot(),game,running_windows=0).reason,"UNVERIFIED_INFO")
            self.assertFalse(check_open_game_preflight(
                claims(verified=False),game,running_windows=0).allowed)

    def test_blocked_or_missing_login_rights(self):
        with self.with_game() as td:
            game=self.result(td)
            for snap in (claims(blocked=True),claims(permissions={"start_tab"})):
                answer=check_open_game_preflight(snap,game,running_windows=0)
                self.assertFalse(answer.allowed)
                self.assertEqual(answer.reason,"NO_LOGIN_PERMISSION")

    def test_running_count_unknown_or_invalid_rejected(self):
        with self.with_game() as td:
            game=self.result(td)
            for count in (None,-1,True,0.3,"0"):
                r=check_open_game_preflight(claims(),game,running_windows=count)
                self.assertFalse(r.allowed)
                self.assertEqual(r.reason,"RUNNING_WINDOW_COUNT_UNKNOWN")

    def test_limit_exact_extra_one(self):
        with self.with_game() as td:
            game=self.result(td)
            ok=check_open_game_preflight(claims(limit=3),game,running_windows=2)
            deny=check_open_game_preflight(claims(limit=3),game,running_windows=3)
            self.assertTrue(ok.allowed)
            self.assertEqual((ok.running,ok.max_windows),(2,3))
            self.assertEqual(ok.reason,"PREFLIGHT_ONLY_NOT_LAUNCHED")
            self.assertFalse(deny.allowed)
            self.assertEqual(deny.reason,"ACCOUNT_LIMIT_EXTRA_ONE")

    def test_invalid_limit_and_no_default_count(self):
        with self.with_game() as td:
            game=self.result(td)
            self.assertEqual(check_open_game_preflight(
                claims(limit=0),game,running_windows=0).reason,"INVALID_WINDOW_LIMIT")

    def test_missing_selection_and_missing_exe(self):
        with self.with_game() as td:
            bad=GameDirectoryResult(None,"")
            self.assertEqual(check_open_game_preflight(
                claims(),bad,running_windows=0).reason,"GAME_DIRECTORY_NOT_SELECTED")
            game=self.result(td)
            (game.directory/EXE_NAME).unlink()
            ans=check_open_game_preflight(claims(),game,running_windows=0)
            self.assertEqual(ans.reason,"GAME_EXECUTABLE_MISSING")
            self.assertIsNone(ans.executable)

    def test_directory_exe_revalidated(self):
        with self.with_game() as td:
            game=self.result(td)
            ans=check_open_game_preflight(claims(),game,running_windows=0)
            self.assertTrue(ans.allowed)
            self.assertEqual(ans.executable,Path(td)/EXE_NAME)
            self.assertEqual(ans.executable.name,"Thần Long  Mobile.exe")

    def test_reject_unknown_bad_snapshot(self):
        with self.with_game() as td:
            game=self.result(td)
            self.assertEqual(check_open_game_preflight(
                object(),game,running_windows=0).reason,"UNVERIFIED_INFO")

    def test_invalid_pid_never_enumerates(self):
        for pid in (None,0,-1,True,"1"):
            probe=WindowsFixture([(10,42,True,"UnityWndClass","Thần Long")])
            self.assertIsNone(find_main_window_by_pid(pid,probe))
            self.assertEqual(probe.calls,[])

    def test_find_pid_not_title_alone(self):
        probe=WindowsFixture([(101,123,True,UNITY_WINDOW_CLASS,"Thần Long"),
                              (102,123,True,"normal","Other")])
        self.assertIsNone(find_main_window_by_pid(456,probe))
        self.assertEqual(probe.calls,[])

    def test_prefer_unity_class_over_title_then_fallback(self):
        probe=WindowsFixture([
            (11,42,True,"Other","Ordinary"),
            (12,42,True,"Other","The Thần Long game"),
            (13,42,True,UNITY_WINDOW_CLASS,"Unnamed"),
        ])
        self.assertEqual(find_main_window_by_pid(42,probe),13)
        self.assertEqual(probe.calls,[(11,TITLE_TIMEOUT_MS),(12,TITLE_TIMEOUT_MS),
                                      (13,TITLE_TIMEOUT_MS)])

    def test_prefer_title_then_first_visible_fallback(self):
        probe=WindowsFixture([
            (11,42,True,"Other","Ordinary"),
            (12,42,True,"Other","The Thần Long game")])
        self.assertEqual(find_main_window_by_pid(42,probe),12)
        del probe.windows[12]
        self.assertEqual(find_main_window_by_pid(42,probe),11)

    def test_only_visible_pid_owned_candidates(self):
        probe=WindowsFixture([
            (1,99,True,UNITY_WINDOW_CLASS,"Thần Long"),
            (2,42,False,UNITY_WINDOW_CLASS,"Thần Long"),
            (3,42,True,"Generic","A Test")])
        self.assertEqual(find_main_window_by_pid(42,probe),3)
        self.assertEqual(probe.calls,[(3,TITLE_TIMEOUT_MS)])

    def test_reused_hwnd_during_get_title_rejected(self):
        probe=WindowsFixture([
            (11,42,True,UNITY_WINDOW_CLASS,"Thần Long"),
            (12,42,True,"Generic","Alternative")])
        probe.swaps[11]=999
        self.assertEqual(find_main_window_by_pid(42,probe),12)

    def test_final_identity_rechecked(self):
        class Mutating(WindowsFixture):
            def __init__(self):
                super().__init__([(11,42,True,UNITY_WINDOW_CLASS,"Thần Long"),
                                  (12,42,True,"Other","Other")])
                self.reads={11:0,12:0}
            def process_id(self,h):
                self.reads[h]+=1
                if h==11 and self.reads[h]>=3:return 111
                return super().process_id(h)
        probe=Mutating()
        self.assertEqual(find_main_window_by_pid(42,probe),12)

    def test_hidden_or_destroyed_hwnd_yields_none(self):
        probe=WindowsFixture([(3,42,False,"Foo","Bar")])
        self.assertIsNone(find_main_window_by_pid(42,probe))
        del probe.windows[3]
        self.assertIsNone(find_main_window_by_pid(42,probe))

    def test_unrelated_backend_raises_do_not_pick(self):
        class Failure(WindowsFixture):
            def window_class(self,h):
                raise OSError("TEST_ACCESS_DENIED")
        p=Failure([(1,42,True,"Other","Other")])
        self.assertIsNone(find_main_window_by_pid(42,p))


if __name__=="__main__":
    unittest.main()
