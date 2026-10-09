"""S45 real Windows Tk Label/after and F09 worker joint tab teardown.

Real Tcl <Destroy> and real Python threading.Event.wait are exercised with
test-owned HH:MM settings and a test-only stalled clock provider. No live
game, login, close-all, shutdown, license bypass or Proxy actions.
"""
from __future__ import annotations

from datetime import datetime
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s45"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"windows_tk_worker_lifetime.json"


def run()->int:
    facts={
        "task":"S45","status":"NOT_RUN",
        "real_game":"NOT_RUN","real_signed_info":"NOT_CONNECTED",
        "f05_f06":"NOT_CONNECTED","real_close_all":"NOT_CONNECTED",
        "shutdown_pc":"NOT_CALLED","proxy_runtime":"EXCLUDED",
        "product_exe":"NOT_PRODUCT","secrets_in_report":False,
    }
    root=None
    lifetime=None
    release_clock=threading.Event()
    try:
        if os.name!="nt":
            raise RuntimeError("NATIVE_WINDOWS_REQUIRED")
        import tkinter as tk
        from login_schedule_settings import read_schedule_settings
        from login_schedule_lifetime import F09ReadOnlyTabLifetime

        with tempfile.TemporaryDirectory(prefix="S45_TEST_ONLY_") as td:
            path=Path(td)/"TLMTool"/"settings.ini"
            path.parent.mkdir(parents=True)
            path.write_text(
                "[Settings]\n"
                "accounts = ?|S45_DUMMY_USER|S45_DUMMY_SECRET|Có|opaque\n"
                "schedule_on = UNKNOWN_BOOLEAN\n"
                "schedule_close = 04:00\nschedule_open = 04:20\n"
                "shutdown_after_close = UNVERIFIED_POWER\n",encoding="utf-8")
            before=path.read_bytes()
            settings=read_schedule_settings(path)
            facts["read_real_e05_f09_settings"]=settings.status=="READ_ONLY_VALIDATED"
            root=tk.Tk()
            root.withdraw()
            label=tk.Label(root,text="")
            label.pack()
            current=datetime(2026,10,9,3,59,50)
            entered_clock=threading.Event()
            calls=[0]
            def worker_now():
                calls[0]+=1
                if calls[0]==1:
                    return current
                entered_clock.set()
                release_clock.wait(4)
                return datetime(2026,10,9,4,21,10)
            lifetime=F09ReadOnlyTabLifetime(
                label,settings,now=lambda:current,worker_now=worker_now)
            facts["not_auto_started_from_unknown_bool"]=(
                not lifetime.preview.active and not lifetime.worker.thread_alive)
            original_wait=lifetime.worker._cancel.wait
            # Injected acceleration ONLY in test; production always passes 20.
            wait_arguments=[]
            def accelerated_wait(timeout):
                wait_arguments.append(timeout)
                return original_wait(0.01)
            lifetime.worker._cancel.wait=accelerated_wait
            facts["actual_tk_label_and_worker_both_started"]=(
                lifetime.start_preview_and_evaluation()
                and lifetime.preview.has_pending_refresh
                and lifetime.worker.thread_alive)
            facts["countdown_real_tk_text"]=(
                "Tắt 04:00 09/10 còn" in str(label.cget("text")))
            facts["real_worker_entered_blocking_provider"]=entered_clock.wait(2)
            facts["worker_uses_original_20_seconds_argument"]=(
                bool(wait_arguments) and all(x==20 for x in wait_arguments))
            duration=[]
            # Native Tcl mainloop calls Label.destroy; both independent
            # component handlers must run without blocking on stalled now().
            def destroy_label():
                start=time.monotonic()
                label.destroy()
                duration.append(time.monotonic()-start)
            root.after(60,destroy_label)
            root.after(200,root.quit)
            root.mainloop()
            facts["actual_tk_destroy_does_not_wait_for_blocked_worker"]=(
                len(duration)==1 and duration[0]<0.35)
            facts["both_preview_and_worker_cancelled_on_destroy"]=(
                lifetime.closed and lifetime.preview.status=="CLOSED"
                and not lifetime.preview.active and not lifetime.preview.has_pending_refresh
                and lifetime.worker._cancel.is_set())
            facts["worker_still_can_finish_async_after_destroy"]=(
                lifetime.status in ("CLOSING_WORKER","CLOSED_PENDING_JOIN","CLOSED"))
            release_clock.set()
            facts["worker_join_after_clock_unblock"]=(
                lifetime.finish_close(2)
                and not lifetime.worker.thread_alive
                and lifetime.status=="CLOSED")
            facts["no_post_close_blocked_events"]=lifetime.worker.blocked_occurrences()==()
            facts["no_restart_after_widget_destroy"]=not lifetime.start_preview_and_evaluation()
            root.destroy()
            root=None
            facts["settings_original_bytes_unchanged"]=path.read_bytes()==before
            facts["no_ini_backups"]=len(list(path.parent.iterdir()))==1
            required=[k for k in facts if k not in (
                "task","status","real_game","real_signed_info","f05_f06",
                "real_close_all","shutdown_pc","proxy_runtime","product_exe",
                "secrets_in_report")]
            assert all(facts[k] is True for k in required),"S45_NATIVE_CHECK_FAILED"
            facts["status"]="PASS_NATIVE_S45_REAL_TK_WORKER_DESTROY_ASYNC_CANCEL"
    except Exception as exc:
        facts["status"]="FAIL_NATIVE_S45"
        facts["error_type"]=type(exc).__name__
    finally:
        release_clock.set()
        if lifetime is not None:
            try:
                lifetime.close()
                lifetime.finish_close(2)
            except Exception:
                pass
        if root is not None:
            try:
                root.destroy()
            except Exception:
                pass
        REPORT.write_text(json.dumps(facts,ensure_ascii=False,indent=2),encoding="utf-8")
        for key,value in facts.items():
            print("S45_"+key.upper()+"="+json.dumps(value,ensure_ascii=True))
    return 0 if facts["status"]=="PASS_NATIVE_S45_REAL_TK_WORKER_DESTROY_ASYNC_CANCEL" else 1


if __name__=="__main__":
    raise SystemExit(run())
