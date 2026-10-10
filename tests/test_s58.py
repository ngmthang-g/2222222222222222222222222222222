"""S58: C12 original reset-hidden-state contract only after real visible C10/C11 layout.

This is a conservative verification fence around the original recovered
_reset_hidden_state event. Not a guess about conflicting C12 show behavior.
"""
from __future__ import annotations
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"tests"))
from test_s17 import Backend, row, snap
from window_hide import C12HideAll, HiddenResetResult
from window_stacking import C10C11WindowStacker


class S58OriginalHiddenReset(unittest.TestCase):
    def setUp(self):
        self.rows=[row(1),row(2),row(3)]
        self.backend=Backend(self.rows)
        self.hider=C12HideAll(self.backend)
        self.stacker=C10C11WindowStacker(self.backend)
        self.saved=self.hider.hide(snap(*self.rows),max_windows=3)
        self.assertEqual(self.saved.code,"HIDDEN")
        self.assertTrue(self.hider.hidden)
        self.assertEqual(len(self.saved.saved_rects),3)

    def test_tight_layout_physically_restores_visibility_and_clears_hidden(self):
        self.assertEqual(self.stacker.apply(snap(*self.rows),mode="tight",
                                           max_windows=3).code,"STACK_TIGHT_APPLIED")
        done=self.hider.reset_after_verified_layout(snap(*self.rows),mode="tight")
        self.assertEqual(done.code,"VISIBLE_LAYOUT_VERIFIED_STATE_RESET")
        self.assertEqual(done.checked_hwnds,(1,2,3))
        self.assertFalse(self.hider.hidden)
        self.assertFalse(self.hider.partial)
        self.assertEqual(self.hider.saved_window_rects,())

    def test_diagonal_master_is_index_zero_and_clears_hidden(self):
        self.stacker.apply(snap(*self.rows),mode="diagonal",max_windows=3,master_hwnd=3)
        out=self.hider.reset_after_verified_layout(
            snap(*self.rows),mode="diagonal",master_hwnd=3)
        self.assertEqual(out.code,"VISIBLE_LAYOUT_VERIFIED_STATE_RESET")
        self.assertEqual(out.checked_hwnds,(3,1,2))
        self.assertFalse(self.hider.hidden)

    def test_no_real_movement_means_no_status_reset(self):
        out=self.hider.reset_after_verified_layout(snap(*self.rows),mode="tight")
        self.assertEqual(out.code,"LAYOUT_NOT_AT_VERIFIED_VISIBLE_COORDINATES")
        self.assertTrue(self.hider.hidden)
        self.assertEqual(self.hider.saved_window_rects,self.saved.saved_rects)

    def test_one_target_still_offscreen_blocks_all_reset(self):
        self.stacker.apply(snap(*self.rows),mode="diagonal",max_windows=3)
        r=self.backend.positions[2]
        self.backend.positions[2]=(-2200,-2200,-2200+(r[2]-r[0]),-2200+(r[3]-r[1]))
        out=self.hider.reset_after_verified_layout(snap(*self.rows),mode="diagonal")
        self.assertEqual(out.code,"LAYOUT_NOT_AT_VERIFIED_VISIBLE_COORDINATES")
        self.assertTrue(self.hider.hidden)

    def test_wrong_mode_and_missing_master_no_reset(self):
        self.stacker.apply(snap(*self.rows),mode="tight",max_windows=3)
        self.assertEqual(self.hider.reset_after_verified_layout(snap(*self.rows),
                         mode="horizontal").code,"UNVERIFIED_LAYOUT_MODE")
        self.assertEqual(self.hider.reset_after_verified_layout(snap(*self.rows),
                         mode="tight",master_hwnd=999).code,"MASTER_NOT_IN_CACHE")
        self.assertTrue(self.hider.hidden)

    def test_absent_or_duplicate_hwnd_in_cache_does_not_reset(self):
        self.stacker.apply(snap(*self.rows),mode="tight",max_windows=3)
        self.assertEqual(self.hider.reset_after_verified_layout(
            snap(*self.rows[:2]),mode="tight").code,"SAVED_HWND_MISSING_OR_REUSED")
        self.assertEqual(self.hider.reset_after_verified_layout(
            snap(self.rows[0],self.rows[0]),mode="tight").code,
            "INVALID_OR_AMBIGUOUS_CACHE")
        self.assertTrue(self.hider.hidden)

    def test_stale_pid_reuse_blocks_without_leaking_saved_geometry(self):
        self.stacker.apply(snap(*self.rows),mode="tight",max_windows=3)
        self.backend.bumped_pid[2]=990011
        self.assertEqual(self.hider.reset_after_verified_layout(
            snap(*self.rows),mode="tight").code,"STALE_OR_REUSED_PID")
        self.assertEqual(self.hider.saved_window_rects,self.saved.saved_rects)

    def test_permission_revocation_prevents_status_reset(self):
        self.stacker.apply(snap(*self.rows),mode="tight",max_windows=3)
        self.assertEqual(self.hider.reset_after_verified_layout(
            snap(*self.rows),mode="tight",allowed=lambda:False).code,"CANCELLED")
        self.assertTrue(self.hider.hidden)

    def test_read_only_reset_does_not_move_or_resize(self):
        self.stacker.apply(snap(*self.rows),mode="tight",max_windows=3)
        self.backend.moves.clear()
        before=dict(self.backend.positions)
        self.assertEqual(self.hider.reset_after_verified_layout(
            snap(*self.rows),mode="tight").code,
            "VISIBLE_LAYOUT_VERIFIED_STATE_RESET")
        self.assertEqual(self.backend.positions,before)
        self.assertEqual(self.backend.moves,[])

    def test_reset_idempotent_when_already_visible(self):
        self.stacker.apply(snap(*self.rows),mode="tight",max_windows=3)
        self.hider.reset_after_verified_layout(snap(*self.rows),mode="tight")
        self.assertEqual(self.hider.reset_after_verified_layout(
            snap(*self.rows),mode="tight").code,"NOT_HIDDEN")

    def test_partial_hide_reconciles_only_if_all_originally_hidden_hwnds_moved(self):
        # Source-backed C12 reset must also clear PARTIAL only when those
        # moved windows have been independently restored via verified layout.
        rows=[row(8),row(9),row(10)]
        backend=Backend(rows)
        svc=C12HideAll(backend)
        can=[True]
        actual_move=backend.move_no_resize
        def cancel_after_one(h,x,y):
            ok=actual_move(h,x,y)
            can[0]=False
            return ok
        backend.move_no_resize=cancel_after_one
        self.assertEqual(svc.hide(snap(*rows),max_windows=3,allowed=lambda:can[0]).code,
                         "CANCELLED_PARTIAL")
        self.assertTrue(svc.partial)
        backend.move_no_resize=actual_move
        self.assertEqual(svc.reset_after_verified_layout(
            snap(*rows),mode="tight").code,
            "LAYOUT_NOT_AT_VERIFIED_VISIBLE_COORDINATES")
        C10C11WindowStacker(backend).apply(snap(*rows),mode="tight",max_windows=3)
        self.assertEqual(svc.reset_after_verified_layout(
            snap(*rows),mode="tight").code,
            "VISIBLE_LAYOUT_VERIFIED_STATE_RESET")
        self.assertFalse(svc.partial)

    def test_source_does_not_implement_conflicted_show_restore_or_proxy(self):
        self.assertFalse(hasattr(self.hider,"show"))
        self.assertFalse(hasattr(self.hider,"restore"))
        data=(ROOT/"src/window_hide.py").read_text(encoding="utf-8")
        self.assertNotIn("SW_HIDE",data.split("class C12HideAll:")[1])
        for forbidden in ("subprocess.Popen(", "CreateRemoteThread(","PostMessage(",
                          "TLM_PROXY_ENABLE"):
            self.assertNotIn(forbidden,data)

if __name__=="__main__":unittest.main()
