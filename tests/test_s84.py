"""S84 C13 original Đóng xem: actionable detached preview close, not WM_CLOSE game."""
from __future__ import annotations
import sys,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"tests")]
from detached_host import C14DetachedHost
from test_s70 import Root,SourceBackend,Widget,Session
from test_s17 import row,snap

class UiWidget(Widget):
    def __init__(self,events):
        super().__init__(events)
        self.tk=object()

class TestCloseButton:
    def __init__(self,parent,*,text,command):
        self.parent=parent
        self.text=text
        self.command=command
        self.bbox=None
    def place(self,**kw):self.bbox=kw
    def invoke(self):return self.command()

class S84DetachedOriginalCloseTests(unittest.TestCase):
    def setUp(self):
        self.rows=(row(1),row(2))
        self.events=[]
        self.backend=SourceBackend(self.rows)
        self.widgets=[]
        self.buttons=[]
        def widget_factory(_root):
            w=UiWidget(self.events)
            self.widgets.append(w)
            return w
        def button_factory(*args,**kw):
            b=TestCloseButton(*args,**kw)
            self.buttons.append(b)
            return b
        self.patch=patch("tkinter.ttk.Button",side_effect=button_factory)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.host=C14DetachedHost(
            Root(),windows_backend=self.backend,
            toplevel_factory=widget_factory,
            resolve_root_hwnd=lambda hwnd:hwnd,is_topmost=lambda _:True,
            session_factory=lambda:Session(self.events))
    def open(self,allowed=lambda:True):
        return self.host.open(snap(*self.rows),max_windows=2,allowed=allowed)

    def test_01_real_original_C13_label_action_created_after_authorized_open(self):
        self.assertEqual(self.open().code,"HOST_OPEN")
        self.assertEqual(len(self.buttons),1)
        self.assertEqual(self.buttons[0].text,"Đóng xem")
        self.assertEqual(self.host._close_view_button,self.buttons[0])

    def test_02_button_is_a_real_callback_not_placeholder(self):
        self.open()
        self.assertEqual(self.buttons[0].invoke().code,"HOST_CLOSED")
        self.assertEqual(self.host.owner_hwnd,0)
        self.assertFalse(self.widgets[0].exists)

    def test_03_dwm_unregistered_before_host_destroy(self):
        self.open()
        self.buttons[0].invoke()
        self.assertLess(self.events.index("dwm_unregistered"),
                        self.events.index("host_destroy"))

    def test_04_original_sources_are_not_destroyed_by_dong_xem(self):
        self.open()
        self.buttons[0].invoke()
        self.assertEqual(self.backend.rows,{x.hwnd:x for x in self.rows})
        self.assertEqual(self.host.active_hwnds,())
        self.assertEqual(self.backend.enumerate_top_level(),(900,1,2))

    def test_05_host_can_reopen_on_independent_session_after_user_close(self):
        self.open()
        self.buttons[0].invoke()
        self.assertEqual(self.open().code,"HOST_OPEN")
        self.assertEqual(len(self.buttons),2)
        self.assertEqual(self.host.owner_hwnd,900)

    def test_06_unverified_permission_never_creates_control(self):
        self.assertEqual(self.open(allowed=lambda:False).code,"CANCELLED")
        self.assertEqual(self.buttons,[])
        self.assertEqual(self.widgets,[])

    def test_07_closed_owner_clears_button_reference(self):
        self.open()
        self.host.close()
        self.assertIsNone(self.host._close_view_button)

    def test_08_repeat_close_does_not_close_native_source(self):
        self.open()
        self.buttons[0].invoke()
        self.assertEqual(self.host.close().code,"HOST_CLOSED")
        self.assertEqual(len(self.backend.rows),2)

    def test_09_no_screen_region_never_builds_a_button(self):
        self.host.root=Root(w=1024,h=768)
        self.assertEqual(self.open().code,"NO_USABLE_SCREEN_REGION")
        self.assertFalse(self.buttons)

    def test_10_reused_OWNER_identity_refuses_without_button(self):
        self.backend.pid_changed=True
        self.assertEqual(self.open().code,"OWNER_NATIVE_PROOF_FAILED")
        self.assertEqual(len(self.buttons),0)

    def test_11_native_cleanup_error_keeps_explicit_status(self):
        class Broken(Session):
            def shutdown(self):
                self.events.append("dwm_failed")
                raise OSError("TEST_ONLY_DWM_CLEANUP_FAILURE")
        self.host._session_factory=lambda:Broken(self.events)
        self.open()
        self.assertEqual(self.buttons[0].invoke().code,
                         "HOST_CLOSED_NATIVE_CLEANUP_FAILED")
        self.assertIn("host_destroy",self.events)

    def test_12_source_has_no_game_kill_or_fake_authorization(self):
        src=(ROOT/"src/detached_host.py").read_text("utf-8")
        self.assertIn('text="Đóng xem"',src)
        self.assertIn('command=self.close',src)
        for token in ("PostMessage(","TerminateProcess(","CreateRemoteThread(",
                      "ReadProcessMemory(","proxy_tab","tk.Button("):
            self.assertNotIn(token,src)

if __name__=="__main__":unittest.main()
