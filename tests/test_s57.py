"""S57: genuine C12 hide-to-offscreen behavior, no guessed show/restore.

The original TLM 2.1.2 source-backed binary C12 evidence establishes
(-2200,-2200), preserve size, cached window rectangles and NO SW_HIDE.
The actual restore branch conflicts in recovered original docs: saved
positions vs (0,0). Deliberately DO NOT IMPLEMENT show/restore here.
"""
from __future__ import annotations
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"tests"))
from test_s17 import Backend,row,snap
from start_windows import GameWindow,GAME_PROCESS,GAME_TITLE,UNITY_WINDOW_CLASS
from window_hide import C12HideAll, HideResult, HIDE_X, HIDE_Y

class S57OriginalC12HideTests(unittest.TestCase):
    def setUp(self):
        self.rows=[row(1),row(2),row(3)]
        self.b=Backend(self.rows)
        self.service=C12HideAll(self.b)
    def test_original_target_exact_and_master_first(self):
        before=dict(self.b.positions)
        r=self.service.hide(snap(*self.rows),max_windows=3,master_hwnd=3)
        self.assertEqual((HIDE_X,HIDE_Y),(-2200,-2200))
        self.assertEqual(r.code,"HIDDEN")
        self.assertEqual(self.b.moves,[(3,-2200,-2200),(1,-2200,-2200),(2,-2200,-2200)])
        self.assertEqual(r.moved,(3,1,2))
        self.assertEqual(tuple(x[0] for x in r.saved_rects),(3,1,2))
        self.assertEqual(dict((hwnd,rect) for hwnd,_pid,rect in r.saved_rects),before)
        self.assertTrue(self.service.hidden)
        for h,rect in self.b.positions.items():
            self.assertEqual(rect[:2],(-2200,-2200))
            self.assertEqual((rect[2]-rect[0],rect[3]-rect[1]),
                             (before[h][2]-before[h][0],before[h][3]-before[h][1]))
    def test_second_hide_cannot_overwrite_saved_visible_rectangles(self):
        first=self.service.hide(snap(*self.rows),max_windows=3)
        stored=first.saved_rects
        self.b.moves.clear()
        second=self.service.hide(snap(*self.rows),max_windows=3)
        self.assertEqual(second.code,"ALREADY_HIDDEN")
        self.assertEqual(second.saved_rects,stored)
        self.assertEqual(self.b.moves,[])
    def test_no_verified_entitlement_never_moves(self):
        for limit in (None,0,-1,True,"999"):
            with self.subTest(limit=limit):
                self.assertEqual(self.service.hide(snap(*self.rows),
                           max_windows=limit).code,"NO_VERIFIED_WINDOW_LIMIT")
        self.assertEqual(self.b.moves,[])
    def test_validated_limit_rejects_overcount(self):
        r=self.service.hide(snap(*self.rows),max_windows=2)
        self.assertEqual(r.code,"OVER_VERIFIED_LIMIT")
        self.assertEqual(self.b.moves,[])
    def test_bad_snapshot_and_duplicate_hwnd_rejected(self):
        self.assertEqual(self.service.hide(snap(*self.rows,valid=False),
                     max_windows=3).code,"INVALID_CACHE")
        self.assertEqual(self.service.hide(snap(self.rows[0],self.rows[0]),
                     max_windows=3).code,"INVALID_OR_AMBIGUOUS_CACHE")
        self.assertEqual(self.b.moves,[])
    def test_unowned_or_non_game_executable_rejected(self):
        other=GameWindow(1,5001,GAME_TITLE,UNITY_WINDOW_CLASS,"bad.exe")
        self.assertEqual(self.service.hide(snap(other),max_windows=2).code,
                         "INVALID_OR_AMBIGUOUS_CACHE")
        self.b.live_process[5001]="not_game.exe"
        self.assertEqual(self.service.hide(snap(*self.rows),max_windows=3).code,
                         "LIVE_NOT_GAME")
        self.assertEqual(self.b.moves,[])
    def test_stale_pid_rejects_full_batch_before_any_movement(self):
        self.b.bumped_pid[2]=90001
        self.assertEqual(self.service.hide(snap(*self.rows),
                            max_windows=3).code,"STALE_OR_REUSED_PID")
        self.assertEqual(self.b.moves,[])
    def test_missing_master_no_guess(self):
        self.assertEqual(self.service.hide(snap(*self.rows),max_windows=3,
                master_hwnd=123456).code,"MASTER_NOT_IN_CACHE")
        self.assertEqual(self.b.moves,[])
    def test_cancel_before_first_movement_preserves_unhidden(self):
        self.assertEqual(self.service.hide(snap(*self.rows),max_windows=3,
                          allowed=lambda:False).code,"CANCELLED")
        self.assertEqual(self.b.moves,[])
        self.assertFalse(self.service.hidden)
        self.assertFalse(self.service.partial)
    def test_midflight_cancel_reports_partial_not_full_hide(self):
        can=[True]
        real=self.b.move_no_resize
        def once(hwnd,x,y):
            changed=real(hwnd,x,y)
            can[0]=False
            return changed
        self.b.move_no_resize=once
        r=self.service.hide(snap(*self.rows),max_windows=3,
                            allowed=lambda:can[0])
        self.assertEqual(r.code,"CANCELLED_PARTIAL")
        self.assertEqual(r.moved,(1,))
        self.assertFalse(self.service.hidden)
        self.assertTrue(self.service.partial)
        self.assertEqual([row[0] for row in r.saved_rects],[1])
        self.assertEqual(self.service.hide(snap(*self.rows),max_windows=3).code,
                         "PARTIAL_HIDE_REQUIRES_RECONCILIATION")
        self.assertEqual(len(self.b.moves),1)
    def test_pid_reuse_between_moves_stops_and_tracks_partial(self):
        real=self.b.move_no_resize
        def changed(hwnd,x,y):
            v=real(hwnd,x,y)
            self.b.bumped_pid[2]=43210
            return v
        self.b.move_no_resize=changed
        result=self.service.hide(snap(*self.rows),max_windows=3)
        self.assertEqual(result.code,"STALE_BEFORE_MOVE_PARTIAL")
        self.assertEqual(result.moved,(1,))
        self.assertTrue(self.service.partial)
    def test_no_restore_guess_sw_hide_or_runtime_proxy(self):
        self.assertFalse(hasattr(self.service,"show"))
        self.assertFalse(hasattr(self.service,"restore"))
        code=(ROOT/"src/window_hide.py").read_text("utf-8")
        for forbidden in ("SW_HIDE","ShowWindow(","subprocess.Popen(",
                          "CreateRemoteThread","PostMessage(","proxy_tab",
                          "shutdown /s","TLM_PROXY_ENABLE"):
            self.assertNotIn(forbidden,code)

if __name__=="__main__":
    unittest.main()
