"""S93 real Windows/Tk G09 owner-thread status handoff, TEST ONLY NO GAME.

Tests actual Tk widgets/after(), 2 genuine Python worker threads+events,
global RUNNING/STOPPING/IDLE and single-run lifecycle, stale worker result
after destroy. Injected callbacks are TEST OWNED, not game/Info. The UI
contains NO clickable Party create/run controls.
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
OUT=ROOT/"artifacts"/"s93"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"native_party_tk_owner_status.json"


def main():
    report={
        "task":"S93","status":"NOT_RUN",
        "environment":"REAL_WINDOWS_TK_TEST_OWNED",
        "game":"NOT_RUNNING",
        "backend":"ONLY_INJECTED_TEST_EVENTS",
        "signed_info":"NOT_CONNECTED",
        "controls":"READ_ONLY_LABELS_NO_GAME_ACTIONS"
    }
    root=None
    panels=[]
    try:
        if os.name!="nt":raise RuntimeError("WINDOWS_REQUIRED")
        import tkinter as tk
        from tkinter import ttk
        from party_tk_run_status import (
            TkPartyRunStatus, RUNNING_COLOR, STOPPING_COLOR)
        from party_action_coordinator import PartyJob

        root=tk.Tk()
        root.title("S93 TEST-OWNED Party status NO GAME")
        root.geometry("620x460+50+50")
        root.update_idletasks()
        root.update()

        def widgets(w):
            for child in w.winfo_children():
                yield child
                yield from widgets(child)

        default=TkPartyRunStatus(root,groups=(1,2))
        panels.append(default)
        default.pack(fill="x")
        root.update()
        assert default.current.code=="UNAVAILABLE"
        assert "thiếu backend đội hoặc xác thực Info" in default.summary.cget("text")
        assert default.coordinator.start_single(PartyJob(1,("A","B")))==(
            "TEAM_PROTOCOL_UNAVAILABLE")
        assert not any(isinstance(c,ttk.Button) for c in widgets(default))
        report["default_g10_info_missing_explicitly_unavailable"]=True

        started=[]
        mutex=threading.Lock()
        release=threading.Event()
        post=[]
        def test_team(job,cancel):
            with mutex:started.append(job.number)
            while not release.wait(.008):
                pass
            return not cancel.is_set()
        status=TkPartyRunStatus(
            root,groups=(1,2,3),execute=test_team,
            permission=lambda op,count:op=="party" and count>=2,
            after_party=lambda:post.append("ONCE"))
        panels.append(status)
        status.pack(fill="x")
        root.update()

        def until(predicate,timeout=4.0):
            deadline=time.monotonic()+timeout
            while time.monotonic()<deadline:
                root.update()
                if predicate():
                    return True
                time.sleep(.01)
            return False

        assert status.current.code=="IDLE"
        assert not any(isinstance(c,ttk.Button) for c in widgets(status))
        jobs=(PartyJob(1,("A","B")),PartyJob(2,("C","D")))
        assert status.coordinator.start_global(jobs)=="STARTED"
        assert until(lambda:len(started)==2)
        assert until(lambda:status.current.code=="RUNNING")
        assert status.current.global_text=="Dừng lại"
        assert root.winfo_rgb(status.summary.cget("foreground"))==root.winfo_rgb(RUNNING_COLOR), (
            status.summary.cget("foreground"), RUNNING_COLOR)
        assert "⏳" in status.group_labels[1].cget("text")
        assert "⏳" in status.group_labels[2].cget("text")
        report["original_running_text_red_foreground_real_tk"]=True

        assert status.coordinator.stop_global()=="STOPPING"
        assert until(lambda:status.current.code=="STOPPING")
        assert status.current.global_text=="Đang dừng..."
        assert root.winfo_rgb(status.summary.cget("foreground"))==root.winfo_rgb(STOPPING_COLOR), (
            status.summary.cget("foreground"), STOPPING_COLOR)
        # Snapshot belongs to coordinator, UI callbacks must never make
        # a stale event revert STOPPING to previous RUNNING.
        status._queue.put(status._epoch)
        root.update()
        assert status.current.code=="STOPPING"
        release.set()
        assert until(lambda:status.current.code=="IDLE")
        assert post==[]
        report["cancel_stopping_orange_and_back_idle_no_post"]=True

        release.clear()
        with mutex:started.clear()
        assert status.coordinator.start_global(jobs)=="STARTED"
        assert until(lambda:len(started)==2)
        assert until(lambda:status.current.code=="RUNNING")
        release.set()
        assert until(lambda:status.current.code=="IDLE")
        assert post==["ONCE"]
        report["aggregate_success_calls_post_once_and_tk_reset"]=True

        # Different single job shows real busy state, group config changes
        # while Tk UI remains read-only; no fake create/leave buttons.
        release.clear()
        with mutex:started.clear()
        assert status.coordinator.start_single(PartyJob(3,("X","Y")))=="STARTED"
        assert until(lambda:3 in started)
        assert until(lambda:"⏳" in status.group_labels[3].cget("text"))
        status.set_groups((2,3))
        assert 1 not in status.group_labels
        assert 2 in status.group_labels
        assert 3 in status.group_labels
        report["single_group_and_dynamic_readonly_rows"]=True

        # Teardown while original TEST worker is still blocked. Tk subtree
        # is really destroyed; worker's late completion cannot mutate Tk.
        raw_coordinator=status.coordinator
        status.destroy()
        root.update()
        assert status.current.code=="CLOSED"
        assert status._closed and status._pending_after is None
        assert raw_coordinator.snapshot().global_state=="IDLE"
        release.set()
        assert raw_coordinator.wait_idle(3)
        root.update()
        assert status.current.code=="CLOSED"
        assert raw_coordinator.start_single(PartyJob(1,("X","Y")))=="CLOSED"
        report["actual_tk_destroy_blocks_stale_background_callback"]=True
        report["no_fake_clickable_party_buttons"]=True
        report["status"]="PASS_NATIVE_S93_G09_TK_OWNER_STATE_LATE_WORKER_CLOSED"
    except Exception as exc:
        report["status"]="FAIL_NATIVE_S93"
        report["error_type"]=type(exc).__name__
        report["error_text"]=str(exc)[:500]
        report["traceback"]=traceback.format_exc(limit=16)
        print(report["traceback"])
    finally:
        for panel in panels:
            try:panel.shutdown()
            except Exception:pass
        if root is not None:
            try:root.destroy()
            except Exception:pass
        REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
        for k,v in report.items():
            if k!="traceback":
                print("S93_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if report["status"]=="PASS_NATIVE_S93_G09_TK_OWNER_STATE_LATE_WORKER_CLOSED" else 1

if __name__=="__main__":
    raise SystemExit(main())
