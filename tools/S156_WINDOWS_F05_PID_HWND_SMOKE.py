"""S156: F05 main-window-by-launched-PID on real Win64/Tk top-level HWNDs.

Actual user32 EnumWindows, GetWindowThreadProcessId, IsWindowVisible,
GetClassNameW and S08's timed GetWindowText work on three TEST-OWNED Tk
windows. This does not launch/inject game, call signed Info or prove
a real game has this class/window ordering.
"""
from __future__ import annotations
import json,os,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s156"
OUT.mkdir(parents=True,exist_ok=True)


def run() -> int:
    result={
        "status":"NOT_RUN","native_windows":os.name=="nt",
        "windows":"THREE_ACTUAL_TEST_OWNED_TK_TOP_LEVEL_HWNDS",
        "real_thần_long_game_started":False,
        "game_executable_launched":False,
        "DLL_injected":False,"real_Info_entitlement":False,
        "product_exe_built":False,"unsafe_game_action_count":0,
    }
    root=None
    try:
        if os.name!="nt":raise OSError("WINDOWS_REQUIRED")
        import tkinter as tk
        from start_windows import NativeWin32Backend,UNITY_WINDOW_CLASS,TITLE_TIMEOUT_MS
        from login_pid_window import find_main_window_by_pid
        api=NativeWin32Backend()
        root=tk.Tk()
        root.title("S156 root, not selected")
        root.geometry("230x100+80+40")
        tops=[]
        titles=(
            "S156 F05 generic launcher TEST ONLY",
            "Thần Long - S156 TEST ONLY (NOT GAME)",
            "S156 unrelated native Tk child TEST ONLY")
        for i,title in enumerate(titles):
            t=tk.Toplevel(root)
            t.title(title)
            t.geometry(f"270x125+{350+i*280}+{80+30*i}")
            tk.Label(t,text="F05 WIN32 REAL TEST HWND, NOT GAME").pack()
            tops.append(t)
        root.update_idletasks();root.update()
        # GetAncestor(2) resolves actual Tk WM top-level over its child drawable.
        from dwm_preview import NativeDwmBackend
        apidwm=NativeDwmBackend()
        handles=tuple(int(apidwm._ancestor(int(t.winfo_id()),2)) for t in tops)
        pid=os.getpid()
        checks={}
        enumerated=set(api.enumerate_top_level())
        checks["actual_3_distinct_windows_in_native_EnumWindows"]=(
            len(set(handles))==3 and set(handles)<=enumerated)
        checks["real_win32_PIDs_match_test_process"]=all(
            api.process_id(h)==pid and api.is_window(h) and api.is_visible(h)
            for h in handles)
        checks["actual_GetWindowTextW_unicode_title_read"]=all(
            api.title_with_timeout(h,TITLE_TIMEOUT_MS)==t
            for h,t in zip(handles,titles))
        checks["actual_Win32_class_recovered"]=all(api.window_class(h) for h in handles)
        checks["actual_parent_process_is_not_game"]=(
            "thần long" not in api.process_executable(pid).casefold())
        class Scoped:
            def __init__(self,source,hs):
                self.source=source;self.hs=hs
                self.override_class={}
            def enumerate_top_level(self):return self.hs
            def is_window(self,h):return self.source.is_window(h)
            def is_visible(self,h):return self.source.is_visible(h)
            def process_id(self,h):return self.source.process_id(h)
            def window_class(self,h):return self.override_class.get(h,self.source.window_class(h))
            def title_with_timeout(self,h,ms):return self.source.title_with_timeout(h,ms)
        scoped=Scoped(api,handles)

        checks["actual_Win32_prefers_real_title_Thần_Long"]=(
            find_main_window_by_pid(pid,scoped)==handles[1])
        checks["actual_Win32_rejects_other_PID"]=(
            find_main_window_by_pid(pid+1000,scoped) is None)
        scoped.override_class[handles[2]]=UNITY_WINDOW_CLASS
        checks["simulated_only_UnityWndClass_priority_uses_real_PID_HWND"]=(
            find_main_window_by_pid(pid,scoped)==handles[2])
        # No class override when testing the genuine original fallback.
        scoped.override_class.clear()
        tops[1].title("S156 no game title now - TEST ONLY")
        root.update_idletasks();root.update()
        checks["actual_first_visible_PID_owned_fallback"]=(
            find_main_window_by_pid(pid,scoped)==handles[0])
        # One real Win32 HWND disappears, never handed out as live.
        tops[0].destroy()
        root.update_idletasks();root.update()
        checks["actual_closed_Win32_HWND_not_returned"]=(
            not api.is_window(handles[0])
            and find_main_window_by_pid(pid,scoped)==handles[1])
        # Windows-only source preserves exact original read-only contract.
        checks["no_game_process_or_PIDs_mutated"]=all(
            api.is_window(h) and api.process_id(h)==pid for h in handles[1:])
        result["checks"]=checks
        result["status"]=(
            "PASS_NATIVE_S156_F05_REAL_WIN32_PID_MAIN_HWND_TEST_OWNED_NO_GAME"
            if all(checks.values()) else "FAIL_NATIVE_S156_F05")
    except Exception as exc:
        result["status"]="FAIL_NATIVE_S156_F05"
        result["error_type"]=type(exc).__name__
        result["error_detail"]=str(exc)[:200]
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        (OUT/"f05_pid_hwnd_real_win64.json").write_text(
            json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(json.dumps(result,ensure_ascii=True))
    return 0 if result["status"].startswith("PASS_") else 1

if __name__=="__main__":raise SystemExit(run())
