"""S163 original F06 checked-account extraction from already-real F01 Login Tk.

Passwords are never logged, never serialized or compared to star masks;
actual Window/Tk UI proof is tested separately by native S163 smoke.
"""
from __future__ import annotations
from pathlib import Path
import sys,threading,unittest
from unittest.mock import MagicMock
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from login_account_rows import (
    AccountSelectionModel,TLMAccountRows,SelectedLoginInput,SelectedLoginRows,
    MAX_ACCOUNT_ROWS,CAPTCHA_MODES,
)
from login_account_legacy import LegacyAccountRecord

class Var:
    def __init__(self,v=""):self.v=v
    def get(self):return self.v
    def set(self,v):self.v=v

def fixture():
    # Use real production method with test-owned 100-row value sources,
    # bypassing Tk only for fast edge-branch unit tests.
    rows=object.__new__(TLMAccountRows)
    rows._owner_thread=threading.get_ident()
    rows._closed=False
    rows._visible_rows=100
    rows._hidden_rows=[]
    rows._legacy_proxy_rows=set()
    rows.selection=AccountSelectionModel()
    rows.username_vars=[Var() for _ in range(100)]
    rows.password_vars=[Var() for _ in range(100)]
    rows.captcha_vars=[Var("Không") for _ in range(100)]
    return rows

class S163F06SelectedInputTests(unittest.TestCase):
    def test_01_original_f06_five_field_shape_no_proxy_assumption(self):
        x=SelectedLoginInput(2,"u","p","Không")
        self.assertEqual((x.row_index,x.username,x.password,x.captcha_mode,x.proxy),
                         (2,"u","p","Không",None))

    def test_02_selection_reads_only_checked_in_original_order(self):
        v=fixture()
        for i in (80,3,1):
            v.selection.toggle(i)
            v.username_vars[i].set("acc"+str(i))
            v.password_vars[i].set("secret"+str(i))
        res=v.get_selected_login_rows()
        self.assertEqual(res.status,"VALIDATED_INPUT_ONLY_NO_GAME")
        self.assertEqual(tuple(item.row_index for item in res.rows),(1,3,80))

    def test_03_unselected_passwords_never_in_output(self):
        v=fixture()
        v.username_vars[4].set("NOT_SELECTED")
        v.password_vars[4].set("SECRET_NEVER_OUTPUT")
        v.selection.toggle(8)
        v.username_vars[8].set("ok")
        v.password_vars[8].set("TEST_ONLY_PASSWORD")
        result=v.get_selected_login_rows()
        self.assertEqual(tuple(x.username for x in result.rows),("ok",))
        self.assertNotIn("SECRET_NEVER_OUTPUT",repr(result))

    def test_04_username_is_stripped_but_password_whitespace_preserved(self):
        v=fixture();v.selection.toggle(0)
        v.username_vars[0].set("  user \t")
        v.password_vars[0].set(" leading and trailing  ")
        out=v.get_selected_login_rows()
        self.assertEqual(out.rows[0].username,"user")
        self.assertEqual(out.rows[0].password," leading and trailing  ")

    def test_05_star_mask_is_not_used_as_password_value(self):
        v=fixture();v.selection.toggle(4)
        v.username_vars[4].set("user")
        v.password_vars[4].set("REAL_TEST_VALUE")
        self.assertEqual(v.get_selected_login_rows().rows[0].password,
                         "REAL_TEST_VALUE")

    def test_06_empty_account_or_empty_password_blocks_entire_launch_batch(self):
        v=fixture();v.selection.toggle(0);v.selection.toggle(5)
        v.username_vars[0].set("ok");v.password_vars[0].set("p")
        v.username_vars[5].set(" ")
        v.password_vars[5].set("secret")
        z=v.get_selected_login_rows()
        self.assertEqual((z.status,z.invalid_row,z.rows),
                         ("MISSING_USERNAME_OR_PASSWORD",5,()))
        v.username_vars[5].set("ok")
        v.password_vars[5].set("")
        self.assertEqual(v.get_selected_login_rows().invalid_row,5)

    def test_07_no_checked_account_does_not_count_as_login_success(self):
        v=fixture()
        z=v.get_selected_login_rows()
        self.assertEqual(z.status,"NO_CHECKED_ACCOUNTS")
        self.assertFalse(z.rows)

    def test_08_legacy_unknown_checkbox_not_inferred_checked(self):
        v=fixture()
        # Legacy raw token is not a supported boolean even if visually ❔.
        v.username_vars[4].set("old")
        v.password_vars[4].set("old-p")
        self.assertEqual(v.get_selected_login_rows().status,"NO_CHECKED_ACCOUNTS")

    def test_09_legacy_proxy_never_dropped_silently(self):
        v=fixture();v.selection.toggle(3)
        v.username_vars[3].set("test")
        v.password_vars[3].set("test")
        v._legacy_proxy_rows={3}
        z=v.get_selected_login_rows()
        self.assertEqual((z.status,z.invalid_row,z.rows),
                         ("F08_PROXY_POLICY_UNVERIFIED",3,()))

    def test_10_original_captcha_Co_migration_rejected(self):
        v=fixture();v.selection.toggle(0)
        v.username_vars[0].set("test")
        v.password_vars[0].set("test")
        v.captcha_vars[0].set("Có")
        self.assertEqual(v.get_selected_login_rows().status,
                         "F07_CAPTCHA_MODE_UNVERIFIED")

    def test_11_known_three_modes_survive_without_interpreting_captcha(self):
        for mode in CAPTCHA_MODES:
            v=fixture();v.selection.toggle(0)
            v.username_vars[0].set("u")
            v.password_vars[0].set("p")
            v.captcha_vars[0].set(mode)
            self.assertEqual(v.get_selected_login_rows().rows[0].captcha_mode,mode)

    def test_12_hidden_selected_row_cannot_bypass_plan_cap(self):
        v=fixture();v._visible_rows=4
        v.selection.toggle(7)
        v.username_vars[7].set("u")
        v.password_vars[7].set("p")
        z=v.get_selected_login_rows()
        self.assertEqual((z.status,z.invalid_row),
                         ("HIDDEN_ROW_NOT_ACTIONABLE",7))

    def test_13_closed_account_widget_returns_safe_status(self):
        v=fixture();v._closed=True
        self.assertEqual(v.get_selected_login_rows().status,"ACCOUNT_VIEW_CLOSED")

    def test_14_wrong_Tk_thread_must_not_read_live_stringvars(self):
        v=fixture();statuses=[]
        th=threading.Thread(target=lambda:statuses.append(v.get_selected_login_rows().status))
        th.start();th.join(2)
        self.assertEqual(statuses,["WRONG_TK_THREAD"])

    def test_15_selected_tuple_repr_never_prints_credential(self):
        v=fixture();v.selection.toggle(0)
        v.username_vars[0].set("S163_TEST_SECRET_USER")
        v.password_vars[0].set("S163_TEST_SECRET_PASSWORD")
        result=v.get_selected_login_rows()
        self.assertNotIn("S163_TEST_SECRET_PASSWORD",repr(result))
        self.assertNotIn("S163_TEST_SECRET_PASSWORD",repr(result.rows[0]))
        self.assertNotIn("S163_TEST_SECRET_USER",repr(result.rows[0]))

    def test_16_f06_helper_does_not_send_game_input_or_save_password(self):
        text=(ROOT/"src/login_account_rows.py").read_text("utf-8")
        for needle in ("subprocess.Popen(","CreateRemoteThread(","ReadProcessMemory(",
                       "SendInput(","TLM_PROXY_HOST","pickle.dump(","write_settings("):
            self.assertNotIn(needle,text)
        self.assertIn("get_selected_login_rows(self)",text)

if __name__=="__main__":unittest.main()
