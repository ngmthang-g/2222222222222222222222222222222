"""S168 TRUE test-owned Win64 Tk independent rebuild smoke, no TLM issuer.

Physical Windows HWND/PID + real Tk/INI. Legacy original EXE is never
patched/injected. No game commands or license tokens are manufactured.
"""
from __future__ import annotations
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s168"
OUT.mkdir(parents=True,exist_ok=True)


def main():
    proof={"status":"NOT_RUN","original_issuer":False,
           "gameplay_parity":False,"original_exe_modified":False}
    root=None
    producer=None
    try:
        if os.name!="nt":
            raise RuntimeError("S168_REQUIRES_WINDOWS_TK")
        import tkinter as tk
        from start_polling import StartWindowProducer
        from start_windows import NativeWin32Backend
        from shell import TLMMainApp,INFO_KEY
        from permission_guard import PermissionSnapshot
        from farm_train_composition import TkTrainComposition
        from TLMToolIndependent import make_independent_builders

        with tempfile.TemporaryDirectory(prefix="S168_INDEPENDENT_") as td:
            path=Path(td)/"settings.ini"
            raw=(b"[Settings]\r\npassword = preserve_me\r\n"
                 b"[Farm]\r\ntown_condition = cycle\r\n"
                 b"loop_minutes = 30\r\npickup_mode = all\r\n"
                 b"coord_1 = TrainingA|2|12|24\r\n"
                 b"[Party]\r\nparty_after = wait\r\n")
            path.write_bytes(raw)
            root=tk.Tk()
            producer=StartWindowProducer(backend_factory=NativeWin32Backend,
                                        interval_seconds=0.10,join_timeout=1.0)
            app=TLMMainApp(root,make_independent_builders(path,producer),
                           independent_mode=True,local_window_count=lambda:0)
            app.position_window_top_right()
            root.update()
            hwnd=int(root.winfo_id())
            backend=NativeWin32Backend()
            proof["actual_tk_hwnd_same_process"]=(
                hwnd>0 and backend.is_window(hwnd)
                and backend.process_id(hwnd)==os.getpid())
            visible=app.lifecycle.visible
            proof["no_license_info_shows_all_implemented_tabs"]=(
                {"info_tab","start_tab","login_tab","party_tab","farm_tab","trainlsv_tab"}<=visible
                and "proxy_tab" not in visible
                and "trainlsv_tab" not in app.lifecycle._instances)
            proof["no_eager_train_before_selected"]=(
                "farm_tab" not in app.lifecycle._instances)
            app.notebook.select(app._tab_frames["farm_tab"])
            root.update()
            train=app.lifecycle._instances.get("farm_tab")
            proof["real_train_config_enabled_with_zero_game_windows"]=(
                isinstance(train,TkTrainComposition)
                and train._authorized()
                and train.coords is not None
                and train.accounts is not None
                and str(train.train.checks["respawn"].cget("state"))=="normal")
            train.town.mode_var.set("never")
            proof["real_config_save_without_server_or_game"]=(
                train.town._on_mode()
                and b"town_condition = never" in path.read_bytes())
            # Inject a blocked original-license snapshot: independent policy
            # must not hide implemented tab or revoke local config.
            app.apply_info_snapshot(PermissionSnapshot())
            app.apply_verified_permissions(set(),blocked=True)
            root.update()
            proof["old_license_revocation_ignored_in_local_runtime"]=(
                "farm_tab" in app.lifecycle.visible
                and train._authorized()
                and app.lifecycle.current=="farm_tab"
                and train.coords is not None)
            app.notebook.select(app._tab_frames[INFO_KEY])
            root.update()
            proof["local_info_page_is_truthful"]=(
                "info_tab" in app.lifecycle._instances
                and app.lifecycle.current==INFO_KEY)
            app.shutdown()
            root.destroy();root=None
            data=path.read_bytes()
            proof["unrelated_settings_lines_preserved"]=(
                b"password = preserve_me\r\n" in data
                and b"party_after = wait\r\n" in data)
        flags={k:v for k,v in proof.items() if type(v) is bool
               and k not in ("original_issuer","gameplay_parity",
                              "original_exe_modified")}
        if not all(flags.values()):
            raise RuntimeError("FAILED_CHECKS:"+",".join(
                k for k,v in flags.items() if not v))
        proof["status"]="PASS_NATIVE_S168_INDEPENDENT_REAL_TK_LICENSE_FREE_CONFIG_NOT_GAME"
    except Exception as exc:
        proof["status"]="FAILED_S168"
        proof["error_type"]=type(exc).__name__
        proof["error_detail"]=str(exc)[:700]
    finally:
        if producer is not None:
            try:producer.stop()
            except Exception:pass
        if root is not None:
            try:root.destroy()
            except Exception:pass
        (OUT/"independent_runtime.json").write_text(
            json.dumps(proof,ensure_ascii=False,indent=2)+"\n",
            encoding="utf-8")
        for k,v in proof.items():
            print("S168_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if proof["status"].startswith("PASS_NATIVE_") else 1


if __name__=="__main__":
    raise SystemExit(main())
