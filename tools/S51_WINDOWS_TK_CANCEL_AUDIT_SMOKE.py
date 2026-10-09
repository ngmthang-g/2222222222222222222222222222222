"""S51 native Windows real Tk destroys Label mid blocked-only audit materialization.

Original file and authenticated gameplay remain untouched; synthetic INI only.
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
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "artifacts" / "s51"
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT / "native_tk_cancel_during_audit_materialization.json"


def run() -> int:
    result = {
        "task": "S51", "status": "NOT_RUN",
        "real_game": "NOT_RUN", "signed_info": "NOT_CONNECTED",
        "f05_f06": "NOT_CONNECTED", "game_close_all": "NOT_CONNECTED",
        "pc_shutdown": "NOT_CALLED", "proxy_runtime": "EXCLUDED",
        "product_exe": "NOT_PRODUCT", "credentials_in_artifact": False,
    }
    root = None
    life = None
    thread = None
    release = threading.Event()
    try:
        if os.name != "nt":
            raise RuntimeError("S51_REAL_WINDOWS_REQUIRED")
        import tkinter as tk
        from login_schedule_settings import read_schedule_settings
        from login_schedule_lifetime import F09ReadOnlyTabLifetime
        from login_schedule_worker import BlockedScheduleOccurrence, BLOCKED_ACTION

        with tempfile.TemporaryDirectory(prefix="S51_TEST_ONLY_") as folder:
            ini = Path(folder)/"APPDATA"/"TLMTool"/"settings.ini"
            ini.parent.mkdir(parents=True)
            ini.write_text(
                "[Settings]\n"
                "accounts = ?|S51_DUMMY_USER|S51_DUMMY_PASS|Có|opaque\n"
                "schedule_on = OPAQUE_UNKNOWN_BOOLEAN\n"
                "schedule_close = 04:00\nschedule_open = 04:20\n"
                "shutdown_after_close = OPAQUE_POWER_FLAG\n", encoding="utf-8")
            prior_bytes = ini.read_bytes()
            cfg = read_schedule_settings(ini)
            result["verified_readonly_settings"] = (
                cfg.status == "READ_ONLY_VALIDATED")
            current = [datetime(2026, 10, 9, 3, 59, 50)]
            root = tk.Tk()
            root.withdraw()
            label = tk.Label(root, text="")
            label.pack()
            life = F09ReadOnlyTabLifetime(
                label, cfg, now=lambda: current[0])
            result["unknown_flags_not_autoarmed"] = (
                not life.worker.thread_alive and not life.preview.active)
            result["explicit_real_worker_and_tk_start"] = (
                life.start_preview_and_evaluation()
                and life.worker.thread_alive and life.preview.active)

            current[0] = datetime(2026, 10, 9, 4, 21)
            entered = threading.Event()
            results = []
            problems = []
            factory_real = BlockedScheduleOccurrence
            def paused_factory(*args, **kwargs):
                entered.set()
                if not release.wait(2):
                    raise RuntimeError("S51_NATIVE_FACTORY_PAUSE_EXPIRED")
                return factory_real(*args, **kwargs)
            def do_poll():
                try:
                    results.append(life.worker.poll_once())
                except Exception:
                    problems.append("EXCEPTION_SUPPRESSED")
            with patch("login_schedule_worker.BlockedScheduleOccurrence",
                       side_effect=paused_factory):
                thread = threading.Thread(
                    target=do_poll, name="S51-due-audit-test", daemon=True)
                thread.start()
                result["real_poll_after_clock_before_audit_paused"] = (
                    entered.wait(1.5)
                    and thread.is_alive())
                destroyed = []
                def destroy_label():
                    before = time.monotonic()
                    label.destroy()
                    destroyed.append(time.monotonic() - before)
                root.after(40, destroy_label)
                root.after(135, root.quit)
                root.mainloop()
                result["real_tk_destroy_no_lock_wait"] = (
                    len(destroyed) == 1 and destroyed[0] < .25
                    and life.closed and life.preview.status == "CLOSED")
                result["worker_cancelled_during_record_projection"] = (
                    life.worker._cancel.is_set()
                    and life.worker._closed
                    and life.worker._stop_requested.is_set())
                release.set()
                thread.join(2)
            result["no_late_due_records_after_tk_destroy"] = (
                not thread.is_alive()
                and not problems
                and results == [()]
                and life.worker.blocked_occurrences() == ())
            result["worker_finishes_without_rearming"] = (
                life.finish_close(2)
                and not life.worker.thread_alive
                and not life.worker.start()
                and not life.start_preview_and_evaluation())

            root.destroy()
            root = None
            result["synthetic_ini_unchanged"] = ini.read_bytes() == prior_bytes
            result["no_account_file_written"] = (
                len(list(ini.parent.iterdir())) == 1)
            exempt = {
                "task", "status", "real_game", "signed_info", "f05_f06",
                "game_close_all", "pc_shutdown", "proxy_runtime",
                "product_exe", "credentials_in_artifact"}
            assert all(value is True for key, value in result.items()
                       if key not in exempt), "S51_NATIVE_PROOF_FAILED"
            result["status"] = "PASS_NATIVE_S51_TK_CANCEL_DURING_DUE_AUDIT"
    except Exception as exc:
        result["status"] = "FAIL_NATIVE_S51"
        result["error_type"] = type(exc).__name__
    finally:
        release.set()
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
        REPORT.write_text(json.dumps(result, indent=2, ensure_ascii=False),
                          encoding="utf-8")
        for key, value in result.items():
            print("S51_"+key.upper()+"="+json.dumps(value, ensure_ascii=True))
    return 0 if result["status"] == "PASS_NATIVE_S51_TK_CANCEL_DURING_DUE_AUDIT" else 1


if __name__ == "__main__":
    raise SystemExit(run())
