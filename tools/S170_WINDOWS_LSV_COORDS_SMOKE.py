"""S170 native Win64 Tk/INI I10 coordinate-editor smoke; no real game.

Verifies REAL local GUI Entry/Combobox/Buttons in the independent TLMTool
with native Windows HWND/PID, real atomic INI updates and legacy Info
revocation isolation. Does NOT click any game-control buttons.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s170"
OUT.mkdir(parents=True,exist_ok=True)

def main():
    proof={"status":"NOT_RUN","actual_game":False,
           "original_issuer":False,"original_tlm_patched":False,
           "gameplay_controls_verified":False}
    root=None
    producer=None
    try:
        if os.name!="nt":
            raise RuntimeError("REAL_WIN64_TK_REQUIRED")
        import tkinter as tk
        from start_windows import NativeWin32Backend
        from start_polling import StartWindowProducer
        from TLMToolIndependent import make_independent_builders
        from shell import TLMMainApp, INFO_KEY
        from train_lsv_top_tab import TkTrainLsvTopTab
        from train_lsv_coordinates import TrainLsvCoordinatesStore
        from train_lsv_top_settings import TrainLsvTopStore
        from permission_guard import PermissionSnapshot

        with tempfile.TemporaryDirectory(prefix="S170_COORD_EDITOR_") as td:
            path=Path(td)/"settings.ini"
            original=(b"[Login]\r\npassword = SENSITIVE_UNCHANGED\r\n"
                      b"[Farm]\r\ncoord_1 = FarmOnly|2|7|8\r\n"
                      b"[TrainLSV]\r\nrespawn = False\r\n"
                      b"coord_6 = OldLSV|10014|11|22\r\n"
                      b"coord_9 = Retired|19999|3|4\r\n"
                      b"buff_0 = True|1|0|5\r\n"
                      b"[Party]\r\nparty_after = wait\r\n")
            path.write_bytes(original)
            root=tk.Tk()
            producer=StartWindowProducer(backend_factory=NativeWin32Backend,
                                         interval_seconds=0.10,join_timeout=1.0)
            app=TLMMainApp(root,make_independent_builders(path,producer),
                           independent_mode=True,local_window_count=lambda:0)
            app.position_window_top_right()
            root.update()
            hwnd=int(root.winfo_id())
            native=NativeWin32Backend()
            proof["real_test_owned_hwnd_pid"]=(
                hwnd>0 and native.is_window(hwnd)
                and native.process_id(hwnd)==os.getpid())
            proof["lsv_tab_visible_without_original_license"]=(
                "trainlsv_tab" in app.lifecycle.visible
                and "trainlsv_tab" not in app.lifecycle._instances)
            app.notebook.select(app._tab_frames["trainlsv_tab"])
            root.update()
            lsv=app.lifecycle._instances.get("trainlsv_tab")
            editor=lsv.coords
            proof["real_saved_coord_controls_and_retired_skip"]=(
                isinstance(lsv,TkTrainLsvTopTab)
                and 6 in editor.rows and 9 not in editor.rows
                and editor.snapshot.skipped_retired==(19999,)
                and editor.add_btn.cget("state")=="normal"
                and editor.toggle_btn.winfo_exists())
            # Genuine Tk StringVars, Entry and ttk Buttons. Save only the
            # proven original [TrainLSV] record; no game movement invoked.
            draft=editor._make_row(None)
            draft["name"].set("New LSV")
            draft["map"].set("Khô Vinh Đạo")
            draft["x"].set("35")
            draft["y"].set("70")
            draft["save"].invoke()
            root.update()
            on_disk=TrainLsvCoordinatesStore(path).load()
            proof["native_tk_add_real_ini_local_map_id"]=(
                any(r.name=="New LSV" and r.map_id==10007
                    and r.x=="35" and r.y=="70" for r in on_disk.rows)
                and len(on_disk.rows)==2)
            new_id=next(r.key_number for r in on_disk.rows if r.name=="New LSV")
            # Update top settings independently; the coordinate editor's
            # expected_bytes should be resynchronized, not overwrite it.
            lsv.flags["respawn"].set(True)
            proof["top_config_safe_after_coord_save"]=(
                lsv._on_flag("respawn")
                and TrainLsvTopStore(path).load().value.respawn
                and editor.snapshot.file_bytes==path.read_bytes())
            item=editor.rows[new_id]
            item["name"].set("Renamed LSV")
            item["x"].set("40")
            item["save"].invoke()
            root.update()
            on_disk=TrainLsvCoordinatesStore(path).load()
            proof["edit_preserves_original_coord_key_and_toplevel"]=(
                any(r.key_number==new_id and r.name=="Renamed LSV"
                    and r.x=="40" for r in on_disk.rows)
                and TrainLsvTopStore(path).load().value.respawn)
            editor._toggle_list()
            proof["hide_only_body_toolbar_visible"]=(
                not bool(editor.content.winfo_manager())
                and bool(editor.add_btn.master.winfo_manager()))
            editor._toggle_list()
            proof["show_body_without_recreating_settings"]=(
                bool(editor.content.winfo_manager())
                and new_id in editor.rows)
            editor.rows[new_id]["delete"].invoke()
            root.update()
            on_disk=TrainLsvCoordinatesStore(path).load()
            proof["delete_does_not_renumber_other_presets"]=(
                new_id not in {r.key_number for r in on_disk.rows}
                and any(r.key_number==6 for r in on_disk.rows))
            data=path.read_bytes()
            proof["retired_unknown_and_other_settings_bytes_untouched"]=(
                b"coord_9 = Retired|19999|3|4\r\n" in data
                and b"coord_6 = OldLSV|10014|11|22\r\n" in data
                and b"[Farm]\r\ncoord_1 = FarmOnly|2|7|8\r\n" in data
                and b"password = SENSITIVE_UNCHANGED\r\n" in data
                and b"buff_0 = True|1|0|5\r\n" in data
                and b"party_after = wait\r\n" in data)
            app.apply_info_snapshot(PermissionSnapshot())
            app.apply_verified_permissions(set(),blocked=True)
            root.update()
            proof["original_license_revoke_cannot_hide_local_editor"]=(
                app.lifecycle.current=="trainlsv_tab"
                and "trainlsv_tab" in app.lifecycle.visible
                and not editor._blocked)
            app.notebook.select(app._tab_frames[INFO_KEY])
            root.update()
            proof["tab_change_no_game_worker_or_farm_action"]=(
                app.lifecycle.current==INFO_KEY and not producer.active)
            app.shutdown()
            root.destroy()
            root=None
        flags={k:v for k,v in proof.items()
               if type(v) is bool and k not in (
                   "actual_game","original_issuer","original_tlm_patched",
                   "gameplay_controls_verified")}
        if not all(flags.values()):
            raise RuntimeError("S170_NATIVE_FAIL:"+",".join(k for k,v in flags.items() if not v))
        proof["status"]="PASS_NATIVE_S170_REAL_TK_TRAINLSV_COORDS_PERSISTENCE_NOT_GAME"
    except Exception as exc:
        proof["status"]="FAILED_S170"
        proof["error_type"]=type(exc).__name__
        proof["error_detail"]=str(exc)[:750]
    finally:
        if producer is not None:
            try:producer.stop()
            except Exception:pass
        if root is not None:
            try:root.destroy()
            except Exception:pass
        (OUT/"native_lsv_coordinates.json").write_text(
            json.dumps(proof,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        for k,v in proof.items():
            print("S170_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if proof["status"].startswith("PASS_NATIVE_") else 1

if __name__=="__main__":
    raise SystemExit(main())
