"""S68 C14 independent detached DWM session, source-backed bounds only."""
from __future__ import annotations
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"tests"))
from test_s11 import FakeDwmBackend
from test_s17 import row,snap
from detached_preview import (
    DETACHED_TOP,DETACHED_RIGHT_RESERVED,DetachedRegion,verified_detached_region,
    C14DetachedDwmSession,
)
from dwm_preview import PreviewPlacement,ReadOnlyDwmPreviews
from start_windows import GAME_PROCESS,GAME_TITLE,UNITY_WINDOW_CLASS

class WindowsFixture:
    def __init__(self,rows,owner=500,owner_pid=6000):
        self.owner=owner
        self.owner_pid=owner_pid
        self.rows={w.hwnd:w for w in rows}
        self.rect=(0,768,1150,1000)
        self.stale={}
        self.hidden=set()
        self.bad_process=False
    def enumerate_top_level(self):
        return (self.owner,)+tuple(self.rows)
    def is_window(self,h):
        return h==self.owner or h in self.rows
    def is_visible(self,h):
        return self.is_window(h) and h not in self.hidden
    def process_id(self,h):
        return self.stale.get(h,self.owner_pid if h==self.owner else self.rows[h].pid)
    def process_executable(self,p):
        return "invalid.exe" if self.bad_process else GAME_PROCESS
    def window_class(self,h):
        return UNITY_WINDOW_CLASS
    def title_with_timeout(self,h,ms):
        assert ms==150
        return GAME_TITLE
    def window_rect(self,h):
        return self.rect if h==self.owner else (20,20,180,120)

class S68DetachedDwm(unittest.TestCase):
    def setUp(self):
        self.rows=(row(41),row(42))
        self.win=WindowsFixture(self.rows)
        self.dwm=FakeDwmBackend()
        self.dwm.live={w.hwnd:w.pid for w in self.rows}
        self.svc=C14DetachedDwmSession(self.dwm,self.win)
        self.placements=(PreviewPlacement(41,self.rows[0].pid,500,20,788,197,110),
                         PreviewPlacement(42,self.rows[1].pid,500,238,788,197,110))
    def update(self,**kw):
        return self.svc.update(snap(*kw.get("rows",self.rows)),
                    owner_hwnd=kw.get("owner_hwnd",500),
                    owner_pid=kw.get("owner_pid",6000),
                    screen_width=kw.get("screen_width",1600),
                    screen_height=kw.get("screen_height",1000),
                    max_windows=kw.get("max_windows",2),
                    placements=kw.get("placements",self.placements),
                    allowed=kw.get("allowed",lambda:True))
    def test_exact_C14_region_formula_and_no_guessed_height(self):
        self.assertEqual((DETACHED_TOP,DETACHED_RIGHT_RESERVED),(768,450))
        self.assertEqual(verified_detached_region(1600,1000),DetachedRegion(0,768,1150,232))
        self.assertEqual(verified_detached_region(1920,1080),DetachedRegion(0,768,1470,312))
    def test_invalid_or_no_space_desktop_fails_closed(self):
        for dims in ((450,900),(1400,768),(1400,600),(True,900),
                     (1400,True),(1400,0),(-100,1100)):
            self.assertIsNone(verified_detached_region(*dims))
        self.assertEqual(self.update(screen_height=768).code,"NO_USABLE_SCREEN_REGION")
        self.assertEqual(self.dwm.events,[])
    def test_two_verified_distinct_real_DWM_registrations(self):
        result=self.update()
        self.assertEqual(result.code,"DETACHED_DWM_VISIBLE")
        self.assertEqual(result.rendered,(41,42))
        self.assertEqual(self.svc.active_hwnds,(41,42))
        self.assertEqual(sum(e[0]=="register" for e in self.dwm.events),2)
    def test_same_hwnd_update_keeps_dwm_thumbnail_identity(self):
        self.update()
        self.assertEqual(self.update().code,"DETACHED_DWM_VISIBLE")
        self.assertEqual(sum(e[0]=="register" for e in self.dwm.events),2)
    def test_owner_must_be_real_native_region(self):
        self.win.rect=(0,760,1150,992)
        self.assertEqual(self.update().code,"OWNER_REGION_MISMATCH")
        self.assertEqual(self.dwm.events,[])
    def test_owner_generation_reuse_clears_existing_thumbnail(self):
        self.update()
        self.win.stale[500]=1000
        self.assertEqual(self.update().code,"STALE_OR_HIDDEN_OWNER")
        self.assertEqual(self.svc.active_hwnds,())
        self.assertEqual(sum(e[0]=="unregister" for e in self.dwm.events),2)
    def test_window_identity_generation_reuse_clears_existing(self):
        self.update()
        self.win.stale[42]=77777
        self.assertEqual(self.update().code,"STALE_SOURCE_HWND_PID")
        self.assertEqual(self.svc.active_hwnds,())
    def test_reject_duplicate_and_outside_region_placements(self):
        p=self.placements
        for wrong in ((p[0],p[0]),
                      (p[0],PreviewPlacement(42,self.rows[1].pid,500,1100,768,197,110)),
                      (p[0],PreviewPlacement(42,self.rows[1].pid,501,240,788,197,110)),
                      (p[0],PreviewPlacement(42,999999,500,240,788,197,110))):
            self.assertEqual(self.update(placements=wrong).code,
                             "INVALID_OR_OUTSIDE_REGION")
        self.assertEqual(self.svc.active_hwnds,())
    def test_no_permission_or_no_game_source_never_registers(self):
        self.assertEqual(self.update(max_windows=0).code,"NO_VERIFIED_WINDOW_LIMIT")
        self.win.bad_process=True
        self.assertEqual(self.update().code,"LIVE_SOURCE_NOT_GAME")
        self.assertEqual(self.dwm.events,[])
    def test_compositor_registration_failure_destroys_partial_slots(self):
        self.dwm.fail_step="register"
        self.assertEqual(self.update().code,"DWM_INCOMPLETE")
        self.assertEqual(self.svc.active_hwnds,())
        self.assertEqual(sum(e[0]=="destroy" for e in self.dwm.events),2)
    def test_embedded_preview_independent_of_detached_shutdown(self):
        other=FakeDwmBackend()
        other.live=dict(self.dwm.live)
        embedded=ReadOnlyDwmPreviews(other)
        embedded.sync([self.placements[0]])
        self.assertEqual(self.update().code,"DETACHED_DWM_VISIBLE")
        self.svc.shutdown()
        self.assertEqual(self.svc.active_hwnds,())
        self.assertEqual(embedded.active_hwnds,(41,))
        self.assertEqual(self.update().code,"CLOSED")
        embedded.shutdown()
    def test_permission_revocation_releases_existing_and_no_fake_UI(self):
        self.update()
        self.assertEqual(self.update(allowed=lambda:False).code,"CANCELLED")
        self.assertEqual(self.svc.active_hwnds,())
        code=(ROOT/"src/detached_preview.py").read_text("utf-8")
        for x in ("tk.Button(","tk.Toplevel(","PostMessage(","ReadProcessMemory(",
                  "CreateRemoteThread","_toggle_detached_preview(", "proxy_tab"):
            self.assertNotIn(x,code)

if __name__=="__main__":unittest.main()
