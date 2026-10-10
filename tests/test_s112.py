"""S112 F10 exact post-login original value persistence; NEVER run game actions."""
from __future__ import annotations
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from login_after_login_choice import (
    AFTER_CHOICES, ALLOWED_VALUES, AfterLoginChoiceError,
    TLMLoginAfterLoginChoice, read_after_login_choice, save_after_login_choice,
)
from settings_store import read_settings


class S112ChoiceTests(unittest.TestCase):
    def cfg(self, td, data):
        p=Path(td)/"TLMTool"/"settings.ini"
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(data)
        return p

    def test_01_exact_original_values_and_labels(self):
        self.assertEqual(AFTER_CHOICES, (
            ("Chờ","wait"), ("Party","party"), ("Train","train"),
            ("Train LSV","train_lsv"), ("Dồn vàng","don")))
        self.assertEqual(ALLOWED_VALUES,{"wait","party","train","train_lsv","don"})

    def test_02_default_wait_if_file_absent(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"none.ini"
            self.assertEqual(read_after_login_choice(p),("wait","READ_ONLY_VERIFIED_CHOICE"))
            self.assertFalse(p.exists())

    def test_03_read_existing_exact_choice(self):
        with tempfile.TemporaryDirectory() as td:
            for value in ALLOWED_VALUES:
                with self.subTest(mode=value):
                    p=self.cfg(td,("[Settings]\nafter_login = "+value+"\n").encode())
                    self.assertEqual(read_after_login_choice(p)[0],value)

    def test_04_roundtrip_each_choice_preserves_unrelated_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            for value in ALLOWED_VALUES:
                raw=(b"[Settings]\r\naccounts = ?|a|secret|Co|opaque\r\n"
                     b" ?|b|secret2|Tool|opaque\r\nschedule_on = UNKNOWN\r\n"
                     b"after_login = wait\r\n[Other]\r\nx=5\r\n")
                p=self.cfg(td,raw)
                result=save_after_login_choice(value,p)
                self.assertEqual(p.read_bytes(),raw.replace(b"after_login = wait",
                                                            ("after_login = "+value).encode()))
                self.assertIn(result,("UNCHANGED","UPDATED_AFTER_LOGIN_ONLY"))
                self.assertEqual(read_settings(p).get("Settings","after_login"),value)

    def test_05_no_duplicate_or_guessing_invalid_values(self):
        with tempfile.TemporaryDirectory() as td:
            p=self.cfg(td,b"[Settings]\nafter_login=wait\n")
            raw=p.read_bytes()
            for value in ("", "Don", "Dồn vàng", "auto", "WAIT", "off", "dOn", 1):
                with self.subTest(value=value):
                    with self.assertRaises(AfterLoginChoiceError):
                        save_after_login_choice(value,p)
            self.assertEqual(p.read_bytes(),raw)

    def test_06_insert_under_original_settings_only(self):
        with tempfile.TemporaryDirectory() as td:
            p=self.cfg(td,b"[Settings]\naccounts=x\n[Other]\ny=1\n")
            save_after_login_choice("party",p)
            self.assertEqual(p.read_bytes(),
                             b"[Settings]\naccounts=x\nafter_login = party\n[Other]\ny=1\n")

    def test_07_missing_file_new_settings_key(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"TLMTool"/"settings.ini"
            self.assertEqual(save_after_login_choice("don",p),"UPDATED_AFTER_LOGIN_ONLY")
            self.assertEqual(p.read_text(),"[Settings]\nafter_login = don\n")

    def test_08_read_invalid_saved_choice_blocks_not_convert(self):
        with tempfile.TemporaryDirectory() as td:
            p=self.cfg(td,b"[Settings]\nafter_login = legacy_unknown\n")
            self.assertEqual(read_after_login_choice(p),("", "UNKNOWN_SAVED_DESTINATION"))
            with self.assertRaisesRegex(AfterLoginChoiceError,"UNKNOWN_SAVED_DESTINATION"):
                save_after_login_choice("wait",p)

    def test_09_duplicate_after_login_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            raw=b"[Settings]\nafter_login=wait\nafter_login=don\n"
            p=self.cfg(td,raw)
            with self.assertRaisesRegex(AfterLoginChoiceError,"DUPLICATE"):
                save_after_login_choice("party",p)
            self.assertEqual(p.read_bytes(),raw)

    def test_10_duplicate_settings_sections_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            raw=b"[Settings]\nafter_login=wait\n[Settings]\nother=1\n"
            p=self.cfg(td,raw)
            with self.assertRaisesRegex(AfterLoginChoiceError,"DUPLICATE_SETTINGS"):
                save_after_login_choice("party",p)
            self.assertEqual(p.read_bytes(),raw)

    def test_11_account_continuation_cannot_be_reinterpreted(self):
        with tempfile.TemporaryDirectory() as td:
            raw=b"[Settings]\naccounts = a|b|c\n  after_login=don\n"
            p=self.cfg(td,raw)
            with self.assertRaisesRegex(AfterLoginChoiceError,"AMBIGUOUS"):
                save_after_login_choice("party",p)
            self.assertEqual(p.read_bytes(),raw)

    def test_12_non_utf8_bom_and_non_ini_fail(self):
        with tempfile.TemporaryDirectory() as td:
            for raw in (b"[Settings]\nx=\xff\n",
                        b"\xef\xbb\xbf[Settings]\nafter_login=wait\n",
                        b"garbage\n"):
                with self.subTest(raw=raw):
                    p=self.cfg(td,raw)
                    with self.assertRaises(AfterLoginChoiceError):
                        save_after_login_choice("wait",p)
                    self.assertEqual(p.read_bytes(),raw)

    def test_13_unchanged_no_backup_changed_creates_original_backup(self):
        with tempfile.TemporaryDirectory() as td:
            raw=b"[Settings]\nafter_login=wait\n"
            p=self.cfg(td,raw)
            self.assertEqual(save_after_login_choice("wait",p),"UNCHANGED")
            self.assertEqual(len(list(p.parent.glob("settings.*.ini"))),0)
            self.assertEqual(save_after_login_choice("party",p),"UPDATED_AFTER_LOGIN_ONLY")
            self.assertEqual(len(list(p.parent.glob("settings.*.ini"))),1)
            self.assertEqual(list(p.parent.glob("settings.*.ini"))[0].read_bytes(),raw)

    def test_14_tk_save_stubs_updates_only_on_success(self):
        class V:
            def __init__(self,txt):self.v=txt
            def get(self):return self.v
            def set(self,x):self.v=x
        with tempfile.TemporaryDirectory() as td:
            p=self.cfg(td,b"[Settings]\nafter_login=wait\n")
            obj=object.__new__(TLMLoginAfterLoginChoice)
            obj._closed=False;obj._path=p;obj._show_error=None
            obj._stored="wait";obj.selection_var=V("don")
            self.assertTrue(obj._change_selection())
            self.assertEqual(obj.last_status,"UPDATED_AFTER_LOGIN_ONLY")
            self.assertEqual(obj._stored,"don")
            self.assertEqual(read_after_login_choice(p)[0],"don")

    def test_15_tk_rollback_on_unverified_target_or_closed(self):
        class V:
            def __init__(self,v):self.v=v
            def get(self):return self.v
            def set(self,v):self.v=v
        with tempfile.TemporaryDirectory() as td:
            raw=b"[Settings]\nafter_login=unknown\n"
            p=self.cfg(td,raw)
            errors=[]
            obj=object.__new__(TLMLoginAfterLoginChoice)
            obj._closed=False;obj._path=p;obj._show_error=lambda *a: errors.append(a)
            obj._stored="wait";obj.selection_var=V("party")
            self.assertFalse(obj._change_selection())
            self.assertEqual(obj.selection_var.get(),"wait")
            self.assertEqual(obj.last_status,"BLOCKED_AFTER_LOGIN_SAVE")
            self.assertEqual(len(errors),1)
            self.assertEqual(p.read_bytes(),raw)
            obj.shutdown();self.assertFalse(obj._change_selection())

if __name__ == "__main__":
    unittest.main()
