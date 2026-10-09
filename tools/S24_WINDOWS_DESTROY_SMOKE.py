"""S24 E08: actual Win32/Tk <Destroy> ownership and DWM cleanup.

Only REAL TEST-OWNED Tk HWNDs, S24_TEST_ONLY mutex and temporary log paths.
Never starts Thần Long, never sends game input, never grants product rights.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile
import time
import traceback
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "artifacts" / "s24"
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT / "native_destroy_lifecycle.json"


def one_case(*, root_destroy_first: bool):
    import tkinter as tk
    from dwm_preview import NativeDwmBackend
    from grid_master import GridSettingsStore
    from info_tab import TLMInfoTab
    from shell import TLMMainApp, INFO_KEY
    from start_tab import TLMStartTab
    from start_polling import WindowSnapshot
    from start_windows import GameWindow

    root, app, source, view = None, None, None, None
    producer = None
    check = {"path": ("TK_ROOT_DESTROY" if root_destroy_first
                       else "EXPLICIT_APP_SHUTDOWN")}
    try:
        root = tk.Tk()
        root.title("S24 TEST OWNED APP - NOT GAME")
        root.geometry("850x930+15+15")
        source = tk.Toplevel(root)
        source.title("S24 REAL TEST-OWNED Win32 Source - NOT GAME")
        source.geometry("240x170+45+35")
        tk.Label(source, text="S24 TEST HWND - NOT THẦN LONG").pack(
            fill="both", expand=True)
        root.update()
        backend = NativeDwmBackend()
        hwnd = int(backend._ancestor(int(source.winfo_id()), 2))
        pid = os.getpid()
        assert backend.source_matches(hwnd, pid)
        check["real_test_hwnd"] = hwnd
        check["real_win32_pid_match"] = True

        # Test ONLY: expose actual non-game HWND to the view via a controlled
        # cache, not a forged discovery result or actual game entitlement.
        class TestOwnedCache:
            def __init__(self):
                self.active = False
                self.revision = 0
                self.starts = 0
                self.stops = 0
            def start(self):
                if not self.active:
                    self.active = True
                    self.revision += 1
                    self.starts += 1
                return True
            def stop(self):
                if self.active:
                    self.active = False
                    self.revision += 1
                    self.stops += 1
            def read_snapshot(self):
                windows = ((GameWindow(hwnd, pid,
                                      "S24 test-only Tk HWND (NOT GAME)",
                                      "TEST_OWNED_TK", "NOT_A_GAME.exe"),)
                           if self.active else ())
                return WindowSnapshot(self.revision, windows, self.active)
        producer = TestOwnedCache()
        with tempfile.TemporaryDirectory(prefix="s24_grid_testonly_") as folder:
            tabs=[]
            def start_factory(frame):
                tab=TLMStartTab(
                    frame, producer=producer,
                    grid_settings_store=GridSettingsStore(
                        Path(folder)/"TLMTool"/"settings.ini"))
                tabs.append(tab)
                return tab

            app=TLMMainApp(root, {
                "info_tab": lambda frame: TLMInfoTab(frame),
                "start_tab": start_factory,
            })
            app.position_window_top_right()
            root.geometry("850x930+15+15")
            root.update()
            assert app.lifecycle.visible == {INFO_KEY} and not tabs
            app.apply_verified_permissions({"start_tab"})  # isolated TEST-only
            app.notebook.select(app._tab_frames["start_tab"])
            root.update()
            assert tabs and producer.active and app.lifecycle.current == "start_tab"
            view=tabs[0]

            # Allow real Tk geometry/after/real compositor registration; no
            # human clicks and no WinAPI move on any game HWND.
            for attempt in range(24):
                root.after(115, root.quit)
                root.mainloop()
                if (view._preview_controller is not None
                        and hwnd in view._preview_controller.active_hwnds):
                    break
            ctrl = view._preview_controller
            assert ctrl is not None and ctrl.active_hwnds == (hwnd,), (
                "Native DWM thumbnail did not appear for test-owned source")
            destination = ctrl._slots[hwnd].destination
            thumbnail = ctrl._slots[hwnd].thumbnail
            assert destination > 0 and thumbnail > 0
            assert backend._is_window(destination)
            check["real_dwm_registered"] = True

            if root_destroy_first:
                # Real Tk cascade: descendants emit <Destroy> BEFORE root.
                root.destroy()
                root=None
            else:
                app.shutdown()
                app.shutdown()
                assert not backend._is_window(destination)
                root.destroy()
                root=None

            assert app._closed and app.lifecycle._closed
            assert view._closed and not view.poller.active
            assert not view.maintenance.active
            assert view._preview_controller is None
            assert ctrl._closed and not ctrl.active_hwnds
            assert not backend._is_window(destination)
            assert producer.starts == 1 and producer.stops == 1
            check["native_dwm_destination_destroyed"] = True
            check["owner_shutdown_idempotent"] = True
            check["cache_stop_once"] = True
            check["late_grant_denied"] = (
                app.lifecycle.apply_authorized_keys({"start_tab"})
                == frozenset({INFO_KEY}))
            check["no_dwm_owned_resource_left"] = True
            assert check["late_grant_denied"]
            app.shutdown()
            check["repeat_app_close_safe"] = True
        return check
    finally:
        if app is not None:
            app.shutdown()
        if root is not None:
            try:
                root.destroy()
            except Exception:
                pass


def run():
    report={
        "task":"S24","status":"NOT_RUN",
        "sources":"REAL_TEST_OWNED_TK_HWND_NOT_GAME",
        "original_root_destroy_order":"UNKNOWN_E08",
        "real_game":"NOT_RUN","auth_server":"NOT_RUN",
        "product_exe":"NOT_BUILT","proxy":"NOT_DEVELOPED",
        "normal_close_forwarder_global_kill":"NOT_ADDED",
        "os_exit_heartbeat":"NOT_INVOKED",
    }
    try:
        if os.name != "nt":
            raise RuntimeError("S24 requires actual Windows/Tk/DWM")
        from single_instance import SingleInstanceMutex
        from startup_diagnostics import StartupDiagnostics
        from session_logger import SessionTee, central_log_path
        name = "S24_TEST_ONLY_" + uuid.uuid4().hex
        with tempfile.TemporaryDirectory(prefix="s24_testonly_log_") as folder:
            p=Path(folder)
            with SingleInstanceMutex(name):
                with SessionTee(central_log_path(p)):
                    with StartupDiagnostics(p/"crash_fault.log"):
                        cases=[
                            one_case(root_destroy_first=True),
                            one_case(root_destroy_first=False),
                        ]
                        print("S24_NATIVE_TK_OWNERS_CLEANED", flush=True)
            log=central_log_path(p).read_text(encoding="utf-8")
            assert "=== Start " in log and "=== End " in log
            assert "S24_NATIVE_TK_OWNERS_CLEANED" in log
            report["session_log_end_marker"]=True
            report["test_owned_mutex_context_released"]=True
            report["cases"]=cases
            for case in cases:
                assert all(case[key] for key in (
                    "real_win32_pid_match","real_dwm_registered",
                    "native_dwm_destination_destroyed","owner_shutdown_idempotent",
                    "cache_stop_once","late_grant_denied",
                    "no_dwm_owned_resource_left","repeat_app_close_safe"))
        report["status"]="PASS_NATIVE_S24_TK_DESTROY_DWM_OWNER_LOG_MUTEX_CLEANUP"
    except Exception as exc:
        report["status"]="FAIL_NATIVE_S24_DESTROY"
        report["error"]=f"{type(exc).__name__}: {exc}"
        report["traceback"]=traceback.format_exc(limit=15)
    finally:
        REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),
                          encoding="utf-8")
        for k,v in report.items():
            if k!="traceback":
                print("S24_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if report["status"]==(
        "PASS_NATIVE_S24_TK_DESTROY_DWM_OWNER_LOG_MUTEX_CLEANUP") else 1


if __name__=="__main__":
    raise SystemExit(run())
