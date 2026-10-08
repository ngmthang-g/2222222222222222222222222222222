"""TLMTool Stage S bootstrap: explicit refusal until real InfoTab exists.

Use 'python -m unittest discover -s tests -v' to validate reconstructed logic.
This is source groundwork, NOT a working copy of TLMTool 2.1.2.
"""
from __future__ import annotations

import sys

from shell import MissingFeatureError, TLMMainApp


def run_with_info_factory(info_factory) -> None:
    """Only a genuine, separately verified InfoTab/service may open this UI."""
    import tkinter as tk
    root = tk.Tk()
    try:
        app = TLMMainApp(root, {'info_tab':info_factory})
        app.position_window_top_right()
        root.mainloop()
    finally:
        if 'app' in locals():
            app.shutdown()
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
