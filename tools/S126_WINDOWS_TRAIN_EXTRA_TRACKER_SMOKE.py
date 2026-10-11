"""S126 genuine Windows Tk H12 third-line Farm session tracker lifecycle.

Uses a *test-owned* native HWND/PID and TEST-only character info injection;
NO actual game memory, no real signed Info, no control of a game process.
"""
from __future__ import annotations
import json,os,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s126";OUT.mkdir(parents=True,exist_ok=True)

def run():
    q={"status":"NOT_RUN","actual_game":False,"signed_info":False,"proxy":"EXCLUDED"}
    root=None
    try:
        if os.name!="nt":
            raise RuntimeError("WINDOWS_TK_REQUIRED")
        import tkinter as tk
        from permission_guard import PermissionGuard,VerifiedClaims
        from farm_saved_editor import FarmSavedCoordinatesEditor
        from train_saved_coordinates import FarmCoordinate,FarmCoordinatesStore
        from train_account_rows import TkTrainAccountRows
        from train_character_samples import TrainCharacterSample
        from start_windows import NativeWin32Backend,GameWindow
        from start_polling import WindowSnapshot

        with tempfile.TemporaryDirectory(prefix="S126_REAL_TK_EXTRA_") as td:
            path=Path(td)/"settings.ini"
            path.write_bytes(b"[Settings]\r\ncredentials = untouched\r\n[Farm]\r\nkeep = yes\r\n")
            store=FarmCoordinatesStore(path)
            store.save([FarmCoordinate("TrainA",26,"1","2")])
            root=tk.Tk();root.geometry("860x530+0+0")
            editor=FarmSavedCoordinatesEditor(root,store=store)
            editor.pack()
            root.update()
            native=NativeWin32Backend()
            hwnd=int(root.winfo_id())
            pid=native.process_id(hwnd)
            win=GameWindow(hwnd,pid,"CI-only HWND", "TkTopLevel","NOT_GAME.exe")
            q["real_native_windows_hwnd_pid"]=(
                hwnd>0 and pid==os.getpid()
                and native.is_window(hwnd) and native.is_visible(hwnd))
            guard=PermissionGuard()
            owner=TkTrainAccountRows(
                root,editor,allow_account=lambda _:True,
                permission_guard=guard,running_count=lambda:1)
            owner.apply_snapshot(WindowSnapshot(revision=1,windows=(win,),valid=True))
            row=owner._rows[hwnd]
            initial="0h:00p | Túi: ? | Chết: 0 | Vàng: 0,00 | 0,00 vàng/h | 0 exp/h"
            q["initial_h12_exact_static_line_no_session"]=(
                row["label_extra"].cget("text")==initial
                and not row["tracker"].active)
            q["unsigned_info_cannot_start_stats"]=(
                not owner.start_confirmed_tracking(hwnd,pid)
                and not row["tracker"].active)
            guard.receive_token("CI_STUB_NOT_SIGNED",lambda _:
                VerifiedClaims(frozenset({"farm_tab"}),"active",2))
            owner.reapply_permissions()
            q["still_does_not_auto_start_on_authorization"]=(
                not row["tracker"].active)
            q["authorized_lifecycle_start_separately_confirmed"]=(
                owner.start_confirmed_tracking(hwnd,pid)
                and row["tracker"].active)
            def sample(gold=None,exp=None,bag=None,name=None):
                return TrainCharacterSample(hwnd,pid,name,None,bag,gold,exp)
            q["first_read_only_sample_is_baseline"]=(
                owner.apply_character_samples((sample(gold=100000,exp=10000,bag=98),))==1
                and row["tracker"].earned_bound_money_raw==0
                and row["tracker"].earned_exp==0)
            q["positive_deltas_update_true_tk_label"]=(
                owner.apply_character_samples((sample(gold=120000,exp=10500),))==1
                and row["tracker"].earned_bound_money_raw==20000
                and row["tracker"].earned_exp==500
                and "Túi: 98" in row["label_extra"].cget("text")
                and "Vàng: 2,00" in row["label_extra"].cget("text"))
            q["low_wallet_exp_samples_never_decrement"]=(
                owner.apply_character_samples((sample(gold=1000,exp=100),))==1
                and (row["tracker"].earned_bound_money_raw,
                     row["tracker"].earned_exp)==(20000,500))
            q["positive_after_decrease_adds_only_delta"]=(
                owner.apply_character_samples((sample(gold=11000,exp=300),))==1
                and (row["tracker"].earned_bound_money_raw,
                     row["tracker"].earned_exp)==(30000,700))
            q["authenticated_death_episode_call_increments"]=(
                owner.record_confirmed_death(hwnd,pid)
                and "Chết: 1" in row["label_extra"].cget("text"))
            q["wrong_pid_cannot_increase_deaths"]=(
                not owner.record_confirmed_death(hwnd,pid+1)
                and row["tracker"].deaths==1)
            q["stop_lifecycle_resets_without_game_command"]=(
                owner.stop_tracking(hwnd,pid)
                and not row["tracker"].active
                and row["tracker"].earned_exp==0
                and "Chết: 0" in row["label_extra"].cget("text"))
            owner.start_confirmed_tracking(hwnd,pid)
            owner.apply_character_samples((sample(gold=50000,exp=1000,bag=77),))
            guard.clear();owner.reapply_permissions()
            q["info_revoke_erases_stats_and_character_slots"]=(
                not row["tracker"].active
                and row["label_bag"].cget("text")=="Túi: ?"
                and row["label_extra"].cget("text")==initial)
            stale=TrainCharacterSample(hwnd,pid+1,"SHOULD NOT SHOW",30,0,0,0)
            q["old_pid_sample_cannot_update_stats"]=(
                owner.apply_character_samples((stale,))==0
                and row["label_extra"].cget("text")==initial)
            owner.apply_snapshot(WindowSnapshot(revision=2,windows=(),valid=True))
            q["closed_window_destroys_tracker_and_account_widgets"]=(
                not owner._rows and editor.account_bindings.active_count()==0)
            owner.shutdown();owner.container.destroy()
            editor.destroy();root.destroy();root=None
            q["original_unrelated_settings_bytes_preserved"]=(
                b"credentials = untouched\r\n" in path.read_bytes()
                and b"keep = yes\r\n" in path.read_bytes())
        check=[k for k,v in q.items() if type(v) is bool and k not in ("actual_game","signed_info")]
        if not all(q[k] for k in check):
            raise RuntimeError("S126_NATIVE_STATS_TEST_ASSERTION_FAILED")
        q["status"]="PASS_NATIVE_S126_H12_VIETNAMESE_STATS_REAL_TK_NO_GAME"
    except Exception as exc:
        q["status"]="FAIL_NATIVE_S126"
        q["error_type"]=type(exc).__name__
        q["error_detail"]=str(exc)[:130]
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        (OUT/"windows_h12_extra_tracker.json").write_text(
            json.dumps(q,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        for key,value in q.items():
            print("S126_"+key.upper()+"="+json.dumps(value,ensure_ascii=True))
    return 0 if q["status"].startswith("PASS_NATIVE_S126_") else 1

if __name__=="__main__":
    raise SystemExit(run())
