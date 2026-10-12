"""S165 true test-owned native Win64 Tk Train E03 composition integration.

Exercises REAL Tk widgets/INI, no original game, no production Info issuer,
no user tokens/credentials, no game action, no license bypass.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s165"
OUT.mkdir(parents=True,exist_ok=True)


def main():
    proof={"status":"NOT_RUN","signed_original_info":False,
           "actual_game":False,"working_product_exe":False,
           "test_only_info_fixture":True}
    root=None
    try:
        if os.name!="nt":
            raise RuntimeError("S165_WINDOWS_DESKTOP_REQUIRED")
        import tkinter as tk
        from tkinter import ttk
        from permission_guard import PermissionGuard, VerifiedClaims
        from source_backed_tab_builders import source_backed_tab_builders
        from shell import TabLifecycle, ALL_KEYS, INFO_KEY
        from farm_train_composition import TkTrainComposition
        from farm_town_config import FarmTownSettingsStore

        with tempfile.TemporaryDirectory(prefix="S165_REAL_TRAIN_") as td:
            ini=Path(td)/"settings.ini"
            raw=(b"[Settings]\r\npassword = keep_private\r\n"
                 b"[Farm]\r\ntown_condition = cycle\r\n"
                 b"loop_minutes = 30\r\npickup_mode = all\r\n"
                 b"coord_1 = TrainingA|2|12|24\r\n"
                 b"[Party]\r\nparty_after = wait\r\n")
            ini.write_bytes(raw)
            root=tk.Tk()
            root.geometry("1080x920+0+0")
            root.update()
            proof["physical_tk_root"]=(root.winfo_id()>0)
            guard=PermissionGuard()
            count=lambda:1
            builders=source_backed_tab_builders(
                lambda p: ttk.Frame(p),settings_file=ini,
                train_permission_guard=guard,train_running_count=count)
            proof["exact_new_optin_original_slot"]=(
                "farm_tab" in builders and "proxy_tab" not in builders)
            frames={key:ttk.Frame(root) for key in ALL_KEYS}
            lifecycle=TabLifecycle(builders,frames)
            proof["unsigned_never_instantiated"]=(
                "farm_tab" not in lifecycle.visible
                and lifecycle.select("farm_tab") is lifecycle._instances[INFO_KEY]
                and "farm_tab" not in lifecycle._instances)
            # Fixture verification exists ONLY in this smoke, never in app.
            guard.receive_token("TEST_ONLY_NO_ISSUER",lambda _:
                VerifiedClaims(frozenset({"farm_tab"}),"active",2))
            lifecycle.apply_authorized_keys({"farm_tab"})
            comp=lifecycle.select("farm_tab")
            comp.update_idletasks()
            proof["actual_existing_train_tk_composition"]=(
                isinstance(comp,TkTrainComposition)
                and comp.winfo_exists()
                and comp.master is frames["farm_tab"]
                and comp.winfo_manager()=="pack"
                and comp.town is not None and comp.train is not None
                and comp.buffs is not None
                and comp.accounts_section is not None)
            proof["signed_guard_fixture_only_unlocks_configs"]=(
                comp._authorized()
                and str(comp.train.checks["respawn"].cget("state"))=="normal"
                and comp.coords is not None and comp.accounts is not None)
            comp.town.mode_var.set("never")
            proof["real_ini_write_only_under_test_grant"]=(
                comp.town._on_mode()
                and FarmTownSettingsStore(ini).load().value.mode=="never")
            guard.clear()
            comp.reapply_permissions()
            proof["real_revocation_restricts_all"]=(
                not comp._authorized()
                and comp.accounts is None and comp.coords is None
                and str(comp.train.checks["respawn"].cget("state"))=="disabled"
                and not comp.town._on_mode())
            lifecycle.shutdown()
            root.destroy();root=None
            saved=ini.read_bytes()
            proof["unrelated_settings_bytes_preserved"]=(
                b"password = keep_private\r\n" in saved
                and b"party_after = wait\r\n" in saved)
        checks={k:v for k,v in proof.items() if type(v) is bool
                and k not in ("signed_original_info","actual_game",
                              "working_product_exe")}
        if not all(checks.values()):
            raise RuntimeError("S165_CHECK_FAILED:"+",".join(
                k for k,v in checks.items() if not v))
        proof["status"]="PASS_NATIVE_S165_REAL_TK_TRAIN_BUILDER_TEST_OWNED_NOT_PRODUCT"
    except Exception as exc:
        proof["status"]="FAILED_S165"
        proof["error_type"]=type(exc).__name__
        proof["error_detail"]=str(exc)[:500]
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        (OUT/"train_builder_native.json").write_text(
            json.dumps(proof,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        for k,v in proof.items():
            print("S165_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if proof["status"].startswith("PASS_NATIVE_") else 1


if __name__=="__main__":
    raise SystemExit(main())
