"""S54 native Windows Tk: permanent close status survives incomplete stop cleanup.

Real Tk Label.destroy, real read-only worker, independent blocked poll clock.
Synthetic credentials are confined to a TemporaryDirectory; no side effects.
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
OUT = ROOT / "artifacts" / "s54"
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT / "native_tk_closed_status_stop_deadline.json"


def run() -> int:
    result = {
        "task": "S54", "status": "NOT_RUN",
        "real_game": "NOT_RUN", "signed_info": "NOT_CONNECTED",
        "f05_f06": "NOT_CONNECTED", "game_close_all": "NOT_CONNECTED",
        "pc_shutdown": "NOT_CALLED", "proxy_runtime": "EXCLUDED",
        "product_exe": "NOT_PRODUCT", "credentials_in_artifact": False,
    }
    root = None
    life = None
    reader = None
    release = threading.Event()
    try:
        if os.name != "nt":
            raise RuntimeError("S54_REAL_WINDOWS_REQUIRED")
        import tkinter as tk
        from login_schedule_settings import read_schedule_settings
        from login_schedule_lifetime import F09ReadOnlyTabLifetime
        with tempfile.TemporaryDirectory(prefix="S54_TEST_ONLY_") as tmp:
            ini = Path(tmp) / "APPDATA" / "TLMTool" / "settings.ini"
            ini.parent.mkdir(parents=True)
            ini.write_text(
                "[Settings]\n"
                "accounts = ?|S54_TEST_USER|S54_DUMMY_PASSWORD|Có|opaque\n"
                "schedule_on = UNVERIFIED_FLAG\n"
                "schedule_close = 04:00\nschedule_open = 04:20\n"
                "shutdown_after_close = UNVERIFIED_POWER\n",
                encoding="utf-8")
            prior = ini.read_bytes()
            cfg = read_schedule_settings(ini)
            result["readonly_schedule_valid"] = cfg.status == "READ_ONLY_VALIDATED"
            root = tk.Tk()
            root.withdraw()
            label = tk.Label(root, text="")
            label.pack()
            life = F09ReadOnlyTabLifetime(
                label, cfg, now=lambda: datetime(2026, 10, 9, 3, 59, 50))
            result["opaque_flags_do_not_autoarm"] = (
                not life.worker.thread_alive and not life.preview.active)
            result["real_tk_and_worker_explicitly_started"] = (
                life.start_preview_and_evaluation()
                and life.worker.thread_alive and life.preview.active)
            entered = threading.Event()
            events = []
            errors = []
            def held_clock():
                entered.set()
                if not release.wait(3):
                    raise TimeoutError("S54_SYNTHETIC_CLOCK_TEST_TIMEOUT")
                return datetime(2026, 10, 9, 4, 21)
            life.worker._now = held_clock
            def poll():
                try:
                    events.append(life.worker.poll_once())
                except Exception:
                    errors.append("UNEXPECTED_SYNTHETIC_POLL_EXCEPTION")
            reader = threading.Thread(
                target=poll, daemon=True, name="S54-test-only-held-poll")
            reader.start()
            result["independent_poll_holds_cleanup_lock"] = (
                entered.wait(1.5) and reader.is_alive()
                and not life.worker._lock.acquire(blocking=False))
            durations = []
            def destroy():
                began = time.monotonic()
                label.destroy()
                durations.append(time.monotonic()-began)
            root.after(40, destroy)
            root.after(125, root.quit)
            root.mainloop()
            result["real_tk_destroy_nonblocking"] = (
                len(durations) == 1 and durations[0] < .25
                and life.closed and life.preview.status == "CLOSED")
            before = time.monotonic()
            finished = life.finish_close(timeout=.035)
            elapsed = time.monotonic() - before
            result["final_cleanup_deadline_bounded"] = (
                finished is False and elapsed < .25)
            result["worker_stays_closed_during_final_lock_timeout"] = (
                life.worker.status == "CLOSED"
                and life.worker._closed
                and life.worker._stop_requested.is_set()
                and life.worker._cancel.is_set())
            result["lifetime_reports_pending_cleanup_separately"] = (
                life.status in ("CLOSING_WORKER", "CLOSED_PENDING_JOIN"))
            release.set()
            reader.join(2)
            result["no_due_audit_after_destroy"] = (
                not reader.is_alive() and not errors and events == [()]
                and life.worker.blocked_occurrences() == ())
            result["eventual_cleanup_remains_closed_and_unarmed"] = (
                life.finish_close(2)
                and life.worker.status == "CLOSED"
                and not life.worker.thread_alive
                and not life.worker.start()
                and not life.start_preview_and_evaluation())
            root.destroy()
            root = None
            result["settings_ini_byte_identical"] = ini.read_bytes() == prior
            result["no_extra_account_files"] = (
                len(list(ini.parent.iterdir())) == 1)
            metadata = {
                "task", "status", "real_game", "signed_info", "f05_f06",
                "game_close_all", "pc_shutdown", "proxy_runtime",
                "product_exe", "credentials_in_artifact"}
            assert all(val is True for k, val in result.items()
                       if k not in metadata), "S54_NATIVE_PROOF_FAILED"
            result["status"] = "PASS_NATIVE_S54_PERMANENT_CLOSE_STOP_TIMEOUT"
    except Exception as exc:
        result["status"] = "FAIL_NATIVE_S54"
        result["error_type"] = type(exc).__name__
    finally:
        release.set()
        if reader is not None:
            reader.join(2)
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
        REPORT.write_text(json.dumps(result, indent=2, ensure_ascii=False),
                          encoding="utf-8")
        for key, value in result.items():
            print("S54_"+key.upper()+"="+json.dumps(value, ensure_ascii=True))
    return 0 if result["status"] == "PASS_NATIVE_S54_PERMANENT_CLOSE_STOP_TIMEOUT" else 1


if __name__ == "__main__":
    raise SystemExit(run())
