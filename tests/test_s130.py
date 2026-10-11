"""S130 original H01/H02/B05 verified town trading settings, NO game."""
from __future__ import annotations
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
from farm_town_trade_settings import (
    TownTradeStore, TownTradeConfig, FarmTownTradeError,
    TRADE_KEYS, SELL_MAP_LIST, HP_ITEMS, MP_ITEMS, town_destination_choices,
)
from farm_town_config import FarmTownSettingsStore
from farm_train_settings import FarmTrainSettingsStore
from train_saved_coordinates import FarmCoordinatesStore, FarmCoordinate


class S130OriginalTownTradeTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory(prefix="S130_TOWN_IO_")
        self.addCleanup(tmp.cleanup)
        self.path=Path(tmp.name)/"settings.ini"
        self.store=TownTradeStore(self.path)

    def test_01_exact_ten_original_saved_keys(self):
        self.assertEqual(TRADE_KEYS,(
            "sell_equip","sell_map","sell_tab","buy_hp","hp_item",
            "hp_qty","buy_mp","mp_item","mp_qty","meds_map"))

    def test_02_direct_frozen_original_four_shop_towns(self):
        self.assertEqual(SELL_MAP_LIST,("Đại Lý","Lạc Dương","Tô Châu","Lâu Lan"))

    def test_03_original_hp_medicine_names(self):
        self.assertEqual(HP_ITEMS,("Hành huyết tán","Hoạt huyết tán","Kim sang dược"))

    def test_04_original_mp_medicine_names(self):
        self.assertEqual(MP_ITEMS,("Hành khí tán","Hoài linh đan","Qui linh hoàn"))

    def test_05_conservative_unknown_defaults_not_auto_actions(self):
        value=self.store.load().value
        self.assertFalse(value.sell_equip or value.buy_hp or value.buy_mp)
        self.assertEqual(value.sell_map,"")
        self.assertEqual(value.meds_map,"")

    def test_06_real_roundtrip_all_ten_keys(self):
        config=TownTradeConfig(
            sell_equip=True,sell_map="Đại Lý",sell_tab="4",
            buy_hp=True,hp_item="Kim sang dược",hp_qty="60",
            buy_mp=True,mp_item="Qui linh hoàn",mp_qty="70",
            meds_map="Tô Châu")
        prior=self.store.load()
        saved=self.store.save(config,expected_bytes=prior.file_bytes)
        self.assertEqual(self.store.load().value,config)
        self.assertIn(b"sell_equip = True",saved.file_bytes)
        self.assertIn(b"hp_qty = 60",saved.file_bytes)
        self.assertIn(b"mp_qty = 70",saved.file_bytes)

    def test_07_two_booleans_and_numeric_changes_separately(self):
        c=TownTradeConfig().change("buy_hp",True).change("hp_qty","17")
        self.assertTrue(c.buy_hp)
        self.assertFalse(c.buy_mp)
        self.assertEqual(c.hp_qty,"17")

    def test_08_original_numeric_fields_only_accept_decimal(self):
        for bad in ("-5","3.5"," 50 ","","一百","x","１"):
            for key in ("sell_tab","hp_qty","mp_qty"):
                with self.subTest(bad=bad,key=key):
                    with self.assertRaises(FarmTownTradeError):
                        TownTradeConfig().change(key,bad)

    def test_09_no_guessed_qty_clamp(self):
        self.assertEqual(TownTradeConfig().change("hp_qty","000").hp_qty,"000")

    def test_10_preserve_unrelated_train_town_party_login_bytes(self):
        raw=(b"[Settings]\r\npassword = personal\r\n"
             b"[Farm]\r\ntown_condition = cycle\r\nloop_minutes = 30\r\n"
             b"respawn = False\r\npickup_mode = all\r\n"
             b"coord_1 = First|2|1|2\r\n"
             b"[Party]\r\nparty_after = wait\r\n")
        self.path.write_bytes(raw)
        prev=self.store.load()
        self.store.save(prev.value.change("buy_hp",True),
                        expected_bytes=prev.file_bytes)
        nextdata=self.path.read_bytes()
        for snippet in (
            b"password = personal\r\n",b"town_condition = cycle\r\n",
            b"respawn = False\r\n",b"coord_1 = First|2|1|2\r\n",
            b"party_after = wait\r\n"):
            self.assertIn(snippet,nextdata)

    def test_11_S128_town_store_remains_valid_after_S130(self):
        prev=self.store.load()
        self.store.save(prev.value.change("buy_hp",True),
                        expected_bytes=prev.file_bytes)
        self.assertEqual(FarmTownSettingsStore(self.path).load().value.mode,"cycle")

    def test_12_S129_train_store_remains_valid_after_S130(self):
        prev=self.store.load()
        self.store.save(prev.value.change("buy_mp",True),
                        expected_bytes=prev.file_bytes)
        self.assertEqual(FarmTrainSettingsStore(self.path).load().value.pickup_mode,"all")

    def test_13_saved_config_booleans_case_insensitive(self):
        self.path.write_bytes(b"[Farm]\nsell_equip=yes\nbuy_hp=1\nbuy_mp=ON\n")
        o=self.store.load().value
        self.assertTrue(o.sell_equip and o.buy_hp and o.buy_mp)

    def test_14_saved_malformed_boolean_rejected(self):
        self.path.write_bytes(b"[Farm]\nsell_equip=maybe\n")
        with self.assertRaises(FarmTownTradeError):
            self.store.load()

    def test_15_duplicated_trading_key_rejected(self):
        content=b"[Farm]\nsell_tab=1\nsell_tab=2\n"
        self.path.write_bytes(content)
        with self.assertRaises(FarmTownTradeError):
            self.store.load()
        self.assertEqual(self.path.read_bytes(),content)

    def test_16_duplicate_Farm_section_rejected(self):
        self.path.write_bytes(b"[Farm]\nsell_tab=1\n[Farm]\nsell_tab=2\n")
        with self.assertRaises(FarmTownTradeError):
            self.store.load()

    def test_17_stale_write_rejected_without_overwrite(self):
        prev=self.store.load()
        self.path.write_bytes(b"[Farm]\ncoord_1=Updated|2|1|2\n")
        current=self.path.read_bytes()
        with self.assertRaises(FarmTownTradeError):
            self.store.save(prev.value,expected_bytes=prev.file_bytes)
        self.assertEqual(self.path.read_bytes(),current)

    def test_18_bad_hp_item_rejected_before_any_write(self):
        with self.assertRaises(FarmTownTradeError):
            self.store.save(TownTradeConfig(hp_item="fake"),
                            expected_bytes=b"")
        self.assertFalse(self.path.exists())

    def test_19_bad_mp_item_rejected(self):
        with self.assertRaises(FarmTownTradeError):
            TownTradeConfig().change("mp_item","fake")

    def test_20_unknown_key_not_written(self):
        with self.assertRaises(FarmTownTradeError):
            TownTradeConfig().change("db_password","x")

    def test_21_new_saved_coordinate_in_sell_med_choices(self):
        FarmCoordinatesStore(self.path).save((
            FarmCoordinate("Quầy 1",2,"1","2"),
            FarmCoordinate("Quầy 2",4,"3","4")))
        choices=town_destination_choices(self.path)
        self.assertEqual(choices[:4],SELL_MAP_LIST)
        self.assertEqual(choices[-2:],("Quầy 1","Quầy 2"))

    def test_22_retired_map_id_not_interpreted_as_real_destination(self):
        self.path.write_bytes(b"[Farm]\ncoord_1=Old|999999|1|2\n")
        with self.assertRaises(FarmTownTradeError):
            town_destination_choices(self.path)

    def test_23_ambiguous_manual_name_rejected(self):
        FarmCoordinatesStore(self.path).save((
            FarmCoordinate("Same",2,"1","2"),
            FarmCoordinate("Same",4,"3","4")))
        with self.assertRaises(FarmTownTradeError):
            town_destination_choices(self.path)

    def test_24_reserved_builtin_city_label_not_reused_by_manual_preset(self):
        FarmCoordinatesStore(self.path).save((
            FarmCoordinate("Lạc Dương",2,"1","2"),))
        with self.assertRaises(FarmTownTradeError):
            town_destination_choices(self.path)

    def test_25_renamed_manual_saved_target_stays_in_ini_not_deleted(self):
        prev=self.store.load()
        self.store.save(prev.value.change("meds_map","Removed preset"),
                        expected_bytes=prev.file_bytes)
        self.assertEqual(self.store.load().value.meds_map,"Removed preset")

    def test_26_original_settings_dated_prewrite_backup(self):
        raw=b"[Farm]\nbuy_hp=False\n"
        self.path.write_bytes(raw)
        prev=self.store.load()
        self.store.save(prev.value.change("buy_hp",True),
                        expected_bytes=prev.file_bytes)
        backup=self.path.with_name("settings."+
                   datetime.now().strftime("%Y%m%d")+".ini")
        self.assertEqual(backup.read_bytes(),raw)

    def test_27_noop_save_no_change(self):
        snap=self.store.load()
        first=self.store.save(snap.value,expected_bytes=snap.file_bytes)
        second=self.store.save(first.value,expected_bytes=first.file_bytes)
        self.assertEqual(first.file_bytes,second.file_bytes)

    def test_28_original_module_has_no_game_packet_or_click(self):
        text=(ROOT/"src/farm_town_trade_settings.py").read_text(encoding="utf8")
        text+=(ROOT/"src/farm_town_trade_panel.py").read_text(encoding="utf8")
        for forbidden in ("ReadProcessMemory(", "WriteProcessMemory(", "PostMessage(",
                          "SendInput(", "sell_inst_fire(", "RequestSellItem(",
                          "click_at(", "ProxyTab("):
            self.assertNotIn(forbidden,text)


if __name__=="__main__":
    unittest.main()
