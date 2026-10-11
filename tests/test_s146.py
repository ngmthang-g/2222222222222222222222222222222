"""S146 C12 exact documented show-at-origin (0,0) branch, no GUI toggle.

Original specific C12 EXE doc/log says return to (0,0) while generic
toggle documentation says old positions. Do NOT declare all branches 1:1.
Native Win32 action is isolated and separately capability-guarded.
"""
from __future__ import annotations
import ast
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"tests")]
from window_hide import C12HideAll,DocumentedOriginShowResult,HIDE_X,HIDE_Y
from test_s17 import Backend,row,snap

class S146DocumentedShowToZeroTests(unittest.TestCase):
    def setUp(self):
        self.rows=[row(1),row(2)]
        self.backend=Backend(self.rows)
        self.handler=C12HideAll(self.backend)
        self.original=dict(self.backend.positions)
        self.snapshot=snap(*self.rows)

    def hide(self):
        r=self.handler.hide(self.snapshot,max_windows=2)
        self.assertEqual(r.code,"HIDDEN")
        self.backend.moves.clear()

    def show(self,**kw):
        kwargs={"max_windows":2,"allowed":lambda:True}
        kwargs.update(kw)
        return self.handler.show_documented_origin(self.snapshot,**kwargs)

    def test_01_not_hidden_never_moves(self):
        self.assertEqual(self.show().code,"NOT_HIDDEN")
        self.assertEqual(self.backend.moves,[])

    def test_02_original_specific_show_to_zero_verified_two_hwnds(self):
        self.hide()
        result=self.show()
        self.assertEqual(result.code,"DOCUMENTED_ORIGIN_ZERO_ZERO_VERIFIED_NOT_FULL_PARITY")
        self.assertEqual(result.moved,(1,2))
        self.assertEqual(self.backend.moves,[(1,0,0),(2,0,0)])
        self.assertFalse(self.handler.hidden)
        self.assertFalse(self.handler.partial)
        self.assertEqual(self.handler.saved_window_rects,())
        for h,now in self.backend.positions.items():
            old=self.original[h]
            self.assertEqual(now[:2],(0,0))
            self.assertEqual((now[2]-now[0],now[3]-now[1]),
                             (old[2]-old[0],old[3]-old[1]))
            self.assertNotEqual(now[:2],old[:2])

    def test_03_no_automatic_full_toggle_or_old_rect_branch(self):
        self.hide()
        self.assertFalse(hasattr(self.handler,"show"))
        self.assertFalse(hasattr(self.handler,"restore"))
        self.assertNotEqual(self.show().code,"ORIGINAL_SHOW_PARITY_PROVEN")

    def test_04_absent_entitlement_blocks_all_moves(self):
        self.hide()
        self.assertEqual(self.show(allowed=lambda:False).code,"CANCELLED")
        self.assertEqual(self.backend.moves,[])
        self.assertTrue(self.handler.hidden)

    def test_05_missing_allowed_callback_blocks(self):
        self.hide()
        self.assertEqual(self.show(allowed=None).code,"NO_AUTHORIZATION_CALLBACK")
        self.assertEqual(self.backend.moves,[])

    def test_06_unverified_window_limit_blocks(self):
        self.hide()
        for limit in (None,0,True,-1,"2"):
            self.assertEqual(self.show(max_windows=limit).code,
                             "NO_VERIFIED_WINDOW_LIMIT")
        self.assertEqual(self.backend.moves,[])

    def test_07_snapshot_members_changed_blocks_entire_batch(self):
        self.hide()
        result=self.handler.show_documented_origin(
           snap(row(1),row(3)),max_windows=2,allowed=lambda:True)
        self.assertEqual(result.code,"SAVED_HWND_MISSING_OR_REUSED")
        self.assertEqual(self.backend.moves,[])

    def test_08_duplicate_snapshot_blocks(self):
        self.hide()
        result=self.handler.show_documented_origin(
            snap(self.rows[0],self.rows[0]),max_windows=2,
            allowed=lambda:True)
        self.assertIn(result.code,("SAVED_WINDOW_SET_MISMATCH",))
        self.assertEqual(self.backend.moves,[])

    def test_09_stale_pid_in_second_hwnd_blocks_without_partial_move(self):
        self.hide()
        self.backend.bumped_pid[2]=99999
        result=self.show()
        self.assertEqual(result.code,"STALE_OR_REUSED_PID")
        self.assertEqual(self.backend.moves,[])
        self.assertTrue(self.handler.hidden)

    def test_10_external_move_while_hidden_blocks_and_preserves(self):
        self.hide()
        self.backend.positions[2]=(44,50,164,140)
        result=self.show()
        self.assertEqual(result.code,"NOT_AT_DOCUMENTED_HIDDEN_GEOMETRY")
        self.assertEqual(self.backend.moves,[])

    def test_11_mid_batch_revocation_marks_partial_and_denies_retry(self):
        self.hide()
        state={"calls":0}
        def auth():
            state["calls"]+=1
            return state["calls"]<3
        result=self.show(allowed=auth)
        self.assertEqual(result.code,"CANCELLED_PARTIAL")
        self.assertEqual(result.moved,(1,))
        self.assertTrue(self.handler.partial)
        self.assertEqual(self.backend.moves,[(1,0,0)])
        self.assertEqual(self.show().code,"PARTIAL_REQUIRES_RECONCILIATION")

    def test_12_positive_move_api_but_no_rect_change_not_verification(self):
        self.hide()
        self.backend.move_no_resize=lambda h,x,y:True
        result=self.show()
        self.assertEqual(result.code,"MOVE_UNVERIFIED_PARTIAL")
        self.assertTrue(self.handler.partial)
        self.assertFalse(self.handler.hidden)

    def test_13_second_hwnd_move_failure_never_claims_full_restore(self):
        self.hide()
        native=self.backend.move_no_resize
        def only_first(h,x,y):
            return native(h,x,y) if h==1 else False
        self.backend.move_no_resize=only_first
        result=self.show()
        self.assertEqual(result.code,"SETWINDOWPOS_FAILED_PARTIAL")
        self.assertEqual(result.moved,(1,))
        self.assertTrue(self.handler.partial)

    def test_14_appearance_and_size_unchanged_not_SW_HIDE(self):
        self.hide()
        self.show()
        source=(ROOT/"src/window_hide.py").read_text(encoding="utf8")
        self.assertNotIn("ShowWindow(",source)
        self.assertNotIn("SW_HIDE",source.split("def show_documented_origin(",1)[1].split("def reset_after_verified_layout",1)[0])
        self.assertTrue(all(rect[:2]==(0,0) for rect in self.backend.positions.values()))

    def test_15_after_full_show_can_hide_again_from_visible(self):
        self.hide()
        self.assertTrue(self.show().code.startswith("DOCUMENTED_ORIGIN"))
        self.assertEqual(self.handler.hide(self.snapshot,max_windows=2).code,"HIDDEN")
        self.assertTrue(self.handler.hidden)
        self.assertEqual(self.handler.saved_window_rects[0][2][:2],(0,0))

    def test_16_missing_verified_hidden_source_does_not_infer_restore(self):
        self.hide()
        self.backend.positions[1]=(-2200,-2200,-2000,-2100)
        result=self.show()
        self.assertEqual(result.code,"NOT_AT_DOCUMENTED_HIDDEN_GEOMETRY")
        self.assertEqual(self.backend.moves,[])

    def test_17_no_original_game_auth_or_proxy_in_test_tool(self):
        src=(ROOT/"src/window_hide.py").read_text(encoding="utf8")
        for banned in ("CreateRemoteThread(","WriteProcessMemory(",
                       "SendInput(","TLM_PROXY_ENABLE","TOKEN_HMAC_SECRET"):
            self.assertNotIn(banned,src)

    def test_18_invalid_snapshot_rejects_full_show(self):
        self.hide()
        result=self.handler.show_documented_origin(
            snap(*self.rows,valid=False),
            max_windows=2,allowed=lambda:True)
        self.assertEqual(result.code,"INVALID_CACHE")
        self.assertTrue(self.handler.hidden)
        self.assertEqual(self.backend.moves,[])

    def test_19_authorization_callback_exception_denies_without_movement(self):
        self.hide()
        def fails():
            raise RuntimeError("AUTH_PROVIDER_DOWN")
        result=self.show(allowed=fails)
        self.assertEqual(result.code,"CANCELLED")
        self.assertTrue(self.handler.hidden)
        self.assertEqual(self.backend.moves,[])

    def test_20_real_native_and_source_ast(self):
        for p in ("src/window_hide.py","tests/test_s146.py",
                  "tools/S146_WINDOWS_C12_SHOW_ORIGIN_SMOKE.py"):
            ast.parse((ROOT/p).read_text(encoding="utf8"))


    def test_21_auth_exception_before_first_move_cancels(self):
        self.hide()
        calls={"n":0}
        def auth():
            calls["n"]+=1
            if calls["n"]==2: raise AssertionError("PROVIDER_DOWN")
            return True
        result=self.show(allowed=auth)
        self.assertEqual(result.code,"CANCELLED")
        self.assertEqual(result.moved,())
        self.assertTrue(self.handler.hidden)
        self.assertEqual(self.backend.moves,[])

    def test_22_auth_exception_after_first_move_records_partial(self):
        self.hide()
        calls={"n":0}
        def auth():
            calls["n"]+=1
            if calls["n"]==3: raise AssertionError("PROVIDER_DOWN")
            return True
        result=self.show(allowed=auth)
        self.assertEqual(result.code,"CANCELLED_PARTIAL")
        self.assertEqual(result.moved,(1,))
        self.assertEqual(self.backend.moves,[(1,0,0)])
        self.assertTrue(self.handler.partial)
        self.assertFalse(self.handler.hidden)
        self.assertEqual(self.show().code,"PARTIAL_REQUIRES_RECONCILIATION")

    def test_23_auth_exception_after_all_moves_is_not_false_success(self):
        self.hide()
        calls={"n":0}
        def auth():
            calls["n"]+=1
            if calls["n"]==4: raise AssertionError("PROVIDER_DOWN")
            return True
        result=self.show(allowed=auth)
        self.assertEqual(result.code,"CANCELLED_PARTIAL")
        self.assertEqual(result.moved,(1,2))
        self.assertEqual(self.backend.moves,[(1,0,0),(2,0,0)])
        self.assertTrue(self.handler.partial)
        self.assertFalse(self.handler.hidden)
        self.assertNotEqual(result.code,"DOCUMENTED_ORIGIN_ZERO_ZERO_VERIFIED_NOT_FULL_PARITY")

if __name__=="__main__":
    unittest.main()
