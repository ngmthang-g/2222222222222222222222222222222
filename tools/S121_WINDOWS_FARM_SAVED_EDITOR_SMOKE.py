"""S121 actual Windows Tk existing saved Farm rows + real disk edit/delete."""
from __future__ import annotations
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s121"
OUT.mkdir(parents=True,exist_ok=True)

def run():
    result={"task":"S121","status":"NOT_RUN","game_run":False,
            "actual_game_info":"UNAVAILABLE","proxy":"EXCLUDED"}
    root=None
    try:
        if os.name!="nt":
            raise RuntimeError("WINDOWS_TK_REQUIRED")
        import tkinter as tk
        from train_saved_coordinates import FarmCoordinatesStore,FarmCoordinate
        from farm_saved_editor import FarmSavedCoordinatesEditor
        with tempfile.TemporaryDirectory(prefix="S121_FARM_COORD_TEST_") as td:
            p=Path(td)/"settings.ini"
            original=b"[Settings]\r\naccounts = TEST_NO_REAL_PASSWORD\r\n[Farm]\r\nkeep = yes\r\n"
            p.write_bytes(original)
            store=FarmCoordinatesStore(p)
            store.save((FarmCoordinate("A",26,"1","2"),FarmCoordinate("B",86,"3","4")))
            root=tk.Tk()
            root.geometry("800x680+0+0")
            editor=FarmSavedCoordinatesEditor(root,store=store)
            editor.pack(fill="both",expand=True)
            root.update()
            result["two_real_existing_rows"]=len(editor.row_widgets)==2
            result["true_map_combobox_from_original_72"]=(
                len(editor.row_widgets[0]["combo"]["values"])==72)
            result["initial_visible_toggle"]=editor._body_visible
            result["actual_hide_header_body_toolbar_stays"]=(
                not editor.toggle_list() and
                not editor._header.winfo_manager() and
                not editor._body.winfo_manager() and
                bool(editor._toolbar.winfo_manager()))
            result["actual_show_again"]=editor.toggle_list() and bool(editor._body.winfo_manager())
            # Explicit Return -> real disk commit of edited preset, new TLM ID.
            editor.row_widgets[0]["name"].set("A-renamed")
            editor.row_widgets[0]["x"].set("11")
            editor.row_widgets[0]["map"].set("Kính Hồ")
            result["real_tk_edit_commit_disk"]=(
                editor.commit_row(0) and
                store.load().rows[0]==FarmCoordinate("A-renamed",30,"11","2"))
            # Choose the first original separator by actual index.
            combo=editor.row_widgets[0]["combo"]
            combo.current(4)
            result["original_separator_skips_to_real_next_map"]=(
                editor._select_map(0) and
                editor.row_widgets[0]["map"].get()=="Phó Bản-Thiên Sơn"
                and store.load().rows[0].map_id==1300)
            before=p.read_bytes()
            # externally saved change: editor must not clobber later file update
            modified=(FarmCoordinate("A-renamed",1300,"11","2"),
                      FarmCoordinate("External",86,"3","4"))
            store.save(modified)
            editor.row_widgets[0]["y"].set("999")
            result["stale_disk_refuses_ui_write"]=(
                not editor.commit_row(0) and
                store.load().rows==modified)
            # restore old editor, recreate -> do real delete
            editor.destroy()
            editor=FarmSavedCoordinatesEditor(root,store=store)
            editor.pack(fill="both",expand=True)
            root.update()
            result["real_tk_delete_disk"]=(
                editor.delete_row(0) and
                store.load().rows==(FarmCoordinate("External",86,"3","4"),))
            result["unrelated_settings_bytes_preserved"]=(
                b"accounts = TEST_NO_REAL_PASSWORD\r\n" in p.read_bytes()
                and b"keep = yes\r\n" in p.read_bytes())
            editor.destroy()
            root.destroy()
            root=None
            # Retired stored map blocks edit and prevents data loss.
            p.write_bytes(b"[Farm]\ncoord_1 = Retired|2600|1|2\ncoord_2 = Kept|26|3|4\n")
            root=tk.Tk()
            blocked=FarmSavedCoordinatesEditor(root,store=store)
            blocked.pack()
            root.update()
            raw=p.read_bytes()
            result["retired_map_blocks_all_mutations"]=(
                blocked._blocked and not blocked.commit_row(0)
                and not blocked.delete_row(0) and p.read_bytes()==raw)
            blocked.destroy()
            root.destroy()
            root=None
        checks=[k for k,v in result.items() if type(v) is bool and k!="game_run"]
        if not all(result[k] for k in checks):
            raise RuntimeError("S121_REAL_TK_FAIL")
        result["status"]="PASS_NATIVE_S121_FARM_EXISTING_PRESETS_TRUE_TK_DISK_NO_GAME"
    except Exception as exc:
        result["status"]="FAIL_NATIVE_S121"
        result["error_type"]=type(exc).__name__
    finally:
        if root is not None:
            try: root.destroy()
            except Exception: pass
        (OUT/"windows_farm_existing_editor.json").write_text(
            json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        for k,v in result.items():
            print("S121_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if result["status"].startswith("PASS_NATIVE_S121_") else 1

if __name__=="__main__":
    raise SystemExit(run())
