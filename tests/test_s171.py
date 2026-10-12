"""S171 original B06/I05 buff manual configuration, WITHOUT game sends.

The original fixed Dạ Minh Châu buff_<n> index remains UNKNOWN; our
new independent editor can only safely append dynamic rows or delete
rows created during the same in-memory UI session.
"""
from __future__ import annotations
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))

from train_lsv_manual_buffs import (
    BUFF_KEYS,BUFF_DEFAULT,TrainLsvBuffError,TrainLsvBuffStore,
    validate_manual_buff,
)
from train_lsv_top_settings import TrainLsvTopStore
from train_lsv_coordinates import TrainLsvCoordinatesStore


class S171BuffStore(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix="S171_")
        self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/"settings.ini"
        self.store=TrainLsvBuffStore(self.path)

    def put(self,v):
        self.path.write_bytes(v)

    def test_01_original_I05_keys_and_defaults(self):
        self.assertEqual(BUFF_KEYS,tuple(f"F{i}" for i in range(1,11))+("1","2","3"))
        self.assertEqual(BUFF_DEFAULT,(False,"1","0","5"))

    def test_02_empty_read_no_write(self):
        p=self.store.load()
        self.assertEqual(p.rows,())
        self.assertEqual(p.file_bytes,b"")
        self.assertFalse(self.path.exists())

    def test_03_append_to_empty_creates_only_buff_one(self):
        p=self.store.load()
        key,after=self.store.append(expected_bytes=p.file_bytes)
        self.assertEqual(key,1)
        self.assertEqual(len(after.rows),1)
        self.assertEqual((after.rows[0].enabled,after.rows[0].key,
                          after.rows[0].minutes,after.rows[0].seconds),
                         BUFF_DEFAULT)
        self.assertEqual(self.path.read_bytes(),
                         b"[TrainLSV]\nbuff_1 = False|1|0|5\n")

    def test_04_append_preserves_original_fixed_unknown_buff_zero(self):
        data=(b"[Login]\r\npassword = SENSITIVE\r\n"
              b"[TrainLSV]\r\nbuff_0 = True|F2|0|5\r\n"
              b"heal_map = unknown\r\n[Party]\r\nparty_after = wait\r\n")
        self.put(data)
        initial=self.store.load()
        k,new=self.store.append(expected_bytes=initial.file_bytes,
             enabled=True,key="F10",minutes="2",seconds="10")
        self.assertEqual(k,1)
        self.assertIn(b"buff_0 = True|F2|0|5\r\n",new.file_bytes)
        self.assertIn(b"buff_1 = True|F10|2|10\r\n",new.file_bytes)
        self.assertIn(b"password = SENSITIVE\r\n",new.file_bytes)
        self.assertIn(b"party_after = wait\r\n",new.file_bytes)

    def test_05_numeric_index_2_10_append_11(self):
        self.put(b"[TrainLSV]\nbuff_10 = True|F5|1|2\n"
                 b"buff_2 = False|1|0|5\n")
        p=self.store.load()
        self.assertEqual([x.number for x in p.rows],[2,10])
        k,n=self.store.append(expected_bytes=p.file_bytes,enabled=True)
        self.assertEqual(k,11)
        self.assertEqual([x.number for x in n.rows],[2,10,11])

    def test_06_unknown_original_record_preserved_and_index_reserved(self):
        self.put(b"[TrainLSV]\nbuff_30 = legacy-custom-future\n"
                 b"coord_1 = Preset|10014|3|4\n")
        p=self.store.load()
        self.assertEqual(p.rows[0].number,30)
        self.assertEqual(p.rows[0].key,"") # intentionally unclassified
        n,x=self.store.append(expected_bytes=p.file_bytes,key="3")
        self.assertEqual(n,31)
        self.assertIn(b"buff_30 = legacy-custom-future\n",x.file_bytes)
        self.assertIn(b"coord_1 = Preset|10014|3|4\n",x.file_bytes)

    def test_07_delete_created_row_only_by_exact_number_and_value(self):
        self.put(b"[TrainLSV]\nbuff_0 = True|1|0|5\n")
        p=self.store.load()
        num,new=self.store.append(expected_bytes=p.file_bytes)
        out=self.store.delete_session_row(
            num,expected_bytes=new.file_bytes,expected_raw=new.rows[-1].raw)
        self.assertEqual([r.number for r in out.rows],[0])
        self.assertIn(b"buff_0 = True|1|0|5\n",self.path.read_bytes())

    def test_08_refuse_delete_if_legacy_value_mismatches(self):
        self.put(b"[TrainLSV]\nbuff_0 = True|1|0|5\n")
        p=self.store.load()
        with self.assertRaisesRegex(TrainLsvBuffError,"CHANGED"):
            self.store.delete_session_row(0,expected_bytes=p.file_bytes,
                expected_raw="False|1|0|5")
        self.assertEqual(self.path.read_bytes(),p.file_bytes)

    def test_09_stale_external_change_refuses_overwrite(self):
        self.put(b"[TrainLSV]\nbuff_4 = False|1|0|5\n")
        p=self.store.load()
        self.put(b"[TrainLSV]\nbuff_4 = False|1|0|6\n")
        with self.assertRaisesRegex(TrainLsvBuffError,"STALE"):
            self.store.append(expected_bytes=p.file_bytes)
        self.assertIn(b"0|6",self.path.read_bytes())

    def test_10_two_same_numeric_indices_refused(self):
        self.put(b"[TrainLSV]\nbuff_2 = False|1|0|5\n"
                 b"BUFF_02 = True|F1|1|0\n")
        with self.assertRaisesRegex(TrainLsvBuffError,"DUPLICATE"):
            self.store.load()

    def test_11_bad_buff_key_refused_before_any_save(self):
        self.put(b"[TrainLSV]\nbuff_xyz = False|1|0|5\n")
        with self.assertRaisesRegex(TrainLsvBuffError,"MALFORMED"):
            self.store.load()

    def test_12_only_original_key_schedule_values_allowed(self):
        for data in ((True,"F11","0","5"),(True,"f1","0","5"),
                     (True,"2","-1","5"),(1,"1","0","5"),
                     (False,"1","0","5.5"),(False,"1","","5"),
                     (False,"1","\n","5")):
            with self.subTest(data=data),self.assertRaises(TrainLsvBuffError):
                validate_manual_buff(*data)

    def test_13_zero_zero_is_data_not_invoked(self):
        self.assertEqual(validate_manual_buff(True,"F1","0","0"),
                         (True,"F1","0","0"))

    def test_14_unrelated_files_byte_exact_except_new_key(self):
        self.put(b"[Login]\r\npassword = keep\r\n[Farm]\r\n"
                 b"coord_1 = Local|10014|1|2\r\n"
                 b"[TrainLSV]\r\ntrist = True\r\n"
                 b"coord_3 = LSVA|10014|5|8\r\n"
                 b"buff_0 = ?unknown-fix\r\n"
                 b"acc_ABC_train = LSVA\r\n")
        original=self.path.read_bytes()
        p=self.store.load()
        _,n=self.store.append(expected_bytes=p.file_bytes,key="F4")
        self.assertEqual(n.file_bytes.replace(b"buff_1 = False|F4|0|5\r\n",b""),original)

    def test_15_backup_preserves_original(self):
        original=b"[TrainLSV]\nbuff_0 = True|1|0|5\n"
        self.put(original)
        p=self.store.load()
        self.store.append(expected_bytes=p.file_bytes)
        copies=list(self.path.parent.glob("settings.*.ini"))
        self.assertEqual(len(copies),1)
        self.assertEqual(copies[0].read_bytes(),original)

    def test_16_duplicate_sections_refused(self):
        self.put(b"[TrainLSV]\nbuff_0 = True|1|0|5\n"
                 b"[trainlsv]\nbuff_1 = False|2|0|5\n")
        with self.assertRaises(TrainLsvBuffError):
            self.store.load()

    def test_17_unsafe_bom_cannot_be_trusted(self):
        self.put(b"\xef\xbb\xbf[TrainLSV]\nbuff_0 = True|1|0|5\n")
        with self.assertRaises(TrainLsvBuffError):
            self.store.load()

    def test_18_can_coexist_with_S169_top_S170_coords(self):
        self.put(b"[TrainLSV]\nrespawn = False\n"
                 b"coord_1 = Preset|10014|12|22\n")
        old=self.store.load()
        num,after=self.store.append(expected_bytes=old.file_bytes,key="F3")
        top=TrainLsvTopStore(self.path).load()
        updated=TrainLsvTopStore(self.path).save_change(
            "respawn",True,expected_bytes=top.file_bytes)
        self.assertTrue(updated.value.respawn)
        self.assertEqual(len(TrainLsvCoordinatesStore(self.path).load().rows),1)
        self.assertIn(f"buff_{num} = False|F3|0|5",self.path.read_text("utf-8"))

    def test_19_no_game_IO_or_original_entitlement_in_source(self):
        for name in ("train_lsv_manual_buffs.py","train_lsv_manual_buff_editor.py"):
            src=(ROOT/"src"/name).read_text(encoding="utf-8")
            for x in ("press_single_key_dll(", "WM_MY_SYNC_KEY",
                      "SendInput(", "PostMessage(", "PermissionGuard(",
                      "receive_token(", "RequestSellItem("):
                self.assertNotIn(x,src)

if __name__=="__main__":
    unittest.main()
