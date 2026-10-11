"""S142 — real F09 time-only settings writer detects outside concurrent edits.

Synthetic INI/credentials exclusively. No game auth, scheduler, shutdown.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import ast
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import login_schedule_times as module
from login_schedule_times import (
    ScheduleTimeWriteError,save_schedule_time,TLMLoginScheduleTimes,
)
from login_schedule_settings import read_schedule_settings

START=(
    "[Settings]\r\n"
    "accounts = ?|S142_FAKE_USER|S142_FAKE_SECRET|Có|opaque\r\n"
    "  ?|S142_SECOND|S142_SECOND_PW|Tool|?\r\n"
    "game_dir = X:\\Game\r\n"
    "schedule_close = 04:00\r\n"
    "schedule_open=04:20\r\n"
    "schedule_on = UNKNOWN\r\n"
    "[Other]\r\npreserve = Việt Nam\r\n"
).encode("utf8")


class S142ScheduledTimeConcurrentWriteTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.target=Path(self.temp.name)/"TLMTool"/"settings.ini"
        self.target.parent.mkdir()
        self.target.write_bytes(START)

    def change_externally_on_fsync(self,data):
        actual=module.os.fsync
        def simulate(fd):
            self.target.write_bytes(data)
            return actual(fd)
        return patch("login_schedule_times.os.fsync",side_effect=simulate)

    def test_01_original_F09_close_save_still_exact(self):
        self.assertEqual(save_schedule_time("09:15","schedule_close",self.target),
                         "UPDATED_ONLY_SCHEDULE_CLOSE")
        self.assertEqual(self.target.read_bytes(),
                         START.replace(b"schedule_close = 04:00",
                                       b"schedule_close = 09:15"))

    def test_02_real_F09_open_save_still_exact(self):
        self.assertEqual(save_schedule_time("05:45","schedule_open",self.target),
                         "UPDATED_ONLY_SCHEDULE_OPEN")
        self.assertEqual(self.target.read_bytes(),
                         START.replace(b"schedule_open=04:20",b"schedule_open=05:45"))

    def test_03_external_other_key_change_refused_and_preserved(self):
        external=START.replace(b"game_dir = X:\\Game",b"game_dir = Y:\\Game")
        with self.change_externally_on_fsync(external):
            with self.assertRaisesRegex(ScheduleTimeWriteError,"STALE"):
                save_schedule_time("05:07","schedule_open",self.target)
        self.assertEqual(self.target.read_bytes(),external)
        self.assertFalse(list(self.target.parent.glob("settings.????????.ini")))

    def test_04_equal_length_and_equal_mtime_external_bytes_still_refused(self):
        first=self.target.stat()
        external=START.replace(b"game_dir = X:\\Game",b"game_dir = Y:\\Game")
        self.assertEqual(len(external),len(START))
        fsync=module.os.fsync
        def mutate(fd):
            self.target.write_bytes(external)
            os.utime(self.target,ns=(first.st_atime_ns,first.st_mtime_ns))
            return fsync(fd)
        with patch("login_schedule_times.os.fsync",side_effect=mutate):
            with self.assertRaisesRegex(ScheduleTimeWriteError,"STALE"):
                save_schedule_time("05:07","schedule_close",self.target)
        self.assertEqual(self.target.read_bytes(),external)

    def test_05_external_credential_change_refused_and_not_overwritten(self):
        external=START.replace(b"S142_FAKE_SECRET",b"EXTERNAL_SECRET!")
        with self.change_externally_on_fsync(external):
            with self.assertRaisesRegex(ScheduleTimeWriteError,"STALE"):
                save_schedule_time("06:00","schedule_close",self.target)
        self.assertEqual(self.target.read_bytes(),external)

    def test_06_externally_deleted_ini_not_recreated(self):
        fsync=module.os.fsync
        def deleted(fd):
            self.target.unlink()
            return fsync(fd)
        with patch("login_schedule_times.os.fsync",side_effect=deleted):
            with self.assertRaisesRegex(ScheduleTimeWriteError,"STALE"):
                save_schedule_time("06:00","schedule_close",self.target)
        self.assertFalse(self.target.exists())

    def test_07_externally_created_ini_when_absent_refused(self):
        self.target.unlink()
        fsync=module.os.fsync
        def created(fd):
            self.target.write_bytes(b"[Settings]\nschedule_close=07:00\n")
            return fsync(fd)
        with patch("login_schedule_times.os.fsync",side_effect=created):
            with self.assertRaisesRegex(ScheduleTimeWriteError,"STALE"):
                save_schedule_time("06:00","schedule_close",self.target)
        self.assertEqual(self.target.read_bytes(),b"[Settings]\nschedule_close=07:00\n")

    def test_08_backup_original_before_successful_replace(self):
        save_schedule_time("03:15","schedule_close",self.target)
        backup=self.target.with_name("settings."+datetime.now().strftime("%Y%m%d")+".ini")
        self.assertEqual(backup.read_bytes(),START)
        self.assertIn(b"schedule_close = 03:15",self.target.read_bytes())

    def test_09_unchanged_no_write_or_backup(self):
        mtime=self.target.stat().st_mtime_ns
        self.assertEqual(save_schedule_time("04:00","schedule_close",self.target),"UNCHANGED")
        self.assertEqual(self.target.stat().st_mtime_ns,mtime)
        self.assertEqual(list(self.target.parent.glob("settings.????????.ini")),[])

    def test_10_tk_existing_callback_failure_rolls_back_only_view(self):
        class Variable:
            def __init__(self,v):self.v=v
            def get(self):return self.v
            def set(self,v):self.v=v
        hour,minute=Variable("06"),Variable("15")
        widget=object.__new__(TLMLoginScheduleTimes)
        widget._closed=False
        widget._path=self.target
        widget._stored={"schedule_close":"04:00"}
        widget.vars={"schedule_close":(hour,minute)}
        errors=[]
        widget._show_error=lambda title,body:errors.append((title,body))
        external=START.replace(b"game_dir = X:\\Game",b"game_dir = Y:\\Game")
        with self.change_externally_on_fsync(external):
            self.assertFalse(widget._save_field("schedule_close"))
        self.assertEqual((hour.get(),minute.get()),("04","00"))
        self.assertEqual(widget.last_status,"BLOCKED_TIME_SAVE")
        self.assertEqual(self.target.read_bytes(),external)
        self.assertEqual(len(errors),1)
        self.assertNotIn("FAKE_SECRET",str(errors))

    def test_11_subsequent_save_against_latest_external_content_succeeds(self):
        external=START.replace(b"game_dir = X:\\Game",b"game_dir = Y:\\Game")
        with self.change_externally_on_fsync(external):
            with self.assertRaises(ScheduleTimeWriteError):
                save_schedule_time("05:00","schedule_open",self.target)
        save_schedule_time("05:00","schedule_open",self.target)
        self.assertEqual(self.target.read_bytes(),
             external.replace(b"schedule_open=04:20",b"schedule_open=05:00"))

    def test_12_existing_unambiguous_account_reader_preserved(self):
        save_schedule_time("09:17","schedule_close",self.target)
        from login_account_legacy import read_legacy_accounts
        info=read_legacy_accounts(self.target)
        self.assertEqual(info.status,"READY")
        self.assertEqual(info.count,2)
        self.assertEqual(info.records[0].captcha_raw,"Có")

    def test_13_no_real_game_or_shutdown_action(self):
        source=(ROOT/"src/login_schedule_times.py").read_text(encoding="utf8")
        for term in ("CreateRemoteThread(","WriteProcessMemory(","shutdown /s",
                     "subprocess.Popen(","SendInput(","VerifiedClaims("):
            self.assertNotIn(term,source)

    def test_14_scope_ast_compiles(self):
        for p in ("src/login_schedule_times.py","tests/test_s142.py",
                  "tools/S142_WINDOWS_LOGIN_TIME_CONCURRENT_SMOKE.py"):
            ast.parse((ROOT/p).read_text(encoding="utf8"))

if __name__=="__main__":
    unittest.main()
