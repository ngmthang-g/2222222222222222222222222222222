"""S72 real Windows test-owned DWM list-change cleanup; NOT an actual game.

All GAME_PROCESS/class/title markers are explicitly TEST-ONLY snapshot
fixtures. Real source HWNDs, PIDs, DWM thumbnails and Win32 teardown are
measured. No detached tile geometry, auto-open or original timer is claimed.
"""
from __future__ import annotations
import ctypes
import json
import os
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "artifacts" / "s72"
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT / "detached_list_change_native.json"


def run():
    report = {
        "task": "S72", "status": "NOT_RUN",
        "sources": "REAL_TEST_OWNED_PYTHON_TK_HWND_NOT_GAME",
        "snapshot_identity": "TEST_ONLY_GAME_MARKER_ADAPTATION",
        "actual_game": "NOT_RUN", "signed_info": "NOT_CONNECTED",
        "detached_auto_open": "NOT_WIRED",
        "original_tile_layout": "UNKNOWN",
        "original_detached_cadence": "UNKNOWN",
        "product_exe": "NOT_PRODUCT",
    }
    root = None
    previews = None
    try:
        if os.name != "nt":
            raise RuntimeError("WINDOWS_REQUIRED")
        import tkinter as tk
        from ctypes import wintypes
        from detached_list_observer import C14DetachedListObserver
        from dwm_preview import NativeDwmBackend, PreviewPlacement, ReadOnlyDwmPreviews
        from start_windows import GameWindow, GAME_TITLE, UNITY_WINDOW_CLASS, GAME_PROCESS
        from start_polling import WindowSnapshot

        user32 = ctypes.WinDLL("user32", use_last_error=True)
        get_pid = user32.GetWindowThreadProcessId
        get_pid.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
        get_pid.restype = wintypes.DWORD
        is_window = user32.IsWindow
        is_window.argtypes = [wintypes.HWND]
        is_window.restype = wintypes.BOOL
        backend = NativeDwmBackend()

        def top_hwnd(widget):
            return int(backend._ancestor(int(widget.winfo_id()), 2))

        def true_pid(hwnd):
            value = wintypes.DWORD()
            get_pid(hwnd, ctypes.byref(value))
            return value.value

        root = tk.Tk()
        root.title("S72 TEST OWNED HOST - NO GAME")
        root.geometry("650x360+120+80")
        src1 = tk.Toplevel(root)
        src1.title("S72 source one TEST ONLY")
        src1.geometry("260x190+60+450")
        src2 = tk.Toplevel(root)
        src2.title("S72 source two TEST ONLY")
        src2.geometry("260x190+340+450")
        tk.Label(src1, text="TEST HWND - NOT A GAME").pack()
        tk.Label(src2, text="TEST HWND - NOT A GAME").pack()
        root.update_idletasks()
        root.update()
        owner = top_hwnd(root)
        sources = (top_hwnd(src1), top_hwnd(src2))
        pid = os.getpid()
        assert len(set((owner,) + sources)) == 3
        assert all(bool(is_window(h)) and true_pid(h) == pid
                   for h in (owner,) + sources)
        assert all(backend.source_matches(h, pid) for h in sources)
        report["native_owned_sources_and_pid_verified"] = True

        class TraceNativeDwm(NativeDwmBackend):
            def __init__(self):
                super().__init__()
                self.events = []
            def unregister(self, token):
                self.events.append(("unregister", int(token)))
                return super().unregister(token)
            def destroy_destination(self, destination):
                self.events.append(("destroy", int(destination)))
                return super().destroy_destination(destination)

        native = TraceNativeDwm()
        previews = ReadOnlyDwmPreviews(native)
        rows = tuple(GameWindow(h, pid, GAME_TITLE, UNITY_WINDOW_CLASS,
                                GAME_PROCESS) for h in sources)

        def rev(value, values):
            return WindowSnapshot(value, tuple(values), True)

        invalidations = []
        def invalidate():
            invalidations.append("C14_SHUT_DOWN_OLD_DESTINATIONS")
            previews.clear()

        observer = C14DetachedListObserver(invalidate)
        initial = observer.observe(rev(1, rows), max_windows=2,
                                   allowed=lambda: True)
        assert initial.code == "LIST_CHANGED"

        actual = previews.sync((
            PreviewPlacement(sources[0], pid, owner, 25, 30, 197, 110),
            PreviewPlacement(sources[1], pid, owner, 245, 30, 197, 110),
        ))
        report["two_actual_DWM_registrations"] = (
            actual.rendered == sources and previews.active_hwnds == sources)
        assert report["two_actual_DWM_registrations"], actual

        same = observer.observe(rev(2, rows), max_windows=2,
                                allowed=lambda: True)
        report["unchanged_revision_no_extra_cleanup"] = (
            same.code == "UNCHANGED" and len(invalidations) == 1
            and previews.active_hwnds == sources)
        assert report["unchanged_revision_no_extra_cleanup"]

        src2.destroy()
        root.update_idletasks()
        root.update()
        assert not bool(is_window(sources[1]))
        changed = observer.observe(rev(3, (rows[0],)), max_windows=2,
                                   allowed=lambda: True)
        report["real_closed_HWND_invalidates_old_native_DWM"] = (
            changed.code == "LIST_CHANGED" and
            previews.active_hwnds == () and
            len([e for e in native.events if e[0] == "unregister"]) == 2 and
            len([e for e in native.events if e[0] == "destroy"]) == 2)
        assert report["real_closed_HWND_invalidates_old_native_DWM"]

        revoked = observer.observe(rev(4, (rows[0],)), max_windows=2,
                                   allowed=lambda: False)
        report["permission_revocation_fails_closed"] = (
            revoked.code == "PERMISSION_REVOKED"
            and observer.identities == ())
        assert report["permission_revocation_fails_closed"]
        report["no_Tk_after_or_Start_tab_lifecycle_required"] = True
        assert observer.shutdown().code == "CLOSED"
        report["status"] = "PASS_NATIVE_S72_C14_HWND_CHANGE_RELEASES_DWM_TEST_ONLY"
    except Exception as exc:
        report["status"] = "FAIL_NATIVE_S72_C14_HWND_CHANGE"
        report["error_type"] = type(exc).__name__
        report["error_text"] = str(exc)[:300]
        report["traceback"] = traceback.format_exc(limit=15)
    finally:
        if previews is not None:
            try:
                previews.shutdown()
            except Exception:
                pass
        if root is not None:
            try:
                root.destroy()
            except Exception:
                pass
        REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2),
                          encoding="utf-8")
        for key, value in report.items():
            if key != "traceback":
                print("S72_" + key.upper() + "=" +
                      json.dumps(value, ensure_ascii=True))
    return 0 if report["status"] == \
        "PASS_NATIVE_S72_C14_HWND_CHANGE_RELEASES_DWM_TEST_ONLY" else 1


if __name__ == "__main__":
    raise SystemExit(run())
