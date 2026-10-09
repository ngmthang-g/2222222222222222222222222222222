"""S08 test: real Start discovery algorithm without HWND fabrication in product."""
from __future__ import annotations

import os
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from start_windows import (
    GAME_PROCESS, GAME_TITLE, TITLE_TIMEOUT_MS, UNITY_WINDOW_CLASS,
    GameWindow, NativeWin32Backend, WindowRegistry, discover_game_windows,
    is_game_candidate,
)


class FakeBackend:
    def __init__(self):
        self.windows = [101, 102, 103, 104, 105]
        self.alive = {101, 102, 103, 104, 105}
        self.visible = {101, 102, 103, 104}
        self.pids = {101: 4101, 102: 4102, 103: 4103, 104: 4104, 105: 4105}
        self.names = {
            4101: r"C:\Games\Thần Long  Mobile.exe",
            4102: "other.exe",
            4103: "thần long mobile.exe",
            4104: "thần long mobile.exe",
            4105: "thần long mobile.exe",
        }
        self.classes = {101: "UnityWndClass", 102: "UnityWndClass",
                        103: "OtherClass", 104: "OtherClass", 105: "UnityWndClass"}
        self.titles = {101: "some account", 102: GAME_TITLE,
                       103: GAME_TITLE, 104: "Lineage W", 105: GAME_TITLE}
        self.title_calls = []
        self.fail_on_title = set()
        self.reuse_on_title = {}

    def enumerate_top_level(self):
        return tuple(self.windows)

    def is_visible(self, hwnd):
        return hwnd in self.visible

    def is_window(self, hwnd):
        return hwnd in self.alive

    def process_id(self, hwnd):
        return self.pids.get(hwnd, 0)

    def process_executable(self, pid):
        return self.names.get(pid, "")

    def window_class(self, hwnd):
        return self.classes.get(hwnd, "")

    def title_with_timeout(self, hwnd, ms):
        self.title_calls.append((hwnd, ms))
        if hwnd in self.fail_on_title:
            raise OSError("hung window")
        if hwnd in self.reuse_on_title:
            self.pids[hwnd] = self.reuse_on_title[hwnd]
        return self.titles.get(hwnd, "")


def gw(hwnd, pid):
    return GameWindow(hwnd, pid, "Thần Long Mobile", UNITY_WINDOW_CLASS, GAME_PROCESS)


class S08StartWindowTests(unittest.TestCase):
    def test_strict_class_or_title_always_requires_game_process(self):
        self.assertTrue(is_game_candidate(GAME_PROCESS, UNITY_WINDOW_CLASS, "Char"))
        self.assertTrue(is_game_candidate(r"C:\Games\Thần Long  Mobile.exe", "Other",
                                          "Thần Long Mobile"))
        self.assertFalse(is_game_candidate("other.exe", UNITY_WINDOW_CLASS, GAME_TITLE))
        self.assertFalse(is_game_candidate("other.exe", "Other", GAME_TITLE))
        self.assertFalse(is_game_candidate(GAME_PROCESS, "Other", "Lineage W"))

    def test_real_candidates_from_provider_only(self):
        api = FakeBackend()
        output = discover_game_windows(api)
        self.assertEqual([(x.hwnd, x.pid) for x in output], [(101, 4101), (103, 4103)])
        self.assertEqual(api.title_calls, [(101, TITLE_TIMEOUT_MS),
                                            (103, TITLE_TIMEOUT_MS),
                                            (104, TITLE_TIMEOUT_MS)])
        self.assertEqual(TITLE_TIMEOUT_MS, 150)

    def test_nonvisible_window_skipped(self):
        api = FakeBackend()
        api.visible.remove(101)
        result = discover_game_windows(api)
        self.assertEqual([x.hwnd for x in result], [103])
        self.assertNotIn((101, 150), api.title_calls)

    def test_no_synthetic_hwnd_or_default_first_window(self):
        api = FakeBackend()
        api.windows = [0, -1, 102, 102, 104]
        result = discover_game_windows(api)
        self.assertEqual(result, ())
        self.assertEqual(api.title_calls, [(104, 150)])

    def test_hung_game_title_is_excluded_not_propagated(self):
        api = FakeBackend()
        api.fail_on_title = {101}
        result = discover_game_windows(api)
        self.assertEqual([x.hwnd for x in result], [103])

    def test_hwnd_pid_reuse_during_read_is_rejected(self):
        api = FakeBackend()
        api.reuse_on_title[101] = 9999
        result = discover_game_windows(api)
        self.assertEqual([x.hwnd for x in result], [103])

    def test_closed_candidate_not_reintroduced(self):
        api = FakeBackend()
        api.alive.remove(101)
        self.assertEqual([x.hwnd for x in discover_game_windows(api)], [103])

    def test_missing_pid_or_unreadable_process_does_not_match(self):
        api = FakeBackend()
        api.pids[101] = 0
        api.names.pop(4103)
        self.assertEqual(discover_game_windows(api), ())

    def test_new_removed_and_reused_hwnd_are_distinct(self):
        model = WindowRegistry()
        old = gw(99, 111)
        add = model.update([old])
        self.assertEqual(add.added, (old,))
        self.assertEqual(add.removed, ())
        self.assertTrue(model.identity_matches(99, 111))
        same = model.update([old])
        self.assertEqual(same.added, ())
        self.assertEqual(same.reused, ())
        new = gw(99, 222)
        changed = model.update([new])
        self.assertEqual(changed.reused, ((old, new),))
        self.assertFalse(model.identity_matches(99, 111))
        self.assertTrue(model.identity_matches(99, 222))
        closed = model.update([])
        self.assertEqual(closed.removed, (new,))
        self.assertFalse(model.identity_matches(99, 222))

    def test_two_hwnds_keep_distinct_pid_identity(self):
        model = WindowRegistry()
        model.update([gw(11, 777), gw(12, 777)])
        self.assertEqual({w.hwnd for w in model.current}, {11, 12})
        self.assertTrue(model.identity_matches(11, 777))
        model.update([gw(12, 777)])
        self.assertFalse(model.identity_matches(11, 777))
        self.assertTrue(model.identity_matches(12, 777))

    def test_duplicate_hwnd_conflicting_pid_rejected(self):
        with self.assertRaises(ValueError):
            WindowRegistry().update([gw(99, 1), gw(99, 2)])

    def test_windows_native_adapter_guard(self):
        if os.name != "nt":
            with self.assertRaises(OSError):
                NativeWin32Backend()


if __name__ == "__main__":
    unittest.main()
