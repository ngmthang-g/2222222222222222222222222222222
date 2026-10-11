"""S125 H12 read-only background character sampling, identity and data validation."""
from __future__ import annotations
import sys
import threading
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from start_windows import GameWindow
from train_character_samples import (
    TrainCharacterSample, TrainCharacterSampler, sanitized_role_name,
    validated_sample,
)

def w(hwnd=11,pid=22):
    return GameWindow(hwnd,pid,"test HWND", "TkTopLevel","TEST_NOT_GAME.exe")

class TestS125(unittest.TestCase):
    def test_01_original_role_name_markup_removed(self):
        self.assertEqual(sanitized_role_name(" <color=#FF0000>Đại Hiệp</color> "),"Đại Hiệp")
    def test_02_empty_sanitized_remains_unknown(self):
        self.assertIsNone(sanitized_role_name("<b></b>"))
    def test_03_none_name_does_not_make_fake_identity(self):
        self.assertIsNone(sanitized_role_name(None))
    def test_04_wrong_name_type_rejected(self):
        with self.assertRaises(ValueError):sanitized_role_name(0)
    def test_05_validated_live_sample_fields(self):
        sample=validated_sample(TrainCharacterSample(11,22,"<b>Long</b>",90,7,100,200),w())
        self.assertEqual((sample.role_name,sample.map_id,sample.bag_slots,
                          sample.bound_money,sample.exp),("Long",90,7,100,200))
    def test_06_unknown_bag_is_not_fabricated_zero(self):
        self.assertIsNone(validated_sample(TrainCharacterSample(11,22),w()).bag_slots)
    def test_07_pid_reuse_rejected(self):
        with self.assertRaises(ValueError):validated_sample(TrainCharacterSample(11,23),w())
    def test_08_hwnd_reuse_rejected(self):
        with self.assertRaises(ValueError):validated_sample(TrainCharacterSample(12,22),w())
    def test_09_negative_site10_rejected(self):
        with self.assertRaises(ValueError):validated_sample(TrainCharacterSample(11,22,bag_slots=-1),w())
    def test_10_bool_is_not_bag_slot_integer(self):
        with self.assertRaises(ValueError):validated_sample(TrainCharacterSample(11,22,bag_slots=True),w())
    def test_11_negative_exp_rejected(self):
        with self.assertRaises(ValueError):validated_sample(TrainCharacterSample(11,22,exp=-1),w())
    def test_12_no_native_reader_no_work(self):
        x=TrainCharacterSampler()
        self.assertFalse(x.enabled)
        self.assertFalse(x.request([w()]))
        self.assertEqual(x.drain(),())
    def test_13_rejected_invalid_windows(self):
        x=TrainCharacterSampler(reader=object())
        self.assertFalse(x.request([GameWindow(0,22,"", "", "")]))
        self.assertFalse(x.request(None))
    def test_14_worker_not_tk_main_thread_and_can_drain(self):
        done=threading.Event()
        owner_thread=threading.get_ident()
        observed=[]
        class Reader:
            def read(self, window):
                observed.append(threading.get_ident())
                done.set()
                return TrainCharacterSample(window.hwnd,window.pid,role_name="<b>A</b>",bag_slots=4)
        x=TrainCharacterSampler(Reader())
        self.assertTrue(x.request((w(),)))
        self.assertTrue(done.wait(2))
        result=()
        for _ in range(500):
            result=x.drain()
            if result: break
            done.wait(.001)
        self.assertEqual(result,(TrainCharacterSample(11,22,"A",None,4),))
        self.assertNotEqual(observed,[owner_thread])
        x.shutdown()
    def test_15_worker_read_exception_never_zeroes_bag(self):
        done=threading.Event()
        class Reader:
            def read(self,window):
                done.set()
                raise OSError("native memory unavailable")
        x=TrainCharacterSampler(Reader())
        self.assertTrue(x.request((w(),)))
        self.assertTrue(done.wait(2))
        self.assertEqual(x.drain(),())
        x.shutdown()
    def test_16_cancel_old_generation_before_publish(self):
        gate=threading.Event()
        entered=threading.Event()
        done=threading.Event()
        class Reader:
            def read(self, window):
                # Ensure the callback is truly IN FLIGHT before cancellation.
                entered.set()
                gate.wait(2)
                done.set()
                return TrainCharacterSample(window.hwnd,window.pid,"STALE",2,1)
        x=TrainCharacterSampler(Reader())
        self.assertTrue(x.request([w()]))
        self.assertTrue(entered.wait(2))
        x.invalidate()
        gate.set()
        self.assertTrue(done.wait(2))
        self.assertEqual(x.drain(),())
        x.shutdown()
    def test_17_close_disables_callback_and_discard(self):
        x=TrainCharacterSampler()
        x.shutdown()
        self.assertFalse(x.request([w()]))
        self.assertEqual(x.drain(),())
    def test_18_no_source_native_reader_or_game_action(self):
        code=(ROOT/"src/train_character_samples.py").read_text(encoding="utf-8")
        for bad in ("ReadProcessMemory(", "PostMessage(", "WriteProcessMemory(",
                    "ctypes.windll", "proxy_tab"):
            self.assertNotIn(bad,code)
    def test_19_actual_row_is_source_backend_only(self):
        code=(ROOT/"src/train_account_rows.py").read_text(encoding="utf-8")
        self.assertIn("self.character_sampler.request(eligible)",code)
        self.assertIn("self.character_sampler.drain()",code)
        self.assertIn("self._allowed(window)",code)
    def test_20_invalid_sample_type_blocks(self):
        with self.assertRaises(ValueError):validated_sample({"RoleName":"M"},w())

if __name__=="__main__":
    unittest.main()
