"""S79 C03 genuine Tk header/preview click -> S78 native HWND source."""
from __future__ import annotations
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"tests")]
from start_tab import TLMStartTab
from start_polling import WindowSnapshot
from test_s15 import prepared,win

class ValidatedBackend:
    def __init__(self):
        self.live={(1,1001),(2,1002),(3,1003)}
        self.calls=[]
        self.allow_foreground=True
        self.throw=False
    def source_matches(self,hwnd,pid):
        self.calls.append(("verify",hwnd,pid))
        if self.throw:
            raise OSError("NATIVE_PID_CHECK_FAILED")
        return (hwnd,pid) in self.live
    def activate_source(self,hwnd):
        self.calls.append(("foreground",hwnd))
        if self.throw:
            raise OSError("NATIVE_SETFOREGROUND_FAILED")
        return self.allow_foreground

class ExistingNativePreview:
    def __init__(self,backend,hwnds):
        self.backend=backend
        self.active_hwnds=tuple(hwnds)

def ready(*,active=True,visible=True):
    obj=prepared(active=active,visible=visible)
    obj.layout_max_windows=3
    backend=ValidatedBackend()
    obj._preview_controller=ExistingNativePreview(backend,(1,2,3))
    return obj,backend

class S79C03TkActivationTests(unittest.TestCase):
    def test_01_live_visible_selected_start_verified_dwm_click_activates(self):
        obj,backend=ready()
        self.assertTrue(obj._activate_preview_source(2,1002))
        self.assertEqual(backend.calls,[("verify",2,1002),("foreground",2)])

    def test_02_inactive_start_refuses_without_backend_or_cache_read(self):
        obj,backend=ready(active=False)
        self.assertFalse(obj._activate_preview_source(2,1002))
        self.assertEqual(backend.calls,[])
        self.assertEqual(obj.poller.producer.reads,0)

    def test_03_hidden_or_restricted_info_start_refuses(self):
        obj,backend=ready(visible=False)
        self.assertFalse(obj._activate_preview_source(2,1002))
        self.assertFalse(backend.calls)
        obj,backend=ready()
        obj.layout_max_windows=0
        self.assertFalse(obj._activate_preview_source(2,1002))
        self.assertEqual(backend.calls,[])

    def test_04_verified_limit_shrinks_below_active_snapshot(self):
        obj,backend=ready()
        obj.layout_max_windows=2
        self.assertFalse(obj._activate_preview_source(2,1002))
        self.assertEqual(backend.calls,[])

    def test_05_invalid_or_error_snapshot_cannot_activate(self):
        obj,backend=ready()
        obj.poller.producer.snap=WindowSnapshot(9,(win(2),),False,error="DISCONNECTED")
        self.assertFalse(obj._activate_preview_source(2,1002))
        self.assertFalse(backend.calls)

    def test_06_current_cache_pid_reused_rejects_stale_closure(self):
        obj,backend=ready()
        obj.poller.producer.snap=WindowSnapshot(10,(win(1),win(2,9100),win(3)),True)
        self.assertFalse(obj._activate_preview_source(2,1002))
        self.assertFalse(backend.calls)

    def test_07_current_tiles_or_active_list_removed_never_activates(self):
        obj,backend=ready()
        obj._tile_items.pop((2,1002))
        self.assertFalse(obj._activate_preview_source(2,1002))
        obj,backend=ready()
        obj._active_windows=(win(1),win(3))
        self.assertFalse(obj._activate_preview_source(2,1002))
        self.assertFalse(backend.calls)

    def test_08_no_genuine_DWM_slot_means_no_click_activation(self):
        obj,backend=ready()
        obj._preview_controller.active_hwnds=(1,3)
        self.assertFalse(obj._activate_preview_source(2,1002))
        self.assertEqual(backend.calls,[])
        obj._preview_controller=None
        self.assertFalse(obj._activate_preview_source(2,1002))

    def test_09_closed_or_hung_or_reused_native_hwnd_denied(self):
        obj,backend=ready()
        backend.live.remove((2,1002))
        self.assertFalse(obj._activate_preview_source(2,1002))
        self.assertEqual(backend.calls,[("verify",2,1002)])

    def test_10_windows_foreground_denial_is_not_reported_success(self):
        obj,backend=ready()
        backend.allow_foreground=False
        self.assertFalse(obj._activate_preview_source(2,1002))
        self.assertEqual(backend.calls[-1],("foreground",2))

    def test_11_win32_verification_failure_no_Tk_exception(self):
        obj,backend=ready()
        backend.throw=True
        self.assertFalse(obj._activate_preview_source(2,1002))
        self.assertEqual(backend.calls,[("verify",2,1002)])

    def test_12_dwm_cleanup_error_latches_against_future_click(self):
        obj,backend=ready()
        obj._preview_cleanup_faulted=True
        self.assertFalse(obj._activate_preview_source(2,1002))
        self.assertEqual(backend.calls,[])

    def test_13_wrong_id_types_and_closed_owner_never_access_backend(self):
        obj,backend=ready()
        for hwnd,pid in ((True,1002),(-2,1002),(2,"1002"),(2,0),(2,True)):
            self.assertFalse(obj._activate_preview_source(hwnd,pid))
        obj._closed=True
        self.assertFalse(obj._activate_preview_source(2,1002))
        self.assertEqual(backend.calls,[])

    def test_14_original_C17_arrows_remain_reorder_not_native_activation(self):
        obj,backend=ready()
        # S15 test-only lightweight object has no live Tk grid StringVar;
        # test C17 source-HWND ordering, not unbuilt Tk widget geometry.
        obj._relayout_tiles=lambda:None
        self.assertTrue(obj._move_preview_item(3,1003,-1))
        self.assertEqual([x.hwnd for x in obj._active_windows],[1,3,2])
        self.assertEqual(backend.calls,[])

    def test_15_source_contains_explicit_Tk_label_frame_surface_bindings(self):
        source=(ROOT/"src/start_tab.py").read_text("utf-8")
        self.assertIn('tile.bind("<Button-1>", on_activate',source)
        self.assertIn('label.bind("<Button-1>", on_activate',source)
        self.assertIn('surface.bind("<Button-1>", on_activate',source)
        self.assertIn("self._activate_preview_source(hwnd, pid)",source)
        # Arrows already have a separate C17 command and MUST stay separate.
        self.assertIn('self._move_preview_item(hwnd, pid, -1)',source)
        self.assertIn('self._move_preview_item(hwnd, pid, 1)',source)
        for token in ("SendInput(","PostMessage(","ReadProcessMemory(",
                      "CreateRemoteThread(", "proxy_tab"):
            self.assertNotIn(token,source)

if __name__=="__main__":unittest.main()
