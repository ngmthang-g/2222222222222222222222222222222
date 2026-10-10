"""S109 F01 actual plan row visibility: local widget-only TEST/external gate.

No persisted credentials, Info simulation, Login action, or Proxy paths.
"""
from __future__ import annotations
from pathlib import Path
import sys,threading,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from login_account_rows import MAX_ACCOUNT_ROWS,ROW_PITCH,TLMAccountRows


class Widget:
    def __init__(self):self.visible=True;self.grid_calls=0;self.hide_calls=0
    def grid_remove(self):self.visible=False;self.hide_calls+=1
    def grid(self):self.visible=True;self.grid_calls+=1


class Frame:
    def __init__(self):self.rows={};self.updates=0
    def grid_rowconfigure(self,n,**kw):self.rows[n]=kw["minsize"]
    def update_idletasks(self):self.updates+=1


class Canvas:
    def __init__(self):self.rects=[]
    def bbox(self,k):return (0,0,420,999)
    def configure(self,**kw):self.rects.append(kw)


def fixture():
    o=object.__new__(TLMAccountRows)
    o._closed=False;o._owner_thread=threading.get_ident()
    o._visible_rows=100;o._hidden_rows=[]
    o.row_selectors=[Widget() for _ in range(100)]
    o.entry_user=[Widget() for _ in range(100)]
    o.entry_pass=[Widget() for _ in range(100)]
    o.captcha_boxes=[Widget() for _ in range(100)]
    o.rows_inner=Frame();o.canvas=Canvas()
    return o


class S109OriginalRowLimitTests(unittest.TestCase):
    def setUp(self):self.o=fixture()
    def apply(self,n,allowed=lambda:True):
        return self.o.apply_account_row_limit(n,allowed=allowed)
    def test_01_initial_fixed_capacity(self):
        self.assertEqual(self.o.visible_row_count,100)
        self.assertEqual(self.o.hidden_row_indices,())
        self.assertEqual(MAX_ACCOUNT_ROWS,100)
    def test_02_shrink_to_3_hides_97_actual_grid_rows(self):
        r=self.apply(3)
        self.assertEqual(r.status,"ROW_VISIBILITY_CHANGED_TEST_EXTERNAL_PLAN")
        self.assertEqual((r.visible_count,r.hidden_count),(3,97))
        self.assertTrue(self.o.entry_user[2].visible)
        self.assertFalse(self.o.entry_user[3].visible)
        self.assertFalse(self.o.entry_pass[99].visible)
        self.assertEqual(self.o.rows_inner.rows[4],0)
    def test_03_unhide_uses_previous_original_grid_slots(self):
        self.apply(3);self.apply(6)
        self.assertEqual(self.o.visible_row_count,6)
        self.assertTrue(all(self.o.entry_user[i].visible for i in range(6)))
        self.assertTrue(all(not self.o.entry_user[i].visible for i in range(6,100)))
        self.assertEqual(self.o.rows_inner.rows[5],ROW_PITCH)
    def test_04_fifo_order_of_hidden_indices(self):
        self.apply(6);self.assertEqual(self.o.hidden_row_indices[:4],(6,7,8,9))
        self.apply(2);self.assertEqual(self.o.hidden_row_indices[:6],(2,3,4,5,6,7))
        self.apply(5);self.assertEqual(self.o.hidden_row_indices[:4],(5,6,7,8))
    def test_05_all_100_restore(self):
        self.apply(1);self.apply(100)
        self.assertEqual(self.o.hidden_row_indices,())
        self.assertTrue(all(w.visible for w in self.o.entry_pass))
    def test_06_hidden_password_widgets_not_destroyed_or_recreated(self):
        original=self.o.entry_pass[72]
        self.apply(2);self.apply(90)
        self.assertIs(original,self.o.entry_pass[72])
    def test_07_full_six-column_existing_widget_model_untouched(self):
        old=(self.o.row_selectors,self.o.entry_user,self.o.entry_pass,self.o.captcha_boxes)
        self.apply(3);self.apply(80)
        self.assertEqual(old,(self.o.row_selectors,self.o.entry_user,self.o.entry_pass,self.o.captcha_boxes))
    def test_08_no_verified_permission_does_not_touch_layout(self):
        r=self.apply(3,None)
        self.assertEqual(r.status,"PERMISSION_NOT_VERIFIED")
        self.assertEqual(self.o.visible_row_count,100)
        self.assertEqual(self.o.rows_inner.rows,{})
    def test_09_explicit_false_permission_does_not_touch_layout(self):
        self.assertEqual(self.apply(3,lambda:False).status,"PERMISSION_NOT_VERIFIED")
    def test_10_callback_exception_fails_closed(self):
        def bad():raise RuntimeError("secret must not leak")
        self.assertEqual(self.apply(3,bad).status,"PERMISSION_NOT_VERIFIED")
    def test_11_callback_must_return_exact_true(self):
        self.assertEqual(self.apply(3,lambda:1).status,"PERMISSION_NOT_VERIFIED")
    def test_12_boolean_is_not_valid_limit(self):
        self.assertEqual(self.apply(True).status,"INVALID_LIMIT_NOT_ORIGINAL_TIER_PROOF")
    def test_13_zero_not_guessed_as_valid_original_tier(self):
        self.assertEqual(self.apply(0).status,"INVALID_LIMIT_NOT_ORIGINAL_TIER_PROOF")
    def test_14_negative_rejected(self):
        self.assertEqual(self.apply(-1).status,"INVALID_LIMIT_NOT_ORIGINAL_TIER_PROOF")
    def test_15_over_100_rejected(self):
        self.assertEqual(self.apply(101).status,"INVALID_LIMIT_NOT_ORIGINAL_TIER_PROOF")
    def test_16_float_rejected(self):
        self.assertEqual(self.apply(4.0).status,"INVALID_LIMIT_NOT_ORIGINAL_TIER_PROOF")
    def test_17_string_rejected(self):
        self.assertEqual(self.apply("4").status,"INVALID_LIMIT_NOT_ORIGINAL_TIER_PROOF")
    def test_18_identical_limit_is_noop(self):
        self.apply(4);n=self.o.rows_inner.updates
        self.assertEqual(self.apply(4).status,"ROW_LIMIT_UNCHANGED")
        self.assertEqual(n,self.o.rows_inner.updates)
    def test_19_only_main_Tk_thread_may_change_rows(self):
        result=[]
        th=threading.Thread(target=lambda:result.append(self.apply(3)))
        th.start();th.join(timeout=2)
        self.assertFalse(th.is_alive())
        self.assertEqual(result[0].status,"WRONG_TK_THREAD")
        self.assertEqual(self.o.visible_row_count,100)
    def test_20_close_refuses_limit_operation(self):
        self.o._closed=True
        self.assertEqual(self.apply(4).status,"ACCOUNT_VIEW_CLOSED")
    def test_21_active_visible_indices_never_include_hidden(self):
        self.apply(7);self.assertEqual(self.o.active_visible_indices(),tuple(range(7)))
        self.assertNotIn(7,self.o.active_visible_indices())
    def test_22_no_active_indices_once_view_closed(self):
        self.o._closed=True
        self.assertEqual(self.o.active_visible_indices(),())
    def test_23_scroll_region_is_refreshed(self):
        self.apply(4)
        self.assertEqual(self.o.rows_inner.updates,1)
        self.assertEqual(self.o.canvas.rects[-1],{"scrollregion":(0,0,420,999)})
    def test_24_every_widget_row_hidden_and_restored(self):
        self.apply(12);self.apply(24)
        self.assertEqual([z.visible for z in self.o._row_widgets(13)],[True]*4)
        self.assertEqual([z.visible for z in self.o._row_widgets(90)],[False]*4)
    def test_25_view_no_login_proxy_or_credential_persistence(self):
        code=(ROOT/"src/login_account_rows.py").read_text("utf-8")
        for forbidden in ("write_settings(", "save_accounts(", "CreateProcessW(", "shutdown /s",
                          "auto_login(", "get_plan_from_server(", "unlock_feature(", "proxy_enable("):
            self.assertNotIn(forbidden,code)
    def test_26_several_changes_still_original_100_capacity(self):
        for count in (80,19,75,1,100,4,98,100):
            self.assertIn(self.apply(count).status,("ROW_VISIBILITY_CHANGED_TEST_EXTERNAL_PLAN","ROW_LIMIT_UNCHANGED"))
        self.assertEqual(len(self.o.entry_pass),100)
        self.assertEqual(self.o.hidden_row_indices,())
    def test_27_failed_widget_transition_does_not_mark_success(self):
        def fail():raise RuntimeError("widget gone")
        self.o.entry_pass[9].grid_remove=fail
        r=self.apply(8)
        self.assertEqual(r.status,"ROW_WIDGET_TRANSITION_FAILED")
        self.assertEqual(r.visible_count,100)
    def test_28_permission_callback_runs_once_per_transition(self):
        n=[0]
        def allowed():n[0]+=1;return True
        self.o.apply_account_row_limit(11,allowed=allowed)
        self.assertEqual(n[0],1)


if __name__=="__main__":unittest.main()
