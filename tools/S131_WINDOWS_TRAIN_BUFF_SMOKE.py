"""S131 real Windows Tk Farm buff list/INI proof. NOT GAME OR REAL INFO."""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s131"
OUT.mkdir(parents=True,exist_ok=True)


def run():
    e={"status":"NOT_RUN","real_game":False,"real_signed_info":False,
       "real_buff_key_press":False,"proxy":"EXCLUDED"}
    root=None
    try:
        if os.name!="nt":
            raise RuntimeError("WINDOWS_NATIVE_TK_REQUIRED")
        import tkinter as tk
        from permission_guard import PermissionGuard, VerifiedClaims
        from farm_buff_settings import FarmBuffSettingsStore, BUFF_KEYS
        from farm_buff_editor import TkFarmBuffEditor
        from train_saved_coordinates import FarmCoordinatesStore,FarmCoordinate
        from farm_town_config import FarmTownSettingsStore
        from start_windows import NativeWin32Backend

        with tempfile.TemporaryDirectory(prefix="S131_WINDOWS_BUFF_") as directory:
            path=Path(directory)/"settings.ini"
            original=(b"[Settings]\r\ncredentials = do_not_erase\r\n"
                      b"[Farm]\r\ntown_condition = cycle\r\n"
                      b"respawn = False\r\n"
                      b"coord_1 = Tiem|2|5|6\r\n"
                      b"[Party]\r\nparty_after = wait\r\n")
            path.write_bytes(original)
            store=FarmBuffSettingsStore(path)
            guard=PermissionGuard()
            root=tk.Tk()
            root.geometry("930x540+0+0")
            root.update()
            backend=NativeWin32Backend()
            hwnd=int(root.winfo_id())
            e["real_windows_test_hwnd_pid"]=(
                backend.is_window(hwnd) and backend.is_visible(hwnd)
                and backend.process_id(hwnd)==os.getpid())
            widget=TkFarmBuffEditor(root,store=store,
                                    permission_guard=guard,
                                    running_count=lambda:1)
            widget.pack(fill="x")
            root.update()
            e["original_zero_buff_rows_and_add"]=(
                len(widget.row_widgets)==0 and widget.add_button.cget("text")=="+ Thêm"
                and store.load().rows==())
            e["unauthorized_add_button_disabled"]=(
                str(widget.add_button.cget("state"))=="disabled"
                and not widget.add_local_row()
                and store.load().rows==())
            guard.receive_token("CI_ONLY_NOT_SIGNED",lambda _:
                VerifiedClaims(frozenset({"farm_tab"}),"active",2))
            widget.reapply_permission()
            e["test_only_guard_allows_add"]=(
                widget._permitted()
                and str(widget.add_button.cget("state"))=="normal")
            added=widget.add_local_row()
            e["actual_add_writes_buff_1_config"]=(
                added and len(widget.row_widgets)==1
                and b"buff_1 = False|F1|0|30\r\n" in path.read_bytes())
            e["original_13_hotkey_options_real_readonly_combo"]=(
                tuple(widget.row_widgets[0]["combo"]["values"])==BUFF_KEYS
                and str(widget.row_widgets[0]["combo"].cget("state"))=="readonly")
            e["before_check"]={
                "flag":widget.row_widgets[0]["flag"].get(),
                "widget_state":str(widget.row_widgets[0]["check"].cget("state")),
                "stored_enabled":store.load().rows[0].enabled}
            widget.row_widgets[0]["check"].invoke()
            e["after_check"]={
                "flag":widget.row_widgets[0]["flag"].get(),
                "widget_state":str(widget.row_widgets[0]["check"].cget("state")),
                "stored_enabled":store.load().rows[0].enabled,
                "widget_error":widget.error}
            e["true_checkbox_persists_enabled"]=(
                store.load().rows[0].enabled is True)
            widget.row_widgets[0]["key"].set("F10")
            selected=widget.commit_field(0,"key")
            e["true_hotkey_selection_persists"]=(
                selected and store.load().rows[0].key=="F10")
            widget.row_widgets[0]["minutes"].set("4")
            minute=widget.commit_field(0,"minutes")
            widget.row_widgets[0]["seconds"].set("45")
            second=widget.commit_field(0,"seconds")
            e["real_minutes_seconds_persist_to_same_row"]=(
                minute and second and store.load().rows[0].minutes=="4"
                and store.load().rows[0].seconds=="45")
            widget.row_widgets[0]["seconds"].set("-1")
            rejected=widget.commit_field(0,"seconds")
            e["invalid_seconds_rollback_no_disk_change"]=(
                not rejected and widget.row_widgets[0]["seconds"].get()=="45"
                and store.load().rows[0].seconds=="45")
            second_added=widget.add_local_row()
            e["real_second_row_buff_2_persisted"]=(
                second_added and len(store.load().rows)==2
                and b"buff_2 = False|F1|0|30\r\n" in path.read_bytes())
            deleted=widget.delete_row(0)
            e["deleting_first_row_renumbers_in_actual_ini"]=(
                deleted and len(store.load().rows)==1
                and store.load().rows[0].key=="F1"
                and b"buff_1 = False|F1|0|30\r\n" in path.read_bytes()
                and b"buff_2" not in path.read_bytes())
            # Existing H11 writer takes same shared lock, widget's prior bytes
            # now stale; buff must never clobber a live coordinate edit.
            coords=FarmCoordinatesStore(path)
            prev=coords.load().rows
            coords.save(prev+(FarmCoordinate("Tiem 2",4,"14","30"),))
            widget.row_widgets[0]["minutes"].set("10")
            stale=widget.commit_field(0,"minutes")
            e["concurrent_H11_change_refuses_stale_buff_save"]=(
                not stale and store.load().rows[0].minutes=="0"
                and b"coord_2 = Tiem 2|4|14|30\r\n" in path.read_bytes())
            refreshed=widget.refresh_from_disk()
            widget.row_widgets[0]["minutes"].set("10")
            new_commit=widget.commit_field(0,"minutes")
            e["explicit_reload_allows_safe_real_buff_edit"]=(
                refreshed and new_commit and store.load().rows[0].minutes=="10")
            guard.clear()
            widget.reapply_permission()
            e["revoked_info_disables_all_row_controls"]=(
                not widget._permitted()
                and str(widget.add_button.cget("state"))=="disabled"
                and all(str(row[k].cget("state"))=="disabled"
                        for row in widget.row_widgets
                        for k in ("check","combo","minute","second","delete")))
            widget.row_widgets[0]["minutes"].set("20")
            blocked=widget.commit_field(0,"minutes")
            e["unsigned_direct_edit_after_revoke_does_not_write"]=(
                not blocked and store.load().rows[0].minutes=="10")
            widget.destroy()
            root.destroy()
            root=None
            source=path.read_bytes()
            e["preserved_credentials_town_train_party"]=(
                b"credentials = do_not_erase\r\n" in source
                and b"town_condition = cycle\r\n" in source
                and b"respawn = False\r\n" in source
                and b"party_after = wait\r\n" in source
                and FarmTownSettingsStore(path).load().value.mode=="cycle")
            backups=list(Path(directory).glob("settings.????????.ini"))
            e["date_backup_exact_original_bytes"]=(
                len(backups)==1 and backups[0].read_bytes()==original)
        flags={k:v for k,v in e.items()
               if type(v) is bool and k not in (
                   "real_game","real_signed_info","real_buff_key_press")}
        if not all(flags.values()):
            raise RuntimeError("S131_NATIVE_ASSERTIONS_FAILED:"+
                               ",".join(k for k,v in flags.items() if not v))
        e["status"]="PASS_NATIVE_S131_TRUE_BUFF_CONFIG_NO_GAME"
    except Exception as exc:
        e["status"]="FAIL_NATIVE_S131"
        e["error_type"]=type(exc).__name__
        e["error_detail"]=str(exc)[:440]
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        (OUT/"native_buff_config.json").write_text(
            json.dumps(e,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        for key,v in e.items():
            print("S131_"+key.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if e["status"].startswith("PASS_NATIVE_") else 1


if __name__=="__main__":
    raise SystemExit(run())
