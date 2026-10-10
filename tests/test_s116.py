"""S116: credential-safe tests for exact legacy field-only INI persistence."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import tempfile
import unittest

from login_existing_account_edits import (
    ExistingAccountEdit, ExistingAccountEditError, update_existing_accounts,
)

TEST_INI = (
    "[Settings]\n"
    "accounts = UNKNOWN|S116_FAKE_U0|S116_FAKE_P0|Có|opaque-forwarder-value\n"
    "  ?|S116_FAKE_U1|S116_FAKE_P1|Tool|\n"
    "schedule_open = 04:20\n"
    "after_login = wait\n"
    "[Unrelated]\n"
    "keep = 123\n"
)
OLD = ExistingAccountEdit(0, "S116_FAKE_U0", "S116_FAKE_P0",
                          "S116_NEW_U0", "S116_NEW_P0")


class S116ExistingEditTests(unittest.TestCase):
    def file(self, folder, payload=TEST_INI):
        path = Path(folder) / "settings.ini"
        path.write_bytes(payload.encode("utf-8"))
        return path

    def test_01_one_real_legacy_row_edit_changes_exact_columns_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.file(tmp)
            original = p.read_bytes()
            output = update_existing_accounts((OLD,), p)
            self.assertEqual(output, "UPDATED_EXISTING_ACCOUNT_FIELDS_ONLY")
            self.assertEqual(p.read_bytes(), original.replace(
                b"S116_FAKE_U0|S116_FAKE_P0", b"S116_NEW_U0|S116_NEW_P0"))
            self.assertTrue((p.parent / ("settings." + datetime.now().strftime("%Y%m%d") + ".ini")).exists())

    def test_02_all_unedited_fields_and_unknown_auth_proxy_tokens_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.file(tmp)
            update_existing_accounts([OLD], p)
            text = p.read_text()
            self.assertIn("UNKNOWN|S116_NEW_U0|S116_NEW_P0|Có|opaque-forwarder-value", text)
            self.assertIn("?|S116_FAKE_U1|S116_FAKE_P1|Tool|", text)
            self.assertIn("after_login = wait", text)
            self.assertIn("[Unrelated]\nkeep = 123", text)

    def test_03_change_hidden_second_row_while_preserving_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.file(tmp)
            change = ExistingAccountEdit(1, "S116_FAKE_U1", "S116_FAKE_P1",
                                         "S116_HIDDEN_U1", "S116_HIDDEN_P1")
            update_existing_accounts((change,), p)
            self.assertIn("  ?|S116_HIDDEN_U1|S116_HIDDEN_P1|Tool|\n", p.read_text())
            self.assertIn("accounts = UNKNOWN|S116_FAKE_U0|S116_FAKE_P0|Có|opaque-forwarder-value", p.read_text())

    def test_04_batch_two_changes_one_atomic_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.file(tmp)
            second = ExistingAccountEdit(1, "S116_FAKE_U1", "S116_FAKE_P1", "A1", "B1")
            update_existing_accounts([OLD, second], p)
            self.assertIn("UNKNOWN|S116_NEW_U0|S116_NEW_P0|Có", p.read_text())
            self.assertIn("  ?|A1|B1|Tool|", p.read_text())

    def test_05_unchanged_does_not_create_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.file(tmp)
            before = p.read_bytes()
            unchanged = ExistingAccountEdit(0, "S116_FAKE_U0", "S116_FAKE_P0",
                                             "S116_FAKE_U0", "S116_FAKE_P0")
            self.assertEqual(update_existing_accounts([unchanged], p), "UNCHANGED")
            self.assertEqual(p.read_bytes(), before)
            self.assertFalse(list(p.parent.glob("settings.*.ini")))

    def test_06_stale_model_never_overwrites_external_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.file(tmp)
            p.write_bytes(p.read_bytes().replace(b"S116_FAKE_U0", b"EXTERNAL_EDIT"))
            before = p.read_bytes()
            with self.assertRaisesRegex(ExistingAccountEditError, "STALE"):
                update_existing_accounts([OLD], p)
            self.assertEqual(p.read_bytes(), before)

    def test_07_unknown_selection_token_remains_opaque(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.file(tmp)
            update_existing_accounts([OLD], p)
            self.assertEqual(p.read_text().splitlines()[1].split("|")[0],
                             "accounts = UNKNOWN")

    def test_08_no_account_key_no_new_check_token_created(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.file(tmp, "[Settings]\nother = abc\n")
            before = p.read_bytes()
            with self.assertRaisesRegex(ExistingAccountEditError, "AMBIGUOUS"):
                update_existing_accounts([OLD], p)
            self.assertEqual(p.read_bytes(), before)

    def test_09_unknown_existing_captcha_disables_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.file(tmp, TEST_INI.replace("|Có|", "|NeverKnown|"))
            before = p.read_bytes()
            with self.assertRaisesRegex(ExistingAccountEditError, "UNVERIFIED"):
                update_existing_accounts([OLD], p)
            self.assertEqual(p.read_bytes(), before)

    def test_10_ambiguous_duplicate_settings_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.file(tmp, TEST_INI + "[Settings]\na = b\n")
            with self.assertRaisesRegex(ExistingAccountEditError, "AMBIGUOUS"):
                update_existing_accounts([OLD], p)

    def test_11_invalid_delimiters_do_not_leak_or_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.file(tmp)
            before = p.read_bytes()
            for value in ("some|pipe", "some\nnewline", "bad\rline", "\x00"):
                change = ExistingAccountEdit(0, "S116_FAKE_U0", "S116_FAKE_P0",
                                             value, "new")
                with self.subTest(kind=len(value)):
                    with self.assertRaises(ExistingAccountEditError):
                        update_existing_accounts([change], p)
                    self.assertEqual(p.read_bytes(), before)

    def test_12_empty_account_store_cannot_mint_selection_token(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.file(tmp, "[Settings]\naccounts =\n")
            with self.assertRaisesRegex(ExistingAccountEditError, "UNVERIFIED"):
                update_existing_accounts([OLD], p)

    def test_13_bad_index_cannot_change_or_append_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.file(tmp)
            change = ExistingAccountEdit(2, "X", "Y", "X1", "Y1")
            with self.assertRaisesRegex(ExistingAccountEditError, "NOT_AN_EXISTING"):
                update_existing_accounts([change], p)

    def test_14_all_or_nothing_batch_stale_second(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.file(tmp)
            change = ExistingAccountEdit(1, "wrong", "S116_FAKE_P1",
                                         "S116_NEW_U1", "S116_NEW_P1")
            before = p.read_bytes()
            with self.assertRaisesRegex(ExistingAccountEditError, "STALE"):
                update_existing_accounts([OLD, change], p)
            self.assertEqual(p.read_bytes(), before)

    def test_15_windows_crlf_line_endings_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.file(tmp, TEST_INI.replace("\n", "\r\n"))
            before = p.read_bytes()
            update_existing_accounts([OLD], p)
            after = p.read_bytes()
            self.assertEqual(after.count(b"\r\n"), before.count(b"\r\n"))
            self.assertEqual(after.replace(b"S116_NEW_U0|S116_NEW_P0",
                                           b"S116_FAKE_U0|S116_FAKE_P0"), before)

    def test_16_utf8_non_ascii_raw_fields_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.file(tmp)
            new = ExistingAccountEdit(0, "S116_FAKE_U0", "S116_FAKE_P0",
                                      "Tài khoản mẫu", "Mật khẩu giả")
            update_existing_accounts([new], p)
            self.assertIn("Tài khoản mẫu|Mật khẩu giả|Có|opaque", p.read_text())

    def test_17_duplicate_row_changes_and_bool_index_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.file(tmp)
            for changes in ([OLD, OLD], [ExistingAccountEdit(True, "X", "Y", "A", "B")]):
                with self.assertRaises(ExistingAccountEditError):
                    update_existing_accounts(changes, p)

    def test_18_separate_legacy_account_reader_stays_consistent(self):
        from login_account_legacy import read_legacy_accounts
        with tempfile.TemporaryDirectory() as tmp:
            p = self.file(tmp)
            update_existing_accounts([OLD], p)
            res = read_legacy_accounts(p)
            self.assertEqual(res.status, "READY")
            self.assertEqual(res.records[0].username, "S116_NEW_U0")
            self.assertEqual(res.records[0].check_raw, "UNKNOWN")
            self.assertEqual(res.records[0].captcha_raw, "Có")


if __name__ == "__main__":
    unittest.main()
