"""S132 genuine Windows Tk integration of existing Farm modules, NOT playable.

Real TEST-owned HWND/PID; TRUE Tk widgets & UTF-8 settings.ini. TEST-only
verified Info claims never make a production signed token. Validate original
H01 ordering, S128/S129/S130/S131 cross-INI rebase, S121 coordinate edit,
S123 passive real native HWND/PID, exact revoke/destroy and no game actions.
"""
from __future__ import annotations
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s132"
OUT.mkdir(parents=True,exist_ok=True)


def run():
    e={"status":"NOT_RUN","real_game":False,"real_signed_info":False,
       "real_auto_farm":False,"real_game_memory":False,"proxy":"EXCLUDED"}
    root=None
    try:
        if os.name!="nt":
            raise RuntimeError("S132_TRUE_WINDOWS_TK_REQUIRED")
        import tkinter as tk
        from permission_guard import PermissionGuard,VerifiedClaims
        from farm_train_composition import TkTrainComposition, TRAIN_SECTIONS
        from train_saved_coordinates import FarmCoordinate,FarmCoordinatesStore
        from farm_town_config import FarmTownSettingsStore
        from farm_town_trade_settings import TownTradeStore
        from farm_train_settings import FarmTrainSettingsStore
        from farm_buff_settings import FarmBuffSettingsStore
        from start_windows import NativeWin32Backend,GameWindow
        from start_polling import WindowSnapshot

        with tempfile.TemporaryDirectory(prefix="S132_TRUE_FARM_LAYOUT_") as td:
            ini=Path(td)/"settings.ini"
            raw=(b"[Settings]\r\npassword = keep_private\r\n"
                 b"[Farm]\r\ntown_condition = cycle\r\nloop_minutes = 30\r\n"
                 b"pickup_mode = all\r\n"
                 b"coord_1 = TrainingA|2|12|24\r\n"
                 b"[Party]\r\nparty_after = wait\r\n")
            ini.write_bytes(raw)
            guard=PermissionGuard()
            root=tk.Tk()
            root.geometry("1170x960+0+0")
            root.update()
            native=NativeWin32Backend()
            hwnd=int(root.winfo_id())
            pid=native.process_id(hwnd)
            e["true_windows_test_owned_hwnd_pid"]=(
                hwnd>0 and pid==os.getpid()
                and native.is_window(hwnd) and native.is_visible(hwnd))
            comp=TkTrainComposition(
                root,settings_file=ini,permission_guard=guard,
                running_count=lambda:1,allow_account=lambda _w: True,
                identity_backend_factory=NativeWin32Backend)
            comp.pack(fill="both",expand=True)
            root.update()
            e["original_four_visible_group_order"]=(
                TRAIN_SECTIONS==(
                    "Cấu hình Về thành","Cấu hình Train",
                    "Cấu hình tọa độ lưu sẵn","Danh sách tài khoản")
                and comp.winfo_children()[:4]==[
                    comp.town,comp.train,comp.coords_section,comp.accounts_section])
            e["original_lower_town_starts_hidden_with_trade_real"]=(
                not bool(comp.town.lower.winfo_manager())
                and not comp.town._body_visible
                and comp.trade.master is comp.town.lower)
            e["original_train_buff_nested_within_train_group"]=(
                comp.buffs.master is comp.train.group
                and len(comp.buffs.row_widgets)==0)
            e["unsigned_config_and_sensitive_sections_fail_closed"]=(
                not comp._authorized() and comp.coords is None
                and comp.accounts is None
                and str(comp.town.radios[0].cget("state"))=="disabled"
                and str(comp.train.checks["respawn"].cget("state"))=="disabled"
                and str(comp.buffs.add_button.cget("state"))=="disabled")
            e["unsigned_readonly_refresh_never_starts"]=(
                not comp.start_readonly_window_refresh()
                and comp.accounts is None)
            # CI-only TEST VERIFIER. This isn't a signed Info provider.
            guard.receive_token("TEST_ONLY_NOT_SIGNED",lambda _:
                VerifiedClaims(frozenset({"farm_tab"}),"active",2))
            attached=comp.reapply_permissions()
            root.update()
            e["genuine_test_right_mounts_existing_H11_and_H12"]=(
                attached and comp._authorized()
                and comp.coords is not None and comp.accounts is not None
                and len(comp.coords.row_widgets)==1
                and comp.coords.account_bindings.active_count()==0
                and bool(comp.accounts_canvas.winfo_exists())
                and bool(comp.accounts_scrollbar.winfo_exists()))
            e["authorized_existing_town_and_buff_enabled"]=(
                str(comp.town.radios[0].cget("state"))=="normal"
                and str(comp.train.checks["respawn"].cget("state"))=="normal"
                and str(comp.buffs.add_button.cget("state"))=="normal"
                and comp.town.toggle_lower_body()
                and bool(comp.town.lower.winfo_manager()))
            native_win=GameWindow(
                hwnd,pid,"Test-owned native Tk window","TkTopLevel","TEST_ONLY.exe")
            trusted=WindowSnapshot(revision=1,windows=(native_win,),valid=True)
            added=comp.apply_trusted_window_snapshot(trusted)
            root.update()
            row=comp.accounts._rows.get(hwnd) if comp.accounts else None
            e["real_test_owned_hwnd_registers_passive_not_playing_account"]=(
                added and len(comp.accounts._rows)==1 and row is not None
                and row["pid"]==pid
                and row["sell"].instate(["readonly"])
                and row["farm"].instate(["readonly"])
                and comp.coords.account_bindings.active_count()==1
                and row["state_label"].cget("text")=="Đã dừng")
            applied=comp.coords.apply_row_to_all(0,target="farm")
            e["real_S121_S123_coord_apply_to_existing_combobox"]=(
                applied==1 and row["farm"].get()=="TrainingA")
            # Four independent original configuration stores share one
            # real settings.ini. Each successful write re-bases the others.
            comp.town.mode_var.set("never")
            town_ok=comp.town._on_mode()
            comp.trade.vars["buy_hp"].set(True)
            trade_ok=comp.trade._on_flag("buy_hp")
            comp.train.flags["respawn"].set(True)
            train_ok=comp.train._on_flag("respawn")
            buff_ok=comp.buffs.add_local_row()
            e["four_farm_subpanels_cross_rebase_real_INI"]=(
                town_ok and trade_ok and train_ok and buff_ok
                and FarmTownSettingsStore(ini).load().value.mode=="never"
                and TownTradeStore(ini).load().value.buy_hp
                and FarmTrainSettingsStore(ini).load().value.respawn
                and len(FarmBuffSettingsStore(ini).load().rows)==1
                and comp.town.error is None and comp.train.error is None
                and comp.trade.error is None and comp.buffs.error is None)
            # Rename on genuine H11 widget: must propagate to *existing*
            # account combo and both medicine/shop destinations.
            comp.coords.row_widgets[0]["name"].set("TrainingB")
            renamed=comp.coords.commit_row(0)
            e["H11_original_coordinate_rename_in_live_account"]=(
                renamed and comp.coords.rows[0].name=="TrainingB"
                and row["farm"].get()=="TrainingB"
                and "TrainingB" in tuple(comp.trade.widgets["meds_map"]["values"])
                and "TrainingB" in tuple(comp.train.heal_combo["values"]))
            comp.trade.vars["meds_map"].set("TrainingB")
            medicine=comp.trade._on_select("meds_map")
            comp.train.heal_var.set("TrainingB")
            healing=comp.train._on_heal_select()
            e["after_coord_rename_both_source_backed_consumers_save"]=(
                medicine and healing
                and TownTradeStore(ini).load().value.meds_map=="TrainingB"
                and FarmTrainSettingsStore(ini).load().value.heal_map=="TrainingB")
            # A verified permission is revoked before the outer owner
            # processes reapply_permissions: direct H11 callbacks still deny.
            old_editor=comp.coords
            guard.clear()
            old_editor.row_widgets[0]["x"].set("999")
            blocked=old_editor.commit_row(0)
            e["after_revocation_coordinate_direct_callback_DENIED"]=(
                not blocked
                and FarmCoordinatesStore(ini).load().rows[0].x=="12")
            e["revoked_config_direct_callback_DENIED"]=(
                not comp.buffs.add_local_row()
                and not comp.train._permitted())
            revoked=comp.reapply_permissions()
            root.update()
            e["revocation_destroyed_sensitive_editor_and_native_rows"]=(
                not revoked and comp.coords is None and comp.accounts is None
                and old_editor._closed
                and old_editor.account_bindings.active_count()==0
                and not comp._authorized())
            e["revoked_config_widgets_all_disabled"]=(
                str(comp.town.radios[0].cget("state"))=="disabled"
                and str(comp.trade.widgets["buy_hp"].cget("state"))=="disabled"
                and str(comp.train.checks["respawn"].cget("state"))=="disabled"
                and str(comp.buffs.add_button.cget("state"))=="disabled")
            comp.shutdown()
            comp.destroy()
            root.destroy();root=None
            saved=ini.read_bytes()
            e["no_loss_of_unrelated_password_party_bytes"]=(
                b"password = keep_private\r\n" in saved
                and b"party_after = wait\r\n" in saved)
            backups=list(Path(td).glob("settings.????????.ini"))
            e["prior_write_backup_is_exact_original"]=(
                len(backups)==1 and backups[0].read_bytes()==raw)
        checks={k:v for k,v in e.items() if type(v) is bool
                and k not in ("real_game","real_signed_info",
                              "real_auto_farm","real_game_memory")}
        if not all(checks.values()):
            raise RuntimeError("S132_NATIVE_COMPOSITION_ASSERTIONS_FAILED:"+
                               ",".join(k for k,v in checks.items() if not v))
        e["status"]="PASS_NATIVE_S132_REAL_TK_TRAIN_LAYOUT_CONFIG_NOT_GAME"
    except Exception as exc:
        e["status"]="FAIL_NATIVE_S132"
        e["error_type"]=type(exc).__name__
        e["error_detail"]=str(exc)[:450]
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        (OUT/"native_train_composition.json").write_text(
            json.dumps(e,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        for name,value in e.items():
            print("S132_"+name.upper()+"="+json.dumps(value,ensure_ascii=True))
    return 0 if e["status"].startswith("PASS_NATIVE_") else 1


if __name__=="__main__":
    raise SystemExit(run())
