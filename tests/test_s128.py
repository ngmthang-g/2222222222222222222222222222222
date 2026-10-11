"""S128 H02 original return-town settings: real file, never game commands."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from farm_town_config import (
    DEFAULT_NAV, NAV_METHODS, TOWN_MODES, TOWN_RADIOS,
    FarmTownConfig, FarmTownSettingsError, FarmTownSettingsStore,
)


class S128TownTests(unittest.TestCase):
    def setUp(self):
        self._temp = tempfile.TemporaryDirectory(prefix="S128_CONFIG_")
        self.addCleanup(self._temp.cleanup)
        self.path = Path(self._temp.name) / "settings.ini"
        self.store = FarmTownSettingsStore(self.path)

    def test_01_original_default_mode_and_30_minutes(self):
        self.assertEqual(self.store.load().value,
                         FarmTownConfig("cycle", "30", DEFAULT_NAV))

    def test_02_original_three_radio_values_only(self):
        self.assertEqual(TOWN_MODES, ("never", "full_bag_timer", "cycle"))
        self.assertEqual(tuple(mode for _, mode in TOWN_RADIOS), TOWN_MODES)

    def test_03_original_nav_options_and_four_defaults(self):
        self.assertEqual(NAV_METHODS, ("", "Phù 1", "Phù 2", "Phù 3", "Ngựa"))
        self.assertEqual(DEFAULT_NAV, NAV_METHODS[1:])

    def test_04_new_save_real_reopen(self):
        snap = self.store.load()
        result = self.store.save(snap.value.change_mode("never"),
                                 expected_bytes=snap.file_bytes)
        self.assertEqual(self.store.load().value.mode, "never")
        self.assertIn(b"town_condition = never", result.file_bytes)
        self.assertIn(b"loop_minutes = 30", result.file_bytes)

    def test_05_switch_mode_retains_period_independent(self):
        cfg = FarmTownConfig().change_minutes("67").change_mode("never")
        self.assertEqual(cfg.minutes, "67")

    def test_06_legacy_full_bag_value_loads_current_radio(self):
        self.path.write_text("[Farm]\ntown_condition = full_bag\n",
                             encoding="utf-8")
        self.assertEqual(self.store.load().value.mode, "full_bag_timer")

    def test_07_legacy_saving_migrates_without_fourth_radio(self):
        self.path.write_text("[Farm]\ntown_condition = full_bag\n",
                             encoding="utf-8")
        snap = self.store.load()
        self.store.save(snap.value, expected_bytes=snap.file_bytes)
        self.assertIn("full_bag_timer", self.path.read_text(encoding="utf-8"))

    def test_08_keep_unrelated_sections_bytes_byte_identical(self):
        original = (b"[Settings]\r\naccount = secret\r\n"
                    b"[Farm]\r\ncoord_1 = A|26|12|34\r\n"
                    b"[Party]\r\nparty_after = wait\r\n")
        self.path.write_bytes(original)
        snap = self.store.load()
        self.store.save(snap.value, expected_bytes=snap.file_bytes)
        raw = self.path.read_bytes()
        self.assertIn(b"[Settings]\r\naccount = secret\r\n", raw)
        self.assertIn(b"coord_1 = A|26|12|34\r\n", raw)
        self.assertIn(b"[Party]\r\nparty_after = wait\r\n", raw)

    def test_09_stale_expected_bytes_blocks_without_write(self):
        snap = self.store.load()
        self.path.write_bytes(b"[Farm]\ncoord_1 = changed|26|1|2\n")
        original = self.path.read_bytes()
        with self.assertRaises(FarmTownSettingsError):
            self.store.save(snap.value, expected_bytes=snap.file_bytes)
        self.assertEqual(self.path.read_bytes(), original)

    def test_10_reopen_saved_four_priority_values(self):
        snap = self.store.load()
        cfg = FarmTownConfig("cycle", "12", ("Ngựa", "Phù 3", "Phù 2", ""))
        self.store.save(cfg, expected_bytes=snap.file_bytes)
        self.assertEqual(self.store.load().value, cfg)

    def test_11_duplicate_priority_forbidden(self):
        with self.assertRaises(FarmTownSettingsError):
            FarmTownConfig("cycle", "30", ("Phù 1", "Phù 1", "", "")).validated()

    def test_12_blank_priority_is_allowed_many_times(self):
        self.assertEqual(FarmTownConfig("never", "0", ("", "", "", "")).validated().navigation,
                         ("", "", "", ""))

    def test_13_invalid_mode_rejected_before_disk(self):
        with self.assertRaises(FarmTownSettingsError):
            self.store.save(FarmTownConfig("other", "30", DEFAULT_NAV),
                            expected_bytes=b"")
        self.assertFalse(self.path.exists())

    def test_14_negative_or_fractional_minutes_not_guessed(self):
        for minutes in ("-1", "1.5", "abc", "", " 30 ", "３"):
            with self.assertRaises(FarmTownSettingsError):
                FarmTownConfig("cycle", minutes, DEFAULT_NAV).validated()

    def test_15_no_invented_min_clamp_of_0(self):
        self.assertEqual(FarmTownConfig("cycle", "0", DEFAULT_NAV).validated().minutes, "0")

    def test_16_malformed_duplicate_Farm_section_refused(self):
        self.path.write_text("[Farm]\nloop_minutes=20\n[Farm]\nloop_minutes=21\n",
                             encoding="utf-8")
        with self.assertRaises(FarmTownSettingsError):
            self.store.load()

    def test_17_duplicate_key_refused_without_destructive_save(self):
        value = b"[Farm]\nloop_minutes=20\nloop_minutes=30\n"
        self.path.write_bytes(value)
        with self.assertRaises(FarmTownSettingsError):
            self.store.load()
        self.assertEqual(self.path.read_bytes(), value)

    def test_18_invalid_existing_value_refused_not_replaced(self):
        value = b"[Farm]\ntown_condition = malicious\n"
        self.path.write_bytes(value)
        with self.assertRaises(FarmTownSettingsError):
            self.store.load()
        self.assertEqual(self.path.read_bytes(), value)

    def test_19_original_date_backup_created(self):
        self.path.write_bytes(b"[Farm]\ntown_condition=cycle\n")
        snap = self.store.load()
        self.store.save(snap.value.change_mode("never"),
                        expected_bytes=snap.file_bytes)
        backup = self.path.with_name("settings." +
                                     datetime.now().strftime("%Y%m%d") + ".ini")
        self.assertEqual(backup.read_bytes(),
                         b"[Farm]\ntown_condition=cycle\n")

    def test_20_second_save_with_no_change_not_write(self):
        snap = self.store.load()
        first = self.store.save(snap.value, expected_bytes=snap.file_bytes)
        second = self.store.save(first.value, expected_bytes=first.file_bytes)
        self.assertEqual(first.file_bytes, second.file_bytes)

    def test_21_save_preserves_existing_unknown_setting(self):
        self.path.write_text("[Farm]\nkeep_mode=all\nloop_minutes=30\n",
                             encoding="utf-8")
        snap = self.store.load()
        self.store.save(snap.value.change_minutes("25"),
                        expected_bytes=snap.file_bytes)
        self.assertIn("keep_mode=all", self.path.read_text(encoding="utf-8"))

    def test_22_selected_priority_change_not_reset_other_priority(self):
        cfg = FarmTownConfig().change_nav(0, "")
        self.assertEqual(cfg.navigation, ("", "Phù 2", "Phù 3", "Ngựa"))

    def test_23_nav_priority_out_of_range_fails(self):
        with self.assertRaises(FarmTownSettingsError):
            FarmTownConfig().change_nav(4, "")

    def test_24_no_false_game_impl_or_proxy(self):
        a = (ROOT / "src/farm_town_config.py").read_text(encoding="utf-8")
        b = (ROOT / "src/farm_town_panel.py").read_text(encoding="utf-8")
        for fragment in ("ReadProcessMemory(", "PostMessage(", "WriteProcessMemory(",
                         "SendInput(", "proxy_tab", "farm_cycle(", "click_at("):
            self.assertNotIn(fragment, a + b)


if __name__ == "__main__":
    unittest.main()
