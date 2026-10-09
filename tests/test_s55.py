"""S55: C10/C11 original-backed position-only stacking, no mock game action."""
from __future__ import annotations
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"tests"))
from test_s17 import Backend, row, snap
from start_windows import GameWindow, GAME_PROCESS, GAME_TITLE, UNITY_WINDOW_CLASS
from window_stacking import C10C11WindowStacker, StackResult

class S55WindowStackBehavior(unittest.TestCase):
    def test_c10_all_to_origin_master_first_preserves_sizes(self):
        entries=[row(10),row(20),row(30)]
        b=Backend(entries)
        widths={k:(r[2]-r[0],r[3]-r[1]) for k,r in b.positions.items()}
        done=C10C11WindowStacker(b).apply(snap(*entries),mode="tight",
                                             master_hwnd=30,max_windows=3)
        self.assertEqual(done.code,"STACK_TIGHT_APPLIED")
        self.assertEqual(b.moves,[(30,0,0),(10,0,0),(20,0,0)])
        self.assertEqual(done.moved,(30,10,20))
        self.assertEqual({k:(r[2]-r[0],r[3]-r[1]) for k,r in b.positions.items()},widths)
    def test_c11_50px_diagonal_order_master_first(self):
        entries=[row(10),row(20),row(30)]
        b=Backend(entries)
        done=C10C11WindowStacker(b).apply(snap(*entries),mode="diagonal",
                                             master_hwnd=20,max_windows=3)
        self.assertEqual(done.code,"STACK_DIAGONAL_APPLIED")
        self.assertEqual(b.moves,[(20,0,0),(10,50,50),(30,100,100)])
    def test_second_tight_stack_is_noop_with_real_coordinates(self):
        rows=[row(1),row(2)]
        b=Backend(rows);svc=C10C11WindowStacker(b)
        self.assertEqual(svc.apply(snap(*rows),mode="tight",max_windows=2).requested,2)
        b.moves.clear()
        result=svc.apply(snap(*rows),mode="tight",max_windows=2)
        self.assertEqual(b.moves,[])
        self.assertEqual(result.unchanged,(1,2))
    def test_no_permission_limit_means_no_movement(self):
        rows=[row(1)]
        b=Backend(rows)
        for limit in (0,-1,None,True,"2"):
            self.assertEqual(C10C11WindowStacker(b).apply(snap(*rows),mode="tight",
                                      max_windows=limit).code,"NO_VERIFIED_WINDOW_LIMIT")
        self.assertEqual(b.moves,[])
    def test_more_than_verified_limit_denied_before_moving(self):
        rows=[row(1),row(2)]
        b=Backend(rows)
        self.assertEqual(C10C11WindowStacker(b).apply(snap(*rows),mode="tight",
                                   max_windows=1).code,"OVER_VERIFIED_LIMIT")
        self.assertEqual(b.moves,[])
    def test_invalid_and_duplicate_cache_fail_closed(self):
        rows=[row(1)]
        b=Backend(rows)
        self.assertEqual(C10C11WindowStacker(b).apply(snap(*rows,valid=False),
                  mode="tight",max_windows=2).code,"INVALID_CACHE")
        self.assertEqual(C10C11WindowStacker(b).apply(snap(rows[0],rows[0]),
                  mode="tight",max_windows=2).code,"INVALID_OR_AMBIGUOUS_CACHE")
        self.assertEqual(b.moves,[])
    def test_stale_identity_is_prevalidated_before_any_move(self):
        rows=[row(1),row(2)]
        b=Backend(rows);b.bumped_pid[2]=99999
        self.assertEqual(C10C11WindowStacker(b).apply(snap(*rows),
                  mode="diagonal",max_windows=2).code,"STALE_OR_REUSED_PID")
        self.assertEqual(b.moves,[])
    def test_live_executable_must_match_original(self):
        rows=[row(1)];b=Backend(rows);b.live_process[5001]="not_the_game.exe"
        self.assertEqual(C10C11WindowStacker(b).apply(snap(*rows),
                  mode="tight",max_windows=1).code,"LIVE_NOT_GAME")
        self.assertEqual(b.moves,[])
    def test_master_must_be_in_cached_windows(self):
        rows=[row(1)];b=Backend(rows)
        self.assertEqual(C10C11WindowStacker(b).apply(snap(*rows),mode="tight",
                  master_hwnd=5,max_windows=1).code,"MASTER_NOT_IN_CACHE")
    def test_cancelled_never_moves_windows(self):
        rows=[row(1)];b=Backend(rows)
        self.assertEqual(C10C11WindowStacker(b).apply(snap(*rows),mode="tight",
                  max_windows=1,allowed=lambda:False).code,"CANCELLED")
        self.assertEqual(b.moves,[])
    def test_revocation_between_windows_stops_rest(self):
        rows=[row(1),row(2),row(3)];b=Backend(rows)
        allow=[True];old=b.move_no_resize
        def stop_after_one(hwnd,x,y):
            value=old(hwnd,x,y)
            allow[0]=False
            return value
        b.move_no_resize=stop_after_one
        result=C10C11WindowStacker(b).apply(snap(*rows),mode="diagonal",
                    max_windows=3,allowed=lambda:allow[0])
        self.assertEqual(result.code,"CANCELLED")
        self.assertEqual(len(b.moves),1)
        self.assertEqual(result.moved,(1,))
    def test_last_instant_pid_change_disallows_stale_window(self):
        rows=[row(1),row(2)];b=Backend(rows)
        old=b.move_no_resize
        def hijack(hwnd,x,y):
            v=old(hwnd,x,y)
            b.bumped_pid[2]=8888
            return v
        b.move_no_resize=hijack
        result=C10C11WindowStacker(b).apply(snap(*rows),mode="diagonal",max_windows=2)
        self.assertEqual(result.code,"STALE_BEFORE_MOVE")
        self.assertEqual(b.moves,[(1,0,0)])
    def test_invalid_modes_and_empty_cache(self):
        b=Backend([])
        self.assertEqual(C10C11WindowStacker(b).apply(snap(),mode="tight",max_windows=3).code,"NO_WINDOWS")
        self.assertEqual(C10C11WindowStacker(b).apply(snap(),mode="unknown",max_windows=3).code,"UNKNOWN_STACK_MODE")
    def test_no_game_launch_proxy_ini_or_fake_buttons(self):
        code=(ROOT/"src/window_stacking.py").read_text(encoding="utf-8")
        for forbidden in ("subprocess.Popen(", "write_settings(", "CreateRemoteThread",
                          "PostMessage(", "proxy_tab", "shutdown /s", "tk.Button("):
            self.assertNotIn(forbidden,code)

if __name__=="__main__":unittest.main()
