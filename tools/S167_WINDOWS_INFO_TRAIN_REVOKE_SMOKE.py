"""S167 native Windows E03 real Notebook + Train Info refresh/revocation.

Exercises real Tk, actual test-owned HWND/PID, native read-only Win32 S09
worker and real guarded config widgets. TEST-ONLY permission fixture lives
here, never in packaged product code.
"""
from __future__ import annotations
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s167"
OUT.mkdir(parents=True,exist_ok=True)


def main():
    proof={"status":"NOT_RUN","actual_game":False,"signed_original_info":False,
           "product_exe":False,"proxy":"EXCLUDED"}
    root=None
    producer=None
    try:
        if os.name!="nt":
            raise RuntimeError("REAL_WIN64_TK_REQUIRED")
        import tkinter as tk
        from tkinter import ttk
        from permission_guard import PermissionGuard,VerifiedClaims
        from source_backed_tab_builders import source_backed_tab_builders
        from shell import INFO_KEY,TLMMainApp
        from farm_train_composition import TkTrainComposition
        from start_polling import StartWindowProducer
        from start_windows import NativeWin32Backend

        with tempfile.TemporaryDirectory(prefix="S167_INFO_TRAIN_") as td:
            cfg=Path(td)/"settings.ini"
            raw=(b"[Settings]\r\npassword = keep_private\r\n"
                 b"[Farm]\r\ntown_condition = cycle\r\n"
                 b"loop_minutes = 30\r\npickup_mode = all\r\n"
                 b"coord_1 = TrainingA|2|12|24\r\n"
                 b"[Party]\r\nparty_after = wait\r\n")
            cfg.write_bytes(raw)
            root=tk.Tk()
            root.geometry("1060x840+0+0")
            root.update()
            backend=NativeWin32Backend()
            hwnd=int(root.winfo_id())
            proof["physical_native_tk_hwnd_and_pid"]=(
                hwnd>0 and backend.is_window(hwnd)
                and backend.process_id(hwnd)==os.getpid())
            producer=StartWindowProducer(
                backend_factory=NativeWin32Backend,
                interval_seconds=0.08,join_timeout=1.0)
            guard=PermissionGuard()
            def test_only_verify(_token):
                return VerifiedClaims(frozenset({"farm_tab"}),"active",2)
            builders=source_backed_tab_builders(
                lambda host:ttk.Frame(host),settings_file=cfg,
                start_producer=producer,train_permission_guard=guard,
                train_running_count=lambda:1)
            app=TLMMainApp(root,builders)
            proof["unsigned_info_hidden_and_not_built"]=(
                "farm_tab" not in app.lifecycle.visible
                and "farm_tab" not in app.lifecycle._instances
                and not producer.active)
            guard.receive_token("CI_SIGNED_INFO_FIXTURE_ONLY",test_only_verify)
            valid=guard.snapshot
            app.apply_info_snapshot(valid)
            root.update()
            proof["real_info_snapshot_shows_train_slot"]=(
                "farm_tab" in app.lifecycle.visible
                and str(app.notebook.tab(app._tab_frames["farm_tab"],"state"))=="normal")
            app.notebook.select(app._tab_frames["farm_tab"])
            root.update()
            train=app.lifecycle._instances.get("farm_tab")
            proof["real_notebook_selected_train_owns_passive_s09"]=(
                isinstance(train,TkTrainComposition)
                and app.lifecycle.current=="farm_tab"
                and train.coords is not None and train.accounts is not None
                and producer.active and train._lifecycle_owns_producer)
            # Guard denied while stale Info shell still thinks Farm may be
            # visible. The new S167 bridge must NOT need a user tab click.
            guard.clear()
            app.apply_info_snapshot(valid)
            root.update()
            proof["info_callback_without_tab_switch_revokes_widgets"]=(
                app.lifecycle.current=="farm_tab"
                and not producer.active
                and train.coords is None and train.accounts is None
                and not train._readonly_refresh_requested
                and str(train.train.checks["respawn"].cget("state"))=="disabled")
            # Newly valid independently verified TEST fixture restores
            # selected Train without an intermediate tab switch.
            guard.receive_token("CI_SIGNED_INFO_FIXTURE_ONLY",test_only_verify)
            app.apply_info_snapshot(guard.snapshot)
            root.update()
            proof["info_callback_resumes_selected_passive_worker"]=(
                app.lifecycle.current=="farm_tab"
                and producer.active
                and train.coords is not None and train.accounts is not None
                and train.accounts._active
                and str(train.train.checks["respawn"].cget("state"))=="normal")
            guard.clear()
            app.apply_info_snapshot(guard.snapshot)
            root.update()
            proof["real_info_revocation_falls_back_to_info"]=(
                app.lifecycle.current==INFO_KEY
                and "farm_tab" not in app.lifecycle.visible
                and not producer.active
                and train.coords is None and train.accounts is None)
            app.shutdown()
            root.destroy();root=None
            proof["unrelated_saved_bytes_not_modified"]=(
                cfg.read_bytes()==raw)
        flags={k:v for k,v in proof.items() if type(v) is bool
               and k not in ("actual_game","signed_original_info","product_exe")}
        if not all(flags.values()):
            raise RuntimeError("S167_NATIVE_CHECKS_FAILED:"+",".join(
                k for k,v in flags.items() if not v))
        proof["status"]="PASS_NATIVE_S167_REAL_TK_INFO_TO_TRAIN_REVOKE_RESUME_NOT_GAME"
    except Exception as exc:
        proof["status"]="FAILED_S167"
        proof["error_type"]=type(exc).__name__
        proof["error_detail"]=str(exc)[:600]
    finally:
        if producer is not None:
            try:producer.stop()
            except Exception:pass
        if root is not None:
            try:root.destroy()
            except Exception:pass
        (OUT/"native_info_train.json").write_text(
            json.dumps(proof,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        for k,v in proof.items():
            print("S167_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if proof["status"].startswith("PASS_NATIVE_") else 1


if __name__=="__main__":
    raise SystemExit(main())
