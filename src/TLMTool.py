"""TLMTool Stage S bootstrap: explicit refusal until real InfoTab exists.

Use 'python -m unittest discover -s tests -v' to validate reconstructed logic.
This is source groundwork, NOT a working copy of TLMTool 2.1.2.
"""
from __future__ import annotations

import sys

from shell import MissingFeatureError, TLMMainApp
from single_instance import SingleInstanceMutex
from startup_diagnostics import StartupDiagnostics
from session_logger import SessionTee


def run_with_info_factory(info_factory) -> None:
    """Guard the real Tk lifecycle; a missing Info service still fails closed.

    S21 single-instance mutex is held for the ENTIRE GUI lifetime and
    released on normal shutdown, startup exception or mainloop exception.
    The production main() entrypoint remains BLOCKED until genuine
    InfoTab/server authorization exists; this helper never grants it.
    """
    with SingleInstanceMutex():
        # S23: local reconstruction of E06 stdout/stderr session tee;
        # E01's exact ordering of logger, diagnostics and splash UNKNOWN.
        # Log setup failures prevent Tk and always release the mutex.
        with SessionTee():
            with StartupDiagnostics():
                import tkinter as tk
                root = tk.Tk()
                try:
                    app = TLMMainApp(root, {'info_tab':info_factory})
                    app.position_window_top_right()
                    root.mainloop()
                finally:
                    try:
                        if 'app' in locals():
                            app.shutdown()
                    finally:
                        try:
                            root.destroy()
                        except tk.TclError:
                            pass


def main() -> int:
    # Feature/source work pending: never create an apparently-functional app.
    print('S01 BLOCKED: genuine InfoTab/server authorization has not been reconstructed; no GUI started.',file=sys.stderr)
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
