"""S111 original-backed F01 hour/minute time selectors and safe E05 editing."""
from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from login_schedule_times import (
    TIME_KEYS, ScheduleTimeWriteError, TLMLoginScheduleTimes,
    save_schedule_time,
)
from login_schedule_settings import read_schedule_settings
from settings_store import read_settings


class ScheduleTimePersistenceTests(unittest.TestCase):
    def make_file(self, root, value):
        p = Path(root) / "TLMTool" / "settings.ini"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(value)
        return p

    def test_01_original_only_time_fields(self):
        self.assertEqual(TIME_KEYS, {"schedule_close", "schedule_open"})

    def test_02_close_changes_only_target_line_preserve_all_other_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            original = (b"[Settings]\r\naccounts = F|alice|secret|Co|p\r\n"
                        b" another|u|pw|Tool|x\r\nschedule_close = 04:00\r\n"
                        b"schedule_open=04:20\r\nschedule_on = UNVERIFIED\r\n"
                        b"[Other]\r\nkey = still here\r\n")
            path = self.make_file(td, original)
            self.assertEqual(save_schedule_time("05:07", "schedule_close", path),
                             "UPDATED_ONLY_SCHEDULE_CLOSE")
            self.assertEqual(path.read_bytes(),
                             original.replace(b"schedule_close = 04:00",
                                              b"schedule_close = 05:07"))
            self.assertEqual(read_schedule_settings(path).close_hhmm, "05:07")

    def test_03_open_also_preserves_other_fields(self):
        with tempfile.TemporaryDirectory() as td:
            original = b"[Settings]\naccounts = x|y|z|Tool|a\nschedule_open = 04:20\n"
            path = self.make_file(td, original)
            save_schedule_time("23:59", "schedule_open", path)
            self.assertEqual(path.read_bytes(),
                             original.replace(b"04:20", b"23:59"))

    def test_04_unchanged_creates_no_backup(self):
        with tempfile.TemporaryDirectory() as td:
            raw = b"[Settings]\nschedule_open=04:20\n"
            path = self.make_file(td, raw)
            self.assertEqual(save_schedule_time("04:20", "schedule_open", path), "UNCHANGED")
            self.assertEqual(path.read_bytes(), raw)
            self.assertEqual(len(list(path.parent.glob("settings.*.ini"))), 0)

    def test_05_changed_creates_e05_dated_backup(self):
        with tempfile.TemporaryDirectory() as td:
            raw = b"[Settings]\nschedule_close=04:00\n"
            path = self.make_file(td, raw)
            save_schedule_time("04:30", "schedule_close", path)
            backups = list(path.parent.glob("settings.*.ini"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_bytes(), raw)

    def test_06_missing_keys_inserted_under_settings_only(self):
        with tempfile.TemporaryDirectory() as td:
            old = b"[Settings]\naccounts = c|u|p|Tool|x\n[Other]\nx = 4\n"
            path = self.make_file(td, old)
            save_schedule_time("02:05", "schedule_close", path)
            data = path.read_bytes()
            self.assertTrue(data.startswith(b"[Settings]\naccounts = c|u|p|Tool|x\n"))
            self.assertIn(b"schedule_close = 02:05\n[Other]", data)
            self.assertEqual(read_settings(path).get("Settings", "accounts"), "c|u|p|Tool|x")

    def test_07_first_write_only_if_empty_file(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "TLMTool" / "settings.ini"
            save_schedule_time("04:20", "schedule_open", path)
            self.assertEqual(path.read_text(), "[Settings]\nschedule_open = 04:20\n")

    def test_08_invalid_hhmm_never_changes_file(self):
        with tempfile.TemporaryDirectory() as td:
            path = self.make_file(td, b"[Settings]\nschedule_close = 04:00\n")
            original = path.read_bytes()
            for invalid in ("24:00", "04:60", "4:00", "04:0", "04:20:00", ""):
                with self.subTest(value=invalid):
                    with self.assertRaises(ScheduleTimeWriteError):
                        save_schedule_time(invalid, "schedule_close", path)
            self.assertEqual(path.read_bytes(), original)

    def test_09_invalid_or_other_key_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = self.make_file(td, b"[Settings]\naccounts=x\n")
            original = path.read_bytes()
            for key in ("accounts", "schedule_on", "shutdown_after_close", ""):
                with self.subTest(key=key):
                    with self.assertRaises(ScheduleTimeWriteError):
                        save_schedule_time("04:00", key, path)
            self.assertEqual(path.read_bytes(), original)

    def test_10_duplicate_time_keys_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            original = b"[Settings]\nschedule_close = 04:00\nschedule_close=05:00\n"
            path = self.make_file(td, original)
            with self.assertRaisesRegex(ScheduleTimeWriteError, "DUPLICATE"):
                save_schedule_time("06:00", "schedule_close", path)
            self.assertEqual(path.read_bytes(), original)

    def test_11_duplicate_sections_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            original = b"[Settings]\nschedule_close=04:00\n[Settings]\nschedule_open=04:20\n"
            path = self.make_file(td, original)
            with self.assertRaisesRegex(ScheduleTimeWriteError, "DUPLICATE"):
                save_schedule_time("06:00", "schedule_close", path)
            self.assertEqual(path.read_bytes(), original)

    def test_12_non_utf8_and_bom_rejected_without_damage(self):
        with tempfile.TemporaryDirectory() as td:
            for raw in (b"[Settings]\ninvalid=\xff\n",
                        b"\xef\xbb\xbf[Settings]\nschedule_close=04:00\n"):
                with self.subTest(raw=raw):
                    path = self.make_file(td, raw)
                    with self.assertRaises(ScheduleTimeWriteError):
                        save_schedule_time("06:00", "schedule_close", path)
                    self.assertEqual(path.read_bytes(), raw)

    def test_13_dont_rewrite_nonempty_unknown_config(self):
        with tempfile.TemporaryDirectory() as td:
            original = b"not an INI\n"
            path = self.make_file(td, original)
            with self.assertRaisesRegex(ScheduleTimeWriteError, "MISSING_SETTINGS"):
                save_schedule_time("04:20", "schedule_open", path)
            self.assertEqual(path.read_bytes(), original)

    def test_14_indented_duplicate_could_be_account_data(self):
        with tempfile.TemporaryDirectory() as td:
            original = b"[Settings]\naccounts = a|b|c\n  schedule_close = 04:00\n"
            path = self.make_file(td, original)
            with self.assertRaisesRegex(ScheduleTimeWriteError, "AMBIGUOUS_INDENTED"):
                save_schedule_time("03:00", "schedule_close", path)
            self.assertEqual(path.read_bytes(), original)

    def test_15_malformed_stored_target_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            original = b"[Settings]\nschedule_close = malformed\n"
            path = self.make_file(td, original)
            with self.assertRaisesRegex(ScheduleTimeWriteError, "UNVERIFIED_STORED"):
                save_schedule_time("04:00", "schedule_close", path)
            self.assertEqual(path.read_bytes(), original)

    def test_16_oversized_file_denied(self):
        with tempfile.TemporaryDirectory() as td:
            original = b"[Settings]\n" + b"x" * (2 * 1024 * 1024)
            path = self.make_file(td, original)
            with self.assertRaisesRegex(ScheduleTimeWriteError, "UNSAFE"):
                save_schedule_time("04:00", "schedule_close", path)
            self.assertEqual(path.stat().st_size, len(original))

    def test_17_no_proxy_or_account_actions_in_module(self):
        import inspect
        import login_schedule_times as source
        text = inspect.getsource(source)
        for token in ("subprocess.Popen", "CreateRemoteThread", "send_packet(",
                      "shutdown /s", "spawn_and_inject", "proxy_tab"):
            self.assertNotIn(token, text)

    def test_18_tk_save_from_stub_success(self):
        class V:
            def __init__(self, text): self.text = text
            def get(self): return self.text
            def set(self, value): self.text = value
        with tempfile.TemporaryDirectory() as td:
            path = self.make_file(td, b"[Settings]\nschedule_close=04:00\n")
            obj = object.__new__(TLMLoginScheduleTimes)
            obj._closed = False
            obj._path = path
            obj._show_error = None
            obj._stored = {"schedule_close": "04:00"}
            obj.vars = {"schedule_close": (V("15"), V("05"))}
            self.assertTrue(obj._save_field("schedule_close"))
            self.assertEqual(obj.last_status, "UPDATED_ONLY_SCHEDULE_CLOSE")
            self.assertIn(b"15:05", path.read_bytes())

    def test_19_tk_stub_failure_restores_prior_values(self):
        class V:
            def __init__(self, text): self.text=text
            def get(self): return self.text
            def set(self, value): self.text=value
        with tempfile.TemporaryDirectory() as td:
            path = self.make_file(td, b"[Settings]\nschedule_close=xx\n")
            h, m = V("20"), V("45")
            errors = []
            obj = object.__new__(TLMLoginScheduleTimes)
            obj._closed = False
            obj._path = path
            obj._stored = {"schedule_close":"04:00"}
            obj.vars = {"schedule_close": (h,m)}
            obj._show_error = lambda *args: errors.append(args)
            self.assertFalse(obj._save_field("schedule_close"))
            self.assertEqual((h.get(),m.get()),("04","00"))
            self.assertEqual(len(errors),1)
            self.assertEqual(obj.last_status,"BLOCKED_TIME_SAVE")

    def test_20_closed_view_refuses_writes(self):
        obj = object.__new__(TLMLoginScheduleTimes)
        obj._closed = True
        self.assertFalse(obj._save_field("schedule_close"))
        self.assertFalse(obj._save_field("schedule_open"))


if __name__ == "__main__":
    unittest.main()
