"""S120 original source maps and H11 disk integration regressions."""
from __future__ import annotations
import pathlib
import sys
import tempfile
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from farm_original_maps import (FARM_MAP_LIST,FARM_MAP_ID_TO_NAME,FARM_MAP_NAME_TO_ID,
    SEPARATOR,coord_id_for_name,coord_name_for_id)
from train_saved_coordinates import FarmCoordinate,FarmCoordinateError,FarmCoordinatesStore

class S120OriginalMapTests(unittest.TestCase):
    def test_01_total_entries(self):
        self.assertEqual(len(FARM_MAP_LIST),72)
        self.assertEqual(sum(mid is None for _,mid in FARM_MAP_LIST),5)
        self.assertEqual(len(FARM_MAP_ID_TO_NAME),67)
    def test_02_first_four_cities(self):
        self.assertEqual(FARM_MAP_LIST[:5],(("Đại Lý",2),("Lạc Dương",3),
            ("Tô Châu",4),("Lâu Lan",5),(SEPARATOR,None)))
    def test_03_original_dungeon_group(self):
        self.assertEqual(FARM_MAP_LIST[5:8],(("Phó Bản-Thiên Sơn",1300),
            ("Phó Bản-Núi Võ Đang",1400),("Phó Bản-Đường Môn",1700)))
    def test_04_exact_original_west_lake_not_client_2600(self):
        self.assertEqual(coord_id_for_name("Tây Hồ"),26)
        self.assertIsNone(coord_id_for_name("Dạ Tây Hồ"))
        self.assertIsNone(coord_name_for_id(2600))
    def test_05_other_client_name_mismatches_not_fuzzy_converted(self):
        self.assertEqual(coord_id_for_name("Yến Vương Cổ Mộ 1"),33)
        self.assertIsNone(coord_id_for_name("Yến Vương Cổ Mộ Tầng 1"))
        self.assertEqual(coord_id_for_name("Tiên Vương Thần"),46)
        self.assertIsNone(coord_id_for_name("Tiên Vương Phần"))
        self.assertEqual(coord_id_for_name("Ngân Nhai Tuyết Nguyên"),47)
        self.assertIsNone(coord_id_for_name("Ngân Ngai Tuyết Nguyên"))
    def test_06_ending_labels(self):
        self.assertEqual(FARM_MAP_LIST[-3:],
            (("Võ Di",83),("Nam Hải",85),("Quỳnh Châu",86)))
    def test_07_no_guessed_map58(self):
        self.assertIsNone(coord_name_for_id(58))
    def test_08_67_bidirectional_pairs_exact_and_unique(self):
        for name,mid in FARM_MAP_LIST:
            if mid is not None:
                self.assertEqual(coord_name_for_id(mid),name)
                self.assertEqual(coord_id_for_name(name),mid)
    def test_09_separator_invalid_boolean_and_unknown(self):
        self.assertIsNone(coord_id_for_name(SEPARATOR))
        self.assertIsNone(coord_id_for_name(None))
        self.assertIsNone(coord_name_for_id(None))
        self.assertIsNone(coord_name_for_id(True))
    def test_10_immutable_mapping(self):
        with self.assertRaises(TypeError):
            FARM_MAP_ID_TO_NAME[26]="Different"
        with self.assertRaises(TypeError):
            FARM_MAP_NAME_TO_ID["Fake"]=999
    def test_11_default_source_map_ids_write_real_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            p=pathlib.Path(td)/"settings.ini"
            original=b"[Settings]\r\naccounts = ORIGINAL_DUMMY\r\n[Farm]\r\nkeep = yes\r\n"
            p.write_bytes(original)
            store=FarmCoordinatesStore(p)
            rows=(FarmCoordinate("Train",26,"15","35"),
                  FarmCoordinate("Quỳnh Châu",86,"a","b"),
                  FarmCoordinate("Dungeon",1700,"9","0"))
            self.assertEqual(store.save(rows),"SAVED_FARM_COORDINATES")
            self.assertEqual(store.load().rows,rows)
            saved=p.read_bytes()
            self.assertIn(b"accounts = ORIGINAL_DUMMY\r\n",saved)
            self.assertIn(b"keep = yes\r\n",saved)
    def test_12_client_only_id_cannot_be_written(self):
        with tempfile.TemporaryDirectory() as td:
            store=FarmCoordinatesStore(pathlib.Path(td)/"settings.ini")
            with self.assertRaises(FarmCoordinateError):
                store.save((FarmCoordinate("Client only",2600,"1","2"),))
    def test_13_stale_client_id_skipped_on_read(self):
        with tempfile.TemporaryDirectory() as td:
            p=pathlib.Path(td)/"settings.ini"
            p.write_text("[Farm]\ncoord_1 = Wrong|2600|1|2\ncoord_2 = Good|26|1|2\n",
                         encoding="utf-8")
            loaded=FarmCoordinatesStore(p).load()
            self.assertEqual(loaded.rows,(FarmCoordinate("Good",26,"1","2"),))
            self.assertEqual(loaded.skipped_retired_map_ids,(2600,))
    def test_14_preserve_original_ui_order_not_sort_by_id(self):
        self.assertEqual(FARM_MAP_LIST[5][1],1300)
        self.assertEqual(FARM_MAP_LIST[9][1],19)
    def test_15_no_auth_proxy_or_game_actions(self):
        text=(ROOT/"src/farm_original_maps.py").read_text(encoding="utf-8")
        for forbidden in ("ReadProcessMemory(", "PostMessage(", "TOKEN_HMAC_SECRET",
                          "ProxyServer(", "CreateRemoteThread("):
            self.assertNotIn(forbidden,text)
    def test_16_S119_now_defaults_to_original_map_registry(self):
        text=(ROOT/"src/train_saved_coordinates.py").read_text(encoding="utf-8")
        self.assertIn("from farm_original_maps import FARM_MAP_ID_TO_NAME",text)
        self.assertIn("if known_map_ids is None:",text)

if __name__=="__main__":
    unittest.main()
