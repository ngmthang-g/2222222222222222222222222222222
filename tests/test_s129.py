"""S129 source-backed H06/H07/H08/H09 Train setting regression."""
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from farm_train_settings import (
    FarmTrainConfig, FarmTrainSettingsStore, FarmTrainSettingsError,
    KEEP_MODES, KEEP_RADIOS, KEEP_PRESET_KEYS, BUILTIN_HEAL,
    HEAL_DEFAULT, HEAL_BUILTIN_SEPARATOR, HEAL_MANUAL_SEPARATOR,
    heal_options, is_real_heal_destination,
)
from farm_town_config import FarmTownSettingsStore
from train_saved_coordinates import FarmCoordinate, FarmCoordinatesStore


class S129TrainSettingsTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="S129_FARM_TRAIN_")
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "settings.ini"
        self.store = FarmTrainSettingsStore(self.path)

    def test_01_original_four_optin_flags_default_false(self):
        c = self.store.load().value
        self.assertFalse(c.respawn)
        self.assertFalse(c.auto_reconnect)
        self.assertFalse(c.pickup_no_cankhon)
        self.assertFalse(c.trist)

    def test_02_original_keep_three_and_default_all(self):
        self.assertEqual(KEEP_MODES, ("none", "weapons", "all"))
        self.assertEqual(tuple(key for _, key in KEEP_RADIOS), KEEP_MODES)
        self.assertEqual(FarmTrainConfig().pickup_mode, "all")

    def test_03_original_exact_keep_preset_rules(self):
        self.assertEqual(KEEP_PRESET_KEYS, {
            "none": ("discard_weapons", "discard_nonweapon"),
            "weapons": ("discard_nonweapon",), "all": ()})

    def test_04_no_drop_packets_for_keep_all(self):
        self.assertEqual(FarmTrainConfig().pickup_discard_preset_keys(), ())

    def test_05_four_original_heal_city_ids_and_tiles(self):
        self.assertEqual(BUILTIN_HEAL, {
            "Trị liệu Đại Lý": (2,43,178),
            "Trị liệu Lạc Dương": (3,255,126),
            "Trị liệu Tô Châu": (4,155,252),
            "Trị liệu Lâu Lan": (5,294,170),
        })
        self.assertEqual(HEAL_DEFAULT, "Trị liệu Tô Châu")

    def test_06_real_all_six_keys_persist(self):
        snap = self.store.load()
        value = (FarmTrainConfig(respawn=True, auto_reconnect=True,
                                 pickup_no_cankhon=True, trist=True,
                                 pickup_mode="weapons",
                                 heal_map="Trị liệu Đại Lý"))
        returned = self.store.save(value, expected_bytes=snap.file_bytes)
        self.assertEqual(self.store.load().value, value)
        self.assertIn(b"respawn = True", returned.file_bytes)
        self.assertIn(b"pickup_mode = weapons", returned.file_bytes)

    def test_07_bools_read_with_original_configparser_aliases(self):
        self.path.write_text("[Farm]\nrespawn=on\nauto_reconnect=yes\n"
                             "pickup_no_cankhon=1\ntrist=True\n",
                             encoding="utf8")
        snap = self.store.load().value
        self.assertTrue(snap.respawn and snap.auto_reconnect
                        and snap.pickup_no_cankhon and snap.trist)

    def test_08_false_aliases(self):
        self.path.write_text("[Farm]\nrespawn=off\nauto_reconnect=no\n"
                             "pickup_no_cankhon=0\ntrist=False\n",
                             encoding="utf8")
        self.assertEqual(self.store.load().value, FarmTrainConfig())

    def test_09_bad_saved_keep_mode_falls_back_all(self):
        self.path.write_text("[Farm]\npickup_mode=unsupported\n", encoding="utf8")
        self.assertEqual(self.store.load().value.pickup_mode, "all")

    def test_10_current_town_config_and_credential_bytes_unchanged(self):
        raw=(b"[Settings]\r\npassword = secret\r\n"
             b"[Farm]\r\ntown_condition = cycle\r\n"
             b"loop_minutes = 30\r\ncoord_1 = N|26|1|2\r\n"
             b"[Party]\r\nparty_after = wait\r\n")
        self.path.write_bytes(raw)
        snap=self.store.load()
        self.store.save(snap.value.change("respawn",True),
                        expected_bytes=snap.file_bytes)
        output=self.path.read_bytes()
        for span in (b"password = secret\r\n",
                     b"town_condition = cycle\r\n",
                     b"loop_minutes = 30\r\n",
                     b"coord_1 = N|26|1|2\r\n",
                     b"[Party]\r\nparty_after = wait\r\n"):
            self.assertIn(span,output)

    def test_11_s128_town_read_after_s129_write(self):
        snap = self.store.load()
        self.store.save(snap.value.change("trist",True),
                        expected_bytes=snap.file_bytes)
        self.assertEqual(FarmTownSettingsStore(self.path).load().value.mode,
                         "cycle")

    def test_12_stale_concurrent_file_refused(self):
        snap=self.store.load()
        self.path.write_bytes(b"[Farm]\nloop_minutes=41\n")
        with self.assertRaises(FarmTrainSettingsError):
            self.store.save(snap.value, expected_bytes=snap.file_bytes)
        self.assertEqual(self.path.read_bytes(),b"[Farm]\nloop_minutes=41\n")

    def test_13_duplicate_active_train_key_refused(self):
        original=b"[Farm]\nrespawn=False\nrespawn=True\n"
        self.path.write_bytes(original)
        with self.assertRaises(FarmTrainSettingsError):
            self.store.load()
        self.assertEqual(self.path.read_bytes(),original)

    def test_14_duplicate_farm_sections_refused(self):
        self.path.write_bytes(b"[Farm]\nrespawn=True\n[Farm]\ntrist=False\n")
        with self.assertRaises(FarmTrainSettingsError):
            self.store.load()

    def test_15_bad_bool_refused(self):
        self.path.write_bytes(b"[Farm]\nrespawn=indeterminate\n")
        with self.assertRaises(FarmTrainSettingsError):
            self.store.load()

    def test_16_bad_bool_input_wont_write(self):
        with self.assertRaises(FarmTrainSettingsError):
            self.store.save(FarmTrainConfig(respawn="yes"),expected_bytes=b"")
        self.assertFalse(self.path.exists())

    def test_17_invalid_mode_input_not_accepted(self):
        with self.assertRaises(FarmTrainSettingsError):
            FarmTrainConfig().change("pickup_mode","everything")

    def test_18_only_known_keys_can_be_changed(self):
        with self.assertRaises(FarmTrainSettingsError):
            FarmTrainConfig().change("admin","on")

    def test_19_manual_destination_value_held_not_auto_deleted(self):
        value=FarmTrainConfig(heal_map="Preset đã xóa")
        snap=self.store.load()
        self.store.save(value,expected_bytes=snap.file_bytes)
        self.assertEqual(self.store.load().value.heal_map,"Preset đã xóa")

    def test_20_builtin_heal_separators_not_destinations(self):
        values=heal_options(self.path)
        self.assertEqual(values[:2],(HEAL_BUILTIN_SEPARATOR,"Trị liệu Đại Lý"))
        self.assertIn(HEAL_MANUAL_SEPARATOR,values)
        self.assertFalse(is_real_heal_destination(HEAL_BUILTIN_SEPARATOR,values))
        self.assertFalse(is_real_heal_destination(HEAL_MANUAL_SEPARATOR,values))

    def test_21_manual_saved_coordinate_names_populate(self):
        coordstore=FarmCoordinatesStore(self.path)
        coordstore.save((
            FarmCoordinate("Chỗ hồi",2,"33","40"),
            FarmCoordinate("Chỗ hai",4,"155","252"),
        ))
        values=heal_options(self.path)
        self.assertEqual(values[-2:],("Chỗ hồi","Chỗ hai"))
        self.assertTrue(is_real_heal_destination("Chỗ hồi",values))

    def test_22_manual_duplicate_preset_names_fail_closed(self):
        coordstore=FarmCoordinatesStore(self.path)
        coordstore.save((FarmCoordinate("Tên",2,"5","6"),
                         FarmCoordinate("Tên",4,"4","3")))
        with self.assertRaises(FarmTrainSettingsError):
            heal_options(self.path)

    def test_23_separators_cannot_be_manual_names(self):
        FarmCoordinatesStore(self.path).save((
            FarmCoordinate(HEAL_MANUAL_SEPARATOR,2,"1","2"),))
        with self.assertRaises(FarmTrainSettingsError):
            heal_options(self.path)

    def test_24_unknown_map_id_not_silent_heal_target(self):
        self.path.write_bytes(b"[Farm]\ncoord_1=VungCu|999999|1|2\n")
        with self.assertRaises(FarmTrainSettingsError):
            heal_options(self.path)

    def test_25_invalid_heal_control_injection_rejected(self):
        for val in ("A\nB","A\rB","\x00", "a"*181):
            with self.assertRaises(FarmTrainSettingsError):
                FarmTrainConfig(heal_map=val).validated()

    def test_26_real_timestamped_backup(self):
        from datetime import datetime
        original=b"[Farm]\nrespawn=False\n"
        self.path.write_bytes(original)
        snap=self.store.load()
        self.store.save(snap.value.change("respawn",True),
                        expected_bytes=snap.file_bytes)
        backup=self.path.with_name("settings."+
                          datetime.now().strftime("%Y%m%d")+".ini")
        self.assertEqual(backup.read_bytes(),original)

    def test_27_repeated_unchanged_save_no_mutation(self):
        snap=self.store.load()
        first=self.store.save(snap.value,expected_bytes=snap.file_bytes)
        second=self.store.save(first.value,expected_bytes=first.file_bytes)
        self.assertEqual(first.file_bytes,second.file_bytes)

    def test_28_no_game_memory_packet_mouse_proxy(self):
        source=(ROOT/"src/farm_train_settings.py").read_text(encoding="utf8")
        panel=(ROOT/"src/farm_train_panel.py").read_text(encoding="utf8")
        for token in ("ReadProcessMemory(", "WriteProcessMemory(",
                      "SendInput(", "PostMessage(", "discard_items(",
                      "move_character(", "click_at(", "ProxyTab("):
            self.assertNotIn(token,source+panel)


if __name__=="__main__":
    unittest.main()
