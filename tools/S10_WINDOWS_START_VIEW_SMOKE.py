"""Native Windows proof of the real S10 passive Start widget + safe auth.

Uses actual Tk Notebook, real Win32 enumeration and S09 3s/2s paths.
Only the TEST fixture supplies a verified claims adapter; product main exits 2.
No real game, game action, server, memory reading, DWM overlay or Proxy.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import sys
import threading
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "artifacts" / "s10"
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT / "native_start_view.json"


def run():
    report = {
        "task": "S10", "status": "NOT_RUN", "os": os.name,
        "real_game_positive": "NOT_RUN", "auth_server": "NOT_RUN",
        "game_actions": 0, "pixel_parity": "NOT_RUN",
        "dwm_preview": "NOT_IMPLEMENTED", "exe_build": "NOT_BUILT",
    }
    root = None
    app = None
    view = None
    worker_threads = []
    try:
        if os.name != "nt":
            raise RuntimeError("Native Windows Tk required")
        import tkinter as tk
        from tkinter import ttk
        from info_tab import TLMInfoTab
        from shell import TLMMainApp, INFO_KEY
        from permission_guard import PermissionGuard, VerifiedClaims
        from start_polling import StartWindowProducer, DISCOVERY_INTERVAL_SECONDS, START_UI_POLL_MS
        from start_windows import NativeWin32Backend
        from start_tab import TLMStartTab

        class NativeTracingBackend:
            def __init__(self):
                worker_threads.append(threading.get_ident())
                self.native = NativeWin32Backend()
            def enumerate_top_level(self):
                worker_threads.append(threading.get_ident())
                return self.native.enumerate_top_level()
            def __getattr__(self, name):
                return getattr(self.native, name)

        producer = StartWindowProducer(NativeTracingBackend)
        built = []
        def start_factory(parent):
            item = TLMStartTab(parent, producer=producer)
            built.append(item)
            return item

        root = tk.Tk()
        app = TLMMainApp(
            root, {"info_tab": lambda parent: TLMInfoTab(parent),
                   "start_tab": start_factory},
        )
        app.position_window_top_right()
        root.update()
        report["initial_visible_keys"] = sorted(app.lifecycle.visible)
        report["initial_start_hidden"] = (
            app.notebook.tab(app._tab_frames["start_tab"], "state") == "hidden")
        assert report["initial_visible_keys"] == [INFO_KEY]
        assert report["initial_start_hidden"] and not built
        assert not producer.active

        # Test-only verifier fixture; NOT used by production run path.
        guard = PermissionGuard()
        assert guard.receive_token(
            "test-only-signed-token-adapter",
            lambda _: VerifiedClaims(
                permissions=frozenset({"start_tab", "info_tab"}),
                plan_status="TEST_ONLY", max_windows=4))
        app.apply_info_snapshot(guard.snapshot)
        root.update()
        assert app.notebook.tab(app._tab_frames["start_tab"], "state") == "normal"
        app.notebook.select(app._tab_frames["start_tab"])
        root.update()
        assert len(built) == 1
        view = built[0]
        assert view.poller.active and producer.active
        start = time.monotonic()
        root.after(2550, root.quit)
        root.mainloop()
        report["elapsed_seconds"] = round(time.monotonic() - start, 3)
        report["worker_threads_background"] = (
            bool(worker_threads)
            and all(t != threading.get_ident() for t in worker_threads))
        report["status_code_after_poll"] = view.readonly_view.code
        report["displayed_rows"] = [
            list(view.table.item(iid, "values"))
            for iid in view.table.get_children()
        ]
        report["ui_poll_interval_ms"] = view.poller.interval_ms
        report["worker_interval_seconds"] = DISCOVERY_INTERVAL_SECONDS
        report["widget_buttons"] = sum(
            isinstance(w, (ttk.Button, tk.Button))
            for w in view.container.winfo_children()
        )
        assert report["worker_threads_background"]
        assert report["ui_poll_interval_ms"] == START_UI_POLL_MS == 2000
        assert report["elapsed_seconds"] >= 2.0
        assert report["status_code_after_poll"] in ("LIVE", "EMPTY")
        assert report["widget_buttons"] == 0

        # Verified grant is revoked; Start must stop and erase handles.
        guard.clear()
        app.apply_info_snapshot(guard.snapshot)
        root.update()
        report["revoked_selected_info"] = app.lifecycle.current == INFO_KEY
        report["revoked_worker_stopped"] = not producer.active
        report["revoked_rows_cleared"] = not view.table.get_children()
        report["revoked_start_hidden"] = (
            app.notebook.tab(app._tab_frames["start_tab"], "state") == "hidden")
        assert all(report[k] for k in (
            "revoked_selected_info", "revoked_worker_stopped",
            "revoked_rows_cleared", "revoked_start_hidden"))
        report["status"] = "PASS_NATIVE_READONLY_START_AUTH_AND_POLLING"
    except Exception as exc:
        report["status"] = "FAIL_NATIVE_START_VIEW"
        report["error"] = f"{type(exc).__name__}: {exc}"
        report["traceback"] = traceback.format_exc(limit=12)
    finally:
        if app is not None:
            try:
                app.shutdown()
            except Exception as exc:
                report["shutdown_error"] = str(exc)
                report["status"] = "FAIL_CLOSE"
        if root is not None:
            try:
                root.destroy()
            except Exception as exc:
                report["destroy_error"] = str(exc)
                report["status"] = "FAIL_CLOSE"
        report["producer_active_after_close"] = (
            view.poller.producer.active if view is not None else False)
        REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        for key, value in report.items():
            if key != "traceback":
                print("S10_" + key.upper() + "=" + json.dumps(value, ensure_ascii=False))
    return 0 if report["status"] == "PASS_NATIVE_READONLY_START_AUTH_AND_POLLING" else 1


if __name__ == "__main__":
    raise SystemExit(run())
