"""S41 native Windows real Tk Label after cancellation and F09 rollover.

All data is synthetic and in a test-owned temp directory. This does NOT
activate a schedule worker, game launch, close-all or Windows PC shutdown.
"""
from __future__ import annotations

from datetime import datetime
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "artifacts" / "s41"
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT / "windows_real_tk_f09_countdown_preview.json"


def run() -> int:
    r = {
        "task": "S41",
        "status": "NOT_RUN",
        "real_game": "NOT_RUN",
        "signed_info": "NOT_CONNECTED",
        "game_launch_close_dispatch": "NOT_CONNECTED",
        "shutdown_pc": "NOT_CALLED",
        "worker": "NOT_STARTED",
        "proxy_runtime": "EXCLUDED",
        "product_exe": "NOT_BUILT",
        "credential_values_in_report": False,
    }
    root = None
    presenter = None
    try:
        if os.name != "nt":
            raise RuntimeError("This smoke requires native Windows Tk")
        import tkinter as tk
        from login_schedule_settings import read_schedule_settings
        from login_schedule_countdown import TkScheduleCountdownPreview

        with tempfile.TemporaryDirectory(prefix="S41_TEST_ONLY_") as td:
            config = Path(td) / "APPDATA" / "TLMTool" / "settings.ini"
            config.parent.mkdir(parents=True)
            config.write_text(
                "[Settings]\n"
                "accounts = OPAQUE|S41_TEST|DUMMY_SECRET|Có|opaque\n"
                "schedule_on = UNKNOWN_TRUE_TOKEN\n"
                "schedule_close = 04:00\n"
                "schedule_open = 04:20\n"
                "shutdown_after_close = UNKNOWN_SHUTDOWN_TOKEN\n",
                encoding="utf-8")
            before = config.read_bytes()
            settings = read_schedule_settings(config)
            r["real_e05_f09_config_read"] = (
                settings.status == "READ_ONLY_VALIDATED"
                and settings.schedule_on_raw == "UNKNOWN_TRUE_TOKEN")
            root = tk.Tk()
            root.withdraw()
            label = tk.Label(root, text="")
            label.pack()
            current = [datetime(2026, 10, 9, 3, 59, 55)]
            presenter = TkScheduleCountdownPreview(label, now=lambda: current[0])
            r["not_auto_started_from_unknown_saved_flag"] = (
                not presenter.active and not presenter.has_pending_refresh
                and str(label.cget("text")) == "")
            r["actual_tk_label_preview_started"] = presenter.preview_start(settings)
            r["initial_f09_text_real_label"] = (
                "Tắt 04:00 09/10 còn" in str(label.cget("text"))
                and "Mở 04:20 09/10 còn" in str(label.cget("text")))
            r["tk_after_queued_on_main_thread"] = presenter.has_pending_refresh
            # Move injected test clock across close deadline; Tk's own
            # 1000 ms .after() performs the actual visual refresh.
            root.after(120, lambda: current.__setitem__(
                0, datetime(2026, 10, 9, 4, 0, 1)))
            root.after(1450, root.quit)
            root.mainloop()
            r["actual_after_tick_rollover_to_tomorrow"] = (
                "Tắt 04:00 10/10 còn" in str(label.cget("text"))
                and "Mở 04:20 09/10 còn" in str(label.cget("text")))
            r["still_single_active_refresh"] = (
                presenter.active and presenter.has_pending_refresh)
            presenter.stop()
            r["real_after_cancel_stops_preview"] = (
                not presenter.active and not presenter.has_pending_refresh
                and str(label.cget("text")) == "")
            presenter.shutdown()
            r["shutdown_ends_controller_without_game_actions"] = (
                presenter.status == "CLOSED" and not presenter.active)
            root.destroy()
            root = None
            r["old_settings_ini_byte_identical"] = config.read_bytes() == before
            r["no_settings_backup_created"] = (
                len(list(config.parent.iterdir())) == 1)
            expected = [k for k in r if k not in (
                "task", "status", "real_game", "signed_info",
                "game_launch_close_dispatch", "shutdown_pc", "worker",
                "proxy_runtime", "product_exe", "credential_values_in_report")]
            assert all(r[k] is True for k in expected), "S41_NATIVE_CHECK_FAILED"
            r["status"] = "PASS_NATIVE_S41_REAL_TK_F09_AFTER_PREVIEW_CANCEL"
    except Exception as exc:
        r["status"] = "FAIL_NATIVE_S41"
        r["error_type"] = type(exc).__name__
        # Exception message suppressed: settings may contain passwords.
    finally:
        if presenter is not None:
            try:
                presenter.shutdown()
            except Exception:
                pass
        if root is not None:
            try:
                root.destroy()
            except Exception:
                pass
        REPORT.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        for key, value in r.items():
            print("S41_" + key.upper() + "=" + json.dumps(value, ensure_ascii=True))
    return 0 if r["status"] == "PASS_NATIVE_S41_REAL_TK_F09_AFTER_PREVIEW_CANCEL" else 1


if __name__ == "__main__":
    raise SystemExit(run())
