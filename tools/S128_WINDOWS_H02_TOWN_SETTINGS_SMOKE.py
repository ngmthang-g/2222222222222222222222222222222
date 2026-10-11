"""S128 Windows native Tk source-backed Farm return-town configuration.

Uses a real test-owned top-level HWND/PID, a CI-only synthetic Info claim
to exercise permission gating, and real isolated settings.ini. No actual
Than Long client or production license verification; no Farm runtime.
"""
from __future__ import annotations
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s128"
OUT.mkdir(parents=True,exist_ok=True)


def run():
    q={"status":"NOT_RUN","real_game":False,"signed_info":False,"proxy":"EXCLUDED"}
    root=None
    try:
        if os.name!="nt":
            raise RuntimeError("WINDOWS_TK_REQUIRED")
        import tkinter as tk
        from permission_guard import PermissionGuard,VerifiedClaims
        from farm_town_config import FarmTownSettingsStore
        from farm_town_panel import TkFarmTownConfig
        from start_windows import NativeWin32Backend

        with tempfile.TemporaryDirectory(prefix="S128_NATIVE_H02_") as td:
            config_path=Path(td)/"settings.ini"
            raw=(b"[Settings]\r\ncredentials = exact_secret\r\n"
                 b"[Farm]\r\ncoord_1 = TrainA|26|1|2\r\n"
                 b"[Party]\r\nparty_after = wait\r\n")
            config_path.write_bytes(raw)
            store=FarmTownSettingsStore(config_path)
            root=tk.Tk()
            root.geometry("800x440+0+0")
            root.update()
            native=NativeWin32Backend()
            hwnd=int(root.winfo_id())
            q["real_test_owned_hwnd_pid"]=(
                native.is_window(hwnd)
                and native.is_visible(hwnd)
                and native.process_id(hwnd)==os.getpid())
            guard=PermissionGuard()
            panel=TkFarmTownConfig(root,store=store,
                                    permission_guard=guard,
                                    running_count=lambda:1)
            panel.pack(fill="x")
            root.update()
            q["original_default_three_radios_and_loop_30"]=(
                panel.mode_var.get()=="cycle"
                and panel.minutes_var.get()=="30"
                and len(panel.radios)==3
                and panel.snapshot.value.navigation==(
                    "Phù 1","Phù 2","Phù 3","Ngựa"))
            q["original_lower_town_body_hidden"]=(
                not panel._body_visible and not panel.lower.winfo_manager()
                and str(panel.toggle.cget("text"))=="Hiện cấu hình")
            q["observed_unsigned_states"]={
                "permitted":panel._permitted(),
                "toggle_state":str(panel.toggle.cget("state")),
                "radio_state":str(panel.radios[0].cget("state"))}
            q["unsigned_cannot_edit_or_show"]=(
                not panel._permitted()
                and not panel.toggle_lower_body()
                and str(panel.radios[0].cget("state"))=="disabled")
            guard.receive_token("CI_ONLY_NO_SERVER_SIGNATURE",lambda _:
                VerifiedClaims(frozenset({"farm_tab"}),"active",2))
            panel.reapply_permission()
            q["observed_authorized_states"]={
                "permitted":panel._permitted(),
                "toggle_state":str(panel.toggle.cget("state")),
                "radio_state":str(panel.radios[0].cget("state"))}
            q["test_only_claim_enables_ui_without_running_farm"]=(
                panel._permitted() and str(panel.radios[0].cget("state"))=="normal"
                and not hasattr(panel,"_farming_acc"))
            panel.radios[0].invoke()
            q["real_radio_never_persisted"]=(
                store.load().value.mode=="never" and panel.mode_var.get()=="never")
            panel.minutes_var.set("47")
            panel._on_minutes()
            q["real_minutes_persist_independent_of_mode"]=(
                store.load().value.minutes=="47" and panel.mode_var.get()=="never")
            shown=panel.toggle_lower_body()
            q["true_hidden_pane_toggle"]=(
                shown and panel._body_visible
                and bool(panel.lower.winfo_manager())
                and str(panel.toggle.cget("text"))=="Ẩn cấu hình")
            panel.radios[1].invoke()
            q["town_condition_change_does_not_toggle_body"]=(
                store.load().value.mode=="full_bag_timer"
                and panel._body_visible and panel.minutes_var.get()=="47")
            panel.nav_vars[0].set("")
            nav_ok=panel._on_nav(0)
            q["priority_edit_really_persists_and_recomputes_uniqueness"]=(
                nav_ok and store.load().value.navigation[0]==""
                and "Phù 2" not in panel.nav_combos[0].cget("values")
                and "Phù 1" in panel.nav_combos[0].cget("values"))
            panel.minutes_var.set("invalid")
            invalid=panel._on_minutes()
            q["invalid_minutes_rollback_no_disk_write"]=(
                not invalid and panel.minutes_var.get()=="47"
                and store.load().value.minutes=="47")
            locked=panel.apply_route_lock(True)
            q["observed_locked"]={
                "applied":locked,"mode":store.load().value.mode,
                "radios":[str(b.cget("state")) for b in panel.radios]}
            q["original_any_locked_route_forces_never_and_disables_radios"]=(
                locked and store.load().value.mode=="never"
                and all(str(b.cget("state"))=="disabled" for b in panel.radios)
                and panel.minutes_var.get()=="47")
            unlocked=panel.apply_route_lock(False)
            q["observed_unlocked"]={
                "applied":unlocked,"mode":store.load().value.mode,
                "radios":[str(b.cget("state")) for b in panel.radios]}
            q["unlock_does_not_invent_old_mode_restoration"]=(
                unlocked and store.load().value.mode=="never"
                and all(str(b.cget("state"))=="normal" for b in panel.radios))
            guard.clear()
            panel.reapply_permission()
            q["observed_revoked"]={
                "permitted":panel._permitted(),
                "spin":str(panel.spin.cget("state")),
                "nav":str(panel.nav_combos[0].cget("state"))}
            q["info_revoke_disables_real_config_controls"]=(
                not panel._permitted()
                and str(panel.spin.cget("state"))=="disabled"
                and str(panel.nav_combos[0].cget("state"))=="disabled")
            panel.mode_var.set("cycle")
            unauth=panel._on_mode()
            q["unsigned_attempt_cannot_modify_settings"]=(
                not unauth and store.load().value.mode=="never")
            panel.destroy()
            root.destroy()
            root=None
            saved=config_path.read_bytes()
            q["other_credentials_party_coordinate_bytes_preserved"]=(
                b"credentials = exact_secret\r\n" in saved
                and b"coord_1 = TrainA|26|1|2\r\n" in saved
                and b"party_after = wait\r\n" in saved)
            backups=list(Path(td).glob("settings.????????.ini"))
            q["dated_backup_created_before_write"]=(
                len(backups)==1 and backups[0].read_bytes()==raw)
        checklist=[k for k,v in q.items()
                   if type(v) is bool and k not in ("real_game","signed_info")]
        if not all(q[k] for k in checklist):
            raise RuntimeError("S128_NATIVE_TOWN_ASSERTION_FAILED")
        q["status"]="PASS_NATIVE_S128_REAL_H02_TOWN_SETTINGS_NO_GAME"
    except Exception as exc:
        q["status"]="FAIL_NATIVE_S128"
        q["error_type"]=type(exc).__name__
        q["error_detail"]=str(exc)[:220]
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        (OUT/"native_h02_town.json").write_text(
            json.dumps(q,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        for key,value in q.items():
            print("S128_"+key.upper()+"="+json.dumps(value,ensure_ascii=True))
    return 0 if q["status"].startswith("PASS_NATIVE_S128_") else 1


if __name__=="__main__":
    raise SystemExit(run())
