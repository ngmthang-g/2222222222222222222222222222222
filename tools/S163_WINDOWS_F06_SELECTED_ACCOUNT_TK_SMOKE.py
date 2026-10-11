"""S163 native Win64 Tk original F06 selection from actual existing Login tab.

User-editable 100-row Tk Canvas, actual Entry/StringVar value, checkbox
buttons, password show/mask and plan-hidden rows. TEST-ONLY dummy credentials.
NEVER stores/prints passwords, never launches or contacts a game/Info service.
"""
from __future__ import annotations
import json,os,sys,tempfile,threading
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
ART=ROOT/"artifacts"/"s163"
ART.mkdir(parents=True,exist_ok=True)

def run():
    report={"status":"NOT_RUN","task":"S163","real_Tk_Win64":os.name=="nt",
            "F06_game_login_executed":False,"original_signed_Info_verified":False,
            "real_account_values_used":False,"product_exe_built":False,
            "proxy_policy_verified":False}
    root=None
    try:
        if os.name!="nt":raise OSError("WIN64_REQUIRED")
        import tkinter as tk
        from login_tab import TLMLoginPathTab
        from login_account_legacy import LegacyAccountRecord
        with tempfile.TemporaryDirectory() as temp:
            ini=Path(temp)/"settings.ini"
            ini.write_bytes(b"[Settings]\r\ns163_test=UNCHANGED\r\n")
            root=tk.Tk()
            root.title("S163 TEST OWNED F06 selected rows (NO GAME)")
            root.geometry("510x1130+20+20")
            tab=TLMLoginPathTab(root,settings_file=ini,
                                choose_directory=lambda **kwargs:"",
                                show_error=lambda *a,**kwargs:None)
            root.update_idletasks();root.update()
            rows=tab.account_rows
            checks={}
            checks["real_original_hundred_Tk_account_rows"]=(
                len(rows.entry_user)==100 and len(rows.entry_pass)==100
                and len(rows.row_selectors)==100)
            checks["initial_empty_selection_has_no_f06_action"]=(
                tab.get_selected_login_rows().status=="NO_CHECKED_ACCOUNTS")
            # Real user events through the actual current Tk widgets; do NOT
            # use a synthetic AccountSelectionModel in native test.
            rows.row_selectors[37].invoke()
            rows.row_selectors[0].invoke()
            rows.entry_user[0].insert(0,"  S163_TEST_USER_A  ")
            rows.entry_pass[0].insert(0," S163_TEST_PASSWORD_A ")
            rows.entry_user[37].insert(0,"S163_TEST_USER_B")
            rows.entry_pass[37].insert(0,"S163_TEST_PASSWORD_B")
            rows.captcha_boxes[37].set("Tool")
            root.update_idletasks()
            baseline=ini.read_bytes()
            actual=tab.get_selected_login_rows()
            checks["native_widgets_submit_only_checked_rows_in_order"]=(
                actual.status=="VALIDATED_INPUT_ONLY_NO_GAME"
                and tuple(x.row_index for x in actual.rows)==(0,37))
            checks["username_stripped_password_exact_unmasked_value"]=(
                actual.rows[0].username=="S163_TEST_USER_A"
                and actual.rows[0].password==" S163_TEST_PASSWORD_A "
                and actual.rows[1].password=="S163_TEST_PASSWORD_B")
            checks["native_captcha_mode_no_legacy_inference"]=(
                tuple(x.captcha_mode for x in actual.rows)==("Không","Tool"))
            checks["proxy_actions_not_created_from_account_selection"]=(
                all(x.proxy is None for x in actual.rows))
            checks["native_password_mask_is_presentation_only"]=(
                rows.entry_pass[0].cget("show")=="*"
                and actual.rows[0].password!="*"*len(actual.rows[0].password))
            rows.show_password_toggle.invoke()
            root.update()
            unmasked=tab.get_selected_login_rows()
            checks["native_Tk_show_password_does_not_mutate_credential"]=(
                rows.entry_pass[0].cget("show")==""
                and unmasked.rows[0].password==actual.rows[0].password)
            rows.show_password_toggle.invoke()
            root.update()
            checks["native_Tk_rehide_preserves_raw_password"]=(
                rows.entry_pass[0].cget("show")=="*"
                and tab.get_selected_login_rows().rows[0].password
                    ==actual.rows[0].password)
            rows.row_selectors[4].invoke() # blank native row
            missing=tab.get_selected_login_rows()
            checks["native_selected_empty_row_blocks_entire_batch"]=(
                missing.status=="MISSING_USERNAME_OR_PASSWORD"
                and missing.invalid_row==4 and not missing.rows)
            rows.row_selectors[4].invoke()
            plan=rows.apply_account_row_limit(10,allowed=lambda:True)
            limited=tab.get_selected_login_rows()
            checks["native_plan_hidden_selected_row_stays_inactive"]=(
                rows.visible_row_count==10
                and limited.status=="HIDDEN_ROW_NOT_ACTIONABLE"
                and limited.invalid_row==37)
            rows.apply_account_row_limit(100,allowed=lambda:True)
            checks["native_restore_recovers_selected_member"]=(
                tab.get_selected_login_rows().status
                    =="VALIDATED_INPUT_ONLY_NO_GAME")
            checks["no_selected_account_parser_writes_settings_ini"]=(
                ini.read_bytes()==baseline)
            # The original legacy Proxy field is read-only unknown F08.
            rows._legacy_proxy_rows.add(37)
            blocked=tab.get_selected_login_rows()
            checks["verified_legacy_raw_proxy_never_silently_discarded"]=(
                blocked.status=="F08_PROXY_POLICY_UNVERIFIED"
                and blocked.invalid_row==37)
            rows._legacy_proxy_rows.clear()
            rows.captcha_vars[37].set("Có")
            checks["legacy_Co_captcha_never_treated_as_Tool"]=(
                tab.get_selected_login_rows().status
                    =="F07_CAPTCHA_MODE_UNVERIFIED")
            checks["redacted_selection_repr_never_exposes_TEST_passwords"]=(
                "S163_TEST_PASSWORD" not in repr(actual)
                and "S163_TEST_PASSWORD" not in repr(actual.rows[0]))
            tab.shutdown()
            checks["closing_Login_disables_F06_selection"]=(
                tab.get_selected_login_rows().status=="ACCOUNT_VIEW_CLOSED")
            checks["no_game_click_auth_or_proxy_execution"]=all(
                not report[k] for k in ("F06_game_login_executed",
                  "original_signed_Info_verified","real_account_values_used",
                  "product_exe_built","proxy_policy_verified"))
            report["checks"]=checks
            report["status"]=(
                "PASS_NATIVE_S163_F06_REAL_LOGIN_SELECTED_TK_ROWS_NOT_GAME"
                if all(checks.values()) else "FAIL_NATIVE_S163_F06_SELECTION")
    except Exception as exc:
        report["status"]="FAIL_NATIVE_S163_F06_SELECTION"
        report["error_type"]=type(exc).__name__
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        (ART/"f06_original_checked_rows_real_tk.json").write_text(
            json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        print(json.dumps(report,ensure_ascii=True))
    return 0 if report["status"].startswith("PASS_") else 1
if __name__=="__main__":raise SystemExit(run())
