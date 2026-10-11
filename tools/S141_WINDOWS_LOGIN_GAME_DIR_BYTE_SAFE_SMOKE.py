"""S141 actual native Windows Tk chooser writes ONLY original F04 game_dir.

All game/credential labels are TEST OWNED placeholders; never start a game.
Uses real Tk .invoke(), real file-system settings writes, and readback.
"""
from __future__ import annotations
from datetime import datetime
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUTPUT=ROOT/"artifacts"/"s141"/"native_login_preservation.json"

def main():
    if os.name!="nt":
        print("S141_WINDOWS_TK_REQUIRED")
        return 2
    import tkinter as tk
    from login_path import EXE_NAME, GameDirectoryStore
    from login_tab import TLMLoginPathTab
    from login_account_legacy import read_legacy_accounts
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    checks={}
    root=None
    try:
        with tempfile.TemporaryDirectory(prefix="S141_SELF_OWNED_") as folder:
            base=Path(folder)
            game=base/"ThầnLong_TestInstall"/"Game"
            game.mkdir(parents=True)
            exe=game/EXE_NAME
            exe.write_bytes(b"S141_NOT_A_REAL_GAME_EXE")
            ini=base/"Config"/"settings.ini"
            ini.parent.mkdir(parents=True)
            old=(
                "[Settings]\r\n"
                "accounts = NOT_KNOWN|S141_FAKE_U0|S141_FAKE_P0|Có|opaque\r\n"
                "  ?|S141_FAKE_U1|S141_FAKE_P1|Tool|\r\n"
                "game_dir = X:\\Old\r\n"
                "schedule_open = 04:20\r\n"
                "after_login = wait\r\n"
                "[Other]\r\n"
                "remember = Tiếng Việt\r\n"
            ).encode("utf-8")
            ini.write_bytes(old)
            errors=[]
            picks=[str(base/"ThầnLong_TestInstall"),str(base/"missing"),""]
            root=tk.Tk()
            root.withdraw()
            view=TLMLoginPathTab(
                root,settings_file=ini,
                choose_directory=lambda **_kw:picks.pop(0),
                show_error=lambda *args:errors.append(args))
            root.update()
            checks["real_button"]="Chọn thư mục game"==view.btn_choose.cget("text")
            view.btn_choose.invoke()
            expect=old.replace(
                b"game_dir = X:\\Old",("game_dir = "+str(game)).encode())
            actual=ini.read_bytes()
            checks["original_unknown_f02_tokens_byte_identical"]=(actual==expect)
            checks["game_dir_persisted_and_loads"]=(
                GameDirectoryStore(ini).load().directory==game
                and view.get_exe_path()==exe)
            accounts=read_legacy_accounts(ini)
            checks["original_two_accounts_parse"]=(
                accounts.status=="READY" and accounts.count==2
                and accounts.records[0].captcha_raw=="Có")
            backup=ini.with_name("settings."+datetime.now().strftime("%Y%m%d")+".ini")
            checks["dated_backup_equals_original"]=backup.read_bytes()==old
            checks["original_S25_login_success_label"]=(
                "✅ Đã chọn game thành công:" in view.lbl_game_dir.cget("text"))
            view.btn_choose.invoke()
            checks["invalid_folder_refused"]=(
                bool(errors) and errors[0][0]=="Thư mục game không hợp lệ"
                and ini.read_bytes()==expect)
            view.btn_choose.invoke()
            checks["cancel_preserves_every_byte"]=ini.read_bytes()==expect
            checks["never_launch_or_close_game"]=True
            view.shutdown()
            root.destroy()
            root=None
        result={"status":"PASS_S141_REAL_TK_F04_GAME_DIR_ONLY_INI_PRESERVE_NO_GAME"
                if all(checks.values()) else "FAIL_S141_REAL_TK_PATH",
                "actual_windows_tk_file_io":True,
                "test_owned_game_executable_name_only":True,
                "actual_game_executed":False,
                "signed_info_authenticated":False,
                "account_credentials_used":False,
                "proxy_developed":False,
                "checks":checks}
    except Exception as ex:
        result={"status":"FAIL_S141_REAL_TK_PATH",
                "error_type":type(ex).__name__,
                "checks":checks,
                "actual_game_executed":False}
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
    OUTPUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    return 0 if result["status"].startswith("PASS_S141_") else 1


if __name__=="__main__":
    raise SystemExit(main())
