"""S141: end-to-end F04 live game-directory save preserves F02 legacy bytes.

Entirely TEST-OWNED fake EXE/files/credentials. No actual game or license.
"""
from __future__ import annotations
from datetime import datetime
from pathlib import Path
import tempfile
import sys
import unittest
from unittest.mock import patch
import ast

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from login_path import (
    EXE_NAME, GameDirectoryResult,GameDirectoryStore,
    _updated_game_dir_bytes,_save_only_game_dir,resolve_game_dir,
)
from settings_store import read_settings

ORIGINAL = (
    "[Settings]\r\n"
    "accounts = opaque-check|S141_FAKE_A|S141_FAKE_SECRET_A|Có|opaque-proxy\r\n"
    "  ?|S141_FAKE_B|S141_FAKE_SECRET_B|Tool|\r\n"
    "schedule_open = 04:20\r\n"
    "game_dir = X:\\OldGame\r\n"
    "after_login = wait\r\n"
    "[Other]\r\n"
    "utf8 = Tiếng Việt\r\n"
).encode("utf-8")


class S141GameDirectoryPreservation(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder=Path(self.tmp.name)
        self.path=self.folder/"TLMTool"/"settings.ini"
        self.path.parent.mkdir(parents=True)
        self.game=self.folder/"Game"
        self.game.mkdir()
        (self.game/EXE_NAME).write_bytes(b"S141_TEST_OWNED_FILE_NOT_GAME_EXE")
        self.selection=GameDirectoryResult(self.game,"")
    def initialize(self,raw=ORIGINAL):
        self.path.write_bytes(raw)
        return raw

    def test_01_existing_path_changes_only_raw_target(self):
        before=self.initialize()
        GameDirectoryStore(self.path).save(self.selection)
        expect=before.replace(b"game_dir = X:\\OldGame",
                              ("game_dir = "+str(self.game)).encode("utf8"))
        self.assertEqual(self.path.read_bytes(),expect)

    def test_02_account_raw_check_and_legacy_captcha_not_normalized(self):
        self.initialize()
        GameDirectoryStore(self.path).save(self.selection)
        raw=self.path.read_bytes()
        self.assertIn("opaque-check|S141_FAKE_A|S141_FAKE_SECRET_A|Có|opaque-proxy".encode(),raw)
        self.assertIn(b"  ?|S141_FAKE_B|S141_FAKE_SECRET_B|Tool|",raw)
        self.assertIn("utf8 = Tiếng Việt".encode(),raw)

    def test_03_native_file_roundtrip_F04(self):
        self.initialize()
        store=GameDirectoryStore(self.path)
        store.save(self.selection)
        self.assertEqual(store.load().directory,self.game)
        self.assertEqual(store.get_exe_path(store.load()),self.game/EXE_NAME)
        self.assertEqual(read_settings(self.path).get("Settings","after_login"),"wait")

    def test_04_backup_exact_prior_bytes(self):
        old=self.initialize()
        GameDirectoryStore(self.path).save(self.selection)
        backup=self.path.with_name("settings."+datetime.now().strftime("%Y%m%d")+".ini")
        self.assertEqual(backup.read_bytes(),old)

    def test_05_idempotent_no_second_backup_or_write(self):
        self.initialize()
        s=GameDirectoryStore(self.path);s.save(self.selection)
        t=self.path.stat().st_mtime_ns
        s.save(self.selection)
        self.assertEqual(t,self.path.stat().st_mtime_ns)
        self.assertEqual(len(list(self.path.parent.glob("settings.????????.ini"))),1)

    def test_06_missing_game_dir_key_appended_before_next_section(self):
        raw=ORIGINAL.replace(b"game_dir = X:\\OldGame\r\n",b"")
        self.initialize(raw)
        GameDirectoryStore(self.path).save(self.selection)
        updated=self.path.read_bytes()
        self.assertEqual(updated.replace(
            ("game_dir = "+str(self.game)+"\r\n").encode(),b""),raw)
        self.assertIn(("game_dir = "+str(self.game)+"\r\n[Other]").encode(),updated)

    def test_07_empty_new_file_still_creates_path(self):
        self.path.unlink(missing_ok=True)
        GameDirectoryStore(self.path).save(self.selection)
        self.assertEqual(read_settings(self.path).get("Settings","game_dir"),str(self.game))

    def test_08_different_sections_preserved(self):
        old=self.initialize()
        GameDirectoryStore(self.path).save(self.selection)
        self.assertEqual(self.path.read_bytes().split(b"[Other]")[1],
                         old.split(b"[Other]")[1])

    def test_09_wrong_nonexistent_game_prevents_any_disk_write(self):
        before=self.initialize()
        with self.assertRaises(ValueError):
            GameDirectoryStore(self.path).save(GameDirectoryResult(self.folder/"nope",""))
        self.assertEqual(self.path.read_bytes(),before)

    def test_10_duplicate_game_dir_refused_and_not_touched(self):
        raw=self.initialize(ORIGINAL.replace(b"game_dir = X:\\OldGame\r\n",
                     b"game_dir = first\r\nGAME_DIR: second\r\n"))
        with self.assertRaisesRegex(ValueError,"AMBIGUOUS"):
            GameDirectoryStore(self.path).save(self.selection)
        self.assertEqual(self.path.read_bytes(),raw)

    def test_11_duplicate_settings_sections_refused(self):
        raw=self.initialize(ORIGINAL+b"[Settings]\r\ngame_dir = second\r\n")
        with self.assertRaisesRegex(ValueError,"AMBIGUOUS"):
            GameDirectoryStore(self.path).save(self.selection)
        self.assertEqual(self.path.read_bytes(),raw)

    def test_12_indented_conflicting_game_dir_does_not_edit_accounts(self):
        raw=self.initialize(ORIGINAL.replace(b"game_dir = X:\\OldGame\r\n",
                      b"  game_dir = some legacy continuation\r\n"))
        with self.assertRaisesRegex(ValueError,"AMBIGUOUS"):
            GameDirectoryStore(self.path).save(self.selection)
        self.assertEqual(self.path.read_bytes(),raw)

    def test_13_non_utf8_refused(self):
        raw=self.initialize(b"[Settings]\r\naccounts = \xff\r\ngame_dir=a\r\n")
        with self.assertRaisesRegex(ValueError,"UNREADABLE"):
            GameDirectoryStore(self.path).save(self.selection)
        self.assertEqual(self.path.read_bytes(),raw)

    def test_14_bom_nul_and_broken_cr_refused(self):
        for raw in (b"\xef\xbb\xbf"+ORIGINAL,ORIGINAL+b"\x00",
                    ORIGINAL.replace(b"\r\n",b"\r")):
            with self.subTest(length=len(raw)):
                self.initialize(raw)
                with self.assertRaisesRegex(ValueError,"AMBIGUOUS"):
                    GameDirectoryStore(self.path).save(self.selection)
                self.assertEqual(self.path.read_bytes(),raw)

    def test_15_reject_invalid_single_key_value_injection(self):
        for path in ("folder\nother = break","folder\rother","folder\x00other"):
            with self.subTest(path=repr(path)):
                with self.assertRaisesRegex(ValueError,"INVALID_GAME_DIR"):
                    _updated_game_dir_bytes(ORIGINAL,path)

    def test_16_missing_settings_in_nonempty_ini_refused(self):
        raw=self.initialize(b"[Other]\nkeep=yes\n")
        with self.assertRaisesRegex(ValueError,"AMBIGUOUS"):
            GameDirectoryStore(self.path).save(self.selection)
        self.assertEqual(self.path.read_bytes(),raw)

    def test_17_external_write_race_fail_closed(self):
        self.initialize()
        original_replace=__import__("os").replace
        import login_path
        def injected_replace(src,dst):
            self.path.write_bytes(b"[Settings]\ngame_dir = EXTERNAL_CHANGED\n")
            return original_replace(src,dst)
        # Simulate external edit between read and final write by patching
        # os.fsync, which runs BEFORE the writer's second stat().
        real_fsync=login_path.os.fsync
        def on_fsync(fd):
            self.path.write_bytes(b"[Settings]\ngame_dir = EXTERNAL_CHANGED\n")
            return real_fsync(fd)
        with patch("login_path.os.fsync",side_effect=on_fsync):
            with self.assertRaisesRegex(ValueError,"STALE"):
                GameDirectoryStore(self.path).save(self.selection)
        self.assertEqual(self.path.read_bytes(),b"[Settings]\ngame_dir = EXTERNAL_CHANGED\n")

    def test_18_value_equal_keeps_original_bytes(self):
        raw=self.initialize(ORIGINAL.replace(b"X:\\OldGame",str(self.game).encode()))
        self.assertEqual(_save_only_game_dir(self.path,str(self.game)),"UNCHANGED")
        self.assertEqual(self.path.read_bytes(),raw)
        self.assertEqual(list(self.path.parent.glob("settings.????????.ini")),[])

    def test_19_untouched_real_legacy_accounts_reader_still_loads(self):
        self.initialize()
        GameDirectoryStore(self.path).save(self.selection)
        from login_account_legacy import read_legacy_accounts
        records=read_legacy_accounts(self.path)
        self.assertEqual(records.status,"READY")
        self.assertEqual(records.count,2)
        self.assertEqual(records.records[0].captcha_raw,"Có")

    def test_20_no_game_launch_info_or_proxy_in_saver(self):
        content=(ROOT/"src/login_path.py").read_text(encoding="utf8")
        for forbidden in ("CreateRemoteThread(", "WriteProcessMemory(",
                          "subprocess.Popen(", "SendInput(", "requests.post(",
                          "receive_server_token(", "VerifiedClaims("):
            self.assertNotIn(forbidden,content)

    def test_21_ast_parse(self):
        for name in ("src/login_path.py","tests/test_s141.py"):
            ast.parse((ROOT/name).read_text(encoding="utf8"))

if __name__=="__main__":
    unittest.main()
