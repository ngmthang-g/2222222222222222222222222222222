"""S129 Windows native Tk test: original Train config real disk, NOT GAME.

Live HWND and Tk widgets belong to the Windows CI Python process.
A synthetic TEST-ONLY permission proof is never shipped to product.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s129"
OUT.mkdir(parents=True,exist_ok=True)


def run():
    evidence={"status":"NOT_RUN","real_game":False,"real_signed_info":False,
              "real_healing":False,"real_discard":False,"proxy":"EXCLUDED"}
    root=None
    try:
        if os.name!="nt":
            raise RuntimeError("WINDOWS_NATIVE_TK_REQUIRED")
        import tkinter as tk
        from permission_guard import PermissionGuard, VerifiedClaims
        from farm_train_panel import TkFarmTrainSettings
        from farm_train_settings import FarmTrainSettingsStore
        from train_saved_coordinates import FarmCoordinatesStore, FarmCoordinate
        from farm_town_config import FarmTownSettingsStore
        from start_windows import NativeWin32Backend

        with tempfile.TemporaryDirectory(prefix="S129_TRUE_TK_") as td:
            path=Path(td)/"settings.ini"
            original=(b"[Settings]\r\naccount_password = never_edit\r\n"
                      b"[Farm]\r\ntown_condition = cycle\r\n"
                      b"loop_minutes = 30\r\ncoord_1 = Bien Gioi|2|18|32\r\n"
                      b"[Party]\r\nparty_after = wait\r\n")
            path.write_bytes(original)
            store=FarmTrainSettingsStore(path)
            root=tk.Tk()
            root.geometry("880x480+0+0")
            root.update()
            hwnd=int(root.winfo_id())
            native=NativeWin32Backend()
            evidence["native_real_test_owned_hwnd_pid"]=(
                native.is_window(hwnd)
                and native.is_visible(hwnd)
                and native.process_id(hwnd)==os.getpid())
            guard=PermissionGuard()
            panel=TkFarmTrainSettings(root,store=store,
                                      permission_guard=guard,
                                      running_count=lambda:1)
            panel.pack(fill="both",expand=True)
            root.update()
            evidence["original_four_flags_false_and_keep_all"]=(
                all(not v.get() for v in panel.flags.values())
                and panel.pickup_var.get()=="all"
                and panel.heal_var.get()=="Trị liệu Tô Châu"
                and len(panel.pickup_radios)==3)
            evidence["real_original_four_heal_city_and_manual_option"]=(
                "Trị liệu Đại Lý" in panel._heal_values
                and "Trị liệu Lạc Dương" in panel._heal_values
                and "Trị liệu Lâu Lan" in panel._heal_values
                and "Bien Gioi" in panel._heal_values)
            evidence["unsigned_real_widgets_disabled"]=(
                not panel._permitted()
                and all(str(w.cget("state"))=="disabled"
                        for w in panel.checks.values())
                and str(panel.heal_combo.cget("state"))=="disabled"
                and all(str(w.cget("state"))=="disabled"
                        for w in panel.pickup_radios.values()))
            panel.flags["respawn"].set(True)
            blocked=panel._on_flag("respawn")
            evidence["unsigned_manual_callback_cannot_edit_disk"]=(
                not blocked and not store.load().value.respawn)
            guard.receive_token("CI_ONLY_NOT_SIGNED",lambda _:
                VerifiedClaims(frozenset({"farm_tab"}),"active",2))
            panel.reapply_permission()
            evidence["test_only_permission_enables_real_tk_widgets"]=(
                panel._permitted()
                and all(str(w.cget("state"))=="normal"
                        for w in panel.checks.values())
                and str(panel.heal_combo.cget("state"))=="readonly")
            panel.checks["respawn"].invoke()
            panel.checks["auto_reconnect"].invoke()
            panel.checks["pickup_no_cankhon"].invoke()
            panel.checks["trist"].invoke()
            value=store.load().value
            evidence["four_checkbuttons_save_real_Farm_ini"]=(
                value.respawn and value.auto_reconnect
                and value.pickup_no_cankhon and value.trist)
            panel.pickup_radios["weapons"].invoke()
            evidence["original_weapons_keep_preset_only_nonweapon"]=(
                panel.pickup_var.get()=="weapons"
                and store.load().value.pickup_mode=="weapons"
                and store.load().value.pickup_discard_preset_keys()==(
                    "discard_nonweapon",))
            panel.heal_var.set("Trị liệu Đại Lý")
            changed=panel._on_heal_select()
            evidence["true_builtin_heal_selector_persisted"]=(
                changed and store.load().value.heal_map=="Trị liệu Đại Lý")
            panel.heal_var.set("======Có sẵn======")
            sep=panel._on_heal_select()
            evidence["builtin_separator_auto_jumps_to_first_city"]=(
                sep and store.load().value.heal_map=="Trị liệu Đại Lý"
                and panel.heal_var.get()=="Trị liệu Đại Lý")
            panel.heal_var.set("=====Thủ công=====")
            manual=panel._on_heal_select()
            evidence["manual_separator_jumps_to_first_real_preset"]=(
                manual and store.load().value.heal_map=="Bien Gioi")
            # Adding a second saved location through the existing H11 store.
            coordinate=FarmCoordinatesStore(path)
            loaded=coordinate.load().rows
            coordinate.save(loaded+(FarmCoordinate("Bai 2",4,"5","9"),))
            changed_list=panel.refresh_heal_destinations()
            evidence["manual_saved_names_refresh_without_auto_switch"]=(
                changed_list and "Bai 2" in panel._heal_values
                and store.load().value.heal_map=="Bien Gioi")
            # An independent section edit occurred after the last H06-H09
            # save: stale snapshot MUST be rejected, not drop H11 new row.
            panel.pickup_radios["all"].invoke()
            evidence["stale_coordinates_prevent_lost_update"]=(
                store.load().value.pickup_mode=="weapons"
                and b"coord_2 = Bai 2|4|5|9" in path.read_bytes()
                and panel.pickup_var.get()=="weapons")
            # Manually refresh the config snapshot after external H11 edit.
            panel.snapshot=store.load()
            panel.pickup_radios["all"].invoke()
            evidence["after_fresh_read_keep_all_really_saved"]=(
                store.load().value.pickup_mode=="all"
                and store.load().value.pickup_discard_preset_keys()==())
            guard.clear()
            panel.reapply_permission()
            panel.checks["trist"].invoke()
            evidence["revoked_auth_disables_even_direct_callbacks"]=(
                not panel._permitted()
                and str(panel.checks["trist"].cget("state"))=="disabled"
                and store.load().value.trist)
            panel.destroy()
            root.destroy()
            root=None
            contents=path.read_bytes()
            evidence["independent_town_login_party_bytes_preserved"]=(
                b"account_password = never_edit\r\n" in contents
                and b"town_condition = cycle\r\n" in contents
                and b"loop_minutes = 30\r\n" in contents
                and b"party_after = wait\r\n" in contents
                and FarmTownSettingsStore(path).load().value.mode=="cycle")
            backup=tuple(Path(td).glob("settings.????????.ini"))
            evidence["dated_prewrite_backup_holds_original"]=(
                len(backup)==1 and backup[0].read_bytes()==original)
        checks={k:v for k,v in evidence.items()
                if type(v) is bool
                and k not in ("real_game","real_signed_info",
                              "real_healing","real_discard")}
        if not all(checks.values()):
            raise RuntimeError("S129_NATIVE_TRAIN_CHECK_FAILED:"+
                               ",".join(k for k,v in checks.items() if not v))
        evidence["status"]="PASS_NATIVE_S129_ORIGINAL_TRAIN_CONFIG_NOT_GAME"
    except Exception as exc:
        evidence["status"]="FAIL_NATIVE_S129"
        evidence["error_type"]=type(exc).__name__
        evidence["error_detail"]=str(exc)[:400]
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        (OUT/"native_train_config.json").write_text(
            json.dumps(evidence,ensure_ascii=False,indent=2)+"\n",
            encoding="utf-8")
        for key,value in evidence.items():
            print("S129_"+key.upper()+"="+json.dumps(value,ensure_ascii=True))
    return 0 if evidence["status"].startswith("PASS_NATIVE_") else 1


if __name__=="__main__":
    raise SystemExit(run())
