"""S50 native Windows worker Thread.start OSError rollback + real Tk Destroy proof.

Test-owned F09 preview only; no game dispatch, account persistence, Proxy or PC.
"""
from __future__ import annotations

from datetime import datetime
import json
import os
from pathlib import Path
import sys
import tempfile
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "artifacts" / "s50"
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT / "native_tk_os_thread_start_failure.json"


def run() -> int:
    outcome = {
        "task": "S50", "status": "NOT_RUN",
        "real_game": "NOT_RUN", "signed_info": "NOT_CONNECTED",
        "f05_f06": "NOT_CONNECTED", "game_close_all": "NOT_CONNECTED",
        "pc_shutdown": "NOT_CALLED", "proxy_runtime": "EXCLUDED",
        "product_exe": "NOT_PRODUCT", "credentials_in_artifact": False,
    }
    root = None
    life = None
    try:
        if os.name != "nt":
            raise RuntimeError("S50_NATIVE_WINDOWS_REQUIRED")
        import tkinter as tk
        from login_schedule_settings import read_schedule_settings
        from login_schedule_lifetime import F09ReadOnlyTabLifetime
        from login_schedule_worker import F09ScheduleEvaluationWorker

        with tempfile.TemporaryDirectory(prefix="S50_TEST_ONLY_") as temp:
            ini = Path(temp)/"APPDATA"/"TLMTool"/"settings.ini"
            ini.parent.mkdir(parents=True)
            ini.write_text(
                "[Settings]\n"
                "accounts = ?|S50_TEST_USER|S50_DUMMY_PASSWORD|Có|opaque\n"
                "schedule_on = OPAQUE_UNKNOWN_BOOLEAN\n"
                "schedule_close = 04:00\nschedule_open = 04:20\n"
                "shutdown_after_close = OPAQUE_UNKNOWN_POWER\n",
                encoding="utf-8")
            original = ini.read_bytes()
            cfg = read_schedule_settings(ini)
            outcome["read_only_f09_settings_valid"] = cfg.status == "READ_ONLY_VALIDATED"
            root = tk.Tk()
            root.withdraw()
            label = tk.Label(root, text="")
            label.pack()
            source_time = lambda: datetime(2026, 10, 9, 3, 59, 50)
            life = F09ReadOnlyTabLifetime(label, cfg, now=source_time)
            outcome["opaque_schedule_flags_never_autostart"] = (
                not life.preview.active and not life.worker.thread_alive)
            # Inject the native OS error only at Thread.start. No patch of
            # worker action logic and no actual user/game process touched.
            with patch("login_schedule_worker.threading.Thread.start",
                       side_effect=OSError(11, "S50_TEST_WORKER_RESOURCE")):
                outcome["oserror_fails_closed_no_fake_running"] = (
                    not life.start_preview_and_evaluation()
                    and life.status == "BLOCKED_WORKER"
                    and life.worker.status == "BLOCKED_THREAD")
            outcome["failed_thread_clock_cleared"] = (
                life.worker._thread is None and life.worker._clock is None
                and life.worker._cancel.is_set()
                and not life.worker.active and not life.worker.thread_alive)
            outcome["tk_countdown_rolled_back"] = (
                not life.preview.active and not life.preview.has_pending_refresh)
            elapsed = []
            def destroy_label():
                now = time.monotonic()
                label.destroy()
                elapsed.append(time.monotonic()-now)
            root.after(30, destroy_label)
            root.after(95, root.quit)
            root.mainloop()
            outcome["real_tk_destroy_after_failure_nothang"] = (
                len(elapsed) == 1 and elapsed[0] < .25
                and life.closed and life.preview.status == "CLOSED")
            outcome["finish_close_idempotent"] = (
                life.finish_close(2) and life.finish_close(2)
                and not life.worker.start() and not life.worker.thread_alive)

            # A NEW explicit healthy worker can still start after a
            # hypothetical earlier native resource exhaustion is lifted.
            other = F09ScheduleEvaluationWorker(cfg, now=source_time)
            try:
                outcome["unaffected_normal_worker_wait20_still_starts"] = (
                    other.start() and other.thread_alive)
                started = time.monotonic()
                outcome["unmodified_twenty_second_wait_cancellable"] = (
                    other.stop(2) and time.monotonic()-started < .5)
                outcome["no_game_actions_on_failure_or_retry"] = (
                    not other.blocked_occurrences()
                    and not life.worker.blocked_occurrences())
            finally:
                other.shutdown(2)

            root.destroy()
            root = None
            outcome["synthetic_ini_byte_identical"] = ini.read_bytes() == original
            outcome["no_backup_or_generated_credential_file"] = (
                len(list(ini.parent.iterdir())) == 1)
            excluded = {
                "task", "status", "real_game", "signed_info", "f05_f06",
                "game_close_all", "pc_shutdown", "proxy_runtime",
                "product_exe", "credentials_in_artifact"}
            assert all(v is True for k, v in outcome.items() if k not in excluded), "S50_NATIVE_CHECK_FAILED"
            outcome["status"] = "PASS_NATIVE_S50_OS_THREAD_START_FAIL_CLOSED_REAL_TK"
    except Exception as exc:
        outcome["status"] = "FAIL_NATIVE_S50"
        outcome["error_type"] = type(exc).__name__
    finally:
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
        REPORT.write_text(json.dumps(outcome, indent=2, ensure_ascii=False), encoding="utf-8")
        for name, value in outcome.items():
            print("S50_"+name.upper()+"="+json.dumps(value, ensure_ascii=True))
    return 0 if outcome["status"] == "PASS_NATIVE_S50_OS_THREAD_START_FAIL_CLOSED_REAL_TK" else 1


if __name__ == "__main__":
    raise SystemExit(run())
