"""S66 exact original C06 Xếp ngang/dọc 50px position-only Win32 engine."""
from __future__ import annotations
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"tests"))
from test_s17 import Backend,row,snap
from window_stacking import C10C11WindowStacker

class S66WindowStacks(unittest.TestCase):
    def setUp(self):
        self.rows=[row(1),row(2),row(3)]
        self.backend=Backend(self.rows)
        self.service=C10C11WindowStacker(self.backend)
    def test_horizontal_master_first_real_offset(self):
        result=self.service.apply(snap(*self.rows),mode="horizontal",
                                  max_windows=3,master_hwnd=3)
        self.assertEqual(result.code,"STACK_HORIZONTAL_APPLIED")
        self.assertEqual(self.backend.moves,[(3,0,0),(1,50,0),(2,100,0)])
    def test_vertical_master_first_real_offset(self):
        result=self.service.apply(snap(*self.rows),mode="vertical",
                                  max_windows=3,master_hwnd=2)
        self.assertEqual(result.code,"STACK_VERTICAL_APPLIED")
        self.assertEqual(self.backend.moves,[(2,0,0),(1,0,50),(3,0,100)])
    def test_both_modes_preserve_native_size(self):
        originals={h:(v[2]-v[0],v[3]-v[1]) for h,v in self.backend.positions.items()}
        for mode in ("horizontal","vertical"):
            self.assertIn("APPLIED",self.service.apply(snap(*self.rows),
                             mode=mode,max_windows=3).code)
            self.assertEqual({h:(v[2]-v[0],v[3]-v[1])
                              for h,v in self.backend.positions.items()},originals)
    def test_second_horizontal_is_idempotent_no_move(self):
        self.service.apply(snap(*self.rows),mode="horizontal",max_windows=3)
        self.backend.moves.clear()
        result=self.service.apply(snap(*self.rows),mode="horizontal",max_windows=3)
        self.assertEqual(result.unchanged,(1,2,3))
        self.assertEqual(self.backend.moves,[])
    def test_second_vertical_is_idempotent_no_move(self):
        self.service.apply(snap(*self.rows),mode="vertical",max_windows=3)
        self.backend.moves.clear()
        result=self.service.apply(snap(*self.rows),mode="vertical",max_windows=3)
        self.assertEqual(result.unchanged,(1,2,3))
        self.assertEqual(self.backend.moves,[])
    def test_all_four_existing_modes_still_supported(self):
        codes={"tight":"STACK_TIGHT_APPLIED","diagonal":"STACK_DIAGONAL_APPLIED",
               "horizontal":"STACK_HORIZONTAL_APPLIED","vertical":"STACK_VERTICAL_APPLIED"}
        for mode,expected in codes.items():
            self.assertEqual(self.service.apply(snap(*self.rows),mode=mode,
                                               max_windows=3).code,expected)
    def test_unverified_or_overlimit_denies_both_modes(self):
        for mode in ("horizontal","vertical"):
            self.assertEqual(self.service.apply(snap(*self.rows),
                mode=mode,max_windows=None).code,"NO_VERIFIED_WINDOW_LIMIT")
            self.assertEqual(self.service.apply(snap(*self.rows),
                mode=mode,max_windows=2).code,"OVER_VERIFIED_LIMIT")
        self.assertEqual(self.backend.moves,[])
    def test_reused_pid_denies_batch_before_move(self):
        self.backend.bumped_pid[3]=9090
        for mode in ("horizontal","vertical"):
            self.assertEqual(self.service.apply(snap(*self.rows),
                mode=mode,max_windows=3).code,"STALE_OR_REUSED_PID")
        self.assertEqual(self.backend.moves,[])
    def test_unknown_master_or_duplicate_hwnd_denied(self):
        for mode in ("horizontal","vertical"):
            self.assertEqual(self.service.apply(snap(*self.rows),
                mode=mode,max_windows=3,master_hwnd=999).code,"MASTER_NOT_IN_CACHE")
            self.assertEqual(self.service.apply(snap(self.rows[0],self.rows[0]),
                mode=mode,max_windows=3).code,"INVALID_OR_AMBIGUOUS_CACHE")
    def test_cancel_before_move(self):
        self.assertEqual(self.service.apply(snap(*self.rows),mode="horizontal",
            max_windows=3,allowed=lambda:False).code,"CANCELLED")
        self.assertEqual(self.backend.moves,[])
    def test_revoke_after_first_native_move_stops_followers(self):
        permit=[True]
        original=self.backend.move_no_resize
        def cancel(h,x,y):
            ok=original(h,x,y)
            permit[0]=False
            return ok
        self.backend.move_no_resize=cancel
        result=self.service.apply(snap(*self.rows),mode="vertical",
            max_windows=3,allowed=lambda:permit[0])
        self.assertEqual(result.code,"CANCELLED")
        self.assertEqual(result.moved,(1,))
        self.assertEqual(self.backend.moves,[(1,0,0)])
    def test_no_new_unverified_ui_no_proxy_no_input(self):
        content=(ROOT/"src/window_stacking.py").read_text("utf-8")
        for unsupported in ("tk.Button(", "CreateRemoteThread", "proxy_tab",
                            "PostMessage(", "ReadProcessMemory(", "shutdown /s"):
            self.assertNotIn(unsupported,content)

if __name__=="__main__":unittest.main()
