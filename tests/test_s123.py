"""S123 original H12 5000ms row identity reconciliation and real source guard."""
from __future__ import annotations
from pathlib import Path
import sys
import unittest
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"src"))
from start_polling import WindowSnapshot
from start_windows import GameWindow
from train_account_rows import TrainAccountRegistry, TRAIN_ACCOUNT_REFRESH_MS

def win(hwnd=101,pid=22,title="Original Game"):
    return GameWindow(hwnd,pid,title,"UnityWndClass","thần long mobile.exe")
def snap(*windows,valid=True):
    return WindowSnapshot(revision=1,windows=tuple(windows),valid=valid)

class S123Cases(unittest.TestCase):
    def test_01_source_locked_5000ms(self):
        self.assertEqual(TRAIN_ACCOUNT_REFRESH_MS,5000)
    def test_02_new_live_window(self):
        r=TrainAccountRegistry()
        self.assertEqual(r.reconcile(snap(win())).added,(win(),))
    def test_03_pid_identity_same_keeps_row(self):
        r=TrainAccountRegistry();r.reconcile(snap(win()))
        result=r.reconcile(snap(win(title="New title")))
        self.assertEqual(result.retained,(win(title="New title"),))
        self.assertFalse(result.added)
    def test_04_recycled_hwnd_replaces(self):
        r=TrainAccountRegistry();r.reconcile(snap(win()))
        result=r.reconcile(snap(win(pid=23)))
        self.assertEqual(result.reused,((win(),win(pid=23)),))
    def test_05_real_closed_window_removes(self):
        r=TrainAccountRegistry();r.reconcile(snap(win()))
        self.assertEqual(r.reconcile(snap()).removed,(win(),))
    def test_06_transient_failure_preserves(self):
        r=TrainAccountRegistry();r.reconcile(snap(win()))
        self.assertTrue(r.reconcile(snap(valid=False)).unknown)
        self.assertEqual(r.rows,(win(),))
    def test_07_invalid_window_fail_closed_no_state_corrupt(self):
        r=TrainAccountRegistry();r.reconcile(snap(win()))
        with self.assertRaises(ValueError):
            r.reconcile(snap(win(pid=0)))
        self.assertEqual(r.rows,(win(),))
    def test_08_ambiguous_duplicate_hwnd_blocks(self):
        r=TrainAccountRegistry()
        with self.assertRaises(ValueError):
            r.reconcile(snap(win(),win(pid=23)))
        self.assertEqual(r.rows,())
    def test_09_zero_hwnd_blocks(self):
        with self.assertRaises(ValueError):
            TrainAccountRegistry().reconcile(snap(win(hwnd=0)))
    def test_10_clear_revokes(self):
        r=TrainAccountRegistry();r.reconcile(snap(win()))
        self.assertEqual(r.clear(),(win(),))
        self.assertEqual(r.rows,())
    def test_11_no_game_action_source(self):
        s=(R/"src/train_account_rows.py").read_text(encoding="utf-8")
        for bad in ("PostMessage(", "start_auto_train(", "WriteProcessMemory(",
                    "proxy_tab", "click_game(", 'text="Bắt đầu"'):
            self.assertNotIn(bad,s)
    def test_12_real_start_producer_background_source(self):
        s=(R/"src/train_account_rows.py").read_text(encoding="utf-8")
        self.assertIn("StartWindowProducer()",s)
        self.assertIn("read_snapshot()",s)
    def test_13_main_thread_tk_widget_action_only(self):
        s=(R/"src/train_account_rows.py").read_text(encoding="utf-8")
        self.assertIn("self.container.after(",s)
        self.assertIn("editor.register_account_combos(",s)
    def test_14_reused_identity_drops_previous_combo(self):
        s=(R/"src/train_account_rows.py").read_text(encoding="utf-8")
        self.assertIn("self._remove(old.hwnd)",s)
    def test_15_entitlement_default_denied(self):
        s=(R/"src/train_account_rows.py").read_text(encoding="utf-8")
        self.assertIn("else False",s)
    def test_16_original_role_name_not_fabricated(self):
        s=(R/"src/train_account_rows.py").read_text(encoding="utf-8")
        self.assertIn("HWND {window.hwnd} / PID {window.pid}",s)
    def test_17_multiple_rows(self):
        r=TrainAccountRegistry()
        d=r.reconcile(snap(win(),win(102,23)))
        self.assertEqual(len(d.added),2)
        self.assertEqual(len(r.rows),2)
    def test_18_invalid_type(self):
        with self.assertRaises(ValueError):
            TrainAccountRegistry().reconcile(None)
if __name__=="__main__": unittest.main()
