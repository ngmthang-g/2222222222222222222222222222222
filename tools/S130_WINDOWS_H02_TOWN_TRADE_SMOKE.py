"""S130 real Windows HWND/Tk, real original H02 hidden town trade INI smoke.

This tests test-owned Tk/UI, TEST ONLY synthetic PermissionGuard claims, and
real byte-preserving settings.ini IO. NO game, NPCShop or actual signing.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s130"
OUT.mkdir(parents=True,exist_ok=True)


def run():
    q={"status":"NOT_RUN","real_game":False,"real_signed_info":False,
       "real_sell_or_buy":False,"proxy":"EXCLUDED"}
    root=None
    try:
        if os.name!="nt":
            raise RuntimeError("WINDOWS_REAL_TK_REQUIRED")
        import tkinter as tk
        from permission_guard import PermissionGuard,VerifiedClaims
        from start_windows import NativeWin32Backend
        from farm_town_panel import TkFarmTownConfig
        from farm_town_trade_panel import TkFarmTownTradeSettings
        from farm_town_trade_settings import TownTradeStore,SELL_MAP_LIST
        from farm_town_config import FarmTownSettingsStore
        from farm_train_settings import FarmTrainSettingsStore
        from train_saved_coordinates import FarmCoordinate,FarmCoordinatesStore

        with tempfile.TemporaryDirectory(prefix="S130_NATIVE_TOWN_") as directory:
            path=Path(directory)/"settings.ini"
            original=(b"[Settings]\r\naccount = keep_private\r\n"
                      b"[Farm]\r\ntown_condition = cycle\r\n"
                      b"loop_minutes = 30\r\npickup_mode = all\r\n"
                      b"coord_1 = Tiem 1|2|14|21\r\n"
                      b"[Party]\r\nparty_after = wait\r\n")
            path.write_bytes(original)
            guard=PermissionGuard()
            root=tk.Tk()
            root.geometry("1000x740+0+0")
            root.update()
            backend=NativeWin32Backend()
            hwnd=int(root.winfo_id())
            q["real_windows_test_owned_hwnd_pid"]=(
                backend.is_window(hwnd) and backend.is_visible(hwnd)
                and backend.process_id(hwnd)==os.getpid())
            s128=TkFarmTownConfig(root,store=FarmTownSettingsStore(path),
                                   permission_guard=guard,
                                   running_count=lambda:1)
            s128.pack(fill="x")
            store=TownTradeStore(path)
            panel=TkFarmTownTradeSettings(
                s128.lower,store=store,permission_guard=guard,
                running_count=lambda:1)
            panel.pack(fill="x")
            root.update()
            q["original_lower_town_body_starts_hidden"]=(
                not s128._body_visible
                and not bool(s128.lower.winfo_manager()))
            q["original_town_selling_HPMPO_choices"]=(
                len(panel.widgets)==10
                and tuple(panel.widgets["hp_item"]["values"])==(
                    "Hành huyết tán","Hoạt huyết tán","Kim sang dược")
                and tuple(panel.widgets["mp_item"]["values"])==(
                    "Hành khí tán","Hoài linh đan","Qui linh hoàn")
                and tuple(panel.widgets["sell_map"]["values"])[:4]==SELL_MAP_LIST
                and "Tiem 1" in panel.destination_choices)
            q["not_authorized_real_widgets_disabled"]=(
                not panel._permitted()
                and all(str(w.cget("state"))=="disabled"
                        for w in panel.widgets.values()))
            panel.vars["buy_hp"].set(True)
            refused=panel._on_flag("buy_hp")
            q["direct_unsigned_callback_cannot_save"]=(
                not refused and not store.load().value.buy_hp)
            guard.receive_token("TEST_ONLY_NOT_REAL_SIGNED_INFO",lambda _:
                VerifiedClaims(frozenset({"farm_tab"}),"active",2))
            s128.reapply_permission()
            panel.reapply_permission()
            q["test_only_guard_allows_visible_hidden_town_settings"]=(
                panel._permitted()
                and str(panel.widgets["buy_hp"].cget("state"))=="normal"
                and str(panel.widgets["hp_item"].cget("state"))=="readonly"
                and s128.toggle_lower_body()
                and bool(s128.lower.winfo_manager()))
            panel.widgets["sell_equip"].invoke()
            panel.widgets["buy_hp"].invoke()
            panel.widgets["buy_mp"].invoke()
            val=store.load().value
            q["real_three_sale_potion_checkboxes_persisted"]=(
                val.sell_equip and val.buy_hp and val.buy_mp)
            panel.vars["sell_map"].set("Tô Châu")
            s1=panel._on_select("sell_map")
            panel.vars["meds_map"].set("Tiem 1")
            s2=panel._on_select("meds_map")
            panel.vars["hp_item"].set("Kim sang dược")
            h=panel._on_select("hp_item")
            panel.vars["mp_item"].set("Qui linh hoàn")
            m=panel._on_select("mp_item")
            val=store.load().value
            q["real_builtins_and_manual_destination_and_items_persisted"]=(
                s1 and s2 and h and m and val.sell_map=="Tô Châu"
                and val.meds_map=="Tiem 1" and val.hp_item=="Kim sang dược"
                and val.mp_item=="Qui linh hoàn")
            panel.vars["sell_tab"].set("4")
            k=panel._on_numeric("sell_tab")
            panel.vars["hp_qty"].set("60")
            p=panel._on_numeric("hp_qty")
            panel.vars["mp_qty"].set("80")
            t=panel._on_numeric("mp_qty")
            val=store.load().value
            q["real_numeric_keep_and_HP_MP_quantities_persisted"]=(
                k and p and t and val.sell_tab=="4"
                and val.hp_qty=="60" and val.mp_qty=="80")
            panel.vars["hp_qty"].set("-1")
            invalid=panel._on_numeric("hp_qty")
            q["invalid_numeric_restored_no_save"]=(
                not invalid and panel.vars["hp_qty"].get()=="60"
                and store.load().value.hp_qty=="60")
            # A different existing H11 component updates stored coords while
            # widget still holds its prior file snapshot. Refuse lost update.
            coords=FarmCoordinatesStore(path)
            loaded=coords.load().rows
            coords.save(loaded+(FarmCoordinate("Tiem 2",4,"22","41"),))
            fresh_options=panel.refresh_destinations()
            q["real_H11_coordinate_refresh_without_auto_switch"]=(
                fresh_options and "Tiem 2" in panel.destination_choices
                and store.load().value.meds_map=="Tiem 1")
            panel.vars["sell_tab"].set("5")
            stale=panel._on_numeric("sell_tab")
            q["stale_prior_snapshot_cannot_erase_H11_coordinate"]=(
                not stale and panel.vars["sell_tab"].get()=="4"
                and b"coord_2 = Tiem 2|4|22|41" in path.read_bytes()
                and store.load().value.sell_tab=="4")
            panel.snapshot=store.load()
            panel.vars["meds_map"].set("Tiem 2")
            chosen=panel._on_select("meds_map")
            q["refreshed_second_real_manual_coordinates_save"]=(
                chosen and store.load().value.meds_map=="Tiem 2")
            guard.clear()
            s128.reapply_permission()
            panel.reapply_permission()
            panel.vars["sell_equip"].set(False)
            revoked=panel._on_flag("sell_equip")
            q["info_revoke_disables_real_controls_and_direct_calls"]=(
                not revoked and store.load().value.sell_equip
                and all(str(w.cget("state"))=="disabled"
                        for w in panel.widgets.values()))
            panel.destroy()
            s128.destroy()
            root.destroy()
            root=None
            contents=path.read_bytes()
            q["all_older_other_tab_bytes_preserved"]=(
                b"account = keep_private\r\n" in contents
                and b"town_condition = cycle\r\n" in contents
                and b"loop_minutes = 30\r\n" in contents
                and b"pickup_mode = all\r\n" in contents
                and b"party_after = wait\r\n" in contents
                and FarmTownSettingsStore(path).load().value.mode=="cycle"
                and FarmTrainSettingsStore(path).load().value.pickup_mode=="all")
            backup=tuple(Path(directory).glob("settings.????????.ini"))
            q["true_prior_content_backup_unchanged"]=(
                len(backup)==1 and backup[0].read_bytes()==original)
        checks={k:v for k,v in q.items()
                if type(v) is bool and k not in (
                    "real_game","real_signed_info","real_sell_or_buy")}
        if not all(checks.values()):
            raise RuntimeError("S130_NATIVE_CHECK_FAIL:"+",".join(
                k for k,v in checks.items() if not v))
        q["status"]="PASS_NATIVE_S130_ORIGINAL_TOWN_TRADE_CONFIG_NO_GAME"
    except Exception as exc:
        q["status"]="FAIL_NATIVE_S130"
        q["error_type"]=type(exc).__name__
        q["error_detail"]=str(exc)[:380]
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        (OUT/"native_town_trade.json").write_text(
            json.dumps(q,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        for key,val in q.items():
            print("S130_"+key.upper()+"="+json.dumps(val,ensure_ascii=True))
    return 0 if q["status"].startswith("PASS_NATIVE_") else 1


if __name__=="__main__":
    raise SystemExit(run())
