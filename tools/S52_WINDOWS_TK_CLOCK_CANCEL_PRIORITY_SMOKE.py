"""S52: REAL Windows Tk Destroy during an injected F09 clock-provider failure.

Only test-owned read-only schedule evaluation, not live game/credentials.
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
OUT = ROOT / "artifacts" / "s52"
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT / "native_tk_exception_after_shutdown.json"


def run() -> int:
    report = {
        "task": "S52", "status": "NOT_RUN",
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
            raise RuntimeError("S52_NATIVE_WINDOWS_REQUIRED")
        import tkinter as tk
        from login_schedule_settings import read_schedule_settings
        from login_schedule_lifetime import F09ReadOnlyTabLifetime

        with tempfile.TemporaryDirectory(prefix="S52_TEST_ONLY_") as folder:
            ini = Path(folder) / "APPDATA" / "TLMTool" / "settings.ini"
            ini.parent.mkdir(parents=True)
            ini.write_text(
                "[Settings]\n"
                "accounts = ?|S52_TEST_USER|S52_DUMMY_PASS|Có|opaque\n"
                "schedule_on = UNKNOWN_OPAQUE_TOKEN\n"
                "schedule_close = 04:00\n"
                "schedule_open = 04:20\n"
                "shutdown_after_close = UNKNOWN_POWER_TOKEN\n",
                encoding="utf-8")
            original = ini.read_bytes()
            cfg = read_schedule_settings(ini)
            report["settings_are_readonly_validated"] = (
                cfg.status == "READ_ONLY_VALIDATED")
            root = tk.Tk()
            root.withdraw()
            label = tk.Label(root, text="")
            label.pack()
            life = F09ReadOnlyTabLifetime(
                label, cfg, now=lambda: datetime(2026, 10, 9, 3, 59, 50))
            report["opaque_flags_never_autoarm"] = (
                not life.worker.thread_alive and not life.preview.active)
            report["explicit_real_tk_and_worker_start"] = (
                life.start_preview_and_evaluation()
                and life.preview.active and life.worker.thread_alive)

            entered = threading.Event()
            results = []
            errors = []
            def failing_provider():
                entered.set()
                if not release.wait(3):
                    raise RuntimeError("S52_TEST_PROVIDER_BARRIER_TIMEOUT")
                raise OSError("S52_INJECTED_BAD_CLOCK")
            life.worker._now = failing_provider

            def background_poll():
                try:
                    results.append(life.worker.poll_once())
                except Exception:
                    errors.append("UNEXPECTED_POLL_EXCEPTION")
            thread = threading.Thread(
                target=background_poll, name="S52-test-poll", daemon=True)
            thread.start()
            report["clock_failure_inflight_before_tk_destroy"] = (
                entered.wait(1.5) and thread.is_alive())

            durations = []
            def destroy_label():
                began = time.monotonic()
                label.destroy()
                durations.append(time.monotonic() - began)
            root.after(40, destroy_label)
            root.after(130, root.quit)
            root.mainloop()
            report["native_label_destroy_nonblocking"] = (
                len(durations) == 1 and durations[0] < .25
                and life.closed and life.preview.status == "CLOSED")
            report["cancel_delivered_to_blocked_worker"] = (
                life.worker._cancel.is_set()
                and life.worker._closed
                and life.worker._stop_requested.is_set())

            release.set()
            thread.join(2)
            report["clock_error_did_not_override_closed"] = (
                not thread.is_alive()
                and not errors
                and results == [()]
                and life.worker.status == "CLOSED")
            report["no_due_records_after_exception_and_shutdown"] = (
                life.worker.blocked_occurrences() == ())
            report["closed_worker_can_join_but_never_rearm"] = (
                life.finish_close(2)
                and not life.worker.thread_alive
                and not life.worker.start()
                and not life.start_preview_and_evaluation())

            root.destroy()
            root = None
            report["synthetic_settings_ini_byte_identical"] = (
                ini.read_bytes() == original)
            report["no_synthetic_account_side_files"] = (
                len(list(ini.parent.iterdir())) == 1)
            fixed = {
                "task", "status", "real_game", "signed_info", "f05_f06",
                "game_close_all", "pc_shutdown", "proxy_runtime",
                "product_exe", "credentials_in_artifact"}
            assert all(v is True for k, v in report.items()
                       if k not in fixed), "S52_NATIVE_TEST_PROOF_FAILED"
            report["status"] = "PASS_NATIVE_S52_TK_CLOCK_EXCEPTION_CANCEL_PRIORITY"
    except Exception as exc:
        report["status"] = "FAIL_NATIVE_S52"
        report["error_type"] = type(exc).__name__
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
        REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False),
                          encoding="utf-8")
        for key, value in report.items():
            print("S52_"+key.upper()+"="+json.dumps(value, ensure_ascii=True))
    return (0 if report["status"] ==
            "PASS_NATIVE_S52_TK_CLOCK_EXCEPTION_CANCEL_PRIORITY" else 1)


if __name__ == "__main__":
    raise SystemExit(run())
