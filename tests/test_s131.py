"""S131 real original H01 Farm manual buff_N records, never game keys."""
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from farm_buff_settings import (
    BUFF_KEYS, FarmBuffRow, FarmBuffSettingsStore, FarmBuffSettingsError,
)
from farm_town_config import FarmTownSettingsStore
from farm_train_settings import FarmTrainSettingsStore
from farm_town_trade_settings import TownTradeStore
from train_saved_coordinates import FarmCoordinatesStore, FarmCoordinate


class S131OriginalBuffTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory(prefix="S131_BUFF_INI_")
        self.addCleanup(temp.cleanup)
        self.path=Path(temp.name)/"settings.ini"
        self.store=FarmBuffSettingsStore(self.path)

    def row(self,key="F1",enabled=True,minutes="0",seconds="30"):
        return FarmBuffRow(enabled,key,minutes,seconds)

    def test_01_exact_13_original_hotkey_choices(self):
        self.assertEqual(BUFF_KEYS,tuple(f"F{i}" for i in range(1,11))
                         +("1","2","3"))

    def test_02_default_ini_has_no_buff_rows(self):
        self.assertEqual(self.store.load().rows,())

    def test_03_real_buff_1_single_row_roundtrip(self):
        snap=self.store.load()
        self.store.save((self.row(),),expected_bytes=snap.file_bytes)
        self.assertEqual(self.store.load().rows,(self.row(),))
        self.assertIn(b"buff_1 = True|F1|0|30",self.path.read_bytes())

    def test_04_real_four_field_record_order(self):
        self.path.write_bytes(b"[Farm]\nbuff_1=True|F10|5|20\n")
        self.assertEqual(self.store.load().rows,(self.row("F10",True,"5","20"),))

    def test_05_disabled_row_roundtrip_not_auto_pressed(self):
        snap=self.store.load()
        self.store.save((self.row("2",False),),expected_bytes=snap.file_bytes)
        self.assertEqual(self.store.load().rows[0].enabled,False)
        self.assertIn(b"False|2|0|30",self.path.read_bytes())

    def test_06_rows_sorted_by_numeric_ini_suffix(self):
        self.path.write_bytes(b"[Farm]\nbuff_12=True|F2|1|0\n"
                              b"buff_2=False|3|2|3\n")
        self.assertEqual(self.store.load().rows,
                         (self.row("3",False,"2","3"),self.row("F2",True,"1","0")))

    def test_07_saving_renumbers_sequential_buff_N(self):
        self.path.write_bytes(b"[Farm]\nbuff_12=True|F2|1|0\n"
                              b"buff_2=False|3|2|3\n")
        snap=self.store.load()
        self.store.save(snap.rows,expected_bytes=snap.file_bytes)
        c=self.path.read_bytes()
        self.assertIn(b"buff_1 = False|3|2|3",c)
        self.assertIn(b"buff_2 = True|F2|1|0",c)
        self.assertNotIn(b"buff_12",c)

    def test_08_appends_second_buff_real_file(self):
        snap=self.store.load()
        first=self.store.save((self.row(),),expected_bytes=snap.file_bytes)
        self.store.save(first.rows+(self.row("1",False,"1","2"),),
                        expected_bytes=first.file_bytes)
        self.assertEqual([r.key for r in self.store.load().rows],["F1","1"])

    def test_09_remove_renumbers_and_preserves_other_lines(self):
        self.path.write_bytes(b"[Farm]\nother=keep\nbuff_1=True|F1|1|2\n"
                              b"buff_2=False|F4|3|4\n")
        old=self.store.load()
        self.store.save((old.rows[1],),expected_bytes=old.file_bytes)
        c=self.path.read_bytes()
        self.assertIn(b"other=keep",c)
        self.assertIn(b"buff_1 = False|F4|3|4",c)
        self.assertNotIn(b"buff_2",c)

    def test_10_remove_last_buff_really_removes_buff_key(self):
        snap=self.store.load()
        first=self.store.save((self.row(),),expected_bytes=snap.file_bytes)
        self.store.save((),expected_bytes=first.file_bytes)
        self.assertEqual(self.store.load().rows,())

    def test_11_minutes_not_falsely_clamped_59(self):
        self.assertEqual(self.row(minutes="99").validated().minutes,"99")

    def test_12_seconds_not_falsely_clamped_59(self):
        self.assertEqual(self.row(seconds="130").validated().seconds,"130")

    def test_13_negative_and_non_ascii_digits_refused(self):
        for number in ("-1","2.5",""," 2 ","２","seconds","1\n2"):
            with self.subTest(number=number):
                with self.assertRaises(FarmBuffSettingsError):
                    self.row(minutes=number).validated()

    def test_14_unrecognized_hotkey_refused(self):
        for key in ("F11","space","0","4","f1",""):
            with self.subTest(key=key):
                with self.assertRaises(FarmBuffSettingsError):
                    self.row(key=key).validated()

    def test_15_truthy_string_not_bool_rejected(self):
        with self.assertRaises(FarmBuffSettingsError):
            FarmBuffRow("True","F1","0","30").validated()

    def test_16_unknown_field_refused(self):
        with self.assertRaises(FarmBuffSettingsError):
            self.row().change("cmd","press_f1")

    def test_17_duplicate_numeric_index_rejected(self):
        raw=b"[Farm]\nbuff_1=True|F1|0|10\nbuff_01=True|F2|0|20\n"
        self.path.write_bytes(raw)
        with self.assertRaises(FarmBuffSettingsError):
            self.store.load()
        self.assertEqual(self.path.read_bytes(),raw)

    def test_18_index_zero_rejected(self):
        self.path.write_bytes(b"[Farm]\nbuff_0=True|F1|0|20\n")
        with self.assertRaises(FarmBuffSettingsError):
            self.store.load()

    def test_19_malformed_buff_underscore_name_refused(self):
        self.path.write_bytes(b"[Farm]\nbuff_wrong=True|F1|0|20\n")
        with self.assertRaises(FarmBuffSettingsError):
            self.store.load()

    def test_20_malformed_delimiter_fields_refused(self):
        self.path.write_bytes(b"[Farm]\nbuff_1=True|F1|30\n")
        with self.assertRaises(FarmBuffSettingsError):
            self.store.load()

    def test_21_non_original_enabled_word_refused(self):
        self.path.write_bytes(b"[Farm]\nbuff_1=yes|F1|0|30\n")
        with self.assertRaises(FarmBuffSettingsError):
            self.store.load()

    def test_22_duplicate_Farm_section_refused(self):
        self.path.write_bytes(b"[Farm]\nbuff_1=True|F1|0|1\n[Farm]\nother=x\n")
        with self.assertRaises(FarmBuffSettingsError):
            self.store.load()

    def test_23_stale_concurrent_write_rejected_without_data_loss(self):
        snap=self.store.load()
        self.path.write_bytes(b"[Farm]\ntown_condition=cycle\n")
        with self.assertRaises(FarmBuffSettingsError):
            self.store.save((self.row(),),expected_bytes=snap.file_bytes)
        self.assertNotIn(b"buff_1",self.path.read_bytes())

    def test_24_unrelated_sections_preserved_exact(self):
        raw=(b"[Settings]\r\ncredentials=secret\r\n"
             b"[Farm]\r\ntown_condition = cycle\r\n"
             b"respawn = False\r\nbuy_hp = False\r\n"
             b"coord_1 = Name|2|1|2\r\n"
             b"[Party]\r\nparty_after=wait\r\n")
        self.path.write_bytes(raw)
        snap=self.store.load()
        self.store.save((self.row(),),expected_bytes=snap.file_bytes)
        c=self.path.read_bytes()
        for original in (b"credentials=secret\r\n",b"town_condition = cycle\r\n",
                         b"respawn = False\r\n",b"buy_hp = False\r\n",
                         b"coord_1 = Name|2|1|2\r\n",b"party_after=wait\r\n"):
            self.assertIn(original,c)

    def test_25_s128_s129_s130_readers_still_work(self):
        snap=self.store.load()
        self.store.save((self.row(),),expected_bytes=snap.file_bytes)
        self.assertEqual(FarmTownSettingsStore(self.path).load().value.mode,"cycle")
        self.assertFalse(FarmTrainSettingsStore(self.path).load().value.respawn)
        self.assertFalse(TownTradeStore(self.path).load().value.sell_equip)

    def test_26_original_dated_backup_captures_prewrite(self):
        raw=b"[Farm]\nloop_minutes=30\n"
        self.path.write_bytes(raw)
        snap=self.store.load()
        self.store.save((self.row(),),expected_bytes=snap.file_bytes)
        backup=self.path.with_name("settings."+datetime.now().strftime("%Y%m%d")+".ini")
        self.assertEqual(backup.read_bytes(),raw)

    def test_27_noop_does_not_rewrite(self):
        snap=self.store.load()
        result=self.store.save(snap.rows,expected_bytes=snap.file_bytes)
        self.assertEqual(result.file_bytes,snap.file_bytes)

    def test_28_source_has_no_game_input_packet_or_proxy(self):
        s=(ROOT/"src/farm_buff_settings.py").read_text(encoding="utf-8")
        s+=(ROOT/"src/farm_buff_editor.py").read_text(encoding="utf-8")
        for token in ("ReadProcessMemory(", "WriteProcessMemory(", "SendInput(",
                      "PostMessage(", "press_single_key_dll(", "click_at(",
                      "ProxyTab(", "inject_into_pid("):
            self.assertNotIn(token,s)

    def test_29_invalid_rows_never_create_disk_file(self):
        with self.assertRaises(FarmBuffSettingsError):
            self.store.save((self.row("F11"),),expected_bytes=b"")
        self.assertFalse(self.path.exists())

    def test_30_mixed_buffer_rows_do_not_modify_coordinates(self):
        FarmCoordinatesStore(self.path).save((FarmCoordinate("N",2,"5","8"),))
        prior=self.store.load()
        self.store.save((self.row(),),expected_bytes=prior.file_bytes)
        self.assertEqual(FarmCoordinatesStore(self.path).load().rows,
                         (FarmCoordinate("N",2,"5","8"),))


if __name__=="__main__":
    unittest.main()
