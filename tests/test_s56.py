"""S56 source-backed Start dispatch for C10/C11, with NO invented Auto pixels.

S56 deliberately adds no UI button. The original Start Auto mode frame layout
is not sufficiently measured in the checked GitHub image evidence.
"""
from __future__ import annotations
import sys
import threading
import time
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from start_tab import TLMStartTab
from start_polling import WindowSnapshot
from start_windows import GameWindow,GAME_PROCESS,GAME_TITLE,UNITY_WINDOW_CLASS
from window_stacking import StackResult

def snapshot():
    return WindowSnapshot(2,(GameWindow(1001,5001,GAME_TITLE,UNITY_WINDOW_CLASS,GAME_PROCESS),),True)

class FakeService:
    def __init__(self,seen,entered=None,release=None):
        self.seen=seen;self.entered=entered;self.release=release
    def apply(self,snapshot,*,mode,max_windows,master_hwnd,allowed):
        if self.entered is not None:self.entered.set()
        if self.release is not None:self.release.wait(2)
        ok=allowed()
        self.seen.append((mode,max_windows,master_hwnd,ok,snapshot))
        return StackResult("STACK_TIGHT_APPLIED" if mode=="tight" else "STACK_DIAGONAL_APPLIED",
                           1,(1001,) if ok else (),())

class S56StartDispatch(unittest.TestCase):
    def setUp(self):
        self.seen=[];self.threads=[]
        self.obj=object.__new__(TLMStartTab)
        self.obj._closed=False
        self.obj.container=SimpleNamespace(winfo_viewable=lambda:True)
        self.obj.poller=SimpleNamespace(active=True,producer=SimpleNamespace(read_snapshot=snapshot))
        self.obj.layout_max_windows=2
        self.obj.layout_master_hwnd=1001
        self.obj.layout_active=False
        self.obj._stack_thread=None
        self.obj._stack_allow=threading.Event()
        self.obj._stack_generation=0
        self.obj._stack_last_result=None
        self.obj._stack_service_factory=lambda: FakeService(self.seen)
    def tearDown(self):
        self.obj._cancel_stack_worker()
        t=self.obj._stack_thread
        if t is not None:
            t.join(2)
            self.assertFalse(t.is_alive(),"S56 worker leaked")
    def _joined(self):
        t=self.obj._stack_thread
        self.assertIsNotNone(t)
        t.join(2)
        self.assertFalse(t.is_alive())
    def test_exact_c10_mode_and_master_limit_snapshot_passed_offthread(self):
        self.assertTrue(self.obj._stack_tight_cmd())
        self._joined()
        self.assertEqual(len(self.seen),1)
        self.assertEqual(self.seen[0][:4],("tight",2,1001,True))
        self.assertTrue(self.seen[0][4].valid)
        self.assertEqual(self.obj._stack_last_result.code,"STACK_TIGHT_APPLIED")
    def test_exact_c11_mode_not_grid(self):
        self.assertTrue(self.obj._stack_diagonal_cmd())
        self._joined()
        self.assertEqual(self.seen[0][0],"diagonal")
        self.assertEqual(self.obj._stack_last_result.code,"STACK_DIAGONAL_APPLIED")
    def test_tk_dispatch_never_waits_for_blocking_native_worker(self):
        entered,release=threading.Event(),threading.Event()
        self.obj._stack_service_factory=lambda: FakeService(self.seen,entered,release)
        try:
            began=time.monotonic()
            self.assertTrue(self.obj._stack_diagonal_cmd())
            self.assertLess(time.monotonic()-began,.2)
            self.assertTrue(entered.wait(1))
            self.assertFalse(self.obj._stack_tight_cmd(),"no overlapping window movers")
        finally:release.set()
        self._joined()
        self.assertEqual(len(self.seen),1)
    def test_revoke_cancels_before_native_window_movement_and_suppresses_late_result(self):
        entered,release=threading.Event(),threading.Event()
        self.obj._stack_service_factory=lambda: FakeService(self.seen,entered,release)
        try:
            self.assertTrue(self.obj._stack_tight_cmd())
            self.assertTrue(entered.wait(1))
            self.obj._cancel_stack_worker()
            self.obj.layout_max_windows=0
        finally:release.set()
        self._joined()
        self.assertEqual(self.seen[0][3],False)
        self.assertIsNone(self.obj._stack_last_result)
        self.assertFalse(self.obj._stack_diagonal_cmd())
    def test_generation_change_suppresses_old_worker_status(self):
        entered,release=threading.Event(),threading.Event()
        self.obj._stack_service_factory=lambda: FakeService(self.seen,entered,release)
        try:
            self.assertTrue(self.obj._stack_tight_cmd())
            self.assertTrue(entered.wait(1))
            self.obj._cancel_stack_worker()
        finally:release.set()
        self._joined()
        self.assertIsNone(self.obj._stack_last_result)
        self.obj._stack_service_factory=lambda: FakeService(self.seen)
        self.assertTrue(self.obj._stack_diagonal_cmd())
        self._joined()
        self.assertEqual(self.obj._stack_last_result.code,"STACK_DIAGONAL_APPLIED")
    def test_unverified_limit_inactive_hidden_closed_invalid_cache_never_start_worker(self):
        o=self.obj
        for modify in (
            lambda:setattr(o,"layout_max_windows",0),
            lambda:setattr(o,"layout_active",True),
            lambda:setattr(o,"_closed",True),
            lambda:setattr(o.poller,"active",False),
            lambda:setattr(o.container,"winfo_viewable",lambda:False),
            lambda:setattr(o.poller.producer,"read_snapshot",lambda:WindowSnapshot()),
        ):
            # reset for each separate precondition
            o._closed=False;o.layout_max_windows=2;o.layout_active=False
            o.poller.active=True
            o.container.winfo_viewable=lambda:True
            o.poller.producer.read_snapshot=snapshot
            modify()
            self.assertFalse(o._stack_tight_cmd())
        self.assertEqual(self.seen,[])
        self.assertIsNone(o._stack_thread)
    def test_closing_during_worker_disallows_late_result_and_all_followups(self):
        entered,release=threading.Event(),threading.Event()
        self.obj._stack_service_factory=lambda: FakeService(self.seen,entered,release)
        try:
            self.assertTrue(self.obj._stack_tight_cmd())
            self.assertTrue(entered.wait(1))
            self.obj._cancel_stack_worker()
            self.obj._closed=True
        finally:release.set()
        self._joined()
        self.assertIsNone(self.obj._stack_last_result)
        self.assertFalse(self.obj._stack_tight_cmd())
    def test_exception_does_not_crash_tk_or_claim_success(self):
        def failed():
            raise OSError("S56_TEST_ONLY")
        self.obj._stack_service_factory=failed
        self.assertTrue(self.obj._stack_tight_cmd())
        self._joined()
        self.assertEqual(self.obj._stack_last_result.code,"STACK_WORKER_ERROR")
    def test_invalid_mode_cannot_dispatch(self):
        self.assertFalse(self.obj._dispatch_auto_stack("horizontal"))
        self.assertEqual(self.seen,[])
    def test_no_unverified_ui_control_or_auth_bypass_in_source(self):
        code=(ROOT/"src/start_tab.py").read_text("utf-8")
        self.assertNotIn("text=\"Xếp gọn\"",code,"do not invent UI geometry")
        self.assertNotIn("text=\"Xếp chéo\"",code,"do not invent UI geometry")
        self.assertNotIn("TEST_ONLY_VERIFIED",code)
        self.assertIn("_stack_tight_cmd",code)
        self.assertIn("_stack_diagonal_cmd",code)

if __name__=="__main__":unittest.main()
