"""S61: C07 exact original 1366x768 origin transition primitive."""
from __future__ import annotations
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"tests"))
from test_s17 import Backend,row,snap
from start_windows import GameWindow,GAME_TITLE,UNITY_WINDOW_CLASS
from window_auto_reset import C07AutoReset,AUTO_WIDTH,AUTO_HEIGHT,AUTO_X,AUTO_Y

class ResizeBackend(Backend):
    def __init__(self,rows):
        super().__init__(rows)
        self.resizes=[]
    def resize_no_move(self,h,w,ht):
        l,t,_,_=self.positions[h]
        self.positions[h]=(l,t,l+w,t+ht)
        self.resizes.append((h,w,ht))
        return True

class S61AutoResetTests(unittest.TestCase):
    def setUp(self):
        self.rows=[row(1),row(2),row(3)]
        self.b=ResizeBackend(self.rows)
        self.svc=C07AutoReset(self.b)

    def test_exact_original_reset_geometry_and_master_first(self):
        result=self.svc.apply(snap(*self.rows),max_windows=3,master_hwnd=3)
        self.assertEqual((AUTO_X,AUTO_Y,AUTO_WIDTH,AUTO_HEIGHT),(0,0,1366,768))
        self.assertEqual(result.code,"AUTO_RESET_APPLIED")
        self.assertEqual(result.resized,(3,1,2))
        self.assertEqual(result.moved,(3,1,2))
        self.assertEqual(self.b.resizes,[(3,1366,768),(1,1366,768),(2,1366,768)])
        self.assertEqual(len(result.saved_rects),3)
        for r in self.b.positions.values():
            self.assertEqual(r,(0,0,1366,768))

    def test_repeat_applied_already_correct_is_noop(self):
        self.svc.apply(snap(*self.rows),max_windows=3)
        self.b.moves.clear();self.b.resizes.clear()
        out=self.svc.apply(snap(*self.rows),max_windows=3)
        self.assertEqual(out.code,"AUTO_RESET_APPLIED")
        self.assertEqual(out.unchanged,(1,2,3))
        self.assertEqual(self.b.resizes,[])
        self.assertEqual(self.b.moves,[])

    def test_bad_limits_and_overlimit_no_native_calls(self):
        for v in (None,0,-1,True,"3"):
            self.assertEqual(self.svc.apply(snap(*self.rows),max_windows=v).code,
                             "NO_VERIFIED_WINDOW_LIMIT")
        self.assertEqual(self.svc.apply(snap(*self.rows),max_windows=2).code,
                         "OVER_VERIFIED_LIMIT")
        self.assertEqual(self.b.resizes,[])

    def test_stale_pid_preflight_blocks_entire_batch(self):
        self.b.bumped_pid[2]=999
        self.assertEqual(self.svc.apply(snap(*self.rows),max_windows=3).code,
                         "STALE_OR_REUSED_PID")
        self.assertEqual(self.b.resizes,[])

    def test_duplicate_invalid_cache_and_non_game_rejected(self):
        self.assertEqual(self.svc.apply(snap(*self.rows,valid=False),max_windows=3).code,
                         "INVALID_CACHE")
        self.assertEqual(self.svc.apply(snap(self.rows[0],self.rows[0]),
                       max_windows=3).code,"INVALID_OR_AMBIGUOUS_CACHE")
        self.b.live_process[self.rows[0].pid]="not_game.exe"
        self.assertEqual(self.svc.apply(snap(*self.rows),max_windows=3).code,
                         "LIVE_NOT_GAME")
        self.assertEqual(self.b.resizes,[])

    def test_unknown_master_and_empty_cache_no_actions(self):
        self.assertEqual(self.svc.apply(snap(*self.rows),max_windows=3,
                         master_hwnd=999).code,"MASTER_NOT_IN_CACHE")
        self.assertEqual(self.svc.apply(snap(),max_windows=3).code,"NO_WINDOWS")

    def test_initial_revocation_no_resize(self):
        self.assertEqual(self.svc.apply(snap(*self.rows),max_windows=3,
                 allowed=lambda:False).code,"CANCELLED")
        self.assertEqual(self.b.resizes,[])

    def test_revoke_after_first_resize_is_partial_and_no_more_changes(self):
        allowed=[True]
        real=self.b.resize_no_move
        def cancel(h,w,ht):
            result=real(h,w,ht);allowed[0]=False;return result
        self.b.resize_no_move=cancel
        out=self.svc.apply(snap(*self.rows),max_windows=3,
                           allowed=lambda:allowed[0])
        self.assertEqual(out.code,"CANCELLED_PARTIAL")
        self.assertEqual(out.resized,(1,))
        self.assertEqual(self.b.moves,[])

    def test_backend_lies_about_resize_fails_closed(self):
        self.b.resize_no_move=lambda h,w,ht:True
        out=self.svc.apply(snap(*self.rows),max_windows=3)
        self.assertEqual(out.code,"RESIZE_UNVERIFIED_PARTIAL")
        self.assertEqual(out.resized,(1,))
        self.assertEqual(self.b.moves,[])

    def test_backend_lies_about_move_fails_closed(self):
        self.b.move_no_resize=lambda h,x,y:True
        out=self.svc.apply(snap(*self.rows),max_windows=3)
        self.assertEqual(out.code,"FINAL_GEOMETRY_UNVERIFIED_PARTIAL")
        self.assertEqual(out.resized,(1,))
        self.assertEqual(out.moved,(1,))

    def test_stale_pid_between_resize_and_move_fails_closed(self):
        real=self.b.resize_no_move
        def reuse(h,w,ht):
            result=real(h,w,ht)
            self.b.bumped_pid[h]=88888
            return result
        self.b.resize_no_move=reuse
        out=self.svc.apply(snap(*self.rows),max_windows=3)
        self.assertEqual(out.code,"STALE_AFTER_RESIZE_PARTIAL")

    def test_source_does_not_mock_mode_ui_or_proxy(self):
        code=(ROOT/"src/window_auto_reset.py").read_text("utf-8")
        for forbidden in ("tk.Button(", "tk.Radiobutton(", "proxy_tab",
                          "PostMessage(", "CreateRemoteThread", "shutdown /s"):
            self.assertNotIn(forbidden,code)
if __name__=="__main__":unittest.main()
