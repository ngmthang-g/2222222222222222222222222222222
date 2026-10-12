"""S169 genuine Win64 Tk Notebook, real TrainLSV form and section-isolated INI.

Test-owned OS HWND/PID; no original TLM license issuer, no gameplay actions.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s169"
OUT.mkdir(parents=True,exist_ok=True)

def main():
    proof={"status":"NOT_RUN","actual_game":False,"original_license":False,
           "lsv_gameplay_sender":False,"original_tlm_modified":False}
    root=None
    producer=None
    try:
        if os.name!="nt":
            raise RuntimeError("S169_REAL_WIN64_TK_REQUIRED")
        import tkinter as tk
        from start_windows import NativeWin32Backend
        from start_polling import StartWindowProducer
        from TLMToolIndependent import make_independent_builders
        from shell import TLMMainApp, INFO_KEY
        from train_lsv_top_tab import TkTrainLsvTopTab
        from train_lsv_top_settings import TrainLsvTopStore
        from permission_guard import PermissionSnapshot

        with tempfile.TemporaryDirectory(prefix="S169_LSV_") as td:
            path=Path(td)/"settings.ini"
            raw=(b"[Login]\r\npassword = DO_NOT_TOUCH\r\n"
                 b"[Farm]\r\ntown_condition = cycle\r\n"
                 b"[TrainLSV]\r\nheal_map = legacy_value\r\n"
                 b"buff_0 = True|1|0|5\r\n"
                 b"[Party]\r\nparty_after = wait\r\n")
            path.write_bytes(raw)
            root=tk.Tk()
            producer=StartWindowProducer(backend_factory=NativeWin32Backend,
                                         interval_seconds=0.1,join_timeout=1.0)
            app=TLMMainApp(root,make_independent_builders(path,producer),
                           independent_mode=True,local_window_count=lambda:0)
            app.position_window_top_right()
            root.update()
            hwnd=int(root.winfo_id())
            backend=NativeWin32Backend()
            proof["physical_test_owned_native_hwnd_pid"]=(
                hwnd>0 and backend.is_window(hwnd)
                and backend.process_id(hwnd)==os.getpid())
            proof["lsv_module_visible_but_lazy"]=(
                "trainlsv_tab" in app.lifecycle.visible
                and "trainlsv_tab" not in app.lifecycle._instances
                and "proxy_tab" not in app.lifecycle.visible)
            app.notebook.select(app._tab_frames["trainlsv_tab"])
            root.update()
            tab=app.lifecycle._instances.get("trainlsv_tab")
            proof["lsv_real_tk_widgets_offline_with_no_info_token"]=(
                isinstance(tab,TkTrainLsvTopTab)
                and app.lifecycle.current=="trainlsv_tab"
                and tab._permitted()
                and len(tab.checks)==3
                and len(tab.pickup_radios)==3
                and tab.pickup_var.get()=="all"
                and str(tab.checks["respawn"].cget("state"))=="normal")
            tab.flags["respawn"].set(True)
            ok1=tab._on_flag("respawn")
            tab.pickup_var.set("weapons")
            ok2=tab._on_pickup()
            root.update()
            loaded=TrainLsvTopStore(path).load().value
            proof["real_disk_config_changes_only_confirmed_keys"]=(
                ok1 and ok2 and loaded.respawn
                and loaded.pickup_mode=="weapons"
                and tab.snapshot.value==loaded)
            saved=path.read_bytes()
            proof["unrelated_sections_and_unknown_lsv_records_unchanged"]=(
                b"[Login]\r\npassword = DO_NOT_TOUCH\r\n" in saved
                and b"[Farm]\r\ntown_condition = cycle\r\n" in saved
                and b"heal_map = legacy_value\r\n" in saved
                and b"buff_0 = True|1|0|5\r\n" in saved
                and b"[Party]\r\nparty_after = wait\r\n" in saved
                and b"trist = " not in saved
                and b"auto_reconnect = " not in saved)
            # Even a blocked original TLM Info state cannot hide a
            # source-backed local configuration tab.
            app.apply_info_snapshot(PermissionSnapshot())
            app.apply_verified_permissions(set(), blocked=True)
            root.update()
            proof["legacy_license_revoke_not_applied_to_independent_lsv"]=(
                app.lifecycle.current=="trainlsv_tab"
                and "trainlsv_tab" in app.lifecycle.visible
                and tab._permitted())
            app.notebook.select(app._tab_frames[INFO_KEY])
            root.update()
            proof["safe_leave_without_background_game_worker"]=(
                app.lifecycle.current==INFO_KEY
                and not producer.active)
            app.shutdown()
            root.destroy();root=None
        flags={k:v for k,v in proof.items() if type(v) is bool
               and k not in ("actual_game","original_license",
                             "lsv_gameplay_sender","original_tlm_modified")}
        if not all(flags.values()):
            raise RuntimeError("FAILED_CHECKS:"+",".join(
                k for k,v in flags.items() if not v))
        proof["status"]="PASS_NATIVE_S169_REAL_TK_TRAINLSV_LOCAL_INI_NO_GAME"
    except Exception as exc:
        proof["status"]="FAILED_S169"
        proof["error_type"]=type(exc).__name__
        proof["error_detail"]=str(exc)[:650]
    finally:
        if producer is not None:
            try:producer.stop()
            except Exception:pass
        if root is not None:
            try:root.destroy()
            except Exception:pass
        (OUT/"native_lsv_config.json").write_text(
            json.dumps(proof,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        for k,v in proof.items():
            print("S169_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if proof["status"].startswith("PASS_NATIVE_") else 1

if __name__=="__main__":
    raise SystemExit(main())
