"""S40 real E05/F09 read-only schedule.ini loader without game actions."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from login_schedule_settings import (
    ReadOnlyScheduleSettings, SchedulePreview, SCHEDULE_KEYS,
    read_schedule_settings, _bounded_opaque_token,
)


class S40ScheduleSettingsTests(unittest.TestCase):
    def config(self, root, text):
        path = Path(root) / "TLMTool" / "settings.ini"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_exact_f09_original_keys(self):
        self.assertEqual(SCHEDULE_KEYS, (
            "schedule_on", "schedule_close", "schedule_open", "shutdown_after_close"))

    def test_missing_file_uses_original_visible_defaults_not_auto_arming(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "missing.ini"
            info = read_schedule_settings(path)
            self.assertEqual(info.status, "DEFAULTS_ONLY")
            self.assertEqual((info.close_hhmm, info.open_hhmm), ("04:00", "04:20"))
            self.assertIsNone(info.schedule_on_raw)
            self.assertFalse(path.exists())

    def test_empty_settings_section_has_same_time_defaults(self):
        with tempfile.TemporaryDirectory() as td:
            path = self.config(td, "[Settings]\nother = 7\n")
            info = read_schedule_settings(path)
            self.assertEqual(info.status, "READ_ONLY_VALIDATED")
            self.assertEqual((info.close_hhmm, info.open_hhmm), ("04:00", "04:20"))

    def test_explicit_hhmm_is_loaded_as_is(self):
        with tempfile.TemporaryDirectory() as td:
            path = self.config(td, "[Settings]\nschedule_close = 05:17\nschedule_open = 18:39\n")
            info = read_schedule_settings(path)
            self.assertEqual(info.status, "READ_ONLY_VALIDATED")
            self.assertEqual((info.close_hhmm, info.open_hhmm), ("05:17", "18:39"))

    def test_unknown_enabled_and_shutdown_encoded_flags_preserved_as_raw(self):
        with tempfile.TemporaryDirectory() as td:
            path = self.config(td, "[Settings]\nschedule_on = UNVERIFIED_ON\n"
                                    "shutdown_after_close = OLD_BOOLEAN_TOKEN\n")
            info = read_schedule_settings(path)
            self.assertEqual(info.schedule_on_raw, "UNVERIFIED_ON")
            self.assertEqual(info.shutdown_after_close_raw, "OLD_BOOLEAN_TOKEN")
            self.assertNotIsInstance(info.schedule_on_raw, bool)

    def test_opaque_flags_not_inferred_from_truthy_words(self):
        with tempfile.TemporaryDirectory() as td:
            for raw in ("True", "False", "0", "1", "yes", "no", "Có"):
                with self.subTest(raw=raw):
                    path = self.config(td, "[Settings]\nschedule_on = "+raw+"\n")
                    info = read_schedule_settings(path)
                    self.assertEqual(info.schedule_on_raw, raw)
                    self.assertIsNone(info.shutdown_after_close_raw)

    def test_original_accounts_multiline_unchanged_exact_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            path = self.config(td, "[Settings]\n"
                "accounts = UNKNOWN|S40_PRIVATE_SECRET|secret value|Có|opaque\n"
                "  ?|u2|secret2|Tool|\n"
                "schedule_on = UNKNOWN_ON\n"
                "schedule_close = 04:00\nschedule_open = 04:20\n"
                "shutdown_after_close = UNKNOWN_PC\n"
                "[Unrelated]\nkeep = me\n")
            before = path.read_bytes()
            info = read_schedule_settings(path)
            self.assertTrue(info.preview_available)
            preview = info.preview(datetime(2026, 10, 9, 15, 0))
            self.assertIn("10/10", preview.countdown)
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(list(Path(td).rglob("settings.*.ini")), [])

    def test_preview_uses_real_s39_clock_without_arming_worker(self):
        with tempfile.TemporaryDirectory() as td:
            path = self.config(td, "[Settings]\nschedule_on = TRUE_UNKNOWN\n")
            info = read_schedule_settings(path)
            result = info.preview(datetime(2026, 10, 9, 3, 0))
            self.assertIsInstance(result, SchedulePreview)
            self.assertEqual(result.next_close, datetime(2026, 10, 9, 4, 0))
            self.assertEqual(result.next_open, datetime(2026, 10, 9, 4, 20))

    def test_preview_on_missing_file_still_no_side_effect(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "missing.ini"
            result = read_schedule_settings(path).preview(datetime(2026,10,9,15,0))
            self.assertEqual(result.next_close.day, 10)
            self.assertFalse(path.exists())

    def test_bad_time_format_fails_closed_and_never_normalizes(self):
        for bad in ("4:00", "04:60", "25:00", "04%00",
                    "04:00:01", "", "００:００"):
            with self.subTest(bad=bad), tempfile.TemporaryDirectory() as td:
                path = self.config(td, "[Settings]\nschedule_close = "+bad+"\n")
                info = read_schedule_settings(path)
                self.assertEqual(info.status, "BLOCKED_TIME_FORMAT")
                self.assertFalse(info.preview_available)
                with self.assertRaises(RuntimeError):
                    info.preview(datetime(2026, 10, 9))

    def test_invalid_open_time_also_blocks_all_preview(self):
        with tempfile.TemporaryDirectory() as td:
            path = self.config(td, "[Settings]\nschedule_open = 48:20\n")
            self.assertEqual(read_schedule_settings(path).status, "BLOCKED_TIME_FORMAT")

    def test_unreadable_ini_fails_closed_with_no_content_leak(self):
        with tempfile.TemporaryDirectory() as td:
            path=self.config(td, "INVALID_PRIVATE_SECRET\n")
            info=read_schedule_settings(path)
            self.assertEqual(info.status, "BLOCKED_SETTINGS_READ")
            self.assertNotIn("PRIVATE_SECRET", info.status)

    def test_unavailable_default_appdata_is_not_assumed(self):
        with patch.dict(os.environ, {"APPDATA": ""}):
            self.assertEqual(read_schedule_settings().status, "BLOCKED_SETTINGS_READ")

    def test_known_appdata_path_used_no_file_creation(self):
        with tempfile.TemporaryDirectory() as td, patch.dict(os.environ, {"APPDATA": td}):
            info = read_schedule_settings()
            self.assertEqual(info.status, "DEFAULTS_ONLY")
            self.assertFalse((Path(td)/"TLMTool"/"settings.ini").exists())

    def test_opaque_value_safety_limits(self):
        self.assertTrue(_bounded_opaque_token(None))
        self.assertTrue(_bounded_opaque_token("S40_TEST_UNVERIFIED"))
        self.assertTrue(_bounded_opaque_token("A" * 64))
        self.assertFalse(_bounded_opaque_token("A" * 65))
        self.assertFalse(_bounded_opaque_token("A\nB"))
        self.assertFalse(_bounded_opaque_token("A\rB"))
        self.assertFalse(_bounded_opaque_token("A\x00B"))

    def test_bad_opaque_token_fail_closed_no_implicit_bool_true(self):
        with tempfile.TemporaryDirectory() as td:
            path = self.config(td, "[Settings]\nschedule_on = "+("X"*65)+"\n")
            info = read_schedule_settings(path)
            self.assertEqual(info.status,"BLOCKED_OPAQUE_TOKEN")
            self.assertIsNone(info.schedule_on_raw)
            self.assertFalse(info.preview_available)

    def test_current_f09_settings_are_separate_from_legacy_accounts(self):
        with tempfile.TemporaryDirectory() as td:
            path=self.config(td, "[Settings]\naccounts = |broken|not validated here\n"
                                "schedule_close = 08:00\nschedule_open = 20:00\n")
            info=read_schedule_settings(path)
            self.assertEqual(info.status,"READ_ONLY_VALIDATED")
            self.assertEqual(info.open_hhmm, "20:00")
            self.assertIn("accounts = |broken",path.read_text(encoding="utf-8"))

    def test_readonly_settings_never_writes_or_starts_game(self):
        content=Path(sys.modules["login_schedule_settings"].__file__).read_text(encoding="utf-8")
        for forbidden in ("write_settings(", "subprocess.", "os.system(",
                          "SendMessage(", "PostMessage(", "shutdown.exe",
                          "CreateProcessW(", "Tk(", "Thread("):
            self.assertNotIn(forbidden, content)

    def test_no_guess_missing_bool_from_defaults(self):
        info=ReadOnlyScheduleSettings("DEFAULTS_ONLY", "04:00", "04:20")
        self.assertIsNone(info.schedule_on_raw)
        self.assertIsNone(info.shutdown_after_close_raw)

    def test_disabled_or_bad_load_cannot_preview(self):
        for status in ("BLOCKED_SETTINGS_READ", "BLOCKED_TIME_FORMAT",
                       "BLOCKED_OPAQUE_TOKEN"):
            with self.subTest(status=status):
                with self.assertRaises(RuntimeError):
                    ReadOnlyScheduleSettings(status).preview(datetime(2026,10,9))


if __name__=="__main__":
    unittest.main()
