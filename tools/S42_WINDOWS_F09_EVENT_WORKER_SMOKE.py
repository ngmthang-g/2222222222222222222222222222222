"""S42 genuine Windows threading.Event.wait(20) worker in TEST-owned sandbox.

Uses injected test-only acceleration to exercise due-event evaluation without
waiting real-time 20s; separately verifies standard real Event.wait stop wakes
instantly. No game, shutdown, INI mutation, credentials, Proxy or product EXE.
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
OUT=ROOT/"artifacts"/"s42"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"windows_f09_event_wait_blocked_only.json"


def run()->int:
    r={
        "task":"S42","status":"NOT_RUN",
        "real_game":"NOT_RUN",
        "signed_info":"NOT_CONNECTED",
        "f05_f06_handlers":"NOT_CONNECTED",
        "close_all":"NOT_CONNECTED",
        "shutdown_pc":"NOT_CALLED",
        "proxy_runtime":"EXCLUDED",
        "product_exe":"NOT_BUILT",
        "passwords_in_report":False,
    }
    worker=None
    worker2=None
    try:
        if os.name!="nt":
            raise RuntimeError("S42_Windows_native_only")
        from login_schedule_settings import read_schedule_settings
        from login_schedule_worker import F09ScheduleEvaluationWorker, BLOCKED_ACTION
        from login_schedule_clock import WORKER_CHECK_SECONDS

        with tempfile.TemporaryDirectory(prefix="S42_TEST_ONLY_") as td:
            config=Path(td)/"APPDATA"/"TLMTool"/"settings.ini"
            config.parent.mkdir(parents=True)
            config.write_text(
                "[Settings]\n"
                "accounts = ?|S42_TEST_USER|S42_DUMMY_SECRET|Có|opaque\n"
                "schedule_on = ORIGINAL_UNVERIFIED_TRUE_TOKEN\n"
                "schedule_close = 04:00\n"
                "schedule_open = 04:20\n"
                "shutdown_after_close = UNKNOWN_PC_FLAG\n",
                encoding="utf-8")
            before=config.read_bytes()
            settings=read_schedule_settings(config)
            r["f09_e05_readonly_settings"]=settings.status=="READ_ONLY_VALIDATED"
            now=[datetime(2026,10,9,3,59,50)]
            worker=F09ScheduleEvaluationWorker(settings,now=lambda:now[0])
            r["not_autostarted_from_unknown_on_flag"]=(
                not worker.active and not worker.thread_alive)
            r["exact_original_cadence_constant"]=WORKER_CHECK_SECONDS==20
            original_wait=worker._cancel.wait
            called=[]
            fired=threading.Event()

            def test_accelerated_wait(timeout):
                # Actual production code passes 20, this TEST shortens real
                # Event.wait only to reach deadline during native smoke.
                called.append(timeout)
                result=original_wait(0.02)
                fired.set()
                return result

            worker._cancel.wait=test_accelerated_wait
            r["real_background_thread_started"]=worker.start() and worker.thread_alive
            r["duplicate_worker_start_prevented"]=not worker.start()
            now[0]=datetime(2026,10,9,4,20,10)
            deadline=time.monotonic()+3
            while worker.ticks==0 and time.monotonic()<deadline:
                time.sleep(0.005)
            first=worker.blocked_occurrences()
            r["real_worker_observed_20s_wait_argument"]=(
                bool(called) and all(v==20 for v in called))
            r["real_worker_recorded_both_blocked_events_once"]=(
                len(first)==2
                and [i.kind for i in first]==["close","open"]
                and all(i.status==BLOCKED_ACTION for i in first))
            ticks_before=worker.ticks
            time.sleep(0.06)
            r["no_duplicate_events_on_subsequent_worker_polls"]=(
                worker.ticks>ticks_before and len(worker.blocked_occurrences())==2)
            r["safe_worker_stop_joins"]=worker.stop() and not worker.thread_alive
            r["restart_uses_current_time_no_catchup"]=worker.start()
            time.sleep(0.04)
            r["restart_did_not_replay_past_events"]=(
                worker.blocked_occurrences()==())
            r["shutdown_blocks_later_restarts"]=(
                worker.shutdown() and not worker.start()
                and not worker.thread_alive)

            # Second proof: genuinely unmodified 20-second Event.wait() is
            # awakened promptly by cancel rather than requiring 20s.
            worker2=F09ScheduleEvaluationWorker(settings,now=lambda:now[0])
            r["real_unmodified_event_worker_started"]=worker2.start()
            start=time.monotonic()
            r["real_unmodified_wait_interruptible"]=(
                worker2.stop() and not worker2.thread_alive
                and time.monotonic()-start<2)
            r["original_ini_byte_identical"]=config.read_bytes()==before
            r["no_settings_backup_created"]=len(list(config.parent.iterdir()))==1
            assert all(v is True for k,v in r.items() if k not in (
                "task","status","real_game","signed_info","f05_f06_handlers",
                "close_all","shutdown_pc","proxy_runtime","product_exe",
                "passwords_in_report")), "S42_NATIVE_CHECK_FAILED"
            r["status"]="PASS_NATIVE_S42_REAL_EVENT_WAIT20_BLOCKED_ONLY"
    except Exception as exc:
        r["status"]="FAIL_NATIVE_S42"
        r["error_type"]=type(exc).__name__
        # Exception messages suppressed as they could contain credentials.
    finally:
        for obj in (worker,worker2):
            if obj is not None:
                try:
                    obj.shutdown()
                except Exception:
                    pass
        REPORT.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
        for k,v in r.items():
            print("S42_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if r["status"]=="PASS_NATIVE_S42_REAL_EVENT_WAIT20_BLOCKED_ONLY" else 1


if __name__=="__main__":
    raise SystemExit(run())
