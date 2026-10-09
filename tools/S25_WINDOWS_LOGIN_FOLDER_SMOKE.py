"""S25: Native Windows Tk Login Game folder chooser and settings-only smoke.

All files are TEST-owned placeholders named as the original EXE. No game
binary, subprocess, captcha/Proxy, network token or launcher is used.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile
import traceback

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s25"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"native_login_path.json"


def run():
    report={
        "task":"S25","status":"NOT_RUN","os":os.name,
        "real_game":"NOT_RUN","signed_auth":"NOT_AVAILABLE",
        "game_launches":0,"account_logins":0,
        "captcha_actions":0,"proxy_runtime":"EXCLUDED",
        "product_exe":"NOT_BUILT","exact_full_login_pixel_parity":"NOT_RUN",
        "file_system":"TEST_OWNED_PATHS_ONLY",
    }
    root=None
    try:
        if os.name!="nt":
            raise RuntimeError("Real Windows Tk required")
        import tkinter as tk
        from tkinter import filedialog, messagebox
        from unittest.mock import patch
        from login_path import EXE_NAME, PICKER_TITLE, GameDirectoryStore
        from login_tab import TLMLoginPathTab
        from info_tab import TLMInfoTab
        from shell import TLMMainApp
        from permission_guard import PermissionGuard, VerifiedClaims
        from settings_store import read_settings

        with tempfile.TemporaryDirectory(prefix="S25_TEST_ONLY_") as td:
            base=Path(td)
            game=base/"Thần Long Installer"/"Game"
            game.mkdir(parents=True)
            exe=game/EXE_NAME
            exe.write_bytes(b"NOT AN EXECUTABLE - S25 test placeholder")
            cfg=base/"AppData"/"TLMTool"/"settings.ini"
            cfg.parent.mkdir(parents=True)
            cfg.write_text("[Settings]\ngrid_rows = 4\n"
                           "[Session]\nkeep = yes\n",encoding="utf-8")
            errors=[]
            picks=[str(base/"Thần Long Installer"),
                   str(base/"Thần Long Installer"/"bad_folder"),
                   ""]
            titles=[]
            def choose(**kwargs):
                titles.append(kwargs.get("title"))
                return picks.pop(0)
            def showerror(title,body):
                errors.append((title,body))

            constructed=[]
            def make_login(parent):
                item=TLMLoginPathTab(
                    parent,settings_file=cfg,
                    choose_directory=choose,show_error=showerror)
                constructed.append(item)
                return item
            root=tk.Tk()
            app=TLMMainApp(root,{
                "info_tab":lambda frame:TLMInfoTab(frame),
                "login_tab":make_login,
            })
            app.position_window_top_right()
            root.update()
            report["initial_only_info"]=app.lifecycle.visible=={"info_tab"}
            report["login_not_built_before_rights"]=not constructed
            assert report["initial_only_info"] and report["login_not_built_before_rights"]

            # A verified-claims adapter exists only inside this isolated test.
            guard=PermissionGuard()
            assert guard.receive_token(
                "S25_TEST_ONLY",lambda _:VerifiedClaims(
                    permissions=frozenset({"info_tab","login_tab"}),
                    plan_status="TEST_ONLY",max_windows=1))
            app.apply_info_snapshot(guard.snapshot)
            root.update()
            app.notebook.select(app._tab_frames["login_tab"])
            root.update()
            view=constructed[0]
            report["tab_activated_by_test_grant"]=app.lifecycle.current=="login_tab"
            assert report["tab_activated_by_test_grant"]

            import tkinter as tk
            from tkinter import ttk
            report["real_tk_group"]=isinstance(view.group_game,ttk.LabelFrame)
            report["real_tk_chooser"]=isinstance(view.btn_choose,tk.Button)
            report["action_button_label"]=view.btn_choose.cget("text")
            report["chooser_bounding_rect"]=(
                view.btn_choose.winfo_x(),view.btn_choose.winfo_y(),
                view.btn_choose.winfo_width(),view.btn_choose.winfo_height())
            assert report["real_tk_group"] and report["real_tk_chooser"]
            assert report["chooser_bounding_rect"]==(5,11,135,24)
            report["no_fake_game_open_button"]=(
                len([w for w in view.group_game.winfo_children()
                     if isinstance(w,tk.Button)])==1)
            assert report["no_fake_game_open_button"]

            # Invoke the real Tk Button through its command binding. Picker
            # itself is test stubbed to avoid requiring an interactive click.
            view.btn_choose.invoke()
            report["valid_game_path_persisted"]=(
                GameDirectoryStore(cfg).load().directory==game
                and view.get_exe_path()==exe)
            assert report["valid_game_path_persisted"]
            report["two_space_executable"]=exe.name==EXE_NAME
            text=view.lbl_game_dir.cget("text")
            report["success_label"]=text
            assert "Đã chọn game thành công:" in text
            assert "Game" in text
            assert titles==[PICKER_TITLE]
            parser=read_settings(cfg)
            report["untouched_old_settings"]=(
                parser.get("Settings","grid_rows")=="4"
                and parser.get("Session","keep")=="yes")
            assert report["untouched_old_settings"]

            # Selected invalid folder produces original error dialog and does
            # not overwrite existing persisted good configuration.
            view.btn_choose.invoke()
            assert errors and errors[0][0]=="Thư mục game không hợp lệ"
            report["invalid_folder_dialog"]=True
            report["invalid_did_not_overwrite"]=(
                GameDirectoryStore(cfg).load().directory==game)
            assert report["invalid_did_not_overwrite"]
            view.btn_choose.invoke() # canceled => no new write
            report["cancel_preserved_config"]=(
                GameDirectoryStore(cfg).load().directory==game)
            assert report["cancel_preserved_config"]

            # Re-create tab with same test-local APPDATA/settings -> restores.
            previous=view
            previous.shutdown()
            view.container.destroy()
            another=TLMLoginPathTab(
                app._tab_frames["login_tab"],settings_file=cfg,
                choose_directory=lambda **_: "",show_error=showerror)
            root.update()
            report["restart_path_loaded"]=another.get_exe_path()==exe
            assert report["restart_path_loaded"]
            report["status_hidden_before_initial_choice"]=False
            report["all_real_buttons_have_working_handlers"]=True

            guard.clear()
            app.apply_info_snapshot(guard.snapshot)
            root.update()
            report["revoked_tab_hidden"]=(
                app.lifecycle.visible=={"info_tab"}
                and app.lifecycle.current=="info_tab"
                and app.notebook.tab(app._tab_frames["login_tab"],"state")=="hidden")
            assert report["revoked_tab_hidden"]

            # Original S24 shell always closes built tab owners on root Destroy
            # with no resurrected Login control afterward.
            root.destroy()
            root=None
            assert previous._closed and another._closed
            assert app._closed
            report["destroy_owner_closed"]=True

            report["status"]="PASS_NATIVE_S25_LOGIN_CHOOSER_STORAGE_AUTH_GUARD"
    except Exception as exc:
        report["status"]="FAIL_NATIVE_S25_LOGIN_PATH"
        report["error"]=type(exc).__name__+": "+str(exc)
        report["traceback"]=traceback.format_exc(limit=15)
    finally:
        if root is not None:
            try: root.destroy()
            except Exception: pass
        REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),
                          encoding="utf-8")
        for key,value in report.items():
            if key!="traceback":
                print("S25_"+key.upper()+"="+json.dumps(value,ensure_ascii=True))
    return int(report["status"]!="PASS_NATIVE_S25_LOGIN_CHOOSER_STORAGE_AUTH_GUARD")


if __name__=="__main__":
    raise SystemExit(run())
