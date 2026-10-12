"""Independent rebuilt TLMTool entrypoint, no original Info/license issuer.

This is an honest PARTIAL source-backed application, not a claim of 1:1
gameplay parity. Legacy TLMTool.py remains as a frozen comparison fixture
for past tests and S36 diagnostic; run THIS entrypoint for the new tool.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from local_feature_policy import LocalFeaturePolicy, LOCAL_TAB_KEYS
from local_tool_status_tab import LocalToolStatusTab
from settings_store import settings_path
from shell import TLMMainApp
from source_backed_tab_builders import source_backed_tab_builders
from start_polling import StartWindowProducer, WindowSnapshot
from single_instance import SingleInstanceMutex
from startup_diagnostics import StartupDiagnostics
from session_logger import SessionTee


def count_observed_game_windows(producer: StartWindowProducer) -> int:
    """Only real read-only S09 Win32 source; unknown snapshot = zero."""
    snap = producer.read_snapshot()
    if not isinstance(snap, WindowSnapshot) or not snap.valid:
        return 0
    return len(snap.windows)


def make_independent_builders(settings_file: str | Path,
                              producer: StartWindowProducer):
    """Register implemented UI only; no original license API is called."""
    if not isinstance(producer, StartWindowProducer):
        raise ValueError("REAL_SHARED_WIN32_PRODUCER_REQUIRED")
    policy = LocalFeaturePolicy(frozenset({"farm_tab"}))
    count = lambda: count_observed_game_windows(producer)
    return source_backed_tab_builders(
        lambda parent: LocalToolStatusTab(parent),
        settings_file=settings_file,
        start_producer=producer,
        train_permission_guard=policy,
        train_running_count=count,
        # Only windows independently verified by the native H12 gate can
        # appear in read-only Train rows; no guessed RoleName or game sender.
        train_allow_account=lambda window: True,
    )


def run_independent_tool() -> int:
    if os.name != "nt":
        print("Independent desktop tool requires Windows.", file=sys.stderr)
        return 2
    with SingleInstanceMutex():
        with SessionTee():
            with StartupDiagnostics():
                import tkinter as tk
                root = tk.Tk()
                producer = StartWindowProducer()
                try:
                    app = TLMMainApp(
                        root, make_independent_builders(settings_path(), producer),
                        independent_mode=True,
                        local_window_count=lambda:count_observed_game_windows(producer))
                    app.position_window_top_right()
                    root.mainloop()
                    return 0
                finally:
                    try:
                        if 'app' in locals():
                            app.shutdown()
                    finally:
                        producer.stop()
                        try:root.destroy()
                        except tk.TclError:pass


def main(argv=None) -> int:
    args=list(sys.argv[1:] if argv is None else argv)
    if args == ["--self-check"]:
        # Static runtime linkage check; does not pretend actual GUI/game.
        print(json.dumps({
            "entrypoint":"independent_partial",
            "original_license_service":"NOT_USED",
            "local_tab_catalog":sorted(LOCAL_TAB_KEYS),
            "gameplay_parity":"NOT_VERIFIED",
        },ensure_ascii=False))
        return 0
    if args:
        print("Usage: TLMToolIndependent.py [--self-check]",file=sys.stderr)
        return 2
    return run_independent_tool()


if __name__=="__main__":
    raise SystemExit(main())
