"""S37 original F01 real in-memory account row selector model; no persistence."""
from __future__ import annotations
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from login_account_rows import (
    AccountSelectionModel,MAX_ACCOUNT_ROWS,CAPTCHA_MODES,ROW_PITCH,
)


class S37Tests(unittest.TestCase):
    def test_fixed_capacity_matches_original(self):
        m=AccountSelectionModel()
        self.assertEqual(len(m._checks),100)
        self.assertEqual(MAX_ACCOUNT_ROWS,100)

    def test_no_arbitrary_smaller_capacity_that_might_delete_accounts(self):
        for value in (0,1,17,99,101,True):
            with self.subTest(value=value),self.assertRaises(ValueError):
                AccountSelectionModel(value)

    def test_defaults_all_rows_unchecked(self):
        m=AccountSelectionModel()
        self.assertEqual(m.selected_count,0)
        self.assertTrue(all(not m.checked(i) for i in range(100)))

    def test_row_zero_toggle_changes_only_that_row(self):
        m=AccountSelectionModel()
        self.assertTrue(m.toggle(0))
        self.assertTrue(m.checked(0))
        self.assertFalse(m.checked(1))
        self.assertEqual(m.selected_count,1)

    def test_last_row_toggle_really_exists(self):
        m=AccountSelectionModel()
        self.assertTrue(m.toggle(99))
        self.assertTrue(m.checked(99))
        self.assertFalse(m.checked(98))

    def test_toggle_twice_returns_to_unchecked(self):
        m=AccountSelectionModel()
        m.toggle(37)
        self.assertFalse(m.toggle(37))
        self.assertEqual(m.selected_count,0)

    def test_header_any_unchecked_selects_every_row(self):
        m=AccountSelectionModel()
        m.toggle(3)
        self.assertTrue(m.toggle_all())
        self.assertEqual(m.selected_count,100)

    def test_header_all_checked_clears_every_row(self):
        m=AccountSelectionModel()
        m.toggle_all()
        self.assertFalse(m.toggle_all())
        self.assertEqual(m.selected_count,0)

    def test_header_first_click_checks_all(self):
        m=AccountSelectionModel()
        self.assertTrue(m.toggle_all())
        self.assertTrue(all(m.checked(i) for i in range(100)))

    def test_partial_after_all_select_again_checks_all(self):
        m=AccountSelectionModel()
        m.toggle_all()
        m.toggle(56)
        self.assertTrue(m.toggle_all())
        self.assertEqual(m.selected_count,100)

    def test_exact_original_captcha_choices_not_legacy_migration(self):
        self.assertEqual(CAPTCHA_MODES,("Không","Tool","Proxy"))
        self.assertNotIn("Có",CAPTCHA_MODES)

    def test_row_pitch_matches_original_evidence(self):
        self.assertEqual(ROW_PITCH,35)

    def test_no_disk_persistence_or_proxy_runtime_in_model(self):
        text=Path(sys.modules["login_account_rows"].__file__).read_text(encoding="utf-8")
        for forbidden in ("write_settings(", "save_accounts(", "subprocess.run(",
                          "CreateProcessW(", "ProxyTab("):
            self.assertNotIn(forbidden,text)

    def test_bad_row_index_is_not_wrapped_silently(self):
        m=AccountSelectionModel()
        with self.assertRaises(IndexError):
            m.toggle(100)
        with self.assertRaises(IndexError):
            m.checked(100)

if __name__=="__main__":
    unittest.main()
