"""S62: Start C07 reset worker lifecycle; no fake original Auto mode radio."""
from __future__ import annotations
import sys,threading,time,unittest
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"tests"))
from start_tab import TLMStartTab
from start_polling import WindowSnapshot
from start_windows import GameWindow,GAME_PROCESS,GAME_TITLE,UNITY_WINDOW_CLASS
from window_auto_reset import AutoResetResult

def snap():
    return WindowSnapshot(22,(GameWindow(1001,5001,GAME_TITLE,
        UNITY_WINDOW_CLASS,GAME_PROCESS),),True)

class Service:
    def __init__(self,seen,entered=None,release=None,exc=False):
        self.seen,self.entered,self.release,self.exc=seen,entered,release,exc
    def apply(self,snapshot,*,max_windows,master_hwnd,allowed):
        if self.entered is not None:self.entered.set()
        if self.release is not None:self.release.wait(2)
        if self.exc:raise OSError("TEST_ONLY_NATIVE_FAILURE")
        self.seen.append((snapshot,max_windows,master_hwnd,allowed()))
        return AutoResetResult("AUTO_RESET_APPLIED" if allowed() else "CANCELLED")

class S62StartC07Worker(unittest.TestCase):
    def setUp(self):
        self.seen=[]
        o=self.obj=object.__new__(TLMStartTab)
        o._closed=False
        o.poller=SimpleNamespace(active=True,producer=SimpleNamespace(read_snapshot=snap))
        o.container=SimpleNamespace(winfo_viewable=lambda:True)
        o.layout_max_windows=2
        o.layout_master_hwnd=1001
        o.layout_active=False
        o._stack_thread=None
        o._layout_thread=None
        o._auto_reset_thread=None
        o._auto_reset_allow=threading.Event()
        o._auto_reset_generation=0
        o._auto_reset_last_result=None
        o._auto_reset_service_factory=lambda:Service(self.seen)
    def tearDown(self):
        self.obj._cancel_auto_reset_worker()
        t=self.obj._auto_reset_thread
        if t is not None:
            t.join(2)
            self.assertFalse(t.is_alive(),"S62 worker leaked")
    def joined(self):
        t=self.obj._auto_reset_thread
        self.assertIsNotNone(t)
        t.join(2)
        self.assertFalse(t.is_alive())
    def test_offthread_real_service_receives_exact_snapshot_limit_master(self):
        self.assertTrue(self.obj._dispatch_auto_reset())
        self.joined()
        self.assertEqual(len(self.seen),1)
        self.assertEqual(self.seen[0][1:],(2,1001,True))
        self.assertTrue(self.seen[0][0].valid)
        self.assertEqual(self.obj._auto_reset_last_result.code,"AUTO_RESET_APPLIED")
    def test_nonblocking_tk_dispatch_and_no_duplicate_live_worker(self):
        entered,release=threading.Event(),threading.Event()
        self.obj._auto_reset_service_factory=lambda:Service(self.seen,entered,release)
        try:
            t=time.monotonic()
            self.assertTrue(self.obj._dispatch_auto_reset())
            self.assertLess(time.monotonic()-t,.2)
            self.assertTrue(entered.wait(1))
            self.assertFalse(self.obj._dispatch_auto_reset())
        finally:release.set()
        self.joined()
    def test_stacking_c10_c11_rejected_while_auto_reset_running(self):
        entered,release=threading.Event(),threading.Event()
        self.obj._auto_reset_service_factory=lambda:Service(self.seen,entered,release)
        self.obj._stack_allow=threading.Event()
        self.obj._stack_generation=0
        self.obj._stack_last_result=None
        try:
            self.assertTrue(self.obj._dispatch_auto_reset())
            self.assertTrue(entered.wait(1))
            self.assertFalse(self.obj._stack_tight_cmd())
            self.assertFalse(self.obj._stack_diagonal_cmd())
        finally:release.set()
        self.joined()
    def test_grid_toggle_rejected_while_auto_reset_running(self):
        entered,release=threading.Event(),threading.Event()
        self.obj._auto_reset_service_factory=lambda:Service(self.seen,entered,release)
        self.obj.btn_layout=SimpleNamespace(configure=lambda **kw:None)
        self.obj.layout_status=SimpleNamespace(configure=lambda **kw:None)
        try:
            self.assertTrue(self.obj._dispatch_auto_reset())
            self.assertTrue(entered.wait(1))
            self.assertFalse(self.obj._toggle_layout())
            self.assertFalse(self.obj.layout_active)
        finally:release.set()
        self.joined()
    def test_cancelled_but_still_alive_stack_blocks_reset(self):
        ev=threading.Event()
        t=threading.Thread(target=lambda:ev.wait(2),daemon=True)
        t.start()
        self.obj._stack_thread=t
        try:self.assertFalse(self.obj._dispatch_auto_reset())
        finally:ev.set();t.join(2)
        self.assertIsNone(self.obj._auto_reset_thread)
    def test_cancelled_grid_worker_blocks_reset_until_exit(self):
        ev=threading.Event()
        t=threading.Thread(target=lambda:ev.wait(2),daemon=True)
        t.start()
        self.obj._layout_thread=t
        try:self.assertFalse(self.obj._dispatch_auto_reset())
        finally:ev.set();t.join(2)
        self.assertIsNone(self.obj._auto_reset_thread)
    def test_permission_revocation_cancels_result(self):
        entered,release=threading.Event(),threading.Event()
        self.obj._auto_reset_service_factory=lambda:Service(self.seen,entered,release)
        try:
            self.assertTrue(self.obj._dispatch_auto_reset())
            self.assertTrue(entered.wait(1))
            self.obj._cancel_auto_reset_worker()
            self.obj.layout_max_windows=0
        finally:release.set()
        self.joined()
        self.assertFalse(self.seen[0][3])
        self.assertIsNone(self.obj._auto_reset_last_result)
    def test_master_change_cancel_and_old_worker_must_exit(self):
        entered,release=threading.Event(),threading.Event()
        self.obj._auto_reset_service_factory=lambda:Service(self.seen,entered,release)
        try:
            self.assertTrue(self.obj._dispatch_auto_reset())
            self.assertTrue(entered.wait(1))
            self.obj._cancel_auto_reset_worker()
            self.obj.layout_master_hwnd=1002
            self.assertFalse(self.obj._dispatch_auto_reset())
        finally:release.set()
        self.joined()
        self.assertFalse(self.seen[0][3])
        self.assertIsNone(self.obj._auto_reset_last_result)
    def test_unverified_limit_hidden_or_stopped_or_invalid_cache_no_dispatch(self):
        o=self.obj
        changes=(
            lambda:setattr(o,"layout_max_windows",0),
            lambda:setattr(o,"layout_active",True),
            lambda:setattr(o,"_closed",True),
            lambda:setattr(o.poller,"active",False),
            lambda:setattr(o.container,"winfo_viewable",lambda:False),
            lambda:setattr(o.poller.producer,"read_snapshot",lambda:WindowSnapshot()),
            lambda:setattr(o.poller.producer,"read_snapshot",
                lambda:WindowSnapshot(1,tuple(snap().windows)*3,True)),
        )
        for modify in changes:
            o._closed=False;o.layout_max_windows=2;o.layout_active=False
            o.poller.active=True;o.container.winfo_viewable=lambda:True
            o.poller.producer.read_snapshot=snap
            modify()
            self.assertFalse(o._dispatch_auto_reset())
        self.assertEqual(self.seen,[])
        self.assertIsNone(o._auto_reset_thread)
    def test_worker_oserror_is_error_not_fake_success(self):
        self.obj._auto_reset_service_factory=lambda:Service(self.seen,exc=True)
        self.assertTrue(self.obj._dispatch_auto_reset())
        self.joined()
        self.assertEqual(self.obj._auto_reset_last_result.code,"AUTO_RESET_WORKER_ERROR")
    def test_tab_shutdown_cancellation_is_nonblocking(self):
        entered,release=threading.Event(),threading.Event()
        self.obj._auto_reset_service_factory=lambda:Service(self.seen,entered,release)
        try:
            self.assertTrue(self.obj._dispatch_auto_reset())
            self.assertTrue(entered.wait(1))
            t=time.monotonic()
            self.obj._cancel_auto_reset_worker()
            self.obj._closed=True
            self.assertLess(time.monotonic()-t,.1)
        finally:release.set()
        self.joined()
        self.assertIsNone(self.obj._auto_reset_last_result)
    def test_no_fake_mode_visual_tiler_and_no_proxy(self):
        code=(ROOT/"src/start_tab.py").read_text("utf-8")
        self.assertIn("def _dispatch_auto_reset(",code)
        self.assertNotIn("self.mode_var =",code)
        self.assertNotIn("self.btn_auto_tile =",code)
        self.assertNotIn("proxy_tab",code)
if __name__=="__main__":unittest.main()
