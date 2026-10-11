"""S123 real Windows Tk owner+Win32 HWND/PID, identity lifecycle and S122 bindings.

The real HWND used for CI is this TEST's own Tk window, NOT a real game
window; the production service exclusively reads the S09 filtered actual
game-window producer. No game read, simulated character, or license grant.
"""
from __future__ import annotations
import json,os,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s123"
OUT.mkdir(parents=True,exist_ok=True)

def run():
    result={"status":"NOT_RUN","test_tk_is_not_game":True,"game_launched":False,"proxy":"EXCLUDED"}
    root=None
    try:
        if os.name!="nt":raise RuntimeError("WINDOWS_REQUIRED")
        import tkinter as tk
        from train_account_rows import TkTrainAccountRows,TRAIN_ACCOUNT_REFRESH_MS
        from farm_saved_editor import FarmSavedCoordinatesEditor
        from train_saved_coordinates import FarmCoordinate,FarmCoordinatesStore
        from start_windows import NativeWin32Backend, GameWindow
        from start_polling import WindowSnapshot

        with tempfile.TemporaryDirectory(prefix="S123_REAL_TK_") as td:
            ini=Path(td)/"settings.ini"
            ini.write_bytes(b"[Settings]\r\naccounts = untouched\r\n[Farm]\r\nextra = yes\r\n")
            store=FarmCoordinatesStore(ini)
            store.save([FarmCoordinate("TrainA",26,"1","2"),FarmCoordinate("TrainB",86,"3","4")])
            root=tk.Tk();root.geometry("780x500+0+0")
            editor=FarmSavedCoordinatesEditor(root,store=store);editor.pack(fill="x")
            host=ttk_host=None
            native=NativeWin32Backend()
            root.update()
            hwnd=int(root.winfo_id())
            # Native HWND/PID are observed through real Win32, not fabricated.
            pid=native.process_id(hwnd)
            result["real_win32_hwnd_pid"]=(
                hwnd>0 and pid==os.getpid() and native.is_window(hwnd)
                and native.is_visible(hwnd))
            snapshot_win=GameWindow(hwnd,pid,"Test-owned Tk HWND","TkTopLevel","TEST_NOT_GAME.exe")
            seq=0
            def sample(*wins, valid=True):
                nonlocal seq
                seq+=1
                return WindowSnapshot(revision=seq,windows=tuple(wins),valid=valid)
            row_owner=TkTrainAccountRows(root,editor,allow_account=lambda _:True)
            result["exact_original_refresh_5000ms"]=TRAIN_ACCOUNT_REFRESH_MS==5000
            result["initially_no_fake_game_rows"]=row_owner.registry.rows==()
            result["actual_valid_win32_identity_adds_one_real_tk_row"]=(
                row_owner.apply_snapshot(sample(snapshot_win))
                and row_owner.registry.rows==(snapshot_win,)
                and len(row_owner._rows)==1
                and row_owner._rows[hwnd]["pid"]==pid
                and editor.account_bindings.active_count()==1)
            first=row_owner._rows[hwnd]
            first["sell"].set("TrainA");first["farm"].set("TrainB")
            new_title=GameWindow(hwnd,pid,"Different native window title","TkTopLevel","TEST_NOT_GAME.exe")
            result["same_pid_preserves_real_widgets_and_choices"]=(
                row_owner.apply_snapshot(sample(new_title))
                and row_owner._rows[hwnd] is first
                and first["sell"].get()=="TrainA"
                and first["farm"].get()=="TrainB")
            result["invalid_sample_preserves_real_widgets"]=(
                not row_owner.apply_snapshot(sample(valid=False))
                and row_owner._rows[hwnd] is first)
            changed_pid=GameWindow(hwnd,pid+1,"PID recycled fixture","TkTopLevel","TEST_NOT_GAME.exe")
            result["pid_reuse_destroys_old_widgets_and_resets_choices"]=(
                row_owner.apply_snapshot(sample(changed_pid))
                and row_owner._rows[hwnd] is not first
                and not first["frame"].winfo_exists()
                and row_owner._rows[hwnd]["sell"].get()==""
                and editor.account_bindings.active_count()==1)
            result["true_valid_empty_removes_stale_rows"]=(
                row_owner.apply_snapshot(sample())
                and len(row_owner._rows)==0
                and editor.account_bindings.active_count()==0)
            # Source signed Info unverified => there must be no local grant.
            denied=TkTrainAccountRows(root,editor)
            result["missing_license_permission_keeps_combo_disabled"]=(
                denied.apply_snapshot(sample(snapshot_win))
                and denied._rows[hwnd]["sell"].instate(["disabled"])
                and denied._rows[hwnd]["farm"].instate(["disabled"]))
            result["real_tk_after_start_stop_no_stale_owned_rows"]=True
            row_owner._start_refresh()
            root.update()
            row_owner._stop_refresh()
            result["real_tk_after_start_stop_no_stale_owned_rows"]=(
                not row_owner._active and not row_owner._rows and row_owner._after_id is None)
            denied.shutdown();row_owner.shutdown()
            result["no_duplicate_registered_tk_accounts"]=editor.account_bindings.active_count()==0
            denied.container.destroy();row_owner.container.destroy()
            editor.destroy();root.destroy();root=None
            result["unrelated_settings_bytes_preserved"]=(
                b"accounts = untouched\r\n" in ini.read_bytes()
                and b"extra = yes\r\n" in ini.read_bytes())
        checks=[k for k,v in result.items() if type(v) is bool and k not in ("game_launched",)]
        if not all(result[k] for k in checks):
            raise RuntimeError("S123_NATIVE_H12_ACCOUNT_ROW_ASSERTION_FAILED")
        result["status"]="PASS_NATIVE_S123_REAL_WIN32_HWND_PID_TK_ACCOUNT_ROWS_PASSIVE_ONLY"
    except Exception as exc:
        result["status"]="FAIL_S123_NATIVE"
        result["error_type"]=type(exc).__name__
        result["error_detail"]=str(exc)[:120]
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        (OUT/"windows_h12_account_rows.json").write_text(
            json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        for k,v in result.items():
            print("S123_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if result["status"].startswith("PASS_NATIVE_S123_") else 1
if __name__=="__main__":
    raise SystemExit(run())
