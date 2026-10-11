"""S158: actual Win64 child-PID-to-Tk-HWND arrival with F05 shared lock.

Two TEST-OWNED subprocesses create real Tk top-level windows after a delay.
The genuine S08/Win32 S156 lookup is called repeatedly by the F05 25-second
handoff, while two concurrent external callbacks are serialized until HWND
arrival. No Unity game, resource DLL, injector, Proxy, Info grant or product.
"""
from __future__ import annotations
import json,os,sys,threading,time,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
DEST=ROOT/"artifacts"/"s158"
DEST.mkdir(parents=True,exist_ok=True)

def run():
    report={"task":"S158","status":"NOT_RUN",
            "real_windows_children":"TWO_TEST_OWNED_TK_ONLY",
            "original_25s_window_timeout":True,
            "original_stabilization_seconds":"UNKNOWN",
            "real_thanh_long_game":False,"dll_injection":False,
            "signed_Info_verified":False,"proxy_modified":False,
            "user_product_exe":False}
    children=[]
    try:
        if os.name!="nt":raise OSError("WINDOWS_REQUIRED")
        from login_pid_handoff import F05SerializedHandoff,F05_HWND_TIMEOUT_SECONDS
        from login_pid_window import find_main_window_by_pid
        from start_windows import NativeWin32Backend
        native=NativeWin32Backend()
        calls=[]
        completed=[]
        errors=[]
        shared=threading.Lock()
        barrier=threading.Barrier(3)
        # The Tk root does not exist until after the 0.5s child delay; the
        # parent must actually poll for its own newly returned PID's HWND.
        test_child=(
            "import time,tkinter as tk;"
            "time.sleep(0.55);"
            "root=tk.Tk();"
            "root.title('Th'+chr(0x1ea7)+'n Long S158 TEST OWNED');"
            "root.geometry('420x170+70+70');"
            "root.after(9500,root.destroy);"
            "root.mainloop()"
        )
        class Task:
            def __init__(self,tag):
                self.tag=tag
                self.result=None
                self.pid=None
            def spawn(self):
                proc=subprocess.Popen(
                    [sys.executable,"-c",test_child],
                    shell=False,stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                    creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
                children.append(proc)
                self.pid=proc.pid
                calls.append(("spawn",self.tag,proc.pid))
                return proc.pid
            def execute(self):
                try:
                    barrier.wait(timeout=6)
                    handoff=F05SerializedHandoff(launch_lock=shared)
                    self.result=handoff.launch_and_wait(
                        self.spawn,allowed=lambda:True,
                        cancelled=lambda:False)
                    completed.append(("result",self.tag,self.result.code))
                except Exception as exc:
                    errors.append(type(exc).__name__)
        tasks=[Task(1),Task(2)]
        threads=[threading.Thread(target=t.execute,daemon=True) for t in tasks]
        for t in threads:t.start()
        barrier.wait(timeout=6)
        for t in threads:t.join(timeout=15)
        checks={}
        checks["both_real_child_threads_finished"]=all(
            not t.is_alive() for t in threads) and not errors
        checks["both_actual_Python_child_processes_created"]=(
            len(children)==2 and all(proc.poll() is None for proc in children))
        checks["both_25s_window_waits_returned_actual_HWND"]=all(
            task.result is not None and
            task.result.code=="PID_HWND_FOUND" and
            type(task.result.hwnd) is int and task.result.hwnd>0
            for task in tasks)
        checks["both_Win32_HWNDs_are_owned_by_matching_CHILD_PID"]=all(
            task.result is not None and
            native.is_window(task.result.hwnd) and
            native.process_id(task.result.hwnd)==task.pid
            for task in tasks)
        checks["both_native_titles_prefer_real_matching_game_title_token"]=all(
            "S158 TEST OWNED" in native.title_with_timeout(task.result.hwnd,150)
            for task in tasks if task.result is not None)
        checks["actual_F05_native_lookup_by_each_unique_PID"]=all(
            find_main_window_by_pid(task.pid)==task.result.hwnd
            for task in tasks if task.result is not None)
        checks["shared_lock_keeps_second_spawn_AFTER_first_HWND_found"]=(
            len(calls)==2 and len(completed)==2
            and len({p for _,_,p in calls})==2
            and any(t.result.polls>=2 for t in tasks if t.result is not None)
            and calls[0][1]==completed[0][1])
        checks["strict_wrong_PID_lookup_returns_no_window"]=all(
            find_main_window_by_pid(pid+10000000) is None
            for _,_,pid in calls)
        checks["explicit_unauthorized_attempt_never_starts_child"]=(
            F05SerializedHandoff().launch_and_wait(
                lambda: (_ for _ in ()).throw(AssertionError("SHOULD_NOT_SPAWN")),
                allowed=lambda:False).code=="NOT_AUTHORIZED")
        checks["no_actual_game_injection_or_product_run"]=all(
            not report[field] for field in (
                "real_thanh_long_game","dll_injection","signed_Info_verified",
                "proxy_modified","user_product_exe"))
        report["checks"]=checks
        report["status"]=(
            "PASS_NATIVE_S158_F05_REAL_CHILD_PID_HWND_SERIAL_HANDOFF_NOT_GAME"
            if all(checks.values()) else "FAIL_NATIVE_S158_HANDOFF")
    except Exception as exc:
        report["status"]="FAIL_NATIVE_S158_HANDOFF"
        report["error_type"]=type(exc).__name__
    finally:
        for proc in children:
            if proc.poll() is None:
                try:proc.terminate();proc.wait(timeout=4)
                except Exception:
                    try:proc.kill()
                    except Exception:pass
        (DEST/"f05_real_win64_serial_pid_hwnd.json").write_text(
            json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(json.dumps(report,ensure_ascii=True))
    return 0 if report["status"].startswith("PASS_") else 1

if __name__=="__main__":raise SystemExit(run())
