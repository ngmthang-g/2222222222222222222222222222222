"""S48 REAL Windows Tk + two concurrent F09 stop callers, test-owned only.

Prove that stopper A cannot clear stopper B's outstanding cancel fence.
Never dispatch game open, close-all, PC shutdown, Proxy or persist accounts.
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
OUT = ROOT / "artifacts" / "s48"
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT / "native_tk_two_stoppers_fence.json"


def run() -> int:
    result = {
        "task": "S48", "status": "NOT_RUN",
        "real_game": "NOT_RUN", "signed_info": "NOT_CONNECTED",
        "f05_f06": "NOT_CONNECTED", "game_close_all": "NOT_CONNECTED",
        "pc_shutdown": "NOT_CALLED", "proxy_runtime": "EXCLUDED",
        "product_exe": "NOT_PRODUCT", "credentials_in_artifact": False,
    }
    root = None
    life = None
    threads = []
    release_join = threading.Event()
    release_first = threading.Event()
    try:
        if os.name != "nt":
            raise RuntimeError("S48_NATIVE_WINDOWS_REQUIRED")
        import tkinter as tk
        from login_schedule_settings import read_schedule_settings
        from login_schedule_lifetime import F09ReadOnlyTabLifetime

        with tempfile.TemporaryDirectory(prefix="S48_TEST_ONLY_") as td:
            ini = Path(td) / "APPDATA" / "TLMTool" / "settings.ini"
            ini.parent.mkdir(parents=True)
            ini.write_text(
                "[Settings]\n"
                "accounts = ?|S48_DUMMY_USER|S48_DUMMY_PASSWORD|Có|opaque\n"
                "schedule_on = UNKNOWN_BOOL_TOKEN\n"
                "schedule_close = 04:00\nschedule_open = 04:20\n"
                "shutdown_after_close = UNKNOWN_BOOL_TOKEN\n",
                encoding="utf-8")
            original = ini.read_bytes()
            cfg = read_schedule_settings(ini)
            result["settings_valid"] = cfg.status == "READ_ONLY_VALIDATED"
            root = tk.Tk()
            root.withdraw()
            label = tk.Label(root, text="")
            label.pack()
            life = F09ReadOnlyTabLifetime(
                label, cfg, now=lambda: datetime(2026, 10, 9, 3, 59, 50))
            result["opaque_flags_not_autoarmed"] = (
                not life.preview.active and not life.worker.thread_alive)
            result["explicit_real_tk_worker_started"] = (
                life.start_preview_and_evaluation()
                and life.worker.thread_alive
                and life.preview.has_pending_refresh)
            worker = life.worker
            old_join = worker._thread.join
            join_held = threading.Event()
            first_cleanup_held = threading.Event()
            recorded = {}
            def pausing_join(timeout=None):
                old_join(timeout)
                join_held.set()
                if not release_join.wait(3):
                    raise RuntimeError("S48_NATIVE_JOIN_HOLD_TIMEOUT")
            worker._thread.join = pausing_join

            original_end = worker._end_stop_request
            def paused_end(cleaned):
                original_end(cleaned)
                if threading.current_thread().name == "S48-A" and cleaned:
                    recorded["first_fence"] = worker._stop_requested.is_set()
                    recorded["other_caller_pending"] = (
                        worker._pending_stop_callers == 1)
                    first_cleanup_held.set()
                    if not release_first.wait(3):
                        raise RuntimeError("S48_NATIVE_FIRST_CLEANUP_TIMEOUT")
            worker._end_stop_request = paused_end
            calls = []
            def stopping(tag):
                try:
                    calls.append((tag, worker.stop(timeout=2)))
                except Exception:
                    calls.append((tag, False))

            a = threading.Thread(target=lambda: stopping("A"),
                                 name="S48-A", daemon=True)
            b = threading.Thread(target=lambda: stopping("B"),
                                 name="S48-B", daemon=True)
            threads.extend((a, b))
            a.start()
            result["first_stopper_join_held"] = join_held.wait(1.5)
            b.start()
            deadline = time.monotonic() + 1.5
            pending = False
            while time.monotonic() < deadline:
                with worker._stop_request_lock:
                    pending = worker._pending_stop_callers == 2
                if pending:
                    break
                time.sleep(.002)
            result["two_stop_requests_registered"] = pending
            release_join.set()
            result["first_cleanup_while_second_waits"] = (
                first_cleanup_held.wait(1.5)
                and recorded.get("first_fence") is True
                and recorded.get("other_caller_pending") is True)
            result["start_denied_during_second_pending_stop"] = (
                not worker.start())
            destroy_times = []
            def destroy_owned_label():
                began = time.monotonic()
                label.destroy()
                destroy_times.append(time.monotonic() - began)
            root.after(40, destroy_owned_label)
            root.after(120, root.quit)
            root.mainloop()
            result["real_tk_destroy_still_nonblocking"] = (
                len(destroy_times) == 1 and destroy_times[0] < 0.25
                and life.closed and life.preview.status == "CLOSED")
            result["permanent_closed_fence_after_tk_destroy"] = (
                worker._closed and worker._stop_requested.is_set()
                and worker._cancel.is_set())
            release_first.set()
            for thread in threads:
                thread.join(2)
            result["both_concurrent_stoppers_clean"] = (
                all(not t.is_alive() for t in threads)
                and sorted(calls) == [("A", True), ("B", True)]
                and worker._pending_stop_callers == 0)
            result["finish_close_idempotent_no_rearm"] = (
                life.finish_close(2) and life.finish_close(2)
                and not worker.thread_alive
                and not life.start_preview_and_evaluation()
                and worker._stop_requested.is_set())
            result["no_late_game_actions"] = (
                worker.blocked_occurrences() == ())
            root.destroy()
            root = None
            result["ini_byte_identical"] = ini.read_bytes() == original
            result["no_legacy_account_backup"] = (
                len(list(ini.parent.iterdir())) == 1)
            excluded = {
                "task", "status", "real_game", "signed_info", "f05_f06",
                "game_close_all", "pc_shutdown", "proxy_runtime",
                "product_exe", "credentials_in_artifact"}
            assert all(v is True for k, v in result.items()
                       if k not in excluded), "S48_NATIVE_PROOF_FAILED"
            result["status"] = "PASS_NATIVE_S48_TWO_STOPPERS_FENCE_REAL_TK"
    except Exception as exc:
        result["status"] = "FAIL_NATIVE_S48"
        result["error_type"] = type(exc).__name__
    finally:
        release_join.set()
        release_first.set()
        for thread in threads:
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
        REPORT.write_text(json.dumps(result, ensure_ascii=False, indent=2),
                          encoding="utf-8")
        for key, value in result.items():
            print("S48_" + key.upper() + "=" +
                  json.dumps(value, ensure_ascii=True))
    return 0 if result["status"] == "PASS_NATIVE_S48_TWO_STOPPERS_FENCE_REAL_TK" else 1


if __name__ == "__main__":
    raise SystemExit(run())
