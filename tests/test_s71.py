"""S71: 12 regression cases for full attempted DWM cleanup despite failure."""
from __future__ import annotations
import sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"tests"))
from test_s11 import FakeDwmBackend, place
from test_s70 import Root, Widget, SourceBackend, Session
from test_s17 import row,snap
from dwm_preview import ReadOnlyDwmPreviews
from detached_host import C14DetachedHost

class ErrorAfterNativeRelease(FakeDwmBackend):
    def __init__(self, fail_at="unregister", failure_count=1):
        super().__init__()
        self.live[43]=1003
        self.fail_at=fail_at
        self.remaining=failure_count
    def unregister(self,thumbnail):
        super().unregister(thumbnail)
        if self.fail_at=="unregister" and self.remaining>0:
            self.remaining-=1
            raise OSError("SIMULATED_UNREGISTER_POST_SUCCESS")
    def destroy_destination(self,destination):
        super().destroy_destination(destination)
        if self.fail_at=="destroy" and self.remaining>0:
            self.remaining-=1
            raise OSError("SIMULATED_DESTROY_POST_SUCCESS")

def three_placements():
    return (place(),place(hwnd=42,pid=1002,x=30),place(hwnd=43,pid=1003,x=60))

class S71DwmFailureSafety(unittest.TestCase):
    def test_initial_three_native_slots_are_registered(self):
        b=ErrorAfterNativeRelease()
        s=ReadOnlyDwmPreviews(b)
        self.assertEqual(s.sync(three_placements()).rendered,(41,42,43))
        self.assertEqual(len(s.active_hwnds),3)
    def test_one_unregister_failure_cannot_strand_rest_of_batch(self):
        b=ErrorAfterNativeRelease()
        s=ReadOnlyDwmPreviews(b)
        s.sync(three_placements())
        with self.assertRaisesRegex(OSError,"SIMULATED_UNREGISTER"):
            s.clear()
        self.assertEqual(s.active_hwnds,())
        self.assertEqual(sum(e[0]=="unregister" for e in b.events),3)
        self.assertEqual(sum(e[0]=="destroy" for e in b.events),3)
    def test_one_destroy_failure_cannot_strand_remaining_slots(self):
        b=ErrorAfterNativeRelease(fail_at="destroy")
        s=ReadOnlyDwmPreviews(b)
        s.sync(three_placements())
        with self.assertRaisesRegex(OSError,"SIMULATED_DESTROY"):
            s.clear()
        self.assertEqual(s.active_hwnds,())
        self.assertEqual(sum(e[0]=="destroy" for e in b.events),3)
    def test_multiple_errors_still_attempt_all_and_report_first(self):
        b=ErrorAfterNativeRelease(failure_count=2)
        s=ReadOnlyDwmPreviews(b)
        s.sync(three_placements())
        with self.assertRaises(OSError):
            s.clear()
        self.assertEqual(s.active_hwnds,())
        self.assertEqual(sum(e[0]=="unregister" for e in b.events),3)
    def test_shutdown_failure_is_reported_and_closed_permanently(self):
        b=ErrorAfterNativeRelease()
        s=ReadOnlyDwmPreviews(b)
        s.sync(three_placements())
        with self.assertRaises(OSError):s.shutdown()
        self.assertEqual(s.active_hwnds,())
        self.assertEqual(s.sync((place(),)).errors,((41,"CLOSED"),))
        s.shutdown()
    def test_clear_twice_after_native_error_is_noop(self):
        b=ErrorAfterNativeRelease()
        s=ReadOnlyDwmPreviews(b)
        s.sync(three_placements())
        with self.assertRaises(OSError):s.clear()
        s.clear()
        self.assertEqual(sum(e[0]=="destroy" for e in b.events),3)
    def test_normal_three_slots_still_cleanup_without_exception(self):
        b=ErrorAfterNativeRelease(failure_count=0)
        s=ReadOnlyDwmPreviews(b)
        s.sync(three_placements())
        s.shutdown()
        self.assertEqual(s.active_hwnds,())
        self.assertEqual(sum(e[0]=="destroy" for e in b.events),3)

class S71HostFailureSafety(unittest.TestCase):
    def setUp(self):
        self.rows=(row(1),row(2))
        self.events=[]
        self.backend=SourceBackend(self.rows)
        class RaisingSession(Session):
            def shutdown(this):
                this.events.append("dwm_unregister_error")
                raise OSError("DWM_TEST_ERROR")
        self.root=Root()
        self.host=C14DetachedHost(
            self.root,windows_backend=self.backend,
            toplevel_factory=lambda parent:Widget(self.events),
            resolve_root_hwnd=lambda hwnd:hwnd,
            is_topmost=lambda hwnd:True,
            session_factory=lambda:RaisingSession(self.events))
    def open(self):
        return self.host.open(snap(*self.rows),max_windows=2,
                              allowed=lambda:True)
    def test_host_closed_after_session_shutdown_raised(self):
        self.assertEqual(self.open().code,"HOST_OPEN")
        result=self.host.close()
        self.assertEqual(result.code,"HOST_CLOSED_NATIVE_CLEANUP_FAILED")
        self.assertIn("host_destroy",self.events)
        self.assertEqual(self.host.owner_hwnd,0)
        self.assertLess(self.events.index("dwm_unregister_error"),
                        self.events.index("host_destroy"))
    def test_shutdown_marks_permanently_closed_even_on_failure(self):
        self.open()
        self.assertEqual(self.host.shutdown().code,"CLOSED_NATIVE_CLEANUP_FAILED")
        self.assertEqual(self.host.open(snap(*self.rows),max_windows=2,
                         allowed=lambda:True).code,"CLOSED")
        self.assertEqual(self.host.owner_hwnd,0)
    def test_close_without_open_remains_successful_and_idempotent(self):
        self.assertEqual(self.host.close().code,"HOST_CLOSED")
        self.assertEqual(self.host.shutdown().code,"CLOSED")
    def test_wrong_thread_cannot_force_native_teardown(self):
        import threading
        self.open()
        results=[]
        t=threading.Thread(target=lambda:results.append(self.host.close().code))
        t.start();t.join()
        self.assertEqual(results,["WRONG_TK_THREAD"])
        self.assertEqual(self.host.owner_hwnd,900)
        self.assertEqual(self.host.close().code,"HOST_CLOSED_NATIVE_CLEANUP_FAILED")
    def test_no_fake_UI_or_input_intrusion(self):
        for path in ("src/dwm_preview.py","src/detached_host.py"):
            source=(ROOT/path).read_text("utf-8")
            for text in ("CreateRemoteThread(","PostMessage(","ReadProcessMemory(",
                         "tk.Button(", "proxy_tab"):
                self.assertNotIn(text,source)

if __name__=="__main__":unittest.main()
