"""S49 native Windows REAL Tk Label destroy amid paused stop-fence clear.

Safe isolated test only; original user credentials, game executables, Proxy and
scheduled game actions are not accessed. No real Login tab scheduler.
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
OUT = ROOT / "artifacts" / "s49"
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT / "native_tk_permanent_shutdown_fence.json"


def run() -> int:
    outcome = {
        "task": "S49", "status": "NOT_RUN",
        "real_game": "NOT_RUN", "signed_info": "NOT_CONNECTED",
        "f05_f06": "NOT_CONNECTED", "game_close_all": "NOT_CONNECTED",
        "pc_shutdown": "NOT_CALLED", "proxy_runtime": "EXCLUDED",
        "product_exe": "NOT_PRODUCT", "credentials_in_artifact": False,
    }
    root = None
    life = None
    stop_thread = None
    release = threading.Event()
    try:
        if os.name != "nt":
            raise RuntimeError("S49_NATIVE_WINDOWS_REQUIRED")
        import tkinter as tk
        from login_schedule_settings import read_schedule_settings
        from login_schedule_lifetime import F09ReadOnlyTabLifetime

        with tempfile.TemporaryDirectory(prefix="S49_TEST_ONLY_") as td:
            ini = Path(td) / "APPDATA" / "TLMTool" / "settings.ini"
            ini.parent.mkdir(parents=True)
            ini.write_text(
                "[Settings]\n"
                "accounts = ?|S49_FAKE_USER|S49_FAKE_PASSWORD|Có|opaque\n"
                "schedule_on = OPAQUE_TOKEN\n"
                "schedule_close = 04:00\n"
                "schedule_open = 04:20\n"
                "shutdown_after_close = OPAQUE_TOKEN\n",
                encoding="utf-8")
            original = ini.read_bytes()
            cfg = read_schedule_settings(ini)
            outcome["readonly_schedule_valid"] = (
                cfg.status == "READ_ONLY_VALIDATED")
            root = tk.Tk()
            root.withdraw()
            label = tk.Label(root, text="")
            label.pack()
            life = F09ReadOnlyTabLifetime(
                label, cfg, now=lambda: datetime(2026, 10, 9, 3, 59, 50))
            outcome["opaque_flags_not_activated"] = (
                not life.preview.active and not life.worker.thread_alive)
            outcome["explicit_native_tk_preview_and_worker"] = (
                life.start_preview_and_evaluation()
                and life.preview.has_pending_refresh
                and life.worker.thread_alive)

            worker = life.worker
            clear_entered = threading.Event()
            actual_clear = worker._stop_requested.clear
            def paused_clear():
                clear_entered.set()
                if not release.wait(3):
                    raise RuntimeError("S49_NATIVE_CLEAR_PAUSE_TIMEOUT")
                actual_clear()
            worker._stop_requested.clear = paused_clear

            results = []
            def background_stop():
                try:
                    results.append(worker.stop(2))
                except Exception:
                    results.append(False)
            stop_thread = threading.Thread(
                target=background_stop, name="S49-stop", daemon=True)
            stop_thread.start()
            outcome["original_s48_clear_interleaving_reproduced"] = (
                clear_entered.wait(1.5))
            outcome["stop_inside_clear_with_no_pending_caller"] = (
                worker._pending_stop_callers == 0
                and worker._lifecycle_lock.locked()
                and not worker._closed)

            destroy_elapsed = []
            def destroy_label():
                started = time.monotonic()
                label.destroy()
                destroy_elapsed.append(time.monotonic() - started)
            root.after(40, destroy_label)
            root.after(130, root.quit)
            root.mainloop()
            outcome["real_tk_destroy_nonblocking"] = (
                len(destroy_elapsed) == 1
                and destroy_elapsed[0] < 0.25
                and life.closed and life.preview.status == "CLOSED")
            outcome["cancel_sent_while_clear_inflight"] = (
                worker._closed and worker._cancel.is_set()
                and worker._stop_requested.is_set())

            release.set()
            stop_thread.join(2)
            outcome["background_stop_completed"] = (
                not stop_thread.is_alive() and results == [True])
            outcome["permanent_fence_still_set_after_clear"] = (
                worker._closed and worker._cancel.is_set()
                and worker._stop_requested.is_set()
                and worker._pending_stop_callers == 0)
            outcome["join_cleanup_and_rearm_denied"] = (
                life.finish_close(2)
                and not worker.thread_alive
                and not worker.start()
                and not life.start_preview_and_evaluation())
            outcome["no_late_due_events"] = worker.blocked_occurrences() == ()
            root.destroy()
            root = None
            outcome["test_ini_byte_identical"] = (
                ini.read_bytes() == original)
            outcome["no_legacy_account_backup"] = (
                len(list(ini.parent.iterdir())) == 1)
            ignore = {
                "task", "status", "real_game", "signed_info", "f05_f06",
                "game_close_all", "pc_shutdown", "proxy_runtime",
                "product_exe", "credentials_in_artifact"}
            assert all(v is True for k, v in outcome.items()
                       if k not in ignore), "S49_NATIVE_PROOF_FAILED"
            outcome["status"] = "PASS_NATIVE_S49_LOCKFREE_TK_CLOSE_FENCE"
    except Exception as exc:
        outcome["status"] = "FAIL_NATIVE_S49"
        outcome["error_type"] = type(exc).__name__
    finally:
        release.set()
        if stop_thread is not None:
            stop_thread.join(2)
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
        REPORT.write_text(json.dumps(outcome, indent=2,
                                     ensure_ascii=False), encoding="utf-8")
        for key, value in outcome.items():
            print("S49_" + key.upper() + "=" +
                  json.dumps(value, ensure_ascii=True))
    return (0 if outcome["status"] ==
            "PASS_NATIVE_S49_LOCKFREE_TK_CLOSE_FENCE" else 1)


if __name__ == "__main__":
    raise SystemExit(run())
