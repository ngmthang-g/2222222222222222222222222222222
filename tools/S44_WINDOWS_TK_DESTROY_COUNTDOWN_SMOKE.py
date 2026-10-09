"""S44 Windows REAL Tk Destroy invalidates F09 countdown, preserves INI.

Test-only widget/mainloop. No real game launch, close-all, OS shutdown,
authenticated Info, Proxy, or writes to legacy F02 accounts.
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
OUT = ROOT / "artifacts" / "s44"
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT / "native_tk_destroy_countdown.json"


def run() -> int:
    result = {
        "task": "S44", "status": "NOT_RUN",
        "real_game": "NOT_RUN", "signed_info": "NOT_CONNECTED",
        "f05_f06_actions": "NOT_CONNECTED",
        "close_all": "NOT_CONNECTED", "shutdown_pc": "NOT_CALLED",
        "proxy_runtime": "EXCLUDED", "product_exe": "NOT_PRODUCT",
        "credentials_in_report": False,
    }
    root = None
    preview = None
    try:
        if os.name != "nt":
            raise RuntimeError("S44_REQUIRES_NATIVE_WINDOWS")
        import tkinter as tk
        from login_schedule_countdown import TkScheduleCountdownPreview
        from login_schedule_settings import read_schedule_settings

        with tempfile.TemporaryDirectory(prefix="S44_TEST_ONLY_") as td:
            path = Path(td) / "TLMTool" / "settings.ini"
            path.parent.mkdir(parents=True)
            path.write_text(
                "[Settings]\n"
                "accounts = ?|S44_DUMMY_USER|S44_DUMMY_SECRET|Có|opaque\n"
                "schedule_on = UNVERIFIED_BOOLEAN\n"
                "schedule_close = 04:00\nschedule_open = 04:20\n"
                "shutdown_after_close = UNKNOWN_POWER_FLAG\n",
                encoding="utf-8")
            original_bytes = path.read_bytes()
            settings = read_schedule_settings(path)
            result["genuine_readonly_f09_settings"] = (
                settings.status == "READ_ONLY_VALIDATED")
            root = tk.Tk()
            root.withdraw()
            label = tk.Label(root, text="")
            label.pack()
            clock = [datetime(2026, 10, 9, 3, 59, 50)]
            preview = TkScheduleCountdownPreview(label, now=lambda: clock[0])
            result["not_auto_started_from_saved_boolean"] = (
                not preview.active and not preview.has_pending_refresh)
            result["real_tk_start_queued_1000ms_callback"] = (
                preview.preview_start(settings)
                and preview.has_pending_refresh)
            prior_id = preview._after_id
            result["real_label_shows_readonly_countdown"] = (
                "Tắt 04:00 09/10 còn" in str(label.cget("text"))
                and "Mở 04:20 09/10 còn" in str(label.cget("text")))

            # Label destroyed BEFORE the 1-second tick; the real Tcl
            # <Destroy> binding, not artificial shutdown(), must cancel it.
            root.after(80, label.destroy)
            root.after(250, root.quit)
            root.mainloop()
            result["actual_tk_destroy_auto_shutdown_preview"] = (
                preview.status == "CLOSED"
                and not preview.active
                and not preview.has_pending_refresh)
            pending_after = root.tk.call("after", "info")
            result["destroyed_label_after_id_cancelled"] = (
                str(prior_id) not in tuple(str(x) for x in pending_after))
            result["destroyed_label_rejects_restart"] = (
                not preview.preview_start(settings))
            root.destroy()
            root = None
            result["original_ini_byte_identical"] = (
                path.read_bytes() == original_bytes)
            result["no_settings_backup_created"] = (
                len(list(path.parent.iterdir())) == 1)
            expected = [key for key in result if key not in (
                "task", "status", "real_game", "signed_info",
                "f05_f06_actions", "close_all", "shutdown_pc",
                "proxy_runtime", "product_exe", "credentials_in_report")]
            assert all(result[key] is True for key in expected), "S44_NATIVE_CHECK_FAILED"
            result["status"] = "PASS_NATIVE_S44_TK_DESTROY_CANCELS_COUNTDOWN"
    except Exception as exc:
        result["status"] = "FAIL_NATIVE_S44"
        result["error_type"] = type(exc).__name__
    finally:
        if preview is not None:
            try:
                preview.shutdown()
            except Exception:
                pass
        if root is not None:
            try:
                root.destroy()
            except Exception:
                pass
        REPORT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        for key, value in result.items():
            print("S44_" + key.upper() + "=" + json.dumps(value, ensure_ascii=True))
    return 0 if result["status"] == "PASS_NATIVE_S44_TK_DESTROY_CANCELS_COUNTDOWN" else 1


if __name__ == "__main__":
    raise SystemExit(run())
