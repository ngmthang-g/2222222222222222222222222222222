"""S85 C14 source-backed close/reopen native DWM refresh only with true placements."""
from __future__ import annotations
import sys,threading,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"tests")]
from detached_host import C14DetachedHost
from dwm_preview import PreviewPlacement
from test_s17 import row,snap
from test_s70 import Root,SourceBackend,Widget,Session

class S85C14ExplicitRefresh(unittest.TestCase):
    def setUp(self):
        self.rows=(row(1),row(2))
        self.events=[]
        self.backend=SourceBackend(self.rows)
        self.host=C14DetachedHost(
            Root(),windows_backend=self.backend,
            toplevel_factory=lambda root:Widget(self.events),
            resolve_root_hwnd=lambda hwnd:hwnd,
            is_topmost=lambda hwnd:True,
            session_factory=lambda:Session(self.events))
        self.snapshot=snap(*self.rows)
        self.calls=[]
    def open(self):
        return self.host.open(self.snapshot,max_windows=2,allowed=lambda:True)
    def factory(self,region,owner_hwnd,snapshot):
        self.calls.append((region,owner_hwnd,tuple(w.hwnd for w in snapshot.windows)))
        return tuple(PreviewPlacement(w.hwnd,w.pid,owner_hwnd,
                       i*205,region.y+10,197,110)
                     for i,w in enumerate(snapshot.windows))
    def refresh(self,**kwargs):
        return self.host.refresh(
            self.snapshot,max_windows=kwargs.get("max_windows",2),
            allowed=kwargs.get("allowed",lambda:True),
            placements_for_owner=kwargs.get("factory",self.factory))
    def test_01_explicit_refresh_is_real_two_phase_DWM_then_owner(self):
        self.assertEqual(self.open().code,"HOST_OPEN")
        ret=self.refresh()
        self.assertEqual(ret.code,"DETACHED_DWM_REFRESHED")
        self.assertEqual(ret.rendered,(1,2))
        self.assertEqual(len(self.calls),1)
        self.assertLess(self.events.index("dwm_unregistered"),self.events.index("host_destroy"))
        self.assertLess(self.events.index("host_destroy"),
                        max(i for i,x in enumerate(self.events) if isinstance(x,tuple) and x[0]=="geometry"))
    def test_02_refuse_refresh_of_nonexistent_host_no_window_creation(self):
        self.assertEqual(self.refresh().code,"NOT_OPEN")
        self.assertEqual(self.events,[])
    def test_03_no_original_placement_source_refuses_and_preserves_current_DWM(self):
        self.open()
        r=self.refresh(factory=None)
        self.assertEqual(r.code,"DETACHED_PLACEMENT_EVIDENCE_MISSING")
        self.assertEqual(self.host.owner_hwnd,900)
        self.assertNotIn("host_destroy",self.events)
    def test_04_no_permission_closes_detached_but_not_game_sources(self):
        self.open()
        self.assertEqual(self.refresh(allowed=lambda:False).code,"CANCELLED")
        self.assertEqual(self.host.owner_hwnd,0)
        self.assertEqual(len(self.backend.rows),2)
    def test_05_reduced_max_windows_closes_previous_detached_host(self):
        self.open()
        self.assertEqual(self.refresh(max_windows=1).code,"OVER_VERIFIED_LIMIT")
        self.assertEqual(self.host.owner_hwnd,0)
    def test_06_source_PID_reuse_refuses_and_closes_stale_host(self):
        self.open()
        self.backend.bumped_pid[2]=98765
        self.assertEqual(self.refresh().code,"STALE_SOURCE")
        self.assertEqual(self.host.owner_hwnd,0)
    def test_07_false_geometry_factory_has_no_native_DWM_success(self):
        self.open()
        def raising(*args):
            raise ValueError("S85_TEST_ONLY_MISSING_GEOMETRY")
        self.assertEqual(self.refresh(factory=raising).code,
                         "DETACHED_PLACEMENTS_UNAVAILABLE")
        self.assertEqual(self.host.owner_hwnd,0)
    def test_08_missing_source_snapshot_closes_stale_host(self):
        self.open()
        self.snapshot=snap()
        self.assertEqual(self.refresh().code,"NO_WINDOWS")
        self.assertEqual(self.host.owner_hwnd,0)
    def test_09_invalid_positive_region_refuses_reopen_after_close(self):
        self.open()
        self.host.root=Root(w=1024,h=768)
        self.assertEqual(self.refresh().code,"NO_USABLE_SCREEN_REGION")
        self.assertEqual(self.host.owner_hwnd,0)
    def test_10_old_native_cleanup_failure_latches_all_future_opens(self):
        class ErrorSession(Session):
            def shutdown(this):
                this.events.append("dwm_error")
                raise OSError("S85_TEST_ONLY_TEARDOWN_ERROR")
        self.host._session_factory=lambda:ErrorSession(self.events)
        self.open()
        self.assertEqual(self.refresh().code,"NATIVE_CLEANUP_FAILED_LOCKED")
        self.assertEqual(self.open().code,"NATIVE_CLEANUP_FAILED_LOCKED")
        self.assertTrue(self.host._refresh_cleanup_faulted)
    def test_11_wrong_Tk_thread_refuses_no_native_operations(self):
        self.open()
        results=[]
        t=threading.Thread(target=lambda:results.append(self.refresh().code))
        t.start();t.join(2)
        self.assertEqual(results,["WRONG_TK_THREAD"])
        self.assertEqual(self.host.owner_hwnd,900)
    def test_12_shutdown_prevents_refresh_and_game_input_not_added(self):
        self.open()
        self.host.shutdown()
        self.assertEqual(self.refresh().code,"CLOSED")
        code=(ROOT/"src/detached_host.py").read_text("utf-8")
        for bad in ("SendInput(","PostMessage(","ReadProcessMemory(","TerminateProcess(",
                    "CreateRemoteThread(","proxy_tab","tk.Button("):
            self.assertNotIn(bad,code)
        self.assertIn("DETACHED_PLACEMENT_EVIDENCE_MISSING",code)
if __name__=="__main__":unittest.main()
