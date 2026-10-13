"""S209: Windows-independent strict F05 PID/Unity discovery regression.

No real game is launched. Simulated fake window backend and fake Popen prove
the source algorithm rejects a PID-owned updater popup, a wrong EXE and
reused HWND, selects a genuine late-arriving Unity window, and publishes
exactly ONE timeout outcome (not fake CANCELLED_AFTER_START).
"""
from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from login_pid_window import find_verified_game_window_by_pid
from login_independent_game_launcher import IndependentGameLaunchController

GAME = r"C:\\Games\\ThanLong\\Thần Long  Mobile.exe"
OTHER = r"C:\\Games\\Other\\Thần Long  Mobile.exe"


class Win32GameWindowsStub:
    def __init__(self, windows, game=GAME):
        # hwnd => (pid, class, title, executable, still_alive)
        self.windows = windows
        self.game = game
        self.top = list(windows)
        self.changing = set()

    def enumerate_top_level(self):
        return tuple(self.top)

    def is_window(self, hwnd):
        return hwnd in self.windows and self.windows[hwnd][-1]

    def is_visible(self, hwnd):
        return self.is_window(hwnd)

    def process_id(self, hwnd):
        return self.windows[hwnd][0] if hwnd in self.windows else 0

    def process_executable(self, pid):
        rows = [v for v in self.windows.values() if v[0] == pid]
        return rows[0][3] if rows else ""

    def window_class(self, hwnd):
        return self.windows[hwnd][1]

    def title_with_timeout(self, hwnd, timeout):
        if hwnd in self.changing:
            self.windows[hwnd] = (*self.windows[hwnd][:-1], False)
        return self.windows[hwnd][2]


class FakePopen:
    pid = 44550
    def poll(self):
        return None


class S209NativeF05SourceTests(unittest.TestCase):
    def test_popup_before_unity_is_not_window(self):
        windows = Win32GameWindowsStub({
            501: (44550, "#32770", "Unity updater", GAME, True)})
        self.assertIsNone(find_verified_game_window_by_pid(
            44550, GAME, backend=windows))

    def test_visible_popup_before_game_does_not_mask_unity(self):
        windows = Win32GameWindowsStub({
            501: (44550, "#32770", "Unity updater", GAME, True),
            503: (44550, "UnityWndClass", "Thần Long  Mobile", GAME, True)})
        self.assertEqual(find_verified_game_window_by_pid(
            44550, GAME, backend=windows), 503)

    def test_wrong_executable_does_not_qualify(self):
        windows = Win32GameWindowsStub({
            503: (44550, "UnityWndClass", "Thần Long  Mobile", OTHER, True)})
        self.assertIsNone(find_verified_game_window_by_pid(
            44550, GAME, backend=windows))

    def test_two_equally_native_windows_are_ambiguous(self):
        windows = Win32GameWindowsStub({
            503: (44550, "UnityWndClass", "Thần Long  Mobile", GAME, True),
            504: (44550, "UnityWndClass", "Thần Long  Mobile", GAME, True)})
        self.assertIsNone(find_verified_game_window_by_pid(
            44550, GAME, backend=windows))

    def test_closed_or_reused_hwnd_during_title_is_rejected(self):
        windows = Win32GameWindowsStub({
            503: (44550, "UnityWndClass", "Thần Long  Mobile", GAME, True)})
        windows.changing.add(503)
        self.assertIsNone(find_verified_game_window_by_pid(
            44550, GAME, backend=windows))

    def test_wrong_pid_must_not_cause_match(self):
        windows = Win32GameWindowsStub({
            503: (44551, "UnityWndClass", "Thần Long  Mobile", GAME, True)})
        self.assertIsNone(find_verified_game_window_by_pid(
            44550, GAME, backend=windows))

    def test_timeout_publishes_once_not_cancelled(self):
        # The first monotonic call is the deadline; the second is after
        # timeout. No native process, game, global input or DLL is invoked.
        instants = iter((0.0, 30.0))
        controller = IndependentGameLaunchController(clock=lambda: next(instants))
        process = FakePopen()
        # Popen return instance, not actual Windows process.
        with patch(
            "login_independent_game_launcher.count_current_game_processes",
            return_value=SimpleNamespace(
                code="PROCESS_SNAPSHOT_OK",running_exe=0)
        ), patch(
            "login_independent_game_launcher.subprocess.Popen",
            return_value=process
        ):
            controller._launch_once(Path(GAME), {"SystemRoot": "C:\\Windows"})
        responses = controller.drain()
        self.assertEqual(len(responses), 1, responses)
        self.assertEqual(responses[0].code, "STARTED_NO_WINDOW_YET")
        self.assertEqual(responses[0].pid, 44550)
        self.assertTrue(responses[0].process_was_started)
        controller.shutdown()


if __name__ == "__main__":
    unittest.main(verbosity=2)
