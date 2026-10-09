"""S38 F02/F03 fail-closed READ-ONLY legacy account loading tests."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from login_account_legacy import (
    LegacyAccountRecord, MAX_LEGACY_ROWS, parse_legacy_accounts,
    read_legacy_accounts,
)
from login_account_rows import TLMAccountRows


class S38LegacyReadOnlyTests(unittest.TestCase):
    def test_verified_five_field_order(self):
        x = parse_legacy_accounts("MYSTERY|user|pass|Tool|proxy")
        self.assertEqual(x.status, "READY")
        self.assertEqual(x.records, (
            LegacyAccountRecord("MYSTERY", "user", "pass", "Tool", "proxy"),
        ))

    def test_no_guess_for_checkbox_boolean_token(self):
        for token in ("True", "False", "1", "0", "✅", "LEGACY_UNKNOWN"):
            with self.subTest(token=token):
                x = parse_legacy_accounts(token+"|u|p|Không|")
                self.assertEqual(x.status, "READY")
                self.assertEqual(x.records[0].check_raw, token)
                self.assertIsInstance(x.records[0].check_raw, str)

    def test_legacy_co_preserved_without_translation(self):
        x = parse_legacy_accounts("O|u|p|Có|proxy")
        self.assertEqual(x.status, "READY")
        self.assertEqual(x.records[0].captcha_raw, "Có")

    def test_password_whitespace_preserved(self):
        x = parse_legacy_accounts("O| u | a b  |Proxy|")
        self.assertEqual(x.records[0].username, " u ")
        self.assertEqual(x.records[0].password, " a b  ")

    def test_100_original_rows_supported(self):
        raw = "\n".join("O|u|p|Tool|" for _ in range(100))
        x = parse_legacy_accounts(raw)
        self.assertEqual(x.status, "READY")
        self.assertEqual(x.count, MAX_LEGACY_ROWS)

    def test_101_rows_block_entire_batch(self):
        x = parse_legacy_accounts("\n".join("O|u|p|Tool|" for _ in range(101)))
        self.assertEqual(x.status, "BLOCKED_CAPACITY")
        self.assertEqual(x.records, ())

    def test_empty_key_or_absent_payload(self):
        self.assertEqual(parse_legacy_accounts("").status, "EMPTY")
        self.assertEqual(parse_legacy_accounts(None).status, "BLOCKED_FORMAT")

    def test_one_optional_trailing_row_separator(self):
        self.assertEqual(parse_legacy_accounts("O|u|p|Tool|\n").count, 1)
        self.assertEqual(parse_legacy_accounts("O|u|p|Tool|\n\n").status, "BLOCKED_FORMAT")

    def test_malformed_pipe_extra_fields_never_partial_load(self):
        x = parse_legacy_accounts("O|ok|pw|Tool|\nO|bad|a|b|Tool|")
        self.assertEqual(x.status, "BLOCKED_FORMAT")
        self.assertEqual(x.records, ())

    def test_missing_fields_and_blank_rows_refused(self):
        for raw in ("O|user|pwd|Tool", "O|user|pwd|Tool|\n\nO|u|p|Tool|",
                    "|u|p|Tool|", "\nO|u|p|Tool|"):
            with self.subTest(length=len(raw)):
                self.assertEqual(parse_legacy_accounts(raw).records, ())
                self.assertEqual(parse_legacy_accounts(raw).status, "BLOCKED_FORMAT")

    def test_unknown_captcha_fails_closed(self):
        x = parse_legacy_accounts("O|u|p|NO_GUESS|")
        self.assertEqual(x.status, "BLOCKED_CAPTCHA")
        self.assertEqual(x.records, ())

    def test_newline_null_and_carriage_refused(self):
        for raw in ("O|u|p|Tool|\r", "O|u|p|Tool|\x00"):
            self.assertEqual(parse_legacy_accounts(raw).status, "BLOCKED_FORMAT")

    def test_read_ini_without_byte_mutation(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"settings.ini"
            p.write_text("[Settings]\naccounts = X|u|p|Có|opaque\n"
                         "  Y|u2|p2|Không|\n"
                         "game_dir = C:/fake\n[Unrelated]\nkeep = yes\n",
                         encoding="utf-8")
            before=p.read_bytes()
            x=read_legacy_accounts(p)
            self.assertEqual(x.status, "READY")
            self.assertEqual(x.count,2)
            self.assertEqual(x.records[1].username,"u2")
            self.assertEqual(p.read_bytes(), before)

    def test_missing_config_is_not_created(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"absent.ini"
            self.assertEqual(read_legacy_accounts(p).status,"EMPTY")
            self.assertFalse(p.exists())

    def test_broken_ini_fail_closed_and_no_secret_in_status(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"settings.ini"
            secret="S38_TEST_SECRET"
            p.write_text("BROKEN "+secret+"\n",encoding="utf-8")
            x=read_legacy_accounts(p)
            self.assertEqual(x.status,"BLOCKED_READ")
            self.assertEqual(x.records,())
            self.assertNotIn(secret,x.status)

    def test_legacy_hydration_has_no_account_file_writer(self):
        source=Path(sys.modules["login_account_legacy"].__file__).read_text(encoding="utf-8")
        self.assertNotIn("write_settings(",source)
        self.assertNotIn("print(",source)
        source2=Path(sys.modules["login_account_rows"].__file__).read_text(encoding="utf-8")
        self.assertNotIn("save_accounts(",source2)
        self.assertNotIn("write_settings(",source2)

    def test_hydration_rejects_unsafe_before_changing_widgets(self):
        model=TLMAccountRows.__new__(TLMAccountRows)
        model._closed=False
        with self.assertRaises(ValueError):
            model.hydrate_legacy_read_only([
                LegacyAccountRecord("X","u","p","INVALID","")
            ])
        with self.assertRaises(ValueError):
            model.hydrate_legacy_read_only([
                LegacyAccountRecord("X","u","p","Không","")
            ]*101)


if __name__=="__main__":
    unittest.main()
