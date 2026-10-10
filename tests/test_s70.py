"""S70 12 original-backed C14 topmost host tests, no fake user controls."""
from __future__ import annotations
import os,sys,threading,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"tests"))
from test_s17 import Backend,row,snap
from detached_host import C14DetachedHost
from detached_preview import DetachedResult,DetachedRegion
from dwm_preview import PreviewPlacement

class Root:
    def __init__(self,w=1600,h=1000):self.w,self.h=w,h
    def winfo_screenwidth(self):return self.w
    def winfo_screenheight(self):return self.h

class Widget:
    def __init__(self,events):self.events=events;self.exists=True
    def withdraw(self):self.events.append("withdraw")
    def overrideredirect(self,x):self.events.append(("undecorated",x))
    def geometry(self,x):self.events.append(("geometry",x))
    def wm_attributes(self,*a):self.events.append(("wm_attributes",*a))
    def deiconify(self):self.events.append("deiconify")
    def update_idletasks(self):self.events.append("update_idletasks")
    def update(self):self.events.append("update")
    def winfo_id(self):return 900
    def winfo_exists(self):return self.exists
    def destroy(self):self.events.append("host_destroy");self.exists=False

class SourceBackend(Backend):
    def __init__(self,rows):
        super().__init__(rows)
        self.host_pid=os.getpid()
        self.owner_rectangle=(0,768,1150,1000)
        self.host_visible=True
        self.owner_available=True
        self.pid_changed=False
    def enumerate_top_level(self):
        return ((900,) if self.owner_available else ()) + tuple(super().enumerate_top_level())
    def is_window(self,h):
        return self.owner_available if h==900 else super().is_window(h)
    def is_visible(self,h):
        return self.host_visible if h==900 else super().is_visible(h)
    def process_id(self,h):
        return (self.host_pid+1 if self.pid_changed else self.host_pid) if h==900 else super().process_id(h)
    def window_rect(self,h):
        return self.owner_rectangle if h==900 else super().window_rect(h)

class Session:
    def __init__(self,events):
        self.events=events;self.active_hwnds=()
    def update(self,*args,**kwargs):
        self.events.append(("session_update",kwargs["owner_hwnd"],
                            tuple(p.hwnd for p in kwargs["placements"])))
        self.active_hwnds=tuple(p.hwnd for p in kwargs["placements"])
        return DetachedResult("DETACHED_DWM_VISIBLE",self.active_hwnds)
    def shutdown(self):
        self.events.append("dwm_unregistered")
        self.active_hwnds=()

class S70HostTests(unittest.TestCase):
    def setUp(self):
        self.rows=(row(1),row(2))
        self.root=Root()
        self.backend=SourceBackend(self.rows)
        self.events=[]
        self.host=C14DetachedHost(
            self.root,windows_backend=self.backend,
            toplevel_factory=lambda parent:Widget(self.events),
            resolve_root_hwnd=lambda hwnd:hwnd,
            is_topmost=lambda hwnd:True,
            session_factory=lambda:Session(self.events))
    def open(self,**kw):
        return self.host.open(snap(*kw.get("rows",self.rows)),
               max_windows=kw.get("max_windows",2),
               allowed=kw.get("allowed",lambda:True))
    def test_original_C14_owner_geometry_topmost_and_owner_pid(self):
        result=self.open()
        self.assertEqual(result.code,"HOST_OPEN")
        self.assertEqual(result.region,DetachedRegion(0,768,1150,232))
        self.assertIn(("geometry","1150x232+0+768"),self.events)
        self.assertIn(("wm_attributes","-topmost",True),self.events)
        self.assertIn(("undecorated",True),self.events)
        self.assertEqual(self.host.owner_hwnd,900)
    def test_screen_1024x768_real_CI_must_refuse_without_new_window(self):
        self.root.w,self.root.h=1024,768
        self.assertEqual(self.open().code,"NO_USABLE_SCREEN_REGION")
        self.assertFalse(self.events)
    def test_missing_server_window_limit_or_unverified_cache(self):
        self.assertEqual(self.open(max_windows=0).code,"NO_VERIFIED_WINDOW_LIMIT")
        self.assertEqual(self.open(max_windows=1).code,"OVER_VERIFIED_LIMIT")
        self.assertEqual(self.open(rows=()).code,"NO_WINDOWS")
        self.assertFalse(self.events)
    def test_stale_game_source_rejected_before_host_created(self):
        self.backend.bumped_pid[2]=987654
        self.assertEqual(self.open().code,"STALE_SOURCE")
        self.assertEqual(self.events,[])
    def test_no_permission_or_revoked_permission_does_not_create_host(self):
        self.assertEqual(self.open(allowed=lambda:False).code,"CANCELLED")
        self.assertEqual(self.events,[])
    def test_native_owner_wrong_PID_closes_host_and_never_returns_open(self):
        self.backend.pid_changed=True
        self.assertEqual(self.open().code,"OWNER_NATIVE_PROOF_FAILED")
        self.assertEqual(self.host.owner_hwnd,0)
        self.assertIn("host_destroy",self.events)
    def test_native_owner_wrong_rect_closes_without_thumb_registration(self):
        self.backend.owner_rectangle=(0,769,1150,1001)
        self.assertEqual(self.open().code,"OWNER_NATIVE_PROOF_FAILED")
        self.assertNotIn("dwm_unregistered",self.events)
    def test_failed_native_topmost_check_rejects_host(self):
        self.host._is_topmost=lambda h:False
        self.assertEqual(self.open().code,"OWNER_NATIVE_PROOF_FAILED")
    def test_render_delegates_only_explicit_place_from_external_authority(self):
        self.assertEqual(self.open().code,"HOST_OPEN")
        places=(PreviewPlacement(1,self.rows[0].pid,900,10,800,197,110),
                PreviewPlacement(2,self.rows[1].pid,900,250,800,197,110))
        response=self.host.render(snap(*self.rows),max_windows=2,
                 placements=places,allowed=lambda:True)
        self.assertEqual(response.code,"DETACHED_DWM_VISIBLE")
        self.assertEqual(response.rendered,(1,2))
        self.assertEqual(self.host.active_hwnds,(1,2))
    def test_close_dwm_unregisters_before_native_owner_destroy(self):
        self.open()
        self.host.close()
        self.assertLess(self.events.index("dwm_unregistered"),
                        self.events.index("host_destroy"))
        self.assertEqual(self.host.owner_hwnd,0)
        self.assertEqual(self.host.close().code,"HOST_CLOSED")
    def test_owner_reused_pid_or_screen_changed_revokes_and_closes(self):
        self.open()
        self.backend.pid_changed=True
        self.assertEqual(self.open().code,"OWNER_INVALIDATED")
        self.assertEqual(self.host.owner_hwnd,0)
        self.backend.pid_changed=False
        self.open()
        self.root.h=1100
        outcome=self.host.render(snap(*self.rows),max_windows=2,
                  placements=(),allowed=lambda:True)
        self.assertEqual(outcome.code,"SCREEN_CHANGED")
        self.assertFalse(self.host.owner_hwnd)
    def test_owner_thread_restriction_shutdown_and_no_inert_ui(self):
        result=[]
        t=threading.Thread(target=lambda:result.append(self.open().code))
        t.start();t.join()
        self.assertEqual(result,["WRONG_TK_THREAD"])
        self.assertFalse(self.events)
        self.open()
        self.assertEqual(self.host.shutdown().code,"CLOSED")
        self.assertEqual(self.open().code,"CLOSED")
        txt=(ROOT/"src/detached_host.py").read_text("utf-8")
        for token in ("tk.Button(", "PostMessage(", "ReadProcessMemory(",
                      "self._auto_open(", "CreateRemoteThread", "proxy_tab"):
            self.assertNotIn(token,txt)

if __name__=="__main__":unittest.main()
