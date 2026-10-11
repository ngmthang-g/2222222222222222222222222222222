"""S159 genuine Win64 Login-size normalization on two TEST-OWNED Tk HWNDs.

Calls REAL Win32 GetWindowRect and SetWindowPos through unchanged S17
NativeLayoutBackend. One test-only executable identity override is explicit:
the process is PYTHON.EXE, never Thần Long. No signed Info, real game,
accounts, DLL injection or product launch.
"""
from __future__ import annotations
import json,os,sys,threading,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s159"
OUT.mkdir(parents=True,exist_ok=True)

def main() -> int:
    result={"task":"S159","status":"NOT_RUN",
            "test_owned_windows":True,"real_game":False,
            "test_only_executable_identity_override":True,
            "signed_Info_verified":False,"product_exe_built":False,
            "original_flags_parity":"UNKNOWN"}
    root=None
    try:
        if os.name!="nt":raise OSError("WIN64_REQUIRED")
        import tkinter as tk
        from dwm_preview import NativeDwmBackend
        from start_windows import GAME_PROCESS,GAME_TITLE,GameWindow
        from start_polling import WindowSnapshot
        from login_resize_monitor import (
            F05LoginResizeMonitor,NativeF05ResizeBackend,
            F05_LOGIN_RESIZE_INTERVAL_SECONDS,
        )
        root=tk.Tk()
        root.title("S159 ROOT TEST NOT GAME")
        root.geometry("210x130+30+20")
        wins=[]
        for i,(width,height) in enumerate(((530,365),(670,420),(480,300))):
            win=tk.Toplevel(root)
            win.title(GAME_TITLE if i<2 else "NOT_LOGIN_OWNED")
            win.geometry(f"{width}x{height}+{65+i*230}+{80+i*45}")
            tk.Label(win,text="S159 native test HWND, NOT a game").pack()
            wins.append(win)
        root.update_idletasks();root.update()
        native=NativeDwmBackend()
        handles=[int(native._ancestor(int(t.winfo_id()),2)) for t in wins]
        pid=os.getpid()
        assert len(set(handles))==3
        class TestOnlyWindows(NativeF05ResizeBackend):
            def __init__(self):
                super().__init__()
                self.resize_calls=[]
            def process_executable(self,process_id):
                # TEST-ONLY identity adapter: native HWND, size and PID remain
                # genuine Win32; executable is always actually PYTHON.
                return GAME_PROCESS if process_id==pid else "unverified.exe"
            def resize_no_move(self,h,w,he):
                self.resize_calls.append((h,w,he))
                return super().resize_no_move(h,w,he)
        api=TestOnlyWindows()
        rows=tuple(GameWindow(h,pid,GAME_TITLE,"OtherClass",GAME_PROCESS)
                   for h in handles)
        snapshot=WindowSnapshot(1,rows,True)
        owners=set(handles[:2])
        mon=F05LoginResizeMonitor(api)
        checks={}
        checks["three_genuine_native_hwnds_and_PIDs"]=all(
            api.is_window(h) and api.process_id(h)==pid for h in handles)
        checks["actual_executable_is_python_not_original_game"]=(
            "python" in api.observer.process_executable(pid).casefold())
        # The two authorized targets use the exact frozen original visible
        # title; the third is intentionally not Login-owned.
        before={h:api.window_rect(h) for h in handles}
        res=mon.normalize(snapshot,allowed=lambda:True,
                          login_owned=lambda w:w.hwnd in owners)
        checks["native_GetWindowRect_SetWindowPos_actually_resized_two"]=(
            res.code=="PASS" and res.resized==tuple(handles[:2])
            and len(api.resize_calls)==2)
        after={h:api.window_rect(h) for h in handles}
        checks["both_real_hwnds_reach_original_1366x768"]=all(
            (after[h][2]-after[h][0],after[h][3]-after[h][1])==(1366,768)
            for h in handles[:2])
        checks["native_resize_kept_original_xy_positions"]=all(
            before[h][:2]==after[h][:2] for h in handles)
        checks["unowned_native_hwnd_not_modified"]=(
            before[handles[2]]==after[handles[2]]
            and handles[2] in res.skipped)
        second=mon.normalize(snapshot,allowed=lambda:True,
                             login_owned=lambda w:w.hwnd in owners)
        checks["second_tick_correct_size_does_NOT_call_SetWindowPos_again"]=(
            not second.resized and second.unchanged==tuple(handles[:2])
            and len(api.resize_calls)==2)
        rejected=mon.normalize(snapshot,allowed=lambda:False,
                               login_owned=lambda w:True)
        checks["revoked_Info_cannot_mutate_any_HWND"]=(
            rejected.code=="NOT_AUTHORIZED" and len(api.resize_calls)==2)
        native_exe=api.process_executable
        # Reuse a genuine PID mismatch for one target: stale snapshot
        # candidates must not be resized or assumed to be valid.
        stale=GameWindow(handles[0],pid+9999,GAME_TITLE,"OtherClass",GAME_PROCESS)
        wrong=mon.normalize(WindowSnapshot(2,(stale,),True),
                            allowed=lambda:True,login_owned=lambda w:True)
        checks["same_HWND_other_PID_rejected"]=(
            wrong.skipped==(handles[0],) and not wrong.resized)
        checks["exact_original_period_1_second_not_changed"]=(
            F05_LOGIN_RESIZE_INTERVAL_SECONDS==1.0)
        checks["not_real_game_no_Info_no_product"]=(
            not result["real_game"] and not result["signed_Info_verified"]
            and not result["product_exe_built"])
        result["checks"]=checks
        result["status"]=(
            "PASS_NATIVE_S159_F05_REAL_WIN64_CONDITIONAL_RESIZE_TEST_OWNED"
            if all(checks.values()) else "FAIL_NATIVE_S159_RESIZE")
    except Exception as exc:
        result["status"]="FAIL_NATIVE_S159_RESIZE"
        result["error_type"]=type(exc).__name__
        result["error_message"]=str(exc)[:180]
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        (OUT/"f05_login_resize_real_win64.json").write_text(
            json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        print(json.dumps(result,ensure_ascii=True))
    return 0 if result["status"].startswith("PASS_") else 1

if __name__=="__main__":raise SystemExit(main())
