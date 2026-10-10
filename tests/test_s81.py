"""S81 C05 master auto-source identity change cancels C10/C11 native stack."""
from __future__ import annotations
import sys
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"tests")]
from grid_master import MasterSelection
from start_tab import TLMStartTab
from start_windows import GameWindow

def window(hwnd,pid=None,title="S81 TEST NOT GAME"):
    return GameWindow(hwnd,pid if pid is not None else hwnd+1000,
                      title,"TEST_ONLY","NOT_GAME.exe")

class FakeVar:
    def __init__(self):self.value=""
    def set(self,value):self.value=value

class FakeRadio:
    def __init__(self,frame,**kwargs):
        self.kwargs=kwargs
        self.destroyed=False
        self.label=kwargs.get("text")
    def pack(self,**kw):pass
    def configure(self,**kw):
        self.label=kw.get("text",self.label)
    def destroy(self):
        self.destroyed=True

def prepared():
    obj=object.__new__(TLMStartTab)
    obj.master_selection=MasterSelection()
    obj._master_var=FakeVar()
    obj._master_radio_buttons=[]
    obj._master_radio_frame=object()
    obj.layout_active=False
    obj.layout_master_hwnd=None
    obj._layout_allow=threading.Event()
    obj._layout_allow.set()
    obj.sync_loop_id=0
    obj._stack_allow=threading.Event()
    obj._stack_allow.set()
    obj._stack_generation=0
    obj._stack_last_result=None
    obj._auto_reset_allow=threading.Event()
    obj._auto_reset_allow.set()
    obj._auto_reset_generation=0
    obj._auto_reset_last_result=None
    return obj

class S81AutoMasterBoundary(unittest.TestCase):
    def setUp(self):
        self.patcher=patch("tkinter.ttk.Radiobutton",FakeRadio)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def initial(self):
        o=prepared()
        o._update_master_combobox((window(1),window(2),window(3)))
        o._stack_allow=threading.Event()
        o._stack_allow.set()
        o._auto_reset_allow=threading.Event()
        o._auto_reset_allow.set()
        return o

    def test_01_native_stack_cancel_on_closed_master(self):
        o=self.initial()
        old=o._stack_allow
        gen=o._stack_generation
        o._update_master_combobox((window(2),window(3)))
        self.assertFalse(old.is_set())
        self.assertGreater(o._stack_generation,gen)
        self.assertEqual(o.master_selection.selected,(2,1002))

    def test_02_native_reset_worker_still_cancelled_same_identity_boundary(self):
        o=self.initial()
        old=o._auto_reset_allow
        o._update_master_combobox((window(2),window(3)))
        self.assertFalse(old.is_set())

    def test_03_same_hwnd_reused_new_pid_cancels_original_master_generation(self):
        o=self.initial()
        old=o._stack_allow
        o._update_master_combobox((window(1,9999),window(2),window(3)))
        self.assertFalse(old.is_set())
        self.assertEqual(o.master_selection.selected,(1,9999))

    def test_04_non_master_lost_does_not_cancel_live_stacker(self):
        o=self.initial()
        old=o._stack_allow
        o._update_master_combobox((window(1),window(3)))
        self.assertTrue(old.is_set())
        self.assertEqual(o.master_selection.selected,(1,1001))

    def test_05_cache_same_handles_same_pids_do_not_cancel(self):
        o=self.initial()
        old=o._stack_allow
        o._update_master_combobox((window(1),window(2),window(3)))
        self.assertTrue(old.is_set())

    def test_06_tk_title_change_no_new_native_worker_cancellation(self):
        o=self.initial()
        old=o._stack_allow
        o._update_master_combobox((window(1,title="changed"),
                                   window(2),window(3)))
        self.assertTrue(old.is_set())
        self.assertEqual(o._master_radio_buttons[0].label,
                         "changed [HWND 1]")

    def test_07_manual_selection_stays_untouched_when_alive(self):
        o=self.initial()
        self.assertTrue(o.master_selection.choose(2,1002))
        o._update_master_combobox((window(1),window(2),window(3)))
        old=o._stack_allow
        o._update_master_combobox((window(2),window(3)))
        self.assertTrue(old.is_set())
        self.assertEqual(o.master_selection.selected,(2,1002))

    def test_08_all_game_sources_vanish_cancel_stacker_and_clear_master(self):
        o=self.initial()
        old=o._stack_allow
        o._update_master_combobox(())
        self.assertFalse(old.is_set())
        self.assertIsNone(o.layout_master_hwnd)
        self.assertEqual(o._master_var.value,"")

    def test_09_invalid_duplicate_hwnd_cache_cannot_grant_new_master(self):
        o=self.initial()
        old=o._stack_allow
        o._update_master_combobox((window(1),window(1)))
        self.assertTrue(old.is_set())
        self.assertEqual(o.master_selection.selected,(1,1001))

    def test_10_active_grid_worker_generation_invalidated_on_master_loss(self):
        o=self.initial()
        o.layout_active=True
        old=o._layout_allow
        seq=o.sync_loop_id
        o._update_master_combobox((window(2),window(3)))
        self.assertFalse(old.is_set())
        self.assertEqual(o.sync_loop_id,seq+1)
        self.assertTrue(o._layout_allow.is_set())

    def test_11_radio_list_rebuild_still_original_hwnd_backed(self):
        o=self.initial()
        old_radios=tuple(o._master_radio_buttons)
        o._update_master_combobox((window(2),window(3)))
        self.assertTrue(all(x.destroyed for x in old_radios))
        self.assertEqual(len(o._master_radio_buttons),2)
        self.assertEqual(o._master_var.value,"2:1002")

    def test_12_no_new_ui_fake_authority_proxy_or_input_actions(self):
        src=(ROOT/"src/start_tab.py").read_text("utf-8")
        segment=src[src.index("def _update_master_combobox"):
                    src.index("def _on_master_change")]
        self.assertIn("self._cancel_stack_worker()",segment)
        for forbidden in ("SendInput(","ReadProcessMemory(","CreateRemoteThread(",
                          "proxy_tab","process.kill("):
            self.assertNotIn(forbidden,segment)

if __name__=="__main__":
    unittest.main()
