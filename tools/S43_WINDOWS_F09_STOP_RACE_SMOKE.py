"""S43 native Windows deterministic F09 worker start/stop race regression.

Proof uses actual threads and Event.wait; injected clock and join pauses are
TEST-owned only. No F05/F06, no signed Info, no game close/open/poweroff.
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "artifacts" / "s43"
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT / "windows_worker_stop_races.json"


def run() -> int:
    r = {
        "task":"S43", "status":"NOT_RUN",
        "real_game":"NOT_RUN", "signed_info":"NOT_CONNECTED",
        "f05_f06_real_handlers":"NOT_CONNECTED",
        "close_all":"NOT_CONNECTED", "pc_shutdown":"NOT_CALLED",
        "proxy_runtime":"EXCLUDED", "product_exe":"NOT_PRODUCT",
        "credentials_in_report":False,
    }
    worker = None
    release_clock = None
    resume_stop = None
    stopping_thread = None
    try:
        if os.name != "nt":
            raise RuntimeError("WINDOWS_NATIVE_REQUIRED")
        from login_schedule_settings import read_schedule_settings
        from login_schedule_worker import F09ScheduleEvaluationWorker

        with tempfile.TemporaryDirectory(prefix="S43_TEST_ONLY_") as td:
            ini = Path(td)/"APPDATA"/"TLMTool"/"settings.ini"
            ini.parent.mkdir(parents=True)
            ini.write_text(
                "[Settings]\n"
                "accounts = ?|S43_DUMMY_USER|S43_DUMMY_SECRET|Có|opaque\n"
                "schedule_on = UNKNOWN_TRUE_TOKEN\n"
                "schedule_close = 04:00\nschedule_open = 04:20\n"
                "shutdown_after_close = UNKNOWN_POWER_FLAG\n", encoding="utf-8")
            before = ini.read_bytes()
            config = read_schedule_settings(ini)
            r["real_e05_readonly_config"] = config.status=="READ_ONLY_VALIDATED"

            # 1. Stop successfully joined old worker but is deliberately
            # stalled BEFORE final cleanup. Concurrent start must be DENIED.
            now = [datetime(2026,10,9,3,59,50)]
            worker = F09ScheduleEvaluationWorker(config, now=lambda:now[0])
            r["old_worker_started"] = worker.start()
            original_join = worker._thread.join
            joined = threading.Event()
            resume_stop = threading.Event()
            stop_result = []
            def paused_join(timeout=None):
                original_join(timeout)
                joined.set()
                if not resume_stop.wait(2):
                    raise RuntimeError("TEST_STOP_PAUSE_TIMEOUT")
            worker._thread.join = paused_join
            def stop_old():
                try:
                    stop_result.append(worker.stop())
                except Exception:
                    stop_result.append(False)
            stopping_thread = threading.Thread(target=stop_old, daemon=True)
            stopping_thread.start()
            r["old_worker_joined_before_cleanup"] = joined.wait(2)
            r["concurrent_start_refused_while_stop_finishing"] = (
                not worker.start() and not worker.active)
            resume_stop.set()
            stopping_thread.join(2)
            r["old_worker_cleaned_without_resurrection"] = (
                not stopping_thread.is_alive() and stop_result==[True]
                and not worker.thread_alive and worker.status=="STOPPED")
            r["restart_after_stop_valid"] = worker.start()
            r["regular_shutdown_after_restart"] = worker.shutdown() and not worker.thread_alive

            # 2. now() deliberately stalls INSIDE poll_once holding _lock.
            # A stop(timeout=0.02) MUST return promptly instead of hanging
            # while trying to acquire the stalled clock lock.
            release_clock = threading.Event()
            entered = threading.Event()
            first = [True]
            def blocked_now():
                if first[0]:
                    first[0]=False
                    return datetime(2026,10,9,3,59,50)
                entered.set()
                if not release_clock.wait(3):
                    raise RuntimeError("TEST_BLOCKED_CLOCK_TIMEOUT")
                return datetime(2026,10,9,4,20,10)
            worker = F09ScheduleEvaluationWorker(config, now=blocked_now)
            real_wait = worker._cancel.wait
            worker._cancel.wait = lambda timeout: real_wait(0.01)
            r["blocked_clock_worker_started"] = worker.start()
            r["real_thread_entered_blocked_time_source"] = entered.wait(2)
            started = time.monotonic()
            timed_out = worker.stop(timeout=0.02)
            r["timeout_does_not_wait_for_stalled_lock"] = (
                not timed_out and time.monotonic()-started<0.35
                and worker._cancel.is_set() and worker._status=="STOPPING")
            r["restart_refused_while_old_worker_alive"] = not worker.start()
            release_clock.set()
            r["old_clock_worker_eventually_joins"] = (
                worker.stop(timeout=2) and not worker.thread_alive)
            r["blocked_events_never_turn_into_actions"] = (
                worker.blocked_occurrences()==())
            r["worker_shutdown_permanent"] = worker.shutdown() and not worker.start()
            r["settings_ini_byte_identical"] = ini.read_bytes()==before
            r["no_settings_backup"] = len(list(ini.parent.iterdir()))==1

            required = [k for k in r if k not in (
                "task","status","real_game","signed_info",
                "f05_f06_real_handlers","close_all","pc_shutdown",
                "proxy_runtime","product_exe","credentials_in_report")]
            assert all(r[k] is True for k in required), "S43_NATIVE_CHECK_FAILED"
            r["status"]="PASS_NATIVE_S43_WORKER_STOP_RACES_FIXED"
    except Exception as exc:
        r["status"]="FAIL_NATIVE_S43"
        r["error_type"]=type(exc).__name__
    finally:
        if resume_stop is not None:
            resume_stop.set()
        if release_clock is not None:
            release_clock.set()
        if stopping_thread is not None:
            stopping_thread.join(2)
        if worker is not None:
            try:
                worker.shutdown()
            except Exception:
                pass
        REPORT.write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding="utf-8")
        for k,v in r.items():
            print("S43_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if r["status"]=="PASS_NATIVE_S43_WORKER_STOP_RACES_FIXED" else 1


if __name__=="__main__":
    raise SystemExit(run())
