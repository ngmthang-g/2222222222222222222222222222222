"""S152 C14 existing real DWM detached host: permission exception fail closed.

Exact released Nuitka provider error branches UNKNOWN; this is a fix to
reconstructed S70/S85 safety around native OWNER and C13 close_view only.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"tests")]
from test_s17 import row,snap
from test_s70 import Root,SourceBackend,Widget,Session
from detached_host import C14DetachedHost
from dwm_preview import PreviewPlacement


def raising():
    raise AssertionError("S152_TEST_PROVIDER_DISAPPEARED")


class S152C14ProviderExceptions(unittest.TestCase):
    def setUp(self):
        self.rows=(row(1),row(2))
        self.events=[]
        self.backend=SourceBackend(self.rows)
        self.host=C14DetachedHost(
            Root(), windows_backend=self.backend,
            toplevel_factory=lambda _:Widget(self.events),
            resolve_root_hwnd=lambda hwnd:hwnd,
            is_topmost=lambda hwnd:True,
            session_factory=lambda:Session(self.events))
        self.snapshot=snap(*self.rows)

    def open(self, allowed=lambda:True):
        return self.host.open(self.snapshot,max_windows=2,allowed=allowed)

    def factory(self,region,hwnd,snapshot):
        return tuple(PreviewPlacement(w.hwnd,w.pid,hwnd,i*205,780,197,110)
                     for i,w in enumerate(snapshot.windows))

    def test_01_missing_or_throwing_verifier_refuses_before_any_host(self):
        self.assertEqual(self.open(raising).code,"CANCELLED")
        self.assertEqual(self.open(None).code,"CANCELLED")
        self.assertEqual(self.events,[])

    def test_02_non_boolean_provider_truthy_result_cannot_grant(self):
        self.assertEqual(self.open(lambda:1).code,"CANCELLED")
        self.assertEqual(self.open(lambda:"yes").code,"CANCELLED")
        self.assertEqual(self.events,[])

    def test_03_provider_exception_second_check_has_no_native_host(self):
        n=[0]
        def allowed():
            n[0]+=1
            if n[0]==2: raise AssertionError("S152_SECOND_CHECK")
            return True
        self.assertEqual(self.open(allowed).code,"CANCELLED")
        self.assertNotIn("host_destroy",self.events)

    def test_04_provider_exception_after_native_host_realization_cleans_it(self):
        n=[0]
        def allowed():
            n[0]+=1
            if n[0]==3: raise AssertionError("S152_AFTER_CREATED")
            return True
        self.assertEqual(self.open(allowed).code,"OWNER_NATIVE_PROOF_FAILED")
        self.assertIn("host_destroy",self.events)
        self.assertEqual(self.host.owner_hwnd,0)
        self.assertEqual(len(self.backend.rows),2)

    def test_05_render_provider_exception_closes_view_not_game(self):
        self.assertEqual(self.open().code,"HOST_OPEN")
        r=self.host.render(self.snapshot,max_windows=2,placements=self.factory(None,900,self.snapshot),
                           allowed=raising)
        self.assertEqual(r.code,"CANCELLED")
        self.assertIn("dwm_unregistered",self.events)
        self.assertIn("host_destroy",self.events)
        self.assertEqual(len(self.backend.rows),2)

    def test_06_unexpected_session_update_exception_cleans_native_owner(self):
        class Broken(Session):
            def update(self,*args,**kwargs):
                raise AssertionError("S152_NATIVE_CALLBACK_FAILURE")
        self.host._session_factory=lambda:Broken(self.events)
        self.assertEqual(self.open().code,"HOST_OPEN")
        r=self.host.render(self.snapshot,max_windows=2,placements=self.factory(None,900,self.snapshot),
                           allowed=lambda:True)
        self.assertEqual(r.code,"DETACHED_RENDER_FAILED")
        self.assertEqual(self.host.owner_hwnd,0)
        self.assertLess(self.events.index("dwm_unregistered"),
                        self.events.index("host_destroy"))

    def test_07_refresh_initial_provider_exception_closes_old_view(self):
        self.open()
        result=self.host.refresh(self.snapshot,max_windows=2,
                                 placements_for_owner=self.factory,allowed=raising)
        self.assertEqual(result.code,"CANCELLED")
        self.assertEqual(self.host.owner_hwnd,0)
        self.assertIn("host_destroy",self.events)

    def test_08_refresh_provider_exception_after_first_teardown_never_reopens(self):
        self.open()
        started=len(self.events)
        n=[0]
        def allow():
            n[0]+=1
            if n[0]==2: raise AssertionError("S152_AFTER_REFRESH_CLOSE")
            return True
        r=self.host.refresh(self.snapshot,max_windows=2,
                            placements_for_owner=self.factory,allowed=allow)
        self.assertEqual(r.code,"CANCELLED")
        self.assertEqual(self.host.owner_hwnd,0)
        self.assertEqual(sum(x=="host_destroy" for x in self.events),1)
        self.assertFalse(any(isinstance(x,tuple) and x[0]=="geometry"
                             for x in self.events[started:]))

    def test_09_refresh_provider_exception_new_host_construction_cleans(self):
        self.open()
        n=[0]
        def allowed():
            n[0]+=1
            if n[0]==5: raise AssertionError("S152_REOPEN_PROOF")
            return True
        r=self.host.refresh(self.snapshot,max_windows=2,
                            placements_for_owner=self.factory,allowed=allowed)
        self.assertEqual(r.code,"OWNER_NATIVE_PROOF_FAILED")
        self.assertEqual(self.host.owner_hwnd,0)
        self.assertEqual(self.events.count("host_destroy"),2)

    def test_10_verified_native_cleanup_failure_latches_future_open(self):
        class Failed(Session):
            def shutdown(this):
                this.events.append("dwm_unreg_uncertain")
                raise OSError("S152_TEST_NATIVE_DESTINATION_UNKNOWN")
        self.host._session_factory=lambda:Failed(self.events)
        self.open()
        self.assertEqual(self.host.close().code,"HOST_CLOSED_NATIVE_CLEANUP_FAILED")
        self.assertTrue(self.host._refresh_cleanup_faulted)
        self.assertEqual(self.open().code,"NATIVE_CLEANUP_FAILED_LOCKED")

    def test_11_owner_native_verifier_unexpected_error_fails_closed(self):
        self.open()
        def bad(*args):
            raise AssertionError("S152_GETWINDOWRECT_FAILED")
        self.backend.window_rect=bad
        self.assertEqual(self.host.open(self.snapshot,max_windows=2,
                                        allowed=lambda:True).code,"OWNER_INVALIDATED")
        self.assertFalse(self.host.owner_hwnd)

    def test_12_no_game_input_or_guessed_C14_geometry_introduced(self):
        code=(ROOT/"src/detached_host.py").read_text("utf-8")
        for token in ("SendInput(","PostMessage(","ReadProcessMemory(","CreateRemoteThread(",
                      "tk.Button(","proxy_tab","_toggle_detached_preview("):
            self.assertNotIn(token,code)
        self.assertIn("DETACHED_PLACEMENT_EVIDENCE_MISSING",code)


if __name__=="__main__":
    unittest.main()
