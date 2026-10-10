"""S67: confirm real HWND rect and PID after C06 movement, all four modes."""
from __future__ import annotations
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"tests"))
from test_s17 import Backend,row,snap
from window_stacking import C10C11WindowStacker

MODES=("tight","diagonal","horizontal","vertical")

class S67PostMoveTruth(unittest.TestCase):
    def setUp(self):
        self.rows=(row(1),row(2),row(3))
        self.backend=Backend(self.rows)
        self.engine=C10C11WindowStacker(self.backend)

    def test_true_native_return_but_no_physical_move_fails_all_modes(self):
        for mode in MODES:
            b=Backend(self.rows)
            before=dict(b.positions)
            b.move_no_resize=lambda *args:True
            outcome=C10C11WindowStacker(b).apply(snap(*self.rows),
                     mode=mode,max_windows=3)
            self.assertEqual(outcome.code,"MOVE_UNVERIFIED_PARTIAL",mode)
            self.assertEqual(outcome.moved,(1,))
            self.assertEqual(b.positions,before)
    def test_last_hwnd_false_positive_never_returns_applied(self):
        for mode in MODES:
            b=Backend(self.rows)
            original=b.move_no_resize
            b.move_no_resize=lambda h,x,y:True if h==3 else original(h,x,y)
            outcome=C10C11WindowStacker(b).apply(snap(*self.rows),
                     mode=mode,max_windows=3)
            # The original third HWND never moved, except if its pre-existing
            # native position already matched the target, which it does not.
            self.assertEqual(outcome.code,"MOVE_UNVERIFIED_PARTIAL",mode)
            self.assertEqual(outcome.moved,(1,2,3))
    def test_resize_during_move_rejected_all_modes(self):
        for mode in MODES:
            b=Backend(self.rows)
            original=b.move_no_resize
            def illegal(h,x,y):
                ok=original(h,x,y)
                l,t,r,bottom=b.positions[h]
                b.positions[h]=(l,t,r+9,bottom)
                return ok
            b.move_no_resize=illegal
            outcome=C10C11WindowStacker(b).apply(snap(*self.rows),
                     mode=mode,max_windows=3)
            self.assertEqual(outcome.code,"MOVE_UNVERIFIED_PARTIAL")
            self.assertEqual(outcome.moved,(1,))
    def test_pid_reuse_during_move_rejected_all_modes(self):
        for mode in MODES:
            b=Backend(self.rows)
            native=b.move_no_resize
            def reuse(h,x,y):
                ok=native(h,x,y)
                b.bumped_pid[h]=333333
                return ok
            b.move_no_resize=reuse
            result=C10C11WindowStacker(b).apply(snap(*self.rows),
                      mode=mode,max_windows=3)
            self.assertEqual(result.code,"STALE_AFTER_MOVE_PARTIAL",mode)
            self.assertEqual(result.moved,(1,))
    def test_post_readback_failure_on_final_hwnd_is_not_success(self):
        for mode in MODES:
            b=Backend(self.rows)
            native=b.move_no_resize
            def move_then_pid_reuse(h,x,y):
                done=native(h,x,y)
                if h==3:b.bumped_pid[3]=999999
                return done
            b.move_no_resize=move_then_pid_reuse
            outcome=C10C11WindowStacker(b).apply(snap(*self.rows),
                        mode=mode,max_windows=3)
            self.assertEqual(outcome.code,"STALE_AFTER_MOVE_PARTIAL")
            self.assertEqual(outcome.moved,(1,2,3))
    def test_noop_already_positioned_must_still_be_verified(self):
        b=Backend(self.rows)
        b.positions[1]=(0,0,120,90)
        real=b.window_rect
        calls={1:0}
        def drift(h):
            if h==1:
                calls[1]+=1
                if calls[1]>=2:return (400,400,520,490)
            return real(h)
        b.window_rect=drift
        result=C10C11WindowStacker(b).apply(snap(*self.rows),
                    mode="tight",max_windows=3)
        self.assertEqual(result.code,"MOVE_UNVERIFIED_PARTIAL")
        self.assertEqual(result.unchanged,(1,))
        self.assertEqual(b.moves,[])
    def test_correct_real_moves_all_four_modes(self):
        expected={
            "tight":((0,0),(0,0),(0,0)),
            "diagonal":((0,0),(50,50),(100,100)),
            "horizontal":((0,0),(50,0),(100,0)),
            "vertical":((0,0),(0,50),(0,100)),
        }
        for mode,locs in expected.items():
            b=Backend(self.rows)
            before={h:(v[2]-v[0],v[3]-v[1]) for h,v in b.positions.items()}
            result=C10C11WindowStacker(b).apply(snap(*self.rows),
                        mode=mode,max_windows=3)
            self.assertIn("APPLIED",result.code)
            self.assertEqual(tuple(b.positions[h][:2] for h in (1,2,3)),locs)
            self.assertEqual(before,{h:(v[2]-v[0],v[3]-v[1])
                           for h,v in b.positions.items()})
    def test_master_still_first_and_correct_geometry(self):
        result=self.engine.apply(snap(*self.rows),mode="horizontal",
                                 master_hwnd=3,max_windows=3)
        self.assertEqual(result.code,"STACK_HORIZONTAL_APPLIED")
        self.assertEqual(self.backend.moves,[(3,0,0),(1,50,0),(2,100,0)])
    def test_permission_revoke_still_returns_cancelled_legacy_contract(self):
        allowed=[True]
        move=self.backend.move_no_resize
        def cancel(h,x,y):
            out=move(h,x,y)
            allowed[0]=False
            return out
        self.backend.move_no_resize=cancel
        result=self.engine.apply(snap(*self.rows),mode="diagonal",
                                 max_windows=3,allowed=lambda:allowed[0])
        self.assertEqual(result.code,"CANCELLED")
        self.assertEqual(result.moved,(1,))
    def test_invalid_cache_stale_pid_preflight_no_physical_actions(self):
        self.backend.bumped_pid[2]=8888
        self.assertEqual(self.engine.apply(snap(*self.rows),mode="tight",
            max_windows=3).code,"STALE_OR_REUSED_PID")
        self.assertEqual(self.backend.moves,[])
    def test_successfully_positioned_second_pass_no_extra_setwindowpos(self):
        self.engine.apply(snap(*self.rows),mode="vertical",max_windows=3)
        self.backend.moves.clear()
        outcome=self.engine.apply(snap(*self.rows),mode="vertical",max_windows=3)
        self.assertEqual(outcome.code,"STACK_VERTICAL_APPLIED")
        self.assertEqual(outcome.unchanged,(1,2,3))
        self.assertEqual(self.backend.moves,[])
    def test_no_fake_ui_credentials_proxy_or_game_injection(self):
        code=(ROOT/"src/window_stacking.py").read_text("utf-8")
        for forbidden in ("tk.Button(", "ReadProcessMemory(", "PostMessage(",
                         "CreateRemoteThread", "proxy_tab", "write_settings("):
            self.assertNotIn(forbidden,code)

if __name__=="__main__":unittest.main()
