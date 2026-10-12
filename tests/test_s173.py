"""S173: verified I05 manual-buff field edits; I07 heal_map is legacy.

Only same-session owned Tk row can be edited; preexisting buffs incl.
fixed Dạ Minh Châu are immutable through UI. No real game/key sender.
"""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))

from train_lsv_manual_buffs import TrainLsvBuffStore,TrainLsvBuffError
from train_lsv_top_settings import TrainLsvTopStore
from train_lsv_coordinates import TrainLsvCoordinatesStore


class S173BuffUpdate(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix="S173_")
        self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/"settings.ini"
        self.store=TrainLsvBuffStore(self.path)

    def put(self,raw:bytes):
        self.path.write_bytes(raw)

    def create(self):
        snap=self.store.load()
        number,new=self.store.append(expected_bytes=snap.file_bytes,
            enabled=False,key="1",minutes="0",seconds="5")
        return number,new

    def test_01_heal_map_ignored_by_runtime_not_new_selector(self):
        i07="docs/tasks/I07.md"
        content=(ROOT/i07).read_text(encoding="utf-8")
        self.assertIn("legacy compatibility state",content)
        self.assertIn("10000",content)
        self.assertNotIn("heal_map",(
            ROOT/"src/train_lsv_manual_buff_editor.py").read_text("utf-8"))

    def test_02_edit_new_row_all_four_verified_fields(self):
        num,before=self.create()
        after=self.store.update_session_row(num,
            expected_bytes=before.file_bytes,
            expected_raw=before.rows[0].raw,
            enabled=True,key="F10",minutes="3",seconds="17")
        self.assertEqual((num,after.rows[0].enabled,after.rows[0].key,
                          after.rows[0].minutes,after.rows[0].seconds),
                         (1,True,"F10","3","17"))
        self.assertEqual(self.path.read_bytes(),
            b"[TrainLSV]\nbuff_1 = True|F10|3|17\n")

    def test_03_fixed_legacy_buff_zero_and_unknown_key_never_rewritten(self):
        old=(b"[Login]\r\npassword = SECRET\r\n"
             b"[TrainLSV]\r\nbuff_0 = True|1|0|5\r\n"
             b"buff_8 = opaque-future\r\nheal_map = old_invalid_name\r\n"
             b"[Party]\r\nmode = KEEP\r\n")
        self.put(old)
        num,new=self.create()
        self.assertEqual(num,9)
        updated=self.store.update_session_row(num,
            expected_bytes=new.file_bytes,expected_raw=new.rows[-1].raw,
            enabled=True,key="F1",minutes="8",seconds="11")
        body=updated.file_bytes
        for unchanged in (b"buff_0 = True|1|0|5\r\n",
                          b"buff_8 = opaque-future\r\n",
                          b"heal_map = old_invalid_name\r\n",
                          b"password = SECRET\r\n",
                          b"mode = KEEP\r\n"):
            self.assertIn(unchanged,body)
        self.assertIn(b"buff_9 = True|F1|8|11\r\n",body)

    def test_04_preserve_existing_row_colon_and_spacing(self):
        self.put(b"[TrainLSV]\n  buff_7  :  False|1|0|5\n")
        snap=self.store.load()
        v=self.store.update_session_row(7,expected_bytes=snap.file_bytes,
            expected_raw=snap.rows[0].raw,enabled=True,key="2",
            minutes="4",seconds="19")
        self.assertEqual(v.file_bytes,b"[TrainLSV]\n  buff_7  :  True|2|4|19\n")

    def test_05_stale_file_refuses_overwrite(self):
        num,before=self.create()
        self.path.write_bytes(before.file_bytes+b"# external\n")
        with self.assertRaisesRegex(TrainLsvBuffError,"STALE"):
            self.store.update_session_row(num,expected_bytes=before.file_bytes,
                expected_raw=before.rows[0].raw,enabled=True,key="F2",
                minutes="1",seconds="2")
        self.assertIn(b"# external",self.path.read_bytes())

    def test_06_bad_existing_value_refuses_update(self):
        num,before=self.create()
        with self.assertRaisesRegex(TrainLsvBuffError,"CHANGED"):
            self.store.update_session_row(num,expected_bytes=before.file_bytes,
                expected_raw="False|F1|0|5",enabled=True,key="F2",
                minutes="1",seconds="2")
        self.assertEqual(self.path.read_bytes(),before.file_bytes)

    def test_07_invalid_key_interval_enabled_type_no_write(self):
        num,before=self.create()
        for kwargs in (
            dict(enabled=1,key="1",minutes="0",seconds="5"),
            dict(enabled=True,key="F11",minutes="0",seconds="5"),
            dict(enabled=True,key="1",minutes="-2",seconds="5"),
            dict(enabled=True,key="1",minutes="2.5",seconds="5"),
            dict(enabled=True,key="1",minutes="0",seconds="")):
            with self.subTest(kwargs=kwargs),self.assertRaises(TrainLsvBuffError):
                self.store.update_session_row(num,expected_bytes=before.file_bytes,
                    expected_raw=before.rows[0].raw,**kwargs)
        self.assertEqual(self.path.read_bytes(),before.file_bytes)

    def test_08_invalid_number_and_snapshot_fail(self):
        num,before=self.create()
        for bad in (-1,True,"1",None):
            with self.subTest(bad=bad),self.assertRaises(TrainLsvBuffError):
                self.store.update_session_row(bad,expected_bytes=before.file_bytes,
                    expected_raw=before.rows[0].raw,enabled=True,key="1",
                    minutes="0",seconds="5")
        with self.assertRaises(TrainLsvBuffError):
            self.store.update_session_row(num,expected_bytes=bytearray(before.file_bytes),
                expected_raw=before.rows[0].raw,enabled=True,key="1",
                minutes="0",seconds="5")

    def test_09_edit_missing_row_rejected(self):
        num,before=self.create()
        with self.assertRaisesRegex(TrainLsvBuffError,"CHANGED"):
            self.store.update_session_row(909,expected_bytes=before.file_bytes,
                expected_raw=before.rows[0].raw,enabled=True,key="1",
                minutes="0",seconds="5")

    def test_10_post_edit_exact_value_supports_session_delete(self):
        num,before=self.create()
        after=self.store.update_session_row(num,expected_bytes=before.file_bytes,
            expected_raw=before.rows[0].raw,enabled=True,key="3",
            minutes="2",seconds="45")
        last=self.store.delete_session_row(num,expected_bytes=after.file_bytes,
            expected_raw=after.rows[0].raw)
        self.assertFalse(last.rows)
        self.assertIn(b"[TrainLSV]",last.file_bytes)

    def test_11_new_edit_and_top_config_coexist(self):
        self.put(b"[TrainLSV]\nrespawn = False\n"
                 b"coord_1 = LSV|10014|1|2\n")
        n,s=self.create()
        updated=self.store.update_session_row(n,expected_bytes=s.file_bytes,
            expected_raw=s.rows[-1].raw,enabled=True,key="F3",
            minutes="1",seconds="7")
        top=TrainLsvTopStore(self.path).load()
        self.assertFalse(top.value.respawn)
        TrainLsvTopStore(self.path).save_change("respawn",True,
            expected_bytes=top.file_bytes)
        self.assertEqual(len(TrainLsvCoordinatesStore(self.path).load().rows),1)
        self.assertIn(b"True|F3|1|7",self.path.read_bytes())

    def test_12_backup_keeps_pre_edit_bytes(self):
        num,before=self.create()
        self.store.update_session_row(num,expected_bytes=before.file_bytes,
            expected_raw=before.rows[0].raw,enabled=True,key="F4",
            minutes="8",seconds="9")
        backups=list(self.path.parent.glob("settings.*.ini"))
        self.assertEqual(len(backups),1)
        # Update creates the first backup because append created a new file.
        self.assertEqual(backups[0].read_bytes(),before.file_bytes)

    def test_13_stale_duplicate_index_fails_closed(self):
        self.put(b"[TrainLSV]\nbuff_1 = False|1|0|5\nBUFF_01 = True|F1|1|0\n")
        with self.assertRaisesRegex(TrainLsvBuffError,"DUPLICATE"):
            self.store.load()

    def test_14_no_game_sender_and_fixed_index_not_assumed(self):
        text=(ROOT/"src/train_lsv_manual_buff_editor.py").read_text("utf-8")
        for prohibited in ("press_single_key_dll(", "WM_MY_SYNC_KEY", "SendInput(",
                           "PostMessage(", "PermissionGuard(", "RequestSellItem("):
            self.assertNotIn(prohibited,text)
        self.assertIn("number not in self.session_owned",text)

if __name__=="__main__":
    unittest.main()
