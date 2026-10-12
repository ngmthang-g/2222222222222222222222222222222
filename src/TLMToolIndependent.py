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
from train_lsv_top_tab import TkTrainLsvTopTab
from rao_definition_tab import TkRaoConfigTab
from toiuu_monitor_tab import TkToiuuHostTab
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
    builders = source_backed_tab_builders(
        lambda parent: LocalToolStatusTab(parent),
        settings_file=settings_file,
        start_producer=producer,
        # S176: show real shared S09 window membership on Party, but never
        # invent RoleName/HP or permit unknown accounts in group dropdowns.
        party_observe_windows=True,
        train_permission_guard=policy,
        train_running_count=count,
        # Only windows independently verified by the native H12 gate can
        # appear in read-only Train rows; no guessed RoleName or game sender.
        train_allow_account=lambda window: True,
    )
    # S169: real TrainLSV [TrainLSV] config is a dedicated, non-game tab;
    # do not add it to historical Info-gated builders or pretend FSM exists.
    if "trainlsv_tab" not in LOCAL_TAB_KEYS:
        raise ValueError("MISSING_IMPLEMENTED_LSV_LOCAL_CAPABILITY")
    def build_train_lsv(parent):
        panel = TkTrainLsvTopTab(parent, settings_file=settings_file,
                                   start_producer=producer)
        panel.pack(fill="both", expand=True)
        return panel
    builders["trainlsv_tab"] = build_train_lsv
    # PLAN stage M: actual local [Rao] configuration editor only.
    # No invented game chat sender, no account mapping without RoleName.
    if "rao_tab" not in LOCAL_TAB_KEYS:
        raise ValueError("MISSING_IMPLEMENTED_RAO_LOCAL_CAPABILITY")
    def build_rao(parent):
        panel = TkRaoConfigTab(parent, settings_file=settings_file)
        panel.pack(fill="both", expand=True)
        return panel
    builders["rao_tab"] = build_rao
    # PLAN stage N02/N03/N04: host CPU/GPU, real Canvas + detached view.
    # Not the missing TLMP per-account graphics-mode implementation.
    if "toiuu_tab" not in LOCAL_TAB_KEYS:
        raise ValueError("MISSING_IMPLEMENTED_TOIUU_HOST_MONITOR")
    def build_toituu_monitor(parent):
        panel = TkToiuuHostTab(parent)
        panel.pack(fill="both", expand=True)
        return panel
    builders["toiuu_tab"] = build_toituu_monitor
    return builders


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
