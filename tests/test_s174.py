"""S174 real packaged independent Windows GUI acceptance harness unit invariants.

Pure helpers verify exact process-specific HWND matching and isolation;
native CI MUST also run the actual packaged EXE with normal GUI mode.
"""
from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import S174_WINDOWS_PACKAGED_GUI_SMOKE as smoke


class S174PackagedGuiAssertions(unittest.TestCase):
    def test_01_exact_only_independent_main_window_title(self):
        self.assertTrue(smoke.accepted_window(
            321, "TLMTool — Độc lập", True, 450, 600))
        for title in ("TLMTool", "TLMTool.exe", "TLMTool - Độc lập",
                      "TLMTool — Độc lập [DEBUG]", ""):
            self.assertFalse(smoke.accepted_window(321, title, True, 450, 600))

    def test_02_no_pid_zero_hidden_or_tiny_tray_window(self):
        self.assertFalse(smoke.accepted_window(
            0, smoke.WINDOW_TITLE, True, 450, 600))
        self.assertFalse(smoke.accepted_window(
            321, smoke.WINDOW_TITLE, False, 450, 600))
        self.assertFalse(smoke.accepted_window(
            321, smoke.WINDOW_TITLE, True, 100, 600))
        self.assertFalse(smoke.accepted_window(
            321, smoke.WINDOW_TITLE, True, 450, 40))

    def test_03_validates_types_without_python_bool_as_pid(self):
        for p,w,h in ((True,450,500), ("33",450,500),
                      (321,True,500),(321,450,True)):
            with self.subTest(p=p,w=w,h=h):
                self.assertFalse(smoke.accepted_window(
                    p,smoke.WINDOW_TITLE,True,w,h))

    def test_04_test_appdata_is_private_and_parent_env_retained(self):
        with tempfile.TemporaryDirectory(prefix="S174_ENV_") as td:
            root=Path(td)
            env=smoke.isolated_env(root,{"PATH":"original-path",
                                        "APPDATA":"C:\\not-ours",
                                        "LOCALAPPDATA":"C:\\not-ours"})
            self.assertEqual(env["APPDATA"],str(root/"Roaming"))
            self.assertEqual(env["LOCALAPPDATA"],str(root/"Local"))
            self.assertEqual(env["PATH"],"original-path")
            self.assertTrue((root/"Roaming").is_dir())
            self.assertTrue((root/"Local").is_dir())

    def test_05_native_acceptance_uses_normal_app_launch(self):
        source=(ROOT/"tools"/"S174_WINDOWS_PACKAGED_GUI_SMOKE.py").read_text("utf-8")
        self.assertIn("[str(executable)]",source)
        self.assertIn("WM_CLOSE",source)
        self.assertIn("first_gui",source)
        self.assertIn("duplicate_gui",source)
        self.assertIn("reopened_gui",source)
        self.assertIn("process.kill()",source)
        self.assertIn("SMTO_ABORTIFHUNG",source)

    def test_06_original_tlm_and_game_sender_not_launched(self):
        source=(ROOT/"tools"/"S174_WINDOWS_PACKAGED_GUI_SMOKE.py").read_text("utf-8")
        for forbidden in ("TLMTool.py\"]", "press_single_key_dll(",
                          "ReadProcessMemory(", "WM_MY_SYNC_KEY",
                          "PostMessage(game_hwnd", "receive_token(",
                          "SetWindowsHookEx("):
            self.assertNotIn(forbidden,source)

if __name__=="__main__":
    unittest.main()
