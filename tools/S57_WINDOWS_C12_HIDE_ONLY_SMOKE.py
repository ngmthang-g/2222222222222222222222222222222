"""S57 native Windows C12 hide-only proof on two TEST-OWNED Tk HWNDs.

Uses genuine Win32 SetWindowPos/GetWindowRect/IsWindowVisible, but never
moves a real game or touches an original user account/license. A test-local
identity adapter accepts exactly two newly created test HWNDs and cannot
grant permissions in the product. No restore semantics are inferred.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "artifacts" / "s57"
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT / "native_test_only_c12_offscreen.json"


def run():
    out = {
        "task": "S57", "status": "NOT_RUN", "real_game": "NOT_RUN",
        "license": "NOT_CONNECTED", "game_launches": 0, "game_logins": 0,
        "proxy_runtime": "EXCLUDED", "original_restore_branch": "UNKNOWN",
        "original_start_auto_screenshot_raster": "NOT_AVAILABLE",
        "product_exe": "NOT_PRODUCT",
    }
    root = None
    try:
        if os.name != "nt":
            raise RuntimeError("S57_WINDOWS_REQUIRED")
        import ctypes
        import tkinter as tk
        from layout_windows import NativeLayoutBackend
        from window_hide import C12HideAll
        from start_polling import WindowSnapshot
        from start_windows import (
            GameWindow, GAME_PROCESS, GAME_TITLE, UNITY_WINDOW_CLASS)

        root = tk.Tk()
        root.title("S57 TEST ONLY ROOT")
        root.geometry("250x160+180+190")
        other = tk.Toplevel(root)
        other.title("S57 TEST ONLY SECOND")
        other.geometry("270x170+490+310")
        root.update_idletasks()
        root.update()
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        ancestor = user32.GetAncestor
        ancestor.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        ancestor.restype = ctypes.c_void_p
        handles = tuple(int(ancestor(w.winfo_id(), 2)) for w in (root, other))
        real = NativeLayoutBackend()
        pid = os.getpid()
        out["two_real_test_owned_windows"] = (
            len(set(handles)) == 2 and all(
                real.is_window(h) and real.is_visible(h)
                and real.process_id(h) == pid for h in handles))
        out["actual_native_identity_is_python_not_game"] = (
            real.process_executable(pid).casefold().endswith(
                ("python.exe", "pythonw.exe", "python3.exe")))
        before = {h: real.window_rect(h) for h in handles}
        size = lambda r: (r[2] - r[0], r[3] - r[1])

        class TestOnlyTwoWindows:
            def enumerate_top_level(self):
                return tuple(h for h in real.enumerate_top_level() if h in handles)
            def is_window(self, h):
                return h in handles and real.is_window(h)
            def is_visible(self, h):
                return h in handles and real.is_visible(h)
            def process_id(self, h):
                return real.process_id(h) if h in handles else 0
            def process_executable(self, p):
                return GAME_PROCESS if p == pid else ""
            def window_class(self, h):
                return UNITY_WINDOW_CLASS if h in handles else ""
            def title_with_timeout(self, h, _ms):
                return GAME_TITLE if h in handles else ""
            def window_rect(self, h):
                return real.window_rect(h)
            def move_no_resize(self, h, x, y):
                return real.move_no_resize(h, x, y) if h in handles else False

        rows = tuple(GameWindow(h, pid, GAME_TITLE, UNITY_WINDOW_CLASS, GAME_PROCESS)
                     for h in handles)
        snapshot = WindowSnapshot(3, rows, True)
        handler = C12HideAll(TestOnlyTwoWindows())
        out["unauthorized_limits_refuse_hide"] = (
            handler.hide(snapshot, max_windows=0).code == "NO_VERIFIED_WINDOW_LIMIT"
            and all(real.window_rect(h) == before[h] for h in handles))
        first = handler.hide(snapshot, max_windows=2, master_hwnd=handles[1])
        # Refresh Win32 geometry, but do not invoke a guessed restore.
        rects = {h: real.window_rect(h) for h in handles}
        out["native_negative_2200_position_and_size_preserved"] = (
            first.code == "HIDDEN" and handler.hidden
            and first.moved == (handles[1], handles[0])
            and all(rects[h][:2] == (-2200, -2200)
                    and size(rects[h]) == size(before[h]) for h in handles))
        out["saved_exact_pre_hide_windows_rects"] = (
            dict((h, rect) for h, _pid, rect in first.saved_rects) == before)
        out["native_visibility_preserved_not_hidden_api"] = all(
            real.is_window(h) and real.is_visible(h)
            and real.process_id(h) == pid for h in handles)
        second = handler.hide(snapshot, max_windows=2)
        out["repeat_hide_cannot_overwrite_saved_geometry"] = (
            second.code == "ALREADY_HIDDEN"
            and second.saved_rects == first.saved_rects)
        out["restore_ambiguous_and_not_invented"] = (
            not hasattr(handler, "restore") and not hasattr(handler, "show"))
        root.destroy()
        root = None
        checks = (
            "two_real_test_owned_windows", "actual_native_identity_is_python_not_game",
            "unauthorized_limits_refuse_hide",
            "native_negative_2200_position_and_size_preserved",
            "saved_exact_pre_hide_windows_rects",
            "native_visibility_preserved_not_hidden_api",
            "repeat_hide_cannot_overwrite_saved_geometry",
            "restore_ambiguous_and_not_invented",
        )
        assert all(out[k] is True for k in checks), "S57_NATIVE_C12_ASSERTIONS"
        out["status"] = "PASS_NATIVE_S57_C12_HIDE_ONLY_TEST_OWNED_WINDOWS"
    except Exception as exc:
        out["status"] = "FAIL_NATIVE_S57"
        out["error_type"] = type(exc).__name__
        out["error_text"] = str(exc)[:160]
    finally:
        if root is not None:
            try: root.destroy()
            except Exception: pass
        REPORT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
        for key, value in out.items():
            print("S57_" + key.upper() + "=" + json.dumps(value, ensure_ascii=True))
    return int(out["status"] != "PASS_NATIVE_S57_C12_HIDE_ONLY_TEST_OWNED_WINDOWS")


if __name__ == "__main__":
    raise SystemExit(run())
