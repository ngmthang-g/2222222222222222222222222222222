"""S27 native Windows: deferred TEST-OWNED real Tk HWND, cancellation, timeout.

Worker waits with the existing S08 NativeWin32Backend, main thread creates
and destroys Tk windows. No game binaries, injected DLL, real Info grants,
Proxy or game window manipulation.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import threading
import time
import traceback

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s27"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"native_delayed_hwnd_handoff.json"


def run():
    evidence={"task":"S27","status":"NOT_RUN","real_game":"NOT_RUN",
              "signed_info":"NOT_AVAILABLE","game_launches":0,
              "injects":0,"login_attempts":0,"proxy_runtime":"EXCLUDED",
              "product_exe":"NOT_BUILT","HWND_scope":"TEST_OWNED_ONLY"}
    root=None
    try:
        if os.name!="nt":raise RuntimeError("Native Windows required")
        import ctypes
        from ctypes import wintypes
        import tkinter as tk
        from login_window_handoff import (
            MAX_WAIT_SECONDS, SerializedPidWindowHandoff,wait_for_pid_window)
        from start_windows import NativeWin32Backend

        root=tk.Tk()
        root.withdraw()
        native=NativeWin32Backend()
        user32=ctypes.WinDLL("user32",use_last_error=True)
        ancestor=user32.GetAncestor
        ancestor.argtypes=[wintypes.HWND,wintypes.UINT]
        ancestor.restype=wintypes.HWND
        pid=os.getpid()
        allowed=[]
        windows=[]
        def create_win():
            window=tk.Toplevel(root)
            window.title("Thần Long — S27 TEST-OWNED DELAYED HWND")
            window.geometry("350x180+100+100")
            windows.append(window)
            root.update_idletasks()
            allowed.append(int(ancestor(int(window.winfo_id()),2)))

        class NativeTestSubset:
            def enumerate_top_level(self):
                existing=set(native.enumerate_top_level())
                return tuple(hwnd for hwnd in allowed if hwnd in existing)
            def is_window(self,hwnd):return native.is_window(hwnd)
            def is_visible(self,hwnd):return native.is_visible(hwnd)
            def process_id(self,hwnd):return native.process_id(hwnd)
            def window_class(self,hwnd):return native.window_class(hwnd)
            def title_with_timeout(self,hwnd,ms):
                assert ms==150
                return native.title_with_timeout(hwnd,ms)
        subset=NativeTestSubset()
        coordinator=SerializedPidWindowHandoff()
        outcomes={}
        errors=[]
        def run_wait(name,*,event=None,timeout=2):
            try:
                outcomes[name]=coordinator.wait(
                    pid,backend=subset,cancel=event,timeout_seconds=timeout,
                    poll_seconds=.04)
            except Exception as exc:
                errors.append((name,str(exc)))
        def ui_until(thread,deadline=6):
            end=time.monotonic()+deadline
            while thread.is_alive() and time.monotonic()<end:
                root.update()
                time.sleep(.005)
            thread.join(timeout=.1)
            assert not thread.is_alive(),"Handoff worker leaked or exceeded deadline"

        # Tk must only be constructed on the original UI thread; worker waits
        # while root.after arranges actual native top-level creation later.
        root.after(250,create_win)
        launched=time.monotonic()
        first=threading.Thread(target=run_wait,
                               args=("delayed",),daemon=True)
        first.start();ui_until(first)
        result=outcomes["delayed"]
        evidence["delayed_status"]=result.code
        evidence["delayed_scans"]=result.scans
        evidence["elapsed_real_seconds"]=round(time.monotonic()-launched,3)
        evidence["actual_hwnd"]=allowed[0] if allowed else None
        evidence["correct_real_win32_pid"]=(
            len(allowed)==1 and native.is_window(allowed[0])
            and native.process_id(allowed[0])==pid)
        evidence["delayed_hwnd_handoff_found"]=(
            result.found and result.hwnd==allowed[0]
            and result.scans>1 and result.elapsed_seconds>=.12
            and evidence["correct_real_win32_pid"])
        assert evidence["delayed_hwnd_handoff_found"],(result,evidence)

        # A foreign PID must never acquire even a game-titled TEST HWND.
        wrong=wait_for_pid_window(pid+1,backend=subset,timeout_seconds=.12,
                                  poll_seconds=.03)
        evidence["foreign_pid_rejected"]=wrong.code=="TIMEOUT" and wrong.hwnd is None
        assert evidence["foreign_pid_rejected"]

        windows[0].destroy()
        root.update()
        evidence["destroyed_hwnd_is_not_live"]=not native.is_window(allowed[0])
        assert evidence["destroyed_hwnd_is_not_live"]

        # No candidate -> bounded real timeout (short test override, F05
        # production maximum still exactly 25s).
        empty=wait_for_pid_window(pid,backend=subset,timeout_seconds=.16,
                                  poll_seconds=.03)
        evidence["bounded_empty_timeout"]=(
            empty.code=="TIMEOUT" and empty.hwnd is None
            and .10<=empty.elapsed_seconds<1.0)
        assert evidence["bounded_empty_timeout"]

        # A cancellation event interrupts a worker blocked on its timed wait.
        cancelled=threading.Event()
        root.after(125,cancelled.set)
        cancel_thread=threading.Thread(
            target=run_wait,args=("cancelled",),
            kwargs={"event":cancelled,"timeout":3},daemon=True)
        cancel_thread.start();ui_until(cancel_thread)
        r=outcomes["cancelled"]
        evidence["cancel_interrupts_wait"]=(
            r.code=="CANCELLED" and r.hwnd is None
            and r.elapsed_seconds<2 and r.scans>=1)
        assert evidence["cancel_interrupts_wait"]
        evidence["no_worker_exceptions"]=not errors
        assert evidence["no_worker_exceptions"]
        assert MAX_WAIT_SECONDS==25.0
        root.destroy();root=None
        evidence["status"]="PASS_NATIVE_S27_DELAYED_HWND_25S_BOUNDED_CANCEL_TIMEOUT"
    except Exception as exc:
        evidence["status"]="FAIL_NATIVE_S27"
        evidence["error"]=type(exc).__name__+": "+str(exc)
        evidence["traceback"]=traceback.format_exc(limit=15)
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        REPORT.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),
                          encoding="utf-8")
        for k,v in evidence.items():
            if k!="traceback":
                print("S27_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return int(evidence["status"]!="PASS_NATIVE_S27_DELAYED_HWND_25S_BOUNDED_CANCEL_TIMEOUT")


if __name__=="__main__":
    raise SystemExit(run())
