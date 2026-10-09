"""S37 real Windows Tk Login F01 account 100-row UI + preserved legacy config.

TEST-owned credentials ONLY. No real account/login/game/Proxy/ADB/server.
Uses existing S25 Login tab under a test-authenticated shell. Verifies
original persisted Settings.accounts remains byte-for-byte (value) unchanged.
"""
from __future__ import annotations
import json,os,sys,tempfile,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s37";OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"windows_login_100_rows_memory_only.json"

def run():
    r={"task":"S37","status":"NOT_RUN","real_game":"NOT_RUN",
       "real_account_credentials":False,"credentials_in_artifact":False,
       "real_info":"NOT_AVAILABLE","fake_login_buttons":False,
       "proxy_runtime":"EXCLUDED","product_exe":"NOT_BUILT",
       "save_of_accounts":"BLOCKED_UNKNOWN_CHECK_TOKEN"}
    root=None
    try:
        if os.name!="nt":raise RuntimeError("Windows Tk required")
        import tkinter as tk
        from tkinter import ttk
        from login_tab import TLMLoginPathTab
        from login_account_rows import MAX_ACCOUNT_ROWS,CAPTCHA_MODES
        from settings_store import read_settings
        with tempfile.TemporaryDirectory(prefix="S37_TEST_ONLY_") as td:
            cfg=Path(td)/"APPDATA"/"TLMTool"/"settings.ini"
            cfg.parent.mkdir(parents=True)
            legacy="LEGACY_UNKNOWN|test_only_user|test_only_secret|Có|legacy_proxy"
            cfg.write_text("[Settings]\naccounts = "+legacy+
                           "\ngrid_rows = 4\n[Unrelated]\nkeep = yes\n",
                           encoding="utf-8")
            original_accounts=read_settings(cfg).get("Settings","accounts")
            root=tk.Tk();root.geometry("620x1050+0+0")
            tab=TLMLoginPathTab(root,settings_file=cfg,
                                choose_directory=lambda **_: "",
                                show_error=lambda *_:None)
            root.update()
            model=tab.account_rows
            r["real_canvas_scrollbar_and_label_frame"]=(
                isinstance(model.canvas,tk.Canvas)
                and isinstance(model.scrollbar,ttk.Scrollbar)
                and isinstance(model.group_accounts,ttk.LabelFrame))
            r["100_actual_tk_rows_exist"]=(
                len(model.row_selectors)==MAX_ACCOUNT_ROWS==100
                and len(model.entry_user)==100
                and len(model.entry_pass)==100
                and len(model.captcha_boxes)==100)
            r["true_tk_password_mask_on_100_rows"]=all(
                w.cget("show")=="*" for w in model.entry_pass)
            r["real_tk_custom_button_selection"]=(
                model.row_selectors[99].cget("text")=="⬜")
            model.row_selectors[99].invoke()
            r["real_last_row_button_selects"]=(
                model.snapshot(99).selected and not model.snapshot(98).selected)
            model.header_selector.invoke()
            r["real_select_all_synchronizes_100_buttons"]=(
                model.selection.selected_count==100 and
                all(b.cget("text")=="✅️" for b in model.row_selectors))
            model.header_selector.invoke()
            r["real_select_all_can_clear"]=model.selection.selected_count==0
            model.entry_user[99].insert(0,"S37_TEST_USER")
            model.entry_pass[99].insert(0,"S37_TEST_PASSWORD")
            # Test actual readonly user-choice behavior rather than interpreting
            # Tcl's platform-specific textual representation of "values".
            captcha_box=model.captcha_boxes[0]
            observed_modes=[]
            for mode_index in range(len(CAPTCHA_MODES)):
                captcha_box.current(mode_index)
                observed_modes.append(captcha_box.get())
            r["captcha_observed_mode_labels"]=observed_modes
            r["captcha_widget_states"]=sorted(
                {str(w.cget("state")) for w in model.captcha_boxes})
            r["captcha_expected_mode_labels"]=list(CAPTCHA_MODES)
            r["readonly_captcha_modes"]=(
                tuple(observed_modes)==CAPTCHA_MODES
                and all(str(w.cget("state"))=="readonly" for w in model.captcha_boxes))
            r["mask_toggle_preserves_in_memory_password"]=(
                model.snapshot(99).password=="S37_TEST_PASSWORD")
            model.show_password_toggle.invoke()
            r["show_password_unmasks_all_rows"]=all(
                w.cget("show")=="" for w in model.entry_pass)
            model.show_password_toggle.invoke()
            r["password_hidden_again"]=all(
                w.cget("show")=="*" for w in model.entry_pass)
            model.canvas.yview_moveto(1.0);root.update()
            r["canvas_scrolls_to_last_row"]=model.canvas.yview()[0]>0
            r["no_fake_login_or_proxy_action_buttons"]=(
                all(model.rows_inner.grid_slaves(row=i,column=4)==[]
                    and model.rows_inner.grid_slaves(row=i,column=5)==[]
                    for i in range(1,101)))
            r["original_legacy_accounts_untouched_after_ui_edits"]=(
                read_settings(cfg).get("Settings","accounts")==original_accounts
                and "Có" in original_accounts)
            r["existing_s25_game_chooser_remains"]=(
                tab.btn_choose.cget("text")=="Chọn thư mục game")
            tab.shutdown();root.destroy();root=None
            r["on_destroy_does_not_rewrite_unknown_accounts"]=(
                read_settings(cfg).get("Settings","accounts")==original_accounts)
            assert all(r[k] for k in (
                "real_canvas_scrollbar_and_label_frame","100_actual_tk_rows_exist",
                "true_tk_password_mask_on_100_rows",
                "real_tk_custom_button_selection","real_last_row_button_selects",
                "real_select_all_synchronizes_100_buttons","real_select_all_can_clear",
                "readonly_captcha_modes","mask_toggle_preserves_in_memory_password",
                "show_password_unmasks_all_rows","password_hidden_again",
                "canvas_scrolls_to_last_row","no_fake_login_or_proxy_action_buttons",
                "original_legacy_accounts_untouched_after_ui_edits",
                "existing_s25_game_chooser_remains",
                "on_destroy_does_not_rewrite_unknown_accounts"))
            r["status"]="PASS_NATIVE_S37_REAL_TK_100_ROWS_IN_MEMORY_PRESERVE_LEGACY"
    except Exception as exc:
        r["status"]="FAIL_NATIVE_S37"
        r["error"]=type(exc).__name__+": "+str(exc)
        r["traceback"]=traceback.format_exc(limit=12)
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        REPORT.write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding="utf-8")
        for k,v in r.items():
            if k!="traceback":
                print("S37_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return int(r["status"]!="PASS_NATIVE_S37_REAL_TK_100_ROWS_IN_MEMORY_PRESERVE_LEGACY")
if __name__=="__main__":raise SystemExit(run())
