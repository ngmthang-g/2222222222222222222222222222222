"""S92 native Windows/Tk test of original G09 Party Event/thread lifecycle.

REAL Tk owner window, real Python daemon workers/events, test-only
fake protocol + permission injection. This is not a Party UI and does
not send game packets, query game memory or grant a signed license.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import queue
import sys
import threading
import time
import traceback

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s92"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"native_party_event_coordinator.json"


def main():
    report={"task":"S92","status":"NOT_RUN","native":"REAL_WINDOWS_TK_THREAD_EVENTS",
            "protocol":"TEST_ONLY_NO_GAME","permission":"INJECTED_TEST_ONLY_NOT_SIGNED_INFO",
            "game":"NOT_RUNNING","RoleName":"UNAVAILABLE"}
    root=None
    tasks=[]
    try:
        if os.name!="nt":raise RuntimeError("WINDOWS_REQUIRED")
        import tkinter as tk
        from party_action_coordinator import PartyJob, PartyRunCoordinator

        root=tk.Tk()
        root.title("S92 TEST ONLY - not Party")
        root.geometry("440x220+35+35")
        tk.Label(root,text="TEST OWNED - NO GAME BACKEND").pack()
        stage=tk.StringVar(root,value="IDLE")
        tk.Label(root,textvariable=stage).pack()
        root.update_idletasks()
        root.update()
        assert root.winfo_exists()

        cbq=queue.Queue()
        started=[]
        guard=threading.Lock()
        release=threading.Event()
        post=[]
        def protocol(job,cancel):
            with guard:
                started.append(job.number)
            while not cancel.is_set() and not release.wait(.01):
                pass
            return release.is_set() and not cancel.is_set()
        def on_change(s):
            cbq.put(s)  # background callbacks do NOT call Tk
        def pump():
            while True:
                try:msg=cbq.get_nowait()
                except queue.Empty:break
                stage.set(msg.global_state)
            if root is not None and root.winfo_exists():
                root.after(20,pump)
        root.after(20,pump)

        def step_until(predicate,seconds=5.0):
            deadline=time.monotonic()+seconds
            while time.monotonic()<deadline:
                root.update()
                if predicate():return True
                time.sleep(.01)
            return False

        closed=PartyRunCoordinator()  # no signed Info or protocol provided
        assert closed.start_global((PartyJob(1,("A","B")),))=="TEAM_PROTOCOL_UNAVAILABLE"
        assert closed.snapshot().global_state=="IDLE"
        report["default_unwired_blocks_game_command"]=True

        p=PartyRunCoordinator(
            execute=protocol,
            permission=lambda operation,count:operation=="party" and count>=2,
            after_party=lambda:post.append("ONCE"),
            on_change=on_change)
        tasks.append(p)
        jobs=(PartyJob(1,("A","B")),PartyJob(2,("C","D")),PartyJob(3,("E","F")))
        assert p.start_global(jobs)=="STARTED"
        assert step_until(lambda:len(started)==3)
        assert step_until(lambda:stage.get()=="RUNNING")
        assert p.stop_global()=="STOPPING"
        assert step_until(lambda:stage.get()=="STOPPING" or p.snapshot().global_state=="IDLE")
        assert step_until(lambda:p.snapshot().global_state=="IDLE")
        assert post==[]
        report["three_parallel_threads_cancel_without_post"]=True
        report["main_thread_tk_event_handoff"]=True
        # Independently restart after previous cancellation.
        with guard:started.clear()
        release.clear()
        assert p.start_global(jobs)=="STARTED"
        assert step_until(lambda:len(started)==3)
        release.set()
        assert step_until(lambda:p.snapshot().global_state=="IDLE")
        assert len(post)==1 and p.snapshot().post_calls==1
        assert p.snapshot().completed_global==2
        report["second_run_aggregate_post_once"]=True

        # Independent SINGLE cluster: duplicate invocation rejected and
        # subsequent stop closes ONLY its own worker.
        release.clear()
        assert p.start_single(PartyJob(4,("G","H")))=="STARTED"
        assert step_until(lambda:4 in started)
        assert p.start_single(PartyJob(4,("G","H")))=="ALREADY_RUNNING"
        assert p.stop_single(4)=="STOPPING"
        assert step_until(lambda:4 not in p.snapshot().running_single)
        report["single_group_duplicate_guard"]=True
        p.close()
        assert p.start_single(PartyJob(5,("I","J")))=="CLOSED"
        report["closed_fails_shut"]=True
        report["status"]="PASS_NATIVE_S92_G09_REAL_TK_THREAD_CANCEL_EVENTS"
    except Exception as exc:
        report["status"]="FAIL_NATIVE_S92"
        report["error_type"]=type(exc).__name__
        report["error_text"]=str(exc)[:500]
        report["traceback"]=traceback.format_exc(limit=16)
        print(report["traceback"])
    finally:
        for obj in tasks:
            try:obj.close()
            except Exception:pass
        if root is not None:
            try:root.destroy()
            except Exception:pass
        REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
        for k,v in report.items():
            if k!="traceback":print("S92_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if report["status"]=="PASS_NATIVE_S92_G09_REAL_TK_THREAD_CANCEL_EVENTS" else 1

if __name__=="__main__":
    raise SystemExit(main())
