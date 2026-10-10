"""S83 C05 clicking already selected Master radio is a true idempotent no-op."""
from __future__ import annotations
import sys
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"tests")]
from test_s81 import prepared, window
from start_tab import TLMStartTab

def live(*,visible=True,active=True):
    obj=prepared()
    obj._closed=False
    obj.poller=SimpleNamespace(active=active)
    obj.container=SimpleNamespace(winfo_viewable=lambda:visible)
    obj.master_selection.update((window(1),window(2),window(3)))
    obj.layout_master_hwnd=obj.master_selection.hwnd
    obj._master_var.set("1:1001")
    obj._stack_allow.set()
    obj._auto_reset_allow.set()
    return obj

class S83MasterRadioIdempotence(unittest.TestCase):
    def test_01_same_master_radio_returns_selected_without_cancellation(self):
        o=live()
        old_stack=o._stack_allow
        old_reset=o._auto_reset_allow
        stack_generation=o._stack_generation
        reset_generation=o._auto_reset_generation
        self.assertTrue(o._on_master_change(1,1001))
        self.assertTrue(old_stack.is_set())
        self.assertTrue(old_reset.is_set())
        self.assertEqual((o._stack_generation,o._auto_reset_generation),
                         (stack_generation,reset_generation))

    def test_02_real_new_master_still_cancels_native_workers(self):
        o=live()
        old_stack=o._stack_allow
        old_reset=o._auto_reset_allow
        self.assertTrue(o._on_master_change(2,1002))
        self.assertFalse(old_stack.is_set())
        self.assertFalse(old_reset.is_set())
        self.assertEqual(o.master_selection.selected,(2,1002))

    def test_03_same_master_does_not_restart_active_layout_generation(self):
        o=live()
        o.layout_active=True
        old=o._layout_allow
        old_generation=o.sync_loop_id
        self.assertTrue(o._on_master_change(1,1001))
        self.assertIs(o._layout_allow,old)
        self.assertEqual(o.sync_loop_id,old_generation)

    def test_04_different_master_restarts_existing_layout_as_before(self):
        o=live()
        o.layout_active=True
        old=o._layout_allow
        before=o.sync_loop_id
        self.assertTrue(o._on_master_change(2,1002))
        self.assertFalse(old.is_set())
        self.assertNotEqual(o._layout_allow,old)
        self.assertEqual(o.sync_loop_id,before+1)

    def test_05_repeated_click_same_master_is_always_no_op(self):
        o=live()
        for i in range(7):
            self.assertTrue(o._on_master_change(1,1001))
        self.assertEqual(o._stack_generation,0)
        self.assertEqual(o._auto_reset_generation,0)
        self.assertEqual(o._master_var.value,"1:1001")

    def test_06_second_selection_same_new_master_no_cancellation(self):
        o=live()
        self.assertTrue(o._on_master_change(3,1003))
        o._stack_allow=threading.Event()
        o._stack_allow.set()
        o._auto_reset_allow=threading.Event()
        o._auto_reset_allow.set()
        before=(o._stack_generation,o._auto_reset_generation)
        self.assertTrue(o._on_master_change(3,1003))
        self.assertEqual((o._stack_generation,o._auto_reset_generation),before)
        self.assertTrue(o._stack_allow.is_set())
        self.assertTrue(o._auto_reset_allow.is_set())

    def test_07_stale_PID_refused_without_cancelling_workers(self):
        o=live()
        self.assertFalse(o._on_master_change(1,9999))
        self.assertEqual(o._stack_generation,0)
        self.assertEqual(o.master_selection.selected,(1,1001))

    def test_08_nonexistent_HWND_refused_without_cancelling(self):
        o=live()
        self.assertFalse(o._on_master_change(99,9999))
        self.assertTrue(o._stack_allow.is_set())

    def test_09_inactive_owner_denies_even_same_master(self):
        o=live(active=False)
        self.assertFalse(o._on_master_change(1,1001))
        self.assertEqual(o._stack_generation,0)

    def test_10_hidden_start_denies_even_same_master(self):
        o=live(visible=False)
        self.assertFalse(o._on_master_change(1,1001))
        self.assertEqual(o._stack_generation,0)

    def test_11_Tk_master_var_retains_same_correct_identity(self):
        o=live()
        o._master_var.set("UNEXPECTED")
        self.assertTrue(o._on_master_change(1,1001))
        self.assertEqual(o._master_var.value,"1:1001")
        self.assertEqual(o.layout_master_hwnd,1)

    def test_12_no_synthetic_game_input_or_new_master_algorithm(self):
        source=(ROOT/"src/start_tab.py").read_text("utf-8")
        segment=source[source.index("def _on_master_change"):source.index("def _reschedule_layout_for_user_choice")]
        self.assertIn('if previous == (hwnd, pid):',segment)
        self.assertLess(segment.index('if previous == (hwnd, pid):'),
                        segment.index('self._cancel_stack_worker()'))
        for token in ("SendInput(","ReadProcessMemory(","CreateRemoteThread(",
                      "proxy_tab","guess_role_name"):
            self.assertNotIn(token,segment)

if __name__=="__main__":
    unittest.main()
