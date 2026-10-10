"""S73 REAL native Win32 one-shot HWND discovery without any C14 timer.

Only test-owned Python Tk windows are accepted. GAME_PROCESS/Unity class/
GAME_TITLE substitutions are isolated to TestOnlyAdapter. Real NativeWin32Backend
reads HWND existence, visibility and PID, with 150ms original title timeout.
The tool never launches or injects into TLM/game, nor relies on Start-tab view.
"""
from __future__ import annotations

import json
import os
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "artifacts" / "s73"
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT / "detached_one_shot_native.json"


def run():
    report = {
        "task": "S73", "status": "NOT_RUN",
        "native_game_hwn_ds": "NONE",
        "source": "TEST_OWNED_TK_HWND_PIDs_REAL_WIN32",
        "game_identity": "TEST_ONLY_GAME_MARKERS",
        "start_tab": "NOT_CREATED",
        "c14_original_timer": "UNKNOWN_NOT_WIRED",
        "actual_game": "NOT_RUN", "signed_info": "NOT_CONNECTED",
        "product_exe": "NOT_PRODUCT",
    }
    root = None
    scanner = None
    try:
        if os.name != "nt":
            raise RuntimeError("WINDOWS_REQUIRED")
        import tkinter as tk
        from detached_one_shot_scanner import C14DetachedOneShotScanner
        from detached_list_observer import C14DetachedListObserver
        from start_windows import (
            NativeWin32Backend, GAME_PROCESS, GAME_TITLE, UNITY_WINDOW_CLASS,
        )

        root = tk.Tk()
        root.title("S73 owned TEST host - NOT GAME")
        root.geometry("430x270+110+80")
        sources = []
        for i in range(2):
            window = tk.Toplevel(root)
            window.title("S73 TEST WINDOW " + str(i))
            window.geometry(f"240x160+{40+i*260}+430")
            tk.Label(window, text="NO GAME / NO START TAB").pack()
            sources.append(window)
        root.update_idletasks()
        root.update()
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        ancestor = user32.GetAncestor
        ancestor.argtypes = [wintypes.HWND, wintypes.UINT]
        ancestor.restype = wintypes.HWND
        target_hwnds = tuple(int(ancestor(int(w.winfo_id()), 2))
                             for w in sources)
        pid = os.getpid()
        assert len(set(target_hwnds)) == 2

        class TestOnlyAdapter:
            def __init__(self):
                # Construct actual ctypes Win32 adapter on scan worker.
                self.native = NativeWin32Backend()
            def enumerate_top_level(self):
                return tuple(h for h in self.native.enumerate_top_level()
                             if h in target_hwnds)
            def is_window(self, h):
                return self.native.is_window(h)
            def is_visible(self, h):
                return self.native.is_visible(h)
            def process_id(self, h):
                return self.native.process_id(h)
            def process_executable(self, p):
                # TEST-ONLY substitution. Native process identity still
                # validated independently, never treated as a real game.
                return GAME_PROCESS if p == pid else self.native.process_executable(p)
            def window_class(self, h):
                return UNITY_WINDOW_CLASS if h in target_hwnds else self.native.window_class(h)
            def title_with_timeout(self, h, ms):
                assert ms == 150
                # Exercise actual Win32 150ms bounded API before adapting.
                raw = self.native.title_with_timeout(h, ms)
                assert "S73 TEST WINDOW" in raw
                return GAME_TITLE

        def verified_scan():
            code = scanner.request(max_windows=2, allowed=lambda: True)
            assert code == "SCAN_STARTED", code
            worker = scanner._thread
            worker.join(9)
            assert not worker.is_alive()
            outcome = scanner.read()
            assert outcome.code == "READY", outcome
            return outcome.snapshot

        scanner = C14DetachedOneShotScanner(TestOnlyAdapter)
        # S72 owner-side observer consumes only separately requested results.
        observed = []
        observer = C14DetachedListObserver(lambda: observed.append("invalidate"))
        before = verified_scan()
        report["two_real_native_Tk_HWND_PID_validated"] = (
            before.valid and len(before.windows) == 2
            and tuple(w.hwnd for w in before.windows) == target_hwnds
            and all(w.pid == pid for w in before.windows))
        assert report["two_real_native_Tk_HWND_PID_validated"]

        first = observer.observe(before, max_windows=2,
                                 allowed=lambda: True)
        assert first.code == "LIST_CHANGED"
        report["independent_snapshot_received_without_Start_tab"] = True

        sources[1].destroy()
        root.update_idletasks()
        root.update()
        after = verified_scan()
        report["genuine_native_destroy_detected_on_explicit_second_scan"] = (
            after.valid and len(after.windows) == 1
            and after.windows[0].hwnd == target_hwnds[0])
        assert report["genuine_native_destroy_detected_on_explicit_second_scan"]

        changed = observer.observe(after, max_windows=2,
                                   allowed=lambda: True)
        report["s72_list_change_invalidates_previous_renderer"] = (
            changed.code == "LIST_CHANGED"
            and len(observed) == 2
            and observer.identities == ((target_hwnds[0], pid),))
        assert report["s72_list_change_invalidates_previous_renderer"]

        # There are no background iterations after the two explicit requests.
        rev = scanner.read().snapshot.revision
        assert scanner.read().snapshot.revision == rev
        report["one_shot_has_no_unverified_periodic_timer"] = True
        scanner.shutdown()
        report["nonblocking_permanent_shutdown"] = (
            scanner.read().code == "CLOSED"
            and scanner.request(max_windows=2, allowed=lambda: True)
            == "CLOSED")
        assert report["nonblocking_permanent_shutdown"]
        observer.shutdown()
        report["status"] = "PASS_NATIVE_S73_ONE_SHOT_WIN32_C14_INDEPENDENT_TEST_ONLY"
    except Exception as exc:
        report["status"] = "FAIL_NATIVE_S73_ONE_SHOT"
        report["error_type"] = type(exc).__name__
        report["error_text"] = str(exc)[:300]
        report["traceback"] = traceback.format_exc(limit=15)
    finally:
        if scanner is not None:
            try:
                scanner.shutdown()
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
                print("S73_" + key.upper() + "=" +
                      json.dumps(value, ensure_ascii=True))
    return 0 if report["status"] == \
        "PASS_NATIVE_S73_ONE_SHOT_WIN32_C14_INDEPENDENT_TEST_ONLY" else 1


if __name__ == "__main__":
    raise SystemExit(run())
