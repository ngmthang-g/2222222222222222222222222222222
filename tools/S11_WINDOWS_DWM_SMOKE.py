"""S11 true user32/dwmapi smoke with a REAL TEST-OWNED Tk HWND, not game.

Validates DwmRegisterThumbnail, DwmUpdateThumbnailProperties, reposition,
IsWindow/PID gating, DwmUnregisterThumbnail and DestroyWindow. No synthetic
game identity is inserted into S09 producer; no proxy, clicks or server.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "artifacts" / "s11"
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT / "native_dwm.json"


def run():
    result = {
        "task": "S11", "status": "NOT_RUN", "platform": os.name,
        "source_kind": "TEST_OWNED_TK_HWND_NOT_GAME",
        "game_positive": "NOT_RUN", "game_control_count": 0,
        "auth_server": "NOT_RUN", "DWM_pixels": "NOT_MEASURED",
        "exe_build": "NOT_BUILT",
    }
    root = source = ctrl = None
    try:
        if os.name != "nt":
            raise RuntimeError("Windows-only test")
        import tkinter as tk
        from dwm_preview import NativeDwmBackend, PreviewPlacement, ReadOnlyDwmPreviews

        root = tk.Tk()
        root.title("S11 DWM destination (not a game)")
        root.geometry("540x350+400+170")
        target = tk.Frame(root, bg="#000000", width=197, height=110)
        target.place(x=36, y=62, width=197, height=110)

        source = tk.Toplevel(root)
        source.title("S11 original-backed Win32 test-owned source (NOT Thần Long)")
        source.geometry("245x174+90+170")
        tk.Label(source, text="REAL native test-owned HWND\nNO game account", bg="#E0E0E0").pack(
            fill="both", expand=True)
        root.update()
        source.update()
        hwnd = int(source.winfo_id())
        owner = int(root.winfo_id())
        pid = os.getpid()
        backend = NativeDwmBackend()
        result["test_owned_hwnd"] = hwnd
        result["test_owned_pid"] = pid
        result["matches_actual_pid"] = backend.source_matches(hwnd, pid)
        result["mismatched_pid_rejected"] = not backend.source_matches(hwnd, pid + 1)
        assert result["matches_actual_pid"] and result["mismatched_pid_rejected"]

        ctrl = ReadOnlyDwmPreviews(backend)
        def placement():
            root.update_idletasks()
            return PreviewPlacement(
                hwnd, pid, owner,
                target.winfo_rootx(), target.winfo_rooty(),
                target.winfo_width(), target.winfo_height())

        first = ctrl.sync([placement()])
        result["register_update"] = len(first.rendered) == 1 and not first.errors
        result["create_or_register_errors"] = list(first.errors)
        assert result["register_update"], first.errors
        result["destination_count_after_register"] = len(ctrl.active_hwnds)

        target.place_configure(x=64, y=103)
        root.update()
        updated = ctrl.sync([placement()])
        result["reposition_update"] = len(updated.rendered) == 1 and not updated.errors
        assert result["reposition_update"], updated.errors

        # Simulate a REJECTED PID change against a real source HWND.
        # This is a test-only negative case, not a game HWND fabrication.
        denied = PreviewPlacement(hwnd, pid + 1, owner,
                                  target.winfo_rootx(), target.winfo_rooty(), 197, 110)
        mismatch = ctrl.sync([denied])
        result["stale_pid_refused"] = not mismatch.rendered and not ctrl.active_hwnds
        result["stale_pid_errors"] = list(mismatch.errors)
        assert result["stale_pid_refused"]

        second = ctrl.sync([placement()])
        assert second.rendered == (hwnd,), second.errors
        ctrl.clear()
        result["cleared_on_leave"] = not ctrl.active_hwnds
        ctrl.shutdown()
        result["closed_and_cleared"] = not ctrl.active_hwnds
        assert result["cleared_on_leave"] and result["closed_and_cleared"]
        result["status"] = "PASS_NATIVE_DWM_THUMBNAIL_LIFECYCLE"
    except Exception as exc:
        result["status"] = "FAIL_NATIVE_DWM_LIFECYCLE"
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc(limit=12)
    finally:
        if ctrl is not None:
            try: ctrl.shutdown()
            except Exception as exc:
                result["cleanup_error"] = str(exc)
                result["status"] = "FAIL_NATIVE_DWM_CLEANUP"
        if source is not None:
            try: source.destroy()
            except Exception: pass
        if root is not None:
            try: root.destroy()
            except Exception: pass
        REPORT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        for k, v in result.items():
            if k != "traceback":
                print(f"S11_{k.upper()}={json.dumps(v, ensure_ascii=False)}")
    return 0 if result["status"] == "PASS_NATIVE_DWM_THUMBNAIL_LIFECYCLE" else 1


if __name__ == "__main__":
    raise SystemExit(run())
