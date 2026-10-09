"""S47 native Windows total stop/finish_close deadline with held lifecycle lock.

Real Tk widget/Tcl event loop and real F09 Event.wait(20) worker.
A separate stop caller pauses after joining the worker while still holding
the lifecycle lock. finish_close(timeout=0.03) must return on budget.
All account/settings values are synthetic. NO game or OS actions.
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
OUT=ROOT/"artifacts"/"s47"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"native_tk_finish_close_mutex_deadline.json"


def run()->int:
    result={
        "task":"S47","status":"NOT_RUN",
        "real_game":"NOT_RUN","signed_info":"NOT_CONNECTED",
        "f05_f06":"NOT_CONNECTED","game_close_all":"NOT_CONNECTED",
        "pc_shutdown":"NOT_CALLED","proxy_runtime":"EXCLUDED",
        "product_exe":"NOT_PRODUCT","credentials_in_artifact":False,
    }
    root=None
    life=None
    release=threading.Event()
    external=None
    try:
        if os.name!="nt":
            raise RuntimeError("S47_NATIVE_WINDOWS_REQUIRED")
        import tkinter as tk
        from login_schedule_settings import read_schedule_settings
        from login_schedule_lifetime import F09ReadOnlyTabLifetime

        with tempfile.TemporaryDirectory(prefix="S47_TEST_ONLY_") as td:
            path=Path(td)/"APPDATA"/"TLMTool"/"settings.ini"
            path.parent.mkdir(parents=True)
            path.write_text(
                "[Settings]\n"
                "accounts = ?|S47_TEST_USER|S47_TEST_DUMMY_PASSWORD|Có|opaque\n"
                "schedule_on = UNKNOWN_SAVED_VALUE\n"
                "schedule_close = 04:00\nschedule_open = 04:20\n"
                "shutdown_after_close = UNKNOWN_POWER_FLAG\n",encoding="utf-8")
            old=path.read_bytes()
            cfg=read_schedule_settings(path)
            result["e05_readonly_settings_valid"]=cfg.status=="READ_ONLY_VALIDATED"
            root=tk.Tk()
            root.withdraw()
            label=tk.Label(root,text="")
            label.pack()
            life=F09ReadOnlyTabLifetime(
                label,cfg,now=lambda:datetime(2026,10,9,3,59,50))
            result["not_autoarmed_unknown_flag"]=(
                not life.preview.active and not life.worker.thread_alive)
            result["actual_tk_worker_explicitly_started"]=(
                life.start_preview_and_evaluation()
                and life.worker.thread_alive
                and life.preview.has_pending_refresh)
            thread=life.worker._thread
            normal_join=thread.join
            entered=threading.Event()
            other_stop=[]
            def blocked_join(timeout=None):
                normal_join(timeout)
                entered.set()
                if not release.wait(3):
                    raise RuntimeError("TEST_JOIN_HOLD_LIMIT")
            thread.join=blocked_join
            def external_stopper():
                try:
                    other_stop.append(life.worker.stop(timeout=2))
                except Exception:
                    other_stop.append(False)
            external=threading.Thread(target=external_stopper,daemon=True)
            external.start()
            result["other_stopper_owns_lifecycle_lock"]=entered.wait(2)
            result["mutex_actually_contended"]=(
                not life.worker._lifecycle_lock.acquire(blocking=False))

            destroy_duration=[]
            def do_destroy():
                began=time.monotonic()
                label.destroy()
                destroy_duration.append(time.monotonic()-began)
            root.after(60,do_destroy)
            root.after(180,root.quit)
            root.mainloop()
            result["real_tk_destroy_does_not_block"]=(
                len(destroy_duration)==1 and destroy_duration[0]<0.25
                and life.closed and life.preview.status=="CLOSED")
            started=time.monotonic()
            joined=life.finish_close(timeout=0.03)
            waited=time.monotonic()-started
            result["finish_close_includes_mutex_wait_deadline"]=(
                not joined and waited<0.25)
            result["pending_stop_cancellation_remains_set"]=(
                life.worker._cancel.is_set()
                and life.worker._stop_requested.is_set())
            result["life_reports_pending_cleanup"]=life.status=="CLOSING_WORKER"
            release.set()
            external.join(2)
            result["external_stopper_finishes"]=(
                not external.is_alive() and other_stop==[True])
            result["eventual_finish_close_succeeds"]=(
                life.finish_close(timeout=2)
                and life.status=="CLOSED"
                and not life.worker.thread_alive)
            result["no_rearm_after_destroy"]=not life.start_preview_and_evaluation()
            result["no_late_due_event"]=life.worker.blocked_occurrences()==()
            root.destroy()
            root=None
            result["ini_byte_identical"]=path.read_bytes()==old
            result["no_legacy_account_backup"]=len(list(path.parent.iterdir()))==1
            assertions=[k for k in result if k not in (
                "task","status","real_game","signed_info","f05_f06",
                "game_close_all","pc_shutdown","proxy_runtime",
                "product_exe","credentials_in_artifact")]
            assert all(result[k] is True for k in assertions),"S47_NATIVE_PROOF_FAILED"
            result["status"]="PASS_NATIVE_S47_FINISH_CLOSE_TOTAL_TIMEOUT_LOCK_BUDGET"
    except Exception as exc:
        result["status"]="FAIL_NATIVE_S47"
        result["error_type"]=type(exc).__name__
    finally:
        release.set()
        if external is not None:
            external.join(2)
        if life is not None:
            try:
                life.close()
                life.finish_close(2)
            except Exception:
                pass
        if root is not None:
            try:
                root.destroy()
            except Exception:
                pass
        REPORT.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
        for k,v in result.items():
            print("S47_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if result["status"]=="PASS_NATIVE_S47_FINISH_CLOSE_TOTAL_TIMEOUT_LOCK_BUDGET" else 1


if __name__=="__main__":
    raise SystemExit(run())
