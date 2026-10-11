"""S150: original C12 read-only observer, deterministic classification tests."""
from __future__ import annotations
from dataclasses import replace
import tempfile
from pathlib import Path
import unittest

from tools.S150_WINDOWS_ORIGINAL_C12_OBSERVER import (
    RectSample, capture_game_rects, classify_c12, safe_report,
    verify_frozen_original,
)


def sample(hwnd, pid, x, y, w=240, h=160):
    return RectSample(hwnd, pid, x, y, x+w, y+h)


class S150OriginalObservation(unittest.TestCase):
    def setUp(self):
        self.before = (sample(100, 21, 80, 110), sample(200, 22, 470, 220))
        self.hidden = (sample(100, 21, -2200, -2200),
                       sample(200, 22, -2200, -2200))

    def test_01_zero_origin_distinct_from_prior_coordinates(self):
        shown = (sample(100, 21, 0, 0), sample(200, 22, 0, 0))
        self.assertEqual(classify_c12(self.before,self.hidden,shown),
                         "OBSERVED_SHOW_DOCUMENTED_ZERO_ORIGIN")

    def test_02_actual_old_position_restore_is_separate(self):
        self.assertEqual(classify_c12(self.before,self.hidden,self.before),
                         "OBSERVED_RESTORE_OLD_POSITION")

    def test_03_original_all_zero_cannot_disambiguate_branches(self):
        before = (sample(100,21,0,0),sample(200,22,0,0))
        self.assertEqual(classify_c12(before,self.hidden,before),
                         "INCONCLUSIVE_ZERO_EQUALS_OLD_POSITION")

    def test_04_reused_hwnd_pid_is_inconclusive(self):
        shown = (sample(100,21,0,0),sample(200,99,0,0))
        self.assertEqual(classify_c12(self.before,self.hidden,shown),
                         "INCONCLUSIVE_WINDOW_SET_CHANGED")

    def test_05_changed_dimensions_are_inconclusive(self):
        shown=(sample(100,21,0,0,241),sample(200,22,0,0))
        self.assertEqual(classify_c12(self.before,self.hidden,shown),
                         "INCONCLUSIVE_SIZE_CHANGED")

    def test_06_hide_not_observed_refuses_source_claim(self):
        hidden=(sample(100,21,-2200,-2200),sample(200,22,-2190,-2200))
        self.assertEqual(classify_c12(self.before,hidden,self.before),
                         "INCONCLUSIVE_HIDE_NOT_OBSERVED")

    def test_07_mixed_position_is_never_called_full_original_parity(self):
        shown=(sample(100,21,0,0),sample(200,22,470,220))
        self.assertEqual(classify_c12(self.before,self.hidden,shown),
                         "OBSERVED_MIXED_OR_OTHER_POSITION")

    def test_08_empty_or_duplicate_window_set_is_refused(self):
        self.assertEqual(classify_c12((),self.hidden,self.before),
                         "INCONCLUSIVE_EMPTY_PHASE")
        duplicate=(self.before[0],self.before[0])
        self.assertEqual(classify_c12(duplicate,self.hidden,self.before),
                         "INCONCLUSIVE_DUPLICATE_IDENTITY")

    def test_09_report_has_only_numeric_geometry_no_title_or_password(self):
        report=safe_report(self.before,self.hidden,self.before)
        self.assertEqual(report["coordinates_classification"],"OBSERVED_RESTORE_OLD_POSITION")
        self.assertFalse(report["game_input_sent"])
        self.assertFalse(report["original_running_process_identity_proven"])
        self.assertTrue(report["not_source_level_control_flow_proof"])
        self.assertNotIn("title",str(report).lower())
        self.assertNotIn("password",str(report).lower())

    def test_10_reject_nonoriginal_binary_without_stamping_proof(self):
        with tempfile.TemporaryDirectory() as p:
            x=Path(p)/"TLMTool.exe"
            x.write_bytes(b"NOT_THE_ORIGINAL")
            self.assertFalse(verify_frozen_original(x))
            self.assertFalse(verify_frozen_original(Path(p)/"missing.exe"))

    def test_11_real_data_reader_requires_stable_hwnd_and_pid(self):
        class Native:
            def __init__(self): self.pid=59
            def enumerate_top_level(self): return [400]
            def is_window(self,h): return h==400
            def is_visible(self,h): return h==400
            def process_executable(self,p): return "Thần Long  Mobile.exe"
            def process_id(self,h): return self.pid
            def window_class(self,h): return "UnityWndClass"
            def title_with_timeout(self,h,ms): return "Thần Long  Mobile"
        class Rect:
            def window_rect(self,h): return (120,90,400,270)
        b=Native()
        rows=capture_game_rects(b,Rect())
        self.assertEqual(rows,(sample(400,59,120,90,280,180),))
        class ReusedRect:
            def window_rect(self,h):
                b.pid=999
                return (120,90,400,270)
        with self.assertRaisesRegex(ValueError,"STALE_WINDOW_AFTER_RECT"):
            capture_game_rects(b,ReusedRect())

    def test_12_no_game_window_cannot_be_falsely_classified(self):
        class Empty:
            def enumerate_top_level(self): return ()
        with self.assertRaisesRegex(ValueError,"NO_UNAMBIGUOUS"):
            capture_game_rects(Empty(),object())


if __name__ == "__main__":
    unittest.main()
