"""S60: never claim original C12 physical hide without native rectangle proof."""
from __future__ import annotations
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"tests"))
from test_s17 import Backend,row,snap
from window_hide import C12HideAll,HIDE_X,HIDE_Y

class S60NativeReadback(unittest.TestCase):
    def setUp(self):
        self.rows=[row(1),row(2),row(3)]
        self.b=Backend(self.rows)
        self.svc=C12HideAll(self.b)

    def test_noop_success_does_not_mark_hidden(self):
        original=dict(self.b.positions)
        self.b.move_no_resize=lambda h,x,y:True
        result=self.svc.hide(snap(*self.rows),max_windows=3)
        self.assertEqual(result.code,"MOVE_UNVERIFIED_PARTIAL")
        self.assertTrue(self.svc.partial)
        self.assertFalse(self.svc.hidden)
        self.assertEqual(self.b.positions,original)
        self.assertEqual(result.saved_rects,((1,self.rows[0].pid,original[1]),))
        self.assertEqual(self.svc.hide(snap(*self.rows),max_windows=3).code,
                         "PARTIAL_HIDE_REQUIRES_RECONCILIATION")

    def test_last_move_false_positive_does_not_report_hidden(self):
        move=self.b.move_no_resize
        self.b.move_no_resize=lambda h,x,y:True if h==3 else move(h,x,y)
        result=self.svc.hide(snap(*self.rows),max_windows=3)
        self.assertEqual(result.code,"MOVE_UNVERIFIED_PARTIAL")
        self.assertEqual(result.moved,(1,2,3))
        self.assertTrue(self.svc.partial)
        self.assertNotEqual(self.b.positions[3][:2],(HIDE_X,HIDE_Y))

    def test_unexpected_size_change_is_rejected(self):
        move=self.b.move_no_resize
        def resize(h,x,y):
            result=move(h,x,y)
            l,t,r,b=self.b.positions[h]
            self.b.positions[h]=(l,t,r+1,b)
            return result
        self.b.move_no_resize=resize
        self.assertEqual(self.svc.hide(snap(*self.rows),max_windows=3).code,
                         "MOVE_UNVERIFIED_PARTIAL")
        self.assertTrue(self.svc.partial)

    def test_stale_pid_after_move_is_rejected(self):
        move=self.b.move_no_resize
        def reuse(h,x,y):
            result=move(h,x,y)
            self.b.bumped_pid[h]=90000
            return result
        self.b.move_no_resize=reuse
        self.assertEqual(self.svc.hide(snap(*self.rows),max_windows=3).code,
                         "STALE_AFTER_MOVE_PARTIAL")
        self.assertTrue(self.svc.partial)

    def test_previously_offscreen_then_failed_move_tracks_partial(self):
        self.b.positions[1]=(-2200,-2200,-2080,-2110)
        move=self.b.move_no_resize
        self.b.move_no_resize=lambda h,x,y:True if h==2 else move(h,x,y)
        result=self.svc.hide(snap(*self.rows),max_windows=3)
        self.assertEqual(result.code,"MOVE_UNVERIFIED_PARTIAL")
        self.assertEqual(result.unchanged,(1,))
        self.assertEqual(len(result.saved_rects),2)
        self.assertTrue(self.svc.partial)

    def test_real_moves_still_hidden_and_preserve_dimensions(self):
        original=dict(self.b.positions)
        result=self.svc.hide(snap(*self.rows),max_windows=3,master_hwnd=3)
        self.assertEqual(result.code,"HIDDEN")
        self.assertEqual(result.moved,(3,1,2))
        self.assertTrue(self.svc.hidden)
        for h,r in self.b.positions.items():
            self.assertEqual(r[:2],(HIDE_X,HIDE_Y))
            self.assertEqual((r[2]-r[0],r[3]-r[1]),
                    (original[h][2]-original[h][0],original[h][3]-original[h][1]))
        self.assertFalse(hasattr(self.svc,"show"))
        self.assertFalse(hasattr(self.svc,"restore"))
if __name__=="__main__":unittest.main()
