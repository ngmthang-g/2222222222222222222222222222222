"""S53 real Windows Tk: independent blocked poll cannot hang bounded finish_close.

Test-owned F09 only; injected clock and synthetic INI, no real account/game/OS.
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
OUT = ROOT / "artifacts" / "s53"
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT / "native_tk_final_poll_lock_deadline.json"


def run() -> int:
    result = {
        "task": "S53", "status": "NOT_RUN",
        "real_game": "NOT_RUN", "signed_info": "NOT_CONNECTED",
        "f05_f06": "NOT_CONNECTED", "game_close_all": "NOT_CONNECTED",
        "pc_shutdown": "NOT_CALLED", "proxy_runtime": "EXCLUDED",
        "product_exe": "NOT_PRODUCT", "credentials_in_artifact": False,
    }
    release = threading.Event()
    root = None
    life = None
    poll = None
    stopper = None
    try:
        if os.name != "nt":
            raise RuntimeError("S53_NATIVE_WINDOWS_REQUIRED")
        import tkinter as tk
        from login_schedule_settings import read_schedule_settings
        from login_schedule_lifetime import F09ReadOnlyTabLifetime

        with tempfile.TemporaryDirectory(prefix="S53_TEST_ONLY_") as tmp:
            ini = Path(tmp) / "APPDATA" / "TLMTool" / "settings.ini"
            ini.parent.mkdir(parents=True)
            ini.write_text(
                "[Settings]\n"
                "accounts = ?|S53_DUMMY_USER|S53_DUMMY_PASSWORD|Có|opaque\n"
                "schedule_on = OPAQUE_UNKNOWN_FLAG\n"
                "schedule_close = 04:00\n"
                "schedule_open = 04:20\n"
                "shutdown_after_close = OPAQUE_POWER_FLAG\n",
                encoding="utf-8")
            old_ini = ini.read_bytes()
            cfg = read_schedule_settings(ini)
            result["readonly_settings_valid"] = cfg.status == "READ_ONLY_VALIDATED"
            root = tk.Tk()
            root.withdraw()
            label = tk.Label(root, text="")
            label.pack()
            life = F09ReadOnlyTabLifetime(
                label, cfg, now=lambda: datetime(2026, 10, 9, 3, 59, 50))
            result["unknown_saved_flags_not_autoarmed"] = (
                not life.worker.thread_alive and not life.preview.active)
            result["real_tk_and_worker_explicit_start"] = (
                life.start_preview_and_evaluation() and life.worker.thread_alive
                and life.preview.active)
            entered = threading.Event()
            poll_result = []
            errors = []
            def held_clock():
                entered.set()
                if not release.wait(3):
                    raise TimeoutError("S53_SYNTHETIC_CLOCK_TIMEOUT")
                return datetime(2026, 10, 9, 4, 21)
            life.worker._now = held_clock

            def independent_poll():
                try:
                    poll_result.append(life.worker.poll_once())
                except Exception:
                    errors.append("UNEXPECTED_POLL_EXCEPTION")
            poll = threading.Thread(
                target=independent_poll, name="S53-held-readonly-poll",
                daemon=True)
            poll.start()
            result["independent_clock_owns_final_cleanup_lock"] = (
                entered.wait(1.5) and poll.is_alive()
                and not life.worker._lock.acquire(blocking=False))

            destroys = []
            def tk_destroy():
                began = time.monotonic()
                label.destroy()
                destroys.append(time.monotonic() - began)
            root.after(40, tk_destroy)
            root.after(130, root.quit)
            root.mainloop()
            result["real_tk_destroy_nonblocking"] = (
                len(destroys) == 1 and destroys[0] < .25
                and life.closed and life.preview.status == "CLOSED")

            finished = threading.Event()
            outcomes = []
            def bounded_finish():
                try:
                    began = time.monotonic()
                    done = life.finish_close(timeout=.035)
                    outcomes.append((done, time.monotonic() - began))
                except Exception:
                    outcomes.append(("FAILED_FINISH_CLOSE", -1))
                finally:
                    finished.set()
            stopper = threading.Thread(
                target=bounded_finish, daemon=True, name="S53-finish-join")
            stopper.start()
            bounded = finished.wait(.28)
            result["finish_close_returns_within_total_deadline"] = (
                bounded and outcomes == [(False, outcomes[0][1])]
                and outcomes[0][1] < .25 if outcomes else False)
            result["pending_cancel_fence_not_cleared"] = (
                life.worker._closed and life.worker._cancel.is_set()
                and life.worker._stop_requested.is_set())

            release.set()
            poll.join(2)
            stopper.join(2)
            result["poll_does_not_emit_late_due_events"] = (
                not poll.is_alive() and not errors and poll_result == [()]
                and life.worker.blocked_occurrences() == ())
            result["eventual_join_and_permanent_shutdown"] = (
                life.finish_close(2) and life.status == "CLOSED"
                and not life.worker.thread_alive
                and not life.worker.start()
                and not life.start_preview_and_evaluation())
            root.destroy()
            root = None
            result["synthetic_settings_ini_byte_identical"] = (
                ini.read_bytes() == old_ini)
            result["no_legacy_account_side_files"] = (
                len(list(ini.parent.iterdir())) == 1)
            meta = {
                "task", "status", "real_game", "signed_info", "f05_f06",
                "game_close_all", "pc_shutdown", "proxy_runtime",
                "product_exe", "credentials_in_artifact"}
            assert all(v is True for k, v in result.items()
                       if k not in meta), "S53_NATIVE_PROOF_FAILED"
            result["status"] = "PASS_NATIVE_S53_TK_FINAL_POLL_LOCK_TOTAL_TIMEOUT"
    except Exception as exc:
        result["status"] = "FAIL_NATIVE_S53"
        result["error_type"] = type(exc).__name__
    finally:
        release.set()
        for thread in (poll, stopper):
            if thread is not None:
                thread.join(2)
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
        REPORT.write_text(
            json.dumps(result, indent=2, ensure_ascii=False),
            encoding="utf-8")
        for key, value in result.items():
            print("S53_"+key.upper()+"="+json.dumps(value, ensure_ascii=True))
    return (0 if result["status"] ==
            "PASS_NATIVE_S53_TK_FINAL_POLL_LOCK_TOTAL_TIMEOUT" else 1)


if __name__ == "__main__":
    raise SystemExit(run())
