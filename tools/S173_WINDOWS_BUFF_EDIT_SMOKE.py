"""S173 Win64 native Tk test of editable SAME-SESSION LSV manual buffs.

Physical test-owned Tk HWND/PID, actual independent GUI and settings.ini
writes. Existing buff_0/opaque legacy rows NEVER become editable.
No original Info issuer, no actual game keyboard input, no fake player.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s173"
OUT.mkdir(parents=True,exist_ok=True)


def main():
    proof={"status":"NOT_RUN","actual_game":False,"original_issuer":False,
           "game_key_dispatch":False,"original_tlm_exe_modified":False}
    root=None
    producer=None
    try:
        if os.name!="nt":
            raise RuntimeError("REQUIRES_REAL_WINDOWS_TK")
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

        with tempfile.TemporaryDirectory(prefix="S173_BUFF_EDIT_") as folder:
            path=Path(folder)/"settings.ini"
            original=(
                b"[Login]\r\npassword = KEEP_SECRET\r\n"
                b"[Farm]\r\ntown_condition = cycle\r\n"
                b"[TrainLSV]\r\nrespawn = False\r\n"
                b"heal_map = LEGACY_UNUSED\r\n"
                b"buff_0 = True|1|0|5\r\n"
                b"buff_8 = opaque_future_format\r\n"
                b"coord_3 = LSV|10014|11|22\r\n"
                b"acc_Future_train = UNKNOWN\r\n"
                b"[Party]\r\nmode = KEEP\r\n")
            path.write_bytes(original)
            root=tk.Tk()
            producer=StartWindowProducer(backend_factory=NativeWin32Backend,
                    interval_seconds=0.1,join_timeout=1.0)
            app=TLMMainApp(root,make_independent_builders(path,producer),
                           independent_mode=True,local_window_count=lambda:0)
            app.position_window_top_right()
            root.update()
            native=NativeWin32Backend()
            hwnd=int(root.winfo_id())
            proof["physical_test_owned_hwnd_pid"]=(
                hwnd>0 and native.is_window(hwnd)
                and native.process_id(hwnd)==os.getpid())
            app.notebook.select(app._tab_frames["trainlsv_tab"])
            root.update()
            tab=app.lifecycle._instances["trainlsv_tab"]
            buff=tab.manual_buffs
            proof["true_independent_lsv_tab_and_protected_prior_rows"]=(
                isinstance(tab,TkTrainLsvTopTab)
                and buff.session_owned=={}
                and not buff.edit_owned(0)
                and not buff.edit_owned(8)
                and set(buff.row_widgets)=={0,8})
            draft=buff.add_draft()
            draft["enabled"].set(True)
            draft["key"].set("F3")
            draft["minutes"].set("2")
            draft["seconds"].set("15")
            draft["save"].invoke()
            root.update()
            state=TrainLsvBuffStore(path).load()
            number=next(r.number for r in state.rows if r.number not in (0,8))
            proof["real_tk_added_row_on_disk_with_original_syntax"]=(
                number==9 and buff.session_owned.get(number)=="True|F3|2|15"
                and b"buff_9 = True|F3|2|15\r\n" in state.file_bytes)
            edit=buff.edit_owned(number)
            proof["real_tk_edit_controls_only_in_own_session"]=(
                edit is not None and edit["key"].get()=="F3"
                and edit["minutes"].get()=="2"
                and edit["seconds"].get()=="15")
            edit["key"].set("F10")
            edit["minutes"].set("4")
            edit["seconds"].set("17")
            edit["enabled"].set(False)
            edit["save"].invoke()
            root.update()
            after=TrainLsvBuffStore(path).load()
            proof["real_native_edit_persists_exact_same_index_no_legacy_overwrite"]=(
                b"buff_9 = False|F10|4|17\r\n" in after.file_bytes
                and buff.session_owned.get(number)=="False|F10|4|17"
                and b"buff_0 = True|1|0|5\r\n" in after.file_bytes
                and b"buff_8 = opaque_future_format\r\n" in after.file_bytes)
            tab.flags["respawn"].set(True)
            ok=tab._on_flag("respawn")
            root.update()
            proof["top_and_coordinate_other_snapshots_coexist"]=(
                ok and TrainLsvTopStore(path).load().value.respawn
                and len(TrainLsvCoordinatesStore(path).load().rows)==1
                and buff.snapshot.file_bytes==path.read_bytes()
                and tab.coords.snapshot.file_bytes==path.read_bytes())
            proof["protect_old_rows_even_after_new_edit"]=(
                buff.edit_owned(0) is None
                and buff.edit_owned(8) is None
                and not buff.delete_owned(0))
            proof["in_session_edited_record_still_deletable"]=(
                buff.delete_owned(number)
                and {r.number for r in TrainLsvBuffStore(path).load().rows}=={0,8})
            data=path.read_bytes()
            proof["fixed_heal_map_and_unrelated_secret_sections_exact"]=(
                b"heal_map = LEGACY_UNUSED\r\n" in data
                and b"password = KEEP_SECRET\r\n" in data
                and b"town_condition = cycle\r\n" in data
                and b"coord_3 = LSV|10014|11|22\r\n" in data
                and b"acc_Future_train = UNKNOWN\r\n" in data
                and b"mode = KEEP\r\n" in data)
            app.apply_info_snapshot(PermissionSnapshot())
            app.apply_verified_permissions(set(),blocked=True)
            root.update()
            proof["old_license_revocation_does_not_hide_new_config"]=(
                app.lifecycle.current=="trainlsv_tab"
                and buff.add_btn.instate(("!disabled",)))
            app.notebook.select(app._tab_frames[INFO_KEY])
            root.update()
            proof["no_background_game_work_after_leave"]=(
                app.lifecycle.current==INFO_KEY and not producer.active)
            app.shutdown()
            root.destroy();root=None
        actuals={k:v for k,v in proof.items() if type(v) is bool and k not in
                 ("actual_game","original_issuer","game_key_dispatch",
                  "original_tlm_exe_modified")}
        if not all(actuals.values()):
            raise RuntimeError("CHECKS_FAILED:"+",".join(k for k,v in actuals.items() if not v))
        proof["status"]="PASS_NATIVE_S173_IN_SESSION_LSV_BUFF_EDIT_INI_TK_NOT_GAME"
    except Exception as exc:
        proof["status"]="FAILED_S173"
        proof["error_type"]=type(exc).__name__
        proof["error_detail"]=str(exc)[:850]
    finally:
        if producer is not None:
            try:producer.stop()
            except Exception:pass
        if root is not None:
            try:root.destroy()
            except Exception:pass
        (OUT/"native_buff_edit.json").write_text(
            json.dumps(proof,ensure_ascii=False,indent=2)+"\n",
            encoding="utf-8")
        for k,v in proof.items():
            print("S173_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if proof["status"].startswith("PASS_NATIVE_") else 1

if __name__=="__main__":
    raise SystemExit(main())
