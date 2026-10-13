"""S208 — all eleven REAL independent TLM tabs must instantiate on Windows.

Unlike S174's GUI HWND smoke, this traverses every notebook tab with the
CURRENT source+owner-independent dependencies, uses a fresh temp INI,
observes native Tk callback errors and verifies the factory actually
built each tab. It never opens a game, clicks a game, sends a password,
injects DLL, assumes real RoleName or changes user configuration.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile
import time
import tkinter as tk

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from TLMToolIndependent import make_independent_builders
from independent_shared_window_source import IndependentSharedWindowProducer
from independent_character_diagnostic_observer import IndependentCharacterDiagnosticObserver
from independent_original_roi_worker import IndependentOriginalRoiWorker
from shell import TLMMainApp, TAB_SPECS
from local_feature_policy import LOCAL_TAB_KEYS

def main():
    if os.name != "nt":
        raise RuntimeError("S208_WINDOWS_TK_REQUIRED")
    original_errors = []
    checks = []
    with tempfile.TemporaryDirectory(prefix="TLM_S208_ALL_TABS_") as directory:
        settings_file = Path(directory) / "settings.ini"
        root = tk.Tk()
        def catch_callback_error(typ, value, traceback):
            original_errors.append(f"{typ.__name__}: {value!s}")
        root.report_callback_exception = catch_callback_error
        producer = IndependentSharedWindowProducer()
        observer = IndependentCharacterDiagnosticObserver(producer, settings_file)
        roi_worker = IndependentOriginalRoiWorker(producer, settings_file)
        app = None
        try:
            if producer.start() is not True:
                raise RuntimeError("NATIVE_PRODUCER_START_FAILED")
            if observer.start() is not True:
                raise RuntimeError("REAL_OBSERVER_START_FAILED")
            app = TLMMainApp(
                root,
                make_independent_builders(
                    settings_file, producer, observer=observer,
                    roi_worker=roi_worker),
                independent_mode=True,
                local_window_count=lambda: 0)
            app.position_window_top_right()
            root.update_idletasks()
            keys = [spec.key for spec in TAB_SPECS
                    if spec.key in LOCAL_TAB_KEYS or spec.key == "info_tab"]
            for key in keys:
                frame = app._tab_frames[key]
                if str(app.notebook.tab(frame, "state")) == "hidden":
                    raise RuntimeError(f"{key}_NOT_VISIBLE")
                app.notebook.select(frame)
                # Exercise all real lazy constructors + selected
                # _start_refresh, native Tk events and _stop_refresh.
                end = time.monotonic() + 0.22
                while time.monotonic() < end:
                    root.update()
                    time.sleep(0.03)
                instance = app.lifecycle._instances.get(key)
                if instance is None:
                    raise RuntimeError(f"{key}_NOT_BUILT")
                if app.lifecycle.current != key:
                    raise RuntimeError(
                        f"{key}_LIFECYCLE_WRONG_{app.lifecycle.current}")
                if original_errors:
                    raise RuntimeError(
                        "TK_CALLBACK_ERROR:" + ";".join(original_errors))
                checks.append({
                    "key": key,
                    "type": type(instance).__name__,
                    "visible": True,
                    "callback_error": False,
                })
            # Read-only ROI panel must exist as a REAL widget and all
            # original sections must be present (not a phantom tab).
            for key in ("phoban_tab", "donvang_tab"):
                panel = app.lifecycle._instances[key]
                if not hasattr(panel, "roi_panel"):
                    raise RuntimeError(f"{key}_ORIGINAL_PIXEL_ROI_PANEL_MISSING")
            if not {"start_tab","login_tab","party_tab","farm_tab",
                    "trainlsv_tab","phoban_tab","daily_tab","donvang_tab",
                    "rao_tab","toiuu_tab","info_tab"} <= set(keys):
                raise RuntimeError("REQUIRED_ELEVEN_TABS_NOT_AVAILABLE")
            app.notebook.select(app._tab_frames["start_tab"])
            root.update()
            if original_errors:
                raise RuntimeError(
                    "TK_CALLBACK_ERROR_AFTER_RETURN:"+";".join(original_errors))
        finally:
            try:
                if app is not None:
                    app.shutdown()
            finally:
                roi_worker.shutdown()
                observer.shutdown()
                producer.shutdown()
                try:
                    root.destroy()
                except tk.TclError:
                    pass
        if original_errors:
            raise RuntimeError("TK_CALLBACK_ERRORS:"+";".join(original_errors))
    proof = {
        "status": "PASS_REAL_WINDOWS_TK_ELEVEN_TABS_NO_GAME",
        "tab_count": len(checks),
        "tabs": checks,
        "live_game_tested": False,
        "game_action_sender_implemented": False,
        "original_entitlements_used": False,
    }
    out = ROOT / "artifacts" / "s208"
    out.mkdir(parents=True, exist_ok=True)
    (out / "windows_all_tabs.json").write_text(
        json.dumps(proof, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(proof, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
