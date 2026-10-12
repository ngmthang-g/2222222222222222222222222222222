"""S171 REAL Windows Tk Train LSV buffs config, no game sender.

Tests actual Tk widgets & INI, preserving original fixed buff_0 unknown
ownership. Uses only test-owned HWND/PID and independent GUI without
TLM original license/heartbeat.
"""
from __future__ import annotations
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s171"
OUT.mkdir(parents=True,exist_ok=True)

def main():
    proof={"status":"NOT_RUN","original_license_issuer":False,
           "actual_game":False,"keyboard_dll_send":False,
           "original_exe_patched":False}
    root=None
    producer=None
    try:
        if os.name!="nt":raise RuntimeError("REQUIRES_NATIVE_WINDOWS")
        import tkinter as tk
        from start_windows import NativeWin32Backend
        from start_polling import StartWindowProducer
        from TLMToolIndependent import make_independent_builders
        from shell import TLMMainApp,INFO_KEY
        from train_lsv_top_tab import TkTrainLsvTopTab
        from train_lsv_manual_buffs import TrainLsvBuffStore
        from train_lsv_top_settings import TrainLsvTopStore
        from train_lsv_coordinates import TrainLsvCoordinatesStore
        from permission_guard import PermissionSnapshot

        with tempfile.TemporaryDirectory(prefix="S171_BUFF_") as td:
            path=Path(td)/"settings.ini"
            original=(b"[Login]\r\npassword = sensitive\r\n"
                 b"[Farm]\r\ntown_condition = cycle\r\n"
                 b"[TrainLSV]\r\nrespawn = False\r\n"
                 b"buff_0 = True|1|0|5\r\n"
                 b"buff_8 = future_legacy|opaque\r\n"
                 b"coord_3 = LSV|10014|11|22\r\n"
                 b"acc_Test_train = LSV\r\n"
                 b"[Party]\r\nmode = keep\r\n")
            path.write_bytes(original)
            root=tk.Tk()
            producer=StartWindowProducer(
                backend_factory=NativeWin32Backend,
                interval_seconds=0.1,join_timeout=1.0)
            app=TLMMainApp(root,make_independent_builders(path,producer),
                           independent_mode=True,local_window_count=lambda:0)
            app.position_window_top_right()
            root.update()
            native=NativeWin32Backend()
            hwnd=int(root.winfo_id())
            proof["real_tk_hwnd_pid"]=(
                hwnd>0 and native.is_window(hwnd)
                and native.process_id(hwnd)==os.getpid())
            app.notebook.select(app._tab_frames["trainlsv_tab"])
            root.update()
            tab=app.lifecycle._instances.get("trainlsv_tab")
            editor=tab.manual_buffs
            proof["real_lsv_buff_panel_without_license"]=(
                isinstance(tab,TkTrainLsvTopTab)
                and editor.snapshot is not None
                and set(editor.row_widgets)=={0,8}
                and editor.session_owned=={}
                and editor.add_btn.instate(("!disabled",)))
            draft=editor.add_draft()
            root.update()
            proof["native_tk_dynamic_row_original_defaults"]=(
                draft is not None and not draft["enabled"].get()
                and draft["key"].get()=="1"
                and draft["minutes"].get()=="0"
                and draft["seconds"].get()=="5")
            draft["enabled"].set(True)
            draft["key"].set("F10")
            draft["minutes"].set("2")
            draft["seconds"].set("15")
            draft["save"].invoke()
            root.update()
            state=TrainLsvBuffStore(path).load()
            proof["original_schema_real_disk_append_no_collision"]=(
                len(state.rows)==3
                and state.rows[-1].number==9
                and state.rows[-1].enabled
                and state.rows[-1].key=="F10"
                and state.rows[-1].minutes=="2"
                and state.rows[-1].seconds=="15"
                and editor.session_owned.get(9)=="True|F10|2|15")
            # Parent top control must observe new bytes, and the S170
            # saved-coordinate editor must keep the same snapshot.
            tab.flags["respawn"].set(True)
            ok=tab._on_flag("respawn")
            root.update()
            proof["S169_top_config_and_S170_coords_coexist"]=(
                ok and TrainLsvTopStore(path).load().value.respawn
                and len(TrainLsvCoordinatesStore(path).load().rows)==1
                and editor.snapshot.file_bytes==path.read_bytes()
                and tab.coords.snapshot.file_bytes==path.read_bytes())
            # Protect original ambiguous buff_0 and unknown buff_8;
            # delete only row added via live UI this session.
            proof["legacy_fixed_unknown_row_not_deletable"]=(
                not editor.delete_owned(0)
                and not editor.delete_owned(8))
            proof["new_session_row_deleted_without_legacy_damage"]=(
                editor.delete_owned(9) and
                {r.number for r in TrainLsvBuffStore(path).load().rows}=={0,8})
            saved=path.read_bytes()
            proof["unknown_credentials_and_original_buff_bytes_preserved"]=(
                b"password = sensitive\r\n" in saved
                and b"town_condition = cycle\r\n" in saved
                and b"buff_0 = True|1|0|5\r\n" in saved
                and b"buff_8 = future_legacy|opaque\r\n" in saved
                and b"coord_3 = LSV|10014|11|22\r\n" in saved
                and b"acc_Test_train = LSV\r\n" in saved
                and b"mode = keep\r\n" in saved)
            app.apply_info_snapshot(PermissionSnapshot())
            app.apply_verified_permissions(set(),blocked=True)
            root.update()
            proof["original_license_revocation_cannot_hide_new_buff_panel"]=(
                app.lifecycle.current=="trainlsv_tab"
                and "trainlsv_tab" in app.lifecycle.visible
                and editor.add_btn.instate(("!disabled",)))
            app.notebook.select(app._tab_frames[INFO_KEY])
            root.update()
            proof["tab_switch_no_ambient_game_worker"]=(
                app.lifecycle.current==INFO_KEY
                and not producer.active)
            app.shutdown()
            root.destroy()
            root=None
        flags={k:v for k,v in proof.items() if type(v) is bool
            and k not in ("original_license_issuer","actual_game",
                          "keyboard_dll_send","original_exe_patched")}
        if not all(flags.values()):
            raise RuntimeError("S171_NATIVE_FAIL:"+",".join(
                k for k,v in flags.items() if not v))
        proof["status"]="PASS_NATIVE_S171_MANUAL_LSV_BUFF_CONFIG_NO_GAME"
    except Exception as exc:
        proof["status"]="FAILED_S171"
        proof["error_type"]=type(exc).__name__
        proof["error_detail"]=str(exc)[:700]
    finally:
        if producer is not None:
            try:producer.stop()
            except Exception:pass
        if root is not None:
            try:root.destroy()
            except Exception:pass
        (OUT/"native_manual_buff.json").write_text(
            json.dumps(proof,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        for k,v in proof.items():
            print("S171_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if proof["status"].startswith("PASS_NATIVE_") else 1

if __name__=="__main__":
    raise SystemExit(main())
