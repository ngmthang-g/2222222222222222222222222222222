"""S166 real test-owned Windows Tk + shared Win32 S09 producer lifecycle.

Uses a real native EnumWindows backend and Tk HWND owned by the CI process;
never launches an actual game or issues user/game input. Synthetic Info
verified claims exist ONLY inside this offline CI fixture.
"""
from __future__ import annotations
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s166"
OUT.mkdir(parents=True,exist_ok=True)

def main():
    checks={"status":"NOT_RUN","real_game":False,"signed_info_issuer":False,
            "product_exe":False,"proxy":"EXCLUDED"}
    root=None
    producer=None
    try:
        if os.name!="nt":
            raise RuntimeError("WINDOWS_NATIVE_DESKTOP_REQUIRED")
        import tkinter as tk
        from tkinter import ttk
        from start_polling import StartWindowProducer
        from start_windows import NativeWin32Backend
        from permission_guard import PermissionGuard,VerifiedClaims
        from source_backed_tab_builders import source_backed_tab_builders
        from shell import INFO_KEY,ALL_KEYS,TabLifecycle
        from farm_train_composition import TkTrainComposition

        with tempfile.TemporaryDirectory(prefix="S166_TRAIN_LIFECYCLE_") as td:
            path=Path(td)/"settings.ini"
            raw=(b"[Settings]\r\npassword = keep_private\r\n"
                 b"[Farm]\r\ntown_condition = cycle\r\n"
                 b"loop_minutes = 30\r\npickup_mode = all\r\n"
                 b"coord_1 = TrainingA|2|12|24\r\n"
                 b"[Party]\r\nparty_after = wait\r\n")
            path.write_bytes(raw)
            root=tk.Tk()
            root.geometry("1120x900+0+0")
            root.update()
            native=NativeWin32Backend()
            hwnd=int(root.winfo_id())
            checks["real_test_owned_tk_hwnd_pid"]=(
                hwnd>0 and native.is_window(hwnd)
                and native.process_id(hwnd)==os.getpid())
            producer=StartWindowProducer(
                backend_factory=NativeWin32Backend,
                interval_seconds=0.10)
            guard=PermissionGuard()
            builders=source_backed_tab_builders(
                lambda parent:ttk.Frame(parent),
                settings_file=path,start_producer=producer,
                train_permission_guard=guard,train_running_count=lambda:1)
            frames={k:ttk.Frame(root) for k in ALL_KEYS}
            lifecycle=TabLifecycle(builders,frames)
            checks["missing_signed_entitlement_never_activates_worker"]=(
                "farm_tab" not in lifecycle.visible
                and not producer.active)
            # Strictly TEST-OWNED permission fixture, not a trusted issuer.
            guard.receive_token("TEST_FIXTURE_ONLY",lambda _:
                VerifiedClaims(frozenset({"farm_tab"}),"active",2))
            lifecycle.apply_authorized_keys({"farm_tab"})
            comp=lifecycle.select("farm_tab")
            root.update()
            checks["genuine_train_tk_uses_single_existing_S09_producer"]=(
                isinstance(comp,TkTrainComposition)
                and comp.accounts is not None
                and comp.accounts.producer is producer
                and not comp.accounts._own_producer
                and comp.accounts._active
                and producer.active
                and comp._lifecycle_owns_producer
                and comp.winfo_exists())
            # Switching out stops only the selected Train-owned worker.
            lifecycle.select(INFO_KEY)
            root.update()
            checks["tab_deselect_stops_and_cleans_owned_worker"]=(
                not producer.active
                and not comp._lifecycle_owns_producer
                and comp.accounts is not None
                and not comp.accounts._active
                and not comp.accounts._rows)
            # Re-entry must renew a real worker, without a second scan source.
            lifecycle.select("farm_tab")
            root.update()
            checks["reentry_restores_passive_refresh"]=(
                producer.active and comp.accounts._active
                and comp.accounts.producer is producer)
            # A real revocation notification on current Train tears down rows.
            guard.clear()
            comp.reapply_permissions()
            root.update()
            checks["revoke_while_selected_cancels_worker_and_sensitive_rows"]=(
                not producer.active and not comp._lifecycle_owns_producer
                and comp.coords is None and comp.accounts is None
                and not comp._readonly_refresh_requested)
            lifecycle.apply_authorized_keys(set(),blocked=True)
            checks["tab_permission_revoked_falls_back_to_info"]=(
                lifecycle.current==INFO_KEY
                and "farm_tab" not in lifecycle.visible)
            # Externally active producer lease is never owned/stopped by Train.
            guard.receive_token("TEST_FIXTURE_ONLY",lambda _:
                VerifiedClaims(frozenset({"farm_tab"}),"active",2))
            lifecycle.apply_authorized_keys({"farm_tab"})
            external_start=producer.start()
            comp2=lifecycle.select("farm_tab")
            root.update()
            checks["external_shared_worker_not_claimed"]=(
                external_start and producer.active and comp2 is comp
                and comp.accounts is not None and comp.accounts._active
                and not comp._lifecycle_owns_producer)
            lifecycle.select(INFO_KEY)
            root.update()
            checks["deselect_never_stops_external_owner"]=(
                producer.active and not comp.accounts._active)
            producer.stop()
            lifecycle.shutdown()
            root.destroy();root=None
            checks["password_and_party_bytes_preserved"]=(
                b"password = keep_private\r\n" in path.read_bytes()
                and b"party_after = wait\r\n" in path.read_bytes())

        flags={k:v for k,v in checks.items() if type(v) is bool
               and k not in ("real_game","signed_info_issuer","product_exe")}
        if not all(flags.values()):
            raise RuntimeError("S166_NATIVE_FAIL:"+",".join(
                k for k,v in flags.items() if not v))
        checks["status"]="PASS_NATIVE_S166_REAL_TK_TRAIN_TAB_START_STOP_SHARED_WIN32_NOT_GAME"
    except Exception as exc:
        checks["status"]="FAILED_S166"
        checks["error_type"]=type(exc).__name__
        checks["error_detail"]=str(exc)[:600]
    finally:
        if producer is not None:
            try:producer.stop()
            except Exception:pass
        if root is not None:
            try:root.destroy()
            except Exception:pass
        (OUT/"native_train_lifecycle.json").write_text(
            json.dumps(checks,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        for k,v in checks.items():
            print("S166_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if checks["status"].startswith("PASS_NATIVE_") else 1

if __name__=="__main__":
    raise SystemExit(main())
