"""S170: offline Train LSV I10 numeric-map saved-coordinate editor tests.

No game or original licensing. Existing S169 top INI can coexist.
"""
from __future__ import annotations
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))

from train_lsv_coordinates import (
    LSV_MAP_IDS, LSV_MAP_NAMES, TrainLsvCoordinatesStore,
    TrainLsvCoordinateError,
)
from train_lsv_top_settings import TrainLsvTopStore
from TLMToolIndependent import make_independent_builders
from start_polling import StartWindowProducer


class S170Coordinates(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix="S170_")
        self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/"settings.ini"
        self.store=TrainLsvCoordinatesStore(self.path)

    def put(self, data):
        self.path.write_bytes(data)

    def test_01_proven_original_i10_map_registry_only(self):
        self.assertEqual(LSV_MAP_IDS,{
            10014:"Tần Hoàng Địa Cung Tầng 1",
            10015:"Tần Hoàng Địa Cung Tầng 2",
            10016:"Tần Hoàng Địa Cung Tầng 3",
            10017:"Tần Hoàng Địa Cung Tầng 4",
            10004:"Phàm Liên Trại",
            10005:"Thanh Liên Trại",
            10007:"Khô Vinh Đạo"})
        self.assertEqual(LSV_MAP_NAMES["Khô Vinh Đạo"],10007)

    def test_02_empty_load_does_not_create_file_or_fake_coordinate(self):
        snap=self.store.load()
        self.assertEqual(snap.rows,())
        self.assertEqual(snap.skipped_retired,())
        self.assertFalse(self.path.exists())

    def test_03_add_first_local_index_keeps_separate_train_and_login(self):
        self.put(b"[Login]\r\npassword = secret\r\n[Farm]\r\ncoord_1 = Farm|2|1|2\r\n")
        snap=self.store.load()
        new=self.store.save_row(expected_bytes=snap.file_bytes,
            name="LSV A",map_id=10014,x="35",y="70")
        self.assertEqual(new.rows[0].key_number,1)
        self.assertEqual(new.rows[0].map_id,10014)
        self.assertIn(b"[Farm]\r\ncoord_1 = Farm|2|1|2\r\n",self.path.read_bytes())
        self.assertIn(b"[TrainLSV]\r\ncoord_1 = LSV A|10014|35|70\r\n",self.path.read_bytes())
        self.assertIn(b"password = secret\r\n",self.path.read_bytes())

    def test_04_original_numeric_key_order_not_lexical(self):
        self.put(b"[TrainLSV]\ncoord_10 = Tenth|10014|10|11\n"
                 b"coord_2 = Second|10005|2|3\n")
        s=self.store.load()
        self.assertEqual([row.key_number for row in s.rows],[2,10])
        self.assertEqual([row.name for row in s.rows],["Second","Tenth"])

    def test_05_name_can_contain_pipe_per_exact_i10_parser(self):
        self.put(b"[TrainLSV]\ncoord_4 = Before|A|10007|11|22\n")
        row=self.store.load().rows[0]
        self.assertEqual(row.name,"Before|A")
        new=self.store.save_row(key_number=4,expected_bytes=self.store.load().file_bytes,
                                name="New|Pipe",map_id=10007,x="11",y="22")
        self.assertEqual(new.rows[0].name,"New|Pipe")
        self.assertIn(b"New|Pipe|10007|11|22",self.path.read_bytes())

    def test_06_edit_preserves_index_spacing_colon_and_unknown_lsv_keys(self):
        self.put(b"[TrainLSV]\r\ncoord_8 : Old|10004|11|22\r\n"
                 b"buff_0 = fixed_unknown\r\nheal_map = keep\r\n")
        before=self.store.load()
        self.store.save_row(key_number=8,expected_bytes=before.file_bytes,
                            name="Renamed",map_id=10015,x="12",y="34")
        data=self.path.read_bytes()
        self.assertIn(b"coord_8 : Renamed|10015|12|34\r\n",data)
        self.assertIn(b"buff_0 = fixed_unknown\r\n",data)
        self.assertIn(b"heal_map = keep\r\n",data)
        self.assertNotIn(b"coord_1 =",data)

    def test_07_delete_one_record_without_reindex_and_preserve_other(self):
        self.put(b"[TrainLSV]\ncoord_2 = A|10014|2|3\n"
                 b"coord_9 = B|10004|8|9\n")
        snap=self.store.load()
        next_snap=self.store.delete_row(2,expected_bytes=snap.file_bytes)
        self.assertEqual([r.key_number for r in next_snap.rows],[9])
        self.assertNotIn(b"coord_2 =",self.path.read_bytes())
        self.assertIn(b"coord_9 = B|10004|8|9\n",self.path.read_bytes())

    def test_08_append_uses_fresh_local_index_without_renumbering_existing(self):
        self.put(b"[TrainLSV]\ncoord_2 = A|10014|2|3\n"
                 b"coord_10 = B|10004|8|9\n")
        snap=self.store.load()
        fresh=self.store.save_row(expected_bytes=snap.file_bytes,
            name="Fresh",map_id=10007,x="1",y="2")
        self.assertEqual([r.key_number for r in fresh.rows],[2,10,11])
        self.assertIn(b"coord_11 = Fresh|10007|1|2\n",self.path.read_bytes())

    def test_09_retired_map_skips_ui_but_raw_record_survives_other_edits(self):
        self.put(b"[TrainLSV]\ncoord_1 = Unknown|19999|2|3\n"
                 b"coord_3 = Known|10014|1|2\n")
        snap=self.store.load()
        self.assertEqual(snap.skipped_retired,(19999,))
        self.assertEqual([r.key_number for r in snap.rows],[3])
        self.store.save_row(key_number=3,expected_bytes=snap.file_bytes,
                            name="Known",map_id=10015,x="1",y="2")
        self.assertIn(b"coord_1 = Unknown|19999|2|3\n",self.path.read_bytes())

    def test_10_stale_snapshot_refuses_clobber(self):
        self.put(b"[TrainLSV]\ncoord_1 = A|10014|1|2\n")
        old=self.store.load()
        self.put(b"[TrainLSV]\ncoord_1 = A|10014|3|4\n")
        with self.assertRaisesRegex(TrainLsvCoordinateError,"STALE"):
            self.store.delete_row(1,expected_bytes=old.file_bytes)
        self.assertIn(b"|3|4",self.path.read_bytes())

    def test_11_duplicate_numeric_key_is_blocked(self):
        self.put(b"[TrainLSV]\ncoord_1 = A|10014|2|3\nCOORD_01 = B|10015|4|5\n")
        with self.assertRaisesRegex(TrainLsvCoordinateError,"DUPLICATE"):
            self.store.load()

    def test_12_malformed_record_cannot_be_silently_deleted(self):
        for content in (
            b"[TrainLSV]\ncoord_bad = A|10014|2|3\n",
            b"[TrainLSV]\ncoord_3 = A|junk|2|3\n",
            b"[TrainLSV]\ncoord_2 = A|10014|2|3\n continuation\n"):
            with self.subTest(content=content):
                self.put(content)
                with self.assertRaises(TrainLsvCoordinateError):
                    self.store.load()

    def test_13_unsupported_map_or_bad_fields_do_not_write(self):
        snap=self.store.load()
        for vals in (
            ("A",99999,"1","2"),
            ("A",10014,"","2"),
            ("A",10014,"1|2","3"),
            ("A",10014,"1","2\n"),
            ("",10014,"1","2"),
            ("A",True,"1","2")):
            with self.subTest(vals=vals),self.assertRaises(TrainLsvCoordinateError):
                self.store.save_row(expected_bytes=snap.file_bytes,
                    name=vals[0],map_id=vals[1],x=vals[2],y=vals[3])
        self.assertFalse(self.path.exists())

    def test_14_ambiguous_duplicate_preset_name_is_blocked_locally(self):
        self.put(b"[TrainLSV]\ncoord_1 = A|10014|1|2\n")
        snap=self.store.load()
        with self.assertRaisesRegex(TrainLsvCoordinateError,"AMBIGUOUS"):
            self.store.save_row(expected_bytes=snap.file_bytes,
                name="A",map_id=10015,x="8",y="9")
        self.assertEqual(self.path.read_bytes(),snap.file_bytes)

    def test_15_duplicate_trainlsv_section_is_refused(self):
        self.put(b"[TrainLSV]\ncoord_1 = A|10014|1|2\n"
                 b"[trainlsv]\ncoord_2 = B|10015|3|4\n")
        with self.assertRaises(TrainLsvCoordinateError):
            self.store.load()

    def test_16_utf8_bom_and_invalid_bytes_refused(self):
        for data in (b"\xef\xbb\xbf[TrainLSV]\n",
                     b"\xff\x00[TrainLSV]\n"):
            with self.subTest(raw=data):
                self.put(data)
                with self.assertRaises(TrainLsvCoordinateError):
                    self.store.load()

    def test_17_top_panel_changes_and_coordinates_can_be_reloaded(self):
        self.put(b"[TrainLSV]\nrespawn = False\n")
        old=TrainLsvTopStore(self.path).load()
        changed=TrainLsvTopStore(self.path).save_change(
            "respawn",True,expected_bytes=old.file_bytes)
        self.assertTrue(changed.value.respawn)
        next_state=self.store.load()
        saved=self.store.save_row(expected_bytes=next_state.file_bytes,
                                 name="LSV",map_id=10014,x="10",y="20")
        self.assertEqual(len(saved.rows),1)
        self.assertTrue(TrainLsvTopStore(self.path).load().value.respawn)

    def test_18_backup_present_and_unrelated_unknown_records_kept(self):
        self.put(b"[TrainLSV]\r\ncoord_5 = A|10014|1|2\r\n"
                 b"acc_X_train = A\r\n[Login]\r\npassword = stay\r\n")
        old=self.store.load()
        self.store.delete_row(5,expected_bytes=old.file_bytes)
        backups=list(self.path.parent.glob("settings.*.ini"))
        self.assertEqual(len(backups),1)
        self.assertIn(b"coord_5 = A|10014|1|2",backups[0].read_bytes())
        self.assertIn(b"acc_X_train = A\r\n",self.path.read_bytes())
        self.assertIn(b"password = stay\r\n",self.path.read_bytes())

    def test_19_builder_remains_actual_module_local_no_proxy(self):
        b=make_independent_builders(self.path,StartWindowProducer())
        self.assertIn("trainlsv_tab",b)
        self.assertNotIn("proxy_tab",b)

    def test_20_no_game_apis_in_coordinate_editor(self):
        for name in ("train_lsv_coordinates.py","train_lsv_coordinate_editor.py"):
            s=(ROOT/"src"/name).read_text(encoding="utf-8")
            for forbidden in ("PermissionGuard(", "VerifiedClaims(", "SendInput(",
                              "PostMessage(", "RequestSellItem(", "_farm_all("):
                self.assertNotIn(forbidden,s)

if __name__=="__main__":
    unittest.main()
