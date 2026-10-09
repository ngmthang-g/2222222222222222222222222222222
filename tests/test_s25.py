"""S25 F01/F04 narrow real Login folder selection, E05 settings and auth.

Test filesystem files are not actual game binaries. No process execution.
"""
from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from login_path import (
    EXE_NAME, GAME_DIR_KEY, PICKER_TITLE, INVALID_TITLE,
    GameDirectoryResult, GameDirectoryStore, resolve_game_dir,
)
from settings_store import read_settings
from login_tab import TLMLoginPathTab, GROUP_FRAME_BOUNDS
from shell import ALL_KEYS, INFO_KEY, TabLifecycle


class S25FolderTests(unittest.TestCase):
    def make_file(self, directory):
        d=Path(directory)
        d.mkdir(parents=True, exist_ok=True)
        (d / EXE_NAME).write_bytes(b"S25 TEST OWNED PLACEHOLDER - NOT AN EXECUTABLE")
        return d

    def test_exact_filename_has_two_spaces(self):
        self.assertEqual(EXE_NAME, "Thần Long  Mobile.exe")
        self.assertFalse(EXE_NAME.replace("  ", " ") == EXE_NAME)

    def test_direct_game_directory_success(self):
        with tempfile.TemporaryDirectory() as td:
            d=self.make_file(Path(td)/"Install")
            r=resolve_game_dir(d)
            self.assertEqual(r.directory,d)
            self.assertEqual(r.note,"")
            self.assertEqual(r.executable,d/EXE_NAME)

    def test_parent_game_subfolder_success(self):
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)/"Install"
            game=self.make_file(folder/"Game")
            r=resolve_game_dir(folder)
            self.assertEqual(r.directory,game)
            self.assertIn("Game",r.note)

    def test_data_child_selected_recovers_parent(self):
        with tempfile.TemporaryDirectory() as td:
            game=self.make_file(Path(td)/"Game")
            data=game/"ThầnLong_Data"
            data.mkdir()
            r=resolve_game_dir(data)
            self.assertEqual(r.directory,game)
            self.assertIn("lùi",r.note)

    def test_one_level_child_search_prioritizes_game_name(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            other=self.make_file(root/"aaa_other")
            game=self.make_file(root/"z_gameclient")
            r=resolve_game_dir(root)
            self.assertEqual(r.directory,game)
            self.assertNotEqual(r.directory,other)

    def test_no_recursive_unbounded_discovery(self):
        with tempfile.TemporaryDirectory() as td:
            deep=self.make_file(Path(td)/"a"/"b")
            self.assertIsNone(resolve_game_dir(td).directory)
            self.assertTrue((deep/EXE_NAME).is_file())

    def test_wrong_spelling_refused(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td)/"Thần Long Mobile.exe").write_bytes(b"wrong-spaces")
            self.assertIsNone(resolve_game_dir(td).directory)

    def test_bad_nonexistent_blank_and_none(self):
        with tempfile.TemporaryDirectory() as td:
            for item in (None, "", "   ", Path(td)/"missing"):
                self.assertIsNone(resolve_game_dir(item).directory)

    def test_file_vs_directory_invalid(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"not_dir"
            p.write_text("abc")
            self.assertIsNone(resolve_game_dir(p).directory)

    def test_store_roundtrip_preserves_unrelated_keys(self):
        with tempfile.TemporaryDirectory() as td:
            d=self.make_file(Path(td)/"Folder"/"Game")
            cfg=Path(td)/"AppData"/"TLMTool"/"settings.ini"
            cfg.parent.mkdir(parents=True)
            cfg.write_text("[Settings]\ngrid_rows = 4\n[Other]\nkeep = yes\n",
                           encoding="utf-8")
            store=GameDirectoryStore(cfg)
            store.save(GameDirectoryResult(d,""))
            self.assertEqual(store.load().directory,d)
            p=read_settings(cfg)
            self.assertEqual(p.get("Settings","grid_rows"),"4")
            self.assertEqual(p.get("Other","keep"),"yes")
            self.assertEqual(p.get("Settings",GAME_DIR_KEY),str(d))
            self.assertEqual(len(list(cfg.parent.glob("settings.????????.ini"))),1)

    def test_invalid_save_does_not_mutate_settings(self):
        with tempfile.TemporaryDirectory() as td:
            cfg=Path(td)/"TLMTool"/"settings.ini"
            cfg.parent.mkdir()
            cfg.write_text("[Settings]\ngrid_cols = 3\n",encoding="utf-8")
            old=cfg.read_bytes()
            with self.assertRaises(ValueError):
                GameDirectoryStore(cfg).save(GameDirectoryResult(Path(td),""))
            self.assertEqual(cfg.read_bytes(),old)

    def test_missing_file_after_load_is_not_usable(self):
        with tempfile.TemporaryDirectory() as td:
            directory=self.make_file(Path(td)/"Game")
            store=GameDirectoryStore(Path(td)/"AppData"/"TLMTool"/"settings.ini")
            result=resolve_game_dir(directory)
            store.save(result)
            (directory/EXE_NAME).unlink()
            self.assertIsNone(store.get_exe_path(result))
            self.assertIsNone(store.load().directory)

    def test_stored_empty_path_is_not_authority(self):
        with tempfile.TemporaryDirectory() as td:
            store=GameDirectoryStore(Path(td)/"missing"/"settings.ini")
            self.assertIsNone(store.load().directory)

    def test_invalid_selected_directory_never_overwrites_valid_persisted(self):
        with tempfile.TemporaryDirectory() as td:
            game=self.make_file(Path(td)/"Game")
            config=Path(td)/"AppData"/"TLMTool"/"settings.ini"
            store=GameDirectoryStore(config)
            store.save(resolve_game_dir(game))
            self.assertIsNone(resolve_game_dir(Path(td)/"junk").directory)
            self.assertEqual(store.load().directory,game)

    def test_test_only_login_lifecycle_remains_info_without_grant(self):
        constructed=[]
        lifecycle=TabLifecycle(
            {INFO_KEY: lambda _:object(),
             "login_tab":lambda frame: constructed.append(frame) or object()},
            {key:object() for key in ALL_KEYS})
        lifecycle.select(INFO_KEY)
        lifecycle.select("login_tab")
        self.assertEqual(constructed,[])
        self.assertEqual(lifecycle.visible,{INFO_KEY})
        lifecycle.shutdown()

    def test_native_gui_contract_is_path_only(self):
        self.assertEqual(GROUP_FRAME_BOUNDS,(6,10,428,65))
        self.assertFalse(hasattr(TLMLoginPathTab,"open_game"))
        self.assertFalse(hasattr(TLMLoginPathTab,"login_account"))
        self.assertFalse(hasattr(TLMLoginPathTab,"solve_captcha"))
        self.assertFalse(hasattr(TLMLoginPathTab,"rotate_proxy"))


if __name__ == "__main__":
    unittest.main()
