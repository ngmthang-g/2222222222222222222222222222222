"""S46 actual Windows Tk Destroy while worker lifecycle mutex is contended.

Real Tcl Tk Label.after/Destroy and real worker threads. An external stopper
owns worker._lifecycle_lock during join; Tk close must still signal cancel
immediately instead of waiting for the lifecycle mutex. All data test-owned.
NO game/process/PC shutdown, Proxy, product EXE or account config mutation.
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
OUT=ROOT/"artifacts"/"s46"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"windows_tk_lifecycle_mutex_cancel.json"


def run()->int:
    facts={
        "task":"S46","status":"NOT_RUN",
        "real_game":"NOT_RUN","signed_info":"NOT_CONNECTED",
        "f05_f06":"NOT_CONNECTED","close_all":"NOT_CONNECTED",
        "shutdown_pc":"NOT_CALLED","proxy_runtime":"EXCLUDED",
        "product_exe":"NOT_PRODUCT","credential_data_in_report":False,
    }
    root=None
    life=None
    release_join=threading.Event()
    stopper=None
    try:
        if os.name!="nt":
            raise RuntimeError("NATIVE_WINDOWS_ONLY")
        import tkinter as tk
        from login_schedule_lifetime import F09ReadOnlyTabLifetime
        from login_schedule_settings import read_schedule_settings

        with tempfile.TemporaryDirectory(prefix="S46_TEST_ONLY_") as td:
            ini=Path(td)/"TLMTool"/"settings.ini"
            ini.parent.mkdir(parents=True)
            ini.write_text(
                "[Settings]\n"
                "accounts = ?|S46_DUMMY_USER|S46_DUMMY_SECRET|Có|opaque\n"
                "schedule_on = UNVERIFIED_BOOL\n"
                "schedule_close = 04:00\n"
                "schedule_open = 04:20\n"
                "shutdown_after_close = UNKNOWN_POWER\n",encoding="utf-8")
            before=ini.read_bytes()
            cfg=read_schedule_settings(ini)
            facts["real_readonly_config"]=cfg.status=="READ_ONLY_VALIDATED"
            root=tk.Tk()
            root.withdraw()
            lbl=tk.Label(root,text="")
            lbl.pack()
            now=datetime(2026,10,9,3,59,50)
            life=F09ReadOnlyTabLifetime(lbl,cfg,now=lambda:now)
            facts["does_not_autostart_from_opaque_flag"]=(
                not life.preview.active and not life.worker.active)
            facts["real_tk_preview_and_worker_started"]=(
                life.start_preview_and_evaluation()
                and life.worker.thread_alive
                and life.preview.has_pending_refresh)
            ident=life.preview._after_id
            facts["real_preview_initial_label"]=(
                "Tắt 04:00 09/10 còn" in str(lbl.cget("text")))
            target=life.worker._thread
            join_real=target.join
            joined=threading.Event()
            stopped=[]
            def held_join(timeout=None):
                join_real(timeout)
                joined.set()
                if not release_join.wait(2):
                    raise RuntimeError("S46_TEST_JOIN_TIMEOUT")
            target.join=held_join
            def stop_other_thread():
                try:
                    stopped.append(life.worker.stop(timeout=2))
                except Exception:
                    stopped.append(False)
            stopper=threading.Thread(target=stop_other_thread,daemon=True)
            stopper.start()
            facts["independent_stop_owns_lifecycle_mutex"]=joined.wait(2)
            facts["lifecycle_lock_contended"]=(
                not life.worker._lifecycle_lock.acquire(blocking=False))
            durations=[]
            def destroy_owned_label():
                start=time.monotonic()
                lbl.destroy()
                durations.append(time.monotonic()-start)
            root.after(50,destroy_owned_label)
            root.after(175,root.quit)
            root.mainloop()
            facts["real_tk_destroy_returns_promptly_despite_stop_join"]=(
                len(durations)==1 and durations[0]<0.35)
            facts["both_worker_cancel_and_preview_closed"]=(
                life.closed and life.worker._cancel.is_set()
                and not life.preview.active and life.preview.status=="CLOSED")
            facts["tk_after_id_cancelled"]=(
                str(ident) not in
                tuple(str(x) for x in root.tk.call("after","info")))
            facts["rearm_refused_after_tk_destroy"]=(
                not life.start_preview_and_evaluation())
            release_join.set()
            stopper.join(2)
            facts["existing_stopper_completed_without_deadlock"]=(
                not stopper.is_alive() and stopped==[True])
            facts["final_worker_join_after_gui_teardown"]=(
                life.finish_close(2)
                and not life.worker.thread_alive
                and life.status=="CLOSED")
            facts["no_blocked_events_after_teardown"]=(
                life.worker.blocked_occurrences()==())
            root.destroy()
            root=None
            facts["original_ini_byte_identical"]=ini.read_bytes()==before
            facts["no_settings_backup"]=len(list(ini.parent.iterdir()))==1
            keys=[k for k in facts if k not in (
                "task","status","real_game","signed_info","f05_f06",
                "close_all","shutdown_pc","proxy_runtime","product_exe",
                "credential_data_in_report")]
            assert all(facts[k] is True for k in keys),"S46_NATIVE_ASSERT_FAILED"
            facts["status"]="PASS_NATIVE_S46_TK_DESTROY_LIFECYCLE_LOCK_NO_HANG"
    except Exception as exc:
        facts["status"]="FAIL_NATIVE_S46"
        facts["error_type"]=type(exc).__name__
    finally:
        release_join.set()
        if stopper is not None:
            stopper.join(2)
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
        REPORT.write_text(json.dumps(facts,indent=2,ensure_ascii=False),encoding="utf-8")
        for key,value in facts.items():
            print("S46_"+key.upper()+"="+json.dumps(value,ensure_ascii=True))
    return 0 if facts["status"]=="PASS_NATIVE_S46_TK_DESTROY_LIFECYCLE_LOCK_NO_HANG" else 1


if __name__=="__main__":
    raise SystemExit(run())
