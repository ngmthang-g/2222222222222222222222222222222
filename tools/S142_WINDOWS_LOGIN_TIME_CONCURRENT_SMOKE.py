"""S142 native Windows F09 real Tk Combobox and byte-safe concurrent disk edit.

Uses test-owned fake INI, never arms schedule, starts game or shuts PC down.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s142"
OUT.mkdir(parents=True,exist_ok=True)

def main():
    if os.name!="nt":
        raise SystemExit("S142_REAL_WINDOWS_TK_REQUIRED")
    import tkinter as tk
    import login_schedule_times as source
    from login_tab import TLMLoginPathTab
    from login_schedule_settings import read_schedule_settings
    from login_account_legacy import read_legacy_accounts
    checks={}
    root=None
    try:
        with tempfile.TemporaryDirectory(prefix="S142_TEST_ONLY_") as name:
            ini=Path(name)/"TLMTool"/"settings.ini"
            ini.parent.mkdir(parents=True)
            original=(
                "[Settings]\r\n"
                "accounts = ?|S142_FAKE_USER|S142_FAKE_PASSWORD|Có|opaque\r\n"
                "  ?|S142_FAKE_U2|S142_FAKE_P2|Tool|\r\n"
                "game_dir = X:\\S142_TestOnly\r\n"
                "schedule_close = 04:00\r\n"
                "schedule_open=04:20\r\n"
                "schedule_on = UNVERIFIED\r\n"
                "[Other]\r\nsafe = Việt Nam\r\n"
            ).encode("utf8")
            ini.write_bytes(original)
            root=tk.Tk()
            root.geometry("650x1050+15+15")
            errors=[]
            view=TLMLoginPathTab(root,settings_file=ini,
                 choose_directory=lambda **_: "",
                 show_error=lambda title,body:errors.append((title,body)))
            root.update()
            clock=view.schedule_times
            checks["actual_F01_readonly_HHMM"]=all(
                str(combo.cget("state"))=="readonly"
                for pair in clock.combos.values() for combo in pair)
            h,m=clock.vars["schedule_close"]
            h.set("07")
            clock.combos["schedule_close"][0].event_generate("<<ComboboxSelected>>")
            root.update()
            expected=original.replace(b"schedule_close = 04:00",b"schedule_close = 07:00")
            checks["real_close_combobox_only_target_bytes"]=(
                ini.read_bytes()==expected and clock.last_status=="UPDATED_ONLY_SCHEDULE_CLOSE")
            # Another real process can modify settings.ini while our
            # temporary file is being written. Simulate that exact window.
            external=expected.replace(b"game_dir = X:\\S142_TestOnly",
                b"game_dir = Y:\\S142_TestOnly")
            real_fsync=source.os.fsync
            def external_write(fd):
                ini.write_bytes(external)
                return real_fsync(fd)
            h.set("09")
            with patch("login_schedule_times.os.fsync",side_effect=external_write):
                clock.combos["schedule_close"][0].event_generate("<<ComboboxSelected>>")
                root.update()
            checks["external_real_file_edit_is_never_overwritten"]=ini.read_bytes()==external
            checks["real_tk_combobox_reverted_when_disk_stale"]=(
                h.get()=="07" and m.get()=="00" and
                clock.last_status=="BLOCKED_TIME_SAVE")
            checks["sanitized_error_not_secret"]=(
                len(errors)==1 and
                all("S142_FAKE_PASSWORD" not in str(v) for v in errors))
            hh,mm=clock.vars["schedule_open"]
            mm.set("55")
            clock.combos["schedule_open"][1].event_generate("<<ComboboxSelected>>")
            root.update()
            final=external.replace(b"schedule_open=04:20",b"schedule_open=04:55")
            checks["next_F09_save_against_latest_external_bytes"]=(
                ini.read_bytes()==final and
                read_schedule_settings(ini).open_hhmm=="04:55")
            checks["original_F02_accounts_readable"]=(
                read_legacy_accounts(ini).status=="READY"
                and read_legacy_accounts(ini).count==2)
            checks["no_game_launch_shutdown_or_proxy"]=True
            view.shutdown()
            root.destroy()
            root=None
        result={
            "status":"PASS_S142_REAL_WIN64_F09_TK_EXTERNAL_CHANGE_FENCED_NOT_PRODUCT"
                if all(checks.values()) else "FAIL_S142_F09_Native",
            "original_game_run":False,"signed_info_authenticated":False,
            "schedule_armed":False,"pc_shutdown":False,
            "real_windows_tk":True,"test_only_fake_credentials":True,
            "checks":checks,
        }
    except Exception as exc:
        result={"status":"FAIL_S142_F09_Native",
                "error_type":type(exc).__name__,
                "checks":checks,
                "original_game_run":False}
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
    (OUT/"native_f09_time_stale.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(result,ensure_ascii=False))
    return 0 if result["status"].startswith("PASS_S142_") else 1

if __name__=="__main__":
    raise SystemExit(main())
