"""S122 actual Windows Tk Sell/Farm combobox selections and disk."""
import os,sys,json,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
ART=ROOT/"artifacts"/"s122";ART.mkdir(parents=True,exist_ok=True)
def run():
    q={"status":"NOT_RUN","game_started":False,"proxy":"EXCLUDED"}
    root=None
    try:
        if os.name!="nt":raise RuntimeError("WINDOWS_REQUIRED")
        import tkinter as tk
        from tkinter import ttk
        from train_saved_coordinates import FarmCoordinate,FarmCoordinatesStore
        from farm_saved_editor import FarmSavedCoordinatesEditor
        with tempfile.TemporaryDirectory(prefix="S122_NATIVE_TK_") as td:
            p=Path(td)/"settings.ini"
            p.write_bytes(b"[Settings]\r\naccounts = untouched\r\n[Farm]\r\nkeep = yes\r\n")
            store=FarmCoordinatesStore(p)
            store.save([FarmCoordinate("A",26,"1","2"),FarmCoordinate("B",86,"3","4")])
            root=tk.Tk()
            editor=FarmSavedCoordinatesEditor(root,store=store);editor.pack()
            frame=ttk.Frame(root);frame.pack()
            s1,f1,s2,f2=[ttk.Combobox(frame,state="readonly") for _ in range(4)]
            for w in (s1,f1,s2,f2):w.pack()
            root.update()
            q["buttons_disabled_without_account"]=all(
                w.instate(["disabled"]) for row in editor.row_widgets
                for w in (row["apply_sell"],row["apply_train"]))
            editor.register_account_combos(s1,f1)
            editor.register_account_combos(s2,f2)
            root.update()
            q["true_ban_train_buttons_enabled"]=all(
                not w.instate(["disabled"]) for row in editor.row_widgets
                for w in (row["apply_sell"],row["apply_train"]))
            q["true_real_combo_choices"]=all(tuple(w["values"])==("A","B") for w in (s1,f1,s2,f2))
            s1.set("A");f1.set("A");s2.set("B");f2.set("B")
            editor.row_widgets[0]["name"].set("A-Renamed")
            q["name_disk_and_active_choices_renamed"]=(
                editor.commit_row(0) and s1.get()==f1.get()=="A-Renamed"
                and s2.get()==f2.get()=="B"
                and tuple(f2["values"])==("A-Renamed","B")
                and store.load().rows[0].name=="A-Renamed")
            editor.row_widgets[1]["apply_sell"].invoke()
            q["real_ban_button_applies_all_account_name_only"]=(
                s1.get()==s2.get()=="B" and f1.get()=="A-Renamed" and f2.get()=="B")
            editor.row_widgets[0]["apply_train"].invoke()
            q["real_train_button_applies_all_account_name_only"]=(
                f1.get()==f2.get()=="A-Renamed" and s1.get()==s2.get()=="B")
            q["stale_name_ignored"]=(
                not editor.account_bindings.restore_if_known(f1,"Deleted")
                and f1.get()=="A-Renamed")
            q["real_delete_updates_option_lists"]=(
                editor.delete_row(1) and tuple(s1["values"])==tuple(f2["values"])==("A-Renamed",)
                and store.load().rows==(FarmCoordinate("A-Renamed",26,"1","2"),))
            q["deleted_choice_not_fabricated"]=s2.get()=="B"
            s2.configure(state="disabled")
            s1.set("A-Renamed");editor.row_widgets[0]["apply_sell"].invoke()
            q["disabled_choice_not_affected"]=s2.get()=="B" and s1.get()=="A-Renamed"
            s2.destroy();f2.destroy()
            q["destroyed_widgets_pruned"]=editor.account_bindings.active_count()==1
            editor.unregister_account_combos(s1,f1)
            q["explicit_unregistration"]=editor.account_bindings.active_count()==0
            q["unrelated_config_bytes_preserved"]=(
                b"accounts = untouched\r\n" in p.read_bytes()
                and b"keep = yes\r\n" in p.read_bytes())
            editor.destroy();root.destroy();root=None
        if not all(v for k,v in q.items() if type(v) is bool and k!="game_started"):
            raise RuntimeError("S122_NATIVE_FAILURE")
        q["status"]="PASS_NATIVE_S122_H11_REAL_TK_ACCOUNT_PRESET_CHOICES"
    except Exception as exc:
        q["status"]="FAIL_S122_NATIVE";q["error_type"]=type(exc).__name__
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        (ART/"native_real_tk.json").write_text(json.dumps(q,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        for k,v in q.items():print("S122_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if q["status"].startswith("PASS_NATIVE_S122_") else 1
if __name__=="__main__":raise SystemExit(run())
