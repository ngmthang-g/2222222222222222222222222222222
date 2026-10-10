"""S69 C14 detached-auto-open preference/grid persistence: 12 precise tests."""
from __future__ import annotations
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from detached_settings import (
    DETACHED_AUTO_OPEN_DEFAULT, DETACHED_GRID_DEFAULT,
    DETACHED_GRID_ORIGINAL_CHOICES, DetachedSettings, DetachedSettingsStore,
    valid_detached_grid,
)
from settings_store import settings_path
from grid_master import GridSettingsStore

class S69DetachedSettingsTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/"TLMTool"/"settings.ini"
        self.store=DetachedSettingsStore(self.path)

    def test_exact_original_keys_and_defaults(self):
        self.assertIs(DETACHED_AUTO_OPEN_DEFAULT,True)
        self.assertEqual(DETACHED_GRID_DEFAULT,"3")
        self.assertEqual(DetachedSettings(),DetachedSettings(True,"3"))
        self.assertEqual(self.store.load(),DetachedSettings(True,"3"))
        self.assertEqual(DETACHED_GRID_ORIGINAL_CHOICES,"UNKNOWN")

    def test_settings_ini_section_and_roundtrip(self):
        self.store.save(False,"5")
        raw=self.path.read_text(encoding="utf-8")
        self.assertIn("[Settings]",raw)
        self.assertIn("detached_auto_open = False",raw)
        self.assertIn("detached_grid = 5",raw)
        self.assertEqual(self.store.load(),DetachedSettings(False,"5"))

    def test_save_true_and_original_default_string_three(self):
        self.store.save(True,"3")
        self.assertEqual(self.store.load(),DetachedSettings(True,"3"))
        self.assertIn("detached_auto_open = True",self.path.read_text("utf-8"))

    def test_unrelated_sections_keys_and_game_grid_preserved(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text("[Settings]\ngrid_cols=4\ngrid_rows=6\n"
              "custom=untouched\n[Daily]\nkey=unchanged\n",encoding="utf-8")
        before=GridSettingsStore(self.path).load()
        self.store.save(False,"2")
        content=self.path.read_text("utf-8")
        self.assertEqual(before,GridSettingsStore(self.path).load())
        self.assertIn("custom = untouched",content)
        self.assertIn("[Daily]",content)
        self.assertIn("key = unchanged",content)

    def test_grid_writer_roundtrip_keeps_detached_preferences(self):
        self.store.save(False,"7")
        GridSettingsStore(self.path).save(2,3)
        self.assertEqual(self.store.load(),DetachedSettings(False,"7"))
        self.assertEqual(GridSettingsStore(self.path).load().cols,2)

    def test_existing_settings_create_E05_dated_backup(self):
        self.store.save(False,"4")
        self.store.save(True,"6")
        backups=list(self.path.parent.glob("settings.????????.ini"))
        self.assertEqual(len(backups),1)
        self.assertIn("detached_grid = 4",backups[0].read_text("utf-8"))
        self.assertEqual(self.store.load(),DetachedSettings(True,"6"))

    def test_independent_boolean_failure_keeps_valid_grid(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text("[Settings]\ndetached_auto_open=maybe\n"
                             "detached_grid=8\n",encoding="utf-8")
        self.assertEqual(self.store.load(),DetachedSettings(True,"8"))

    def test_invalid_grid_does_not_discard_valid_boolean(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text("[Settings]\ndetached_auto_open=False\n"
                             "detached_grid=not-a-number\n",encoding="utf-8")
        self.assertEqual(self.store.load(),DetachedSettings(False,"3"))

    def test_duplicate_keys_are_last_wins_via_shared_E05_parser(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text("[Settings]\ndetached_auto_open=True\n"
            "detached_auto_open=False\ndetached_grid=2\ndetached_grid=5\n",
            encoding="utf-8")
        self.assertEqual(self.store.load(),DetachedSettings(False,"5"))

    def test_invalid_values_rejected_before_creating_or_mutating_file(self):
        for auto,grid in ((None,"3"),(1,"3"),("False","3"),(False,3),
                          (True,"0"),(True,""),(True,"3x"),(True," 3")):
            with self.subTest(auto=auto,grid=grid):
                with self.assertRaises(ValueError):
                    self.store.save(auto,grid)
                self.assertFalse(self.path.exists())
        self.assertTrue(valid_detached_grid("3"))
        self.assertTrue(valid_detached_grid("12"))
        self.assertFalse(valid_detached_grid("03"))
        self.assertFalse(valid_detached_grid("１"))

    def test_saves_do_not_launch_preview_or_create_windows(self):
        self.store.save(True,"3")
        self.assertEqual(self.store.load(),DetachedSettings(True,"3"))
        code=(ROOT/"src/detached_settings.py").read_text("utf-8")
        for forbidden in ("tk.Button(", "tk.Toplevel(", "DwmRegisterThumbnail",
                          "CreateWindowExW", "GetWindowRect", "CreateRemoteThread",
                          "PostMessage(", "proxy_tab", "ReadProcessMemory("):
            self.assertNotIn(forbidden,code)

    def test_settings_default_APPDATA_follows_original_E05_path(self):
        old=os.environ.get("APPDATA")
        os.environ["APPDATA"]=self.temp.name
        try:
            self.assertEqual(settings_path(),self.path)
            store=DetachedSettingsStore()
            store.save(False,"9")
            self.assertEqual(store.load(),DetachedSettings(False,"9"))
            self.assertEqual(self.store.load(),DetachedSettings(False,"9"))
        finally:
            if old is None:os.environ.pop("APPDATA",None)
            else:os.environ["APPDATA"]=old

if __name__=="__main__":unittest.main()
