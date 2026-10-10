"""S74 genuine Windows Tk/DWM host CLOSED by S73+S72 HWND list change.

Real native processes and HWND/DWM APIs, but sources are two TEST-OWNED
Python Tk windows; only the TEST-ONLY adapter replaces process/class/title.
Positive 1600x1000 desktop metrics are a documented Tk fixture, NOT real
hosted 1024x768 desktop/real game parity or original tile geometry.
No invented polling loop or UI button.
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
OUT = ROOT / "artifacts" / "s74"
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT / "detached_native_lifecycle.json"


def run():
    report = {
        "task": "S74", "status": "NOT_RUN",
        "source_type": "TWO_REAL_TEST_OWNED_PYTHON_TK_HWNDS_NOT_GAME",
        "identity_substitution": "TEST_ONLY_PROCESS_CLASS_TITLE",
        "actual_game": "NOT_RUN", "signed_info": "NOT_CONNECTED",
        "C14_original_detached_cadence": "UNKNOWN_NOT_WIRED",
        "C14_original_tile_geometry": "UNKNOWN_TEST_ONLY_PLACEMENTS",
        "product_exe": "NOT_PRODUCT",
    }
    root = None
    controller = None
    scanner = None
    host = None
    try:
        if os.name != "nt":
            raise RuntimeError("WINDOWS_REQUIRED")
        import tkinter as tk
        from layout_windows import NativeLayoutBackend
        from dwm_preview import NativeDwmBackend, PreviewPlacement
        from detached_preview import C14DetachedDwmSession, verified_detached_region
        from detached_host import C14DetachedHost, _native_is_topmost
        from detached_one_shot_scanner import C14DetachedOneShotScanner
        from detached_lifecycle import C14DetachedLifecycle
        from start_windows import (
            GAME_PROCESS, GAME_TITLE, UNITY_WINDOW_CLASS, NativeWin32Backend)

        backend = NativeLayoutBackend()
        events = []
        class CountedDwm(NativeDwmBackend):
            def register(self, *args):
                token = super().register(*args)
                events.append(("register", int(token)))
                return token
            def unregister(self, token):
                events.append(("unregister", int(token)))
                return super().unregister(token)
            def destroy_destination(self, hwnd):
                events.append(("destroy_destination", int(hwnd)))
                return super().destroy_destination(hwnd)
        native_dwm = CountedDwm()
        root = tk.Tk()
        root.title("S74 test root NOT GAME")
        root.geometry("420x260+130+60")
        sources = []
        for i in range(2):
            t = tk.Toplevel(root)
            t.title("S74 test-owned source %d"%(i+1))
            t.geometry(f"220x160+{15+i*230}+460")
            tk.Label(t, text="NO GAME TEST HWND").pack()
            sources.append(t)
        root.update_idletasks()
        root.update()
        source_hwnds = tuple(
            int(native_dwm._ancestor(int(w.winfo_id()), 2))
            for w in sources)
        pid = os.getpid()
        assert len(set(source_hwnds)) == 2
        assert all(native_dwm.source_matches(h, pid) for h in source_hwnds)

        raw_native_titles = []
        class TestOnlyIdentity:
            def __init__(self):
                self.actual = NativeWin32Backend()
            def enumerate_top_level(self):
                return self.actual.enumerate_top_level()
            def is_window(self, h):
                return self.actual.is_window(h)
            def is_visible(self, h):
                return self.actual.is_visible(h)
            def process_id(self, h):
                return self.actual.process_id(h)
            def process_executable(self, p):
                # ONLY TEST fixture claims these real Python windows are game.
                return GAME_PROCESS if p == pid else self.actual.process_executable(p)
            def window_class(self, h):
                return UNITY_WINDOW_CLASS if h in source_hwnds else self.actual.window_class(h)
            def title_with_timeout(self, h, ms):
                assert ms == 150
                raw = self.actual.title_with_timeout(h, ms)
                assert isinstance(raw, str)
                if h in source_hwnds:
                    raw_native_titles.append(raw)
                    return GAME_TITLE
                return raw
            def window_rect(self, h):
                return backend.window_rect(h)
        id_backend = TestOnlyIdentity()

        class TracedHost(tk.Toplevel):
            def destroy(self):
                events.append(("destroy_host",
                               int(native_dwm._ancestor(int(self.winfo_id()),2))))
                return super().destroy()

        host = C14DetachedHost(
            root, windows_backend=id_backend,
            toplevel_factory=lambda parent: TracedHost(parent),
            session_factory=lambda: C14DetachedDwmSession(native_dwm,id_backend))
        scanner = C14DetachedOneShotScanner(TestOnlyIdentity)
        controller = C14DetachedLifecycle(scanner,host)

        def scan_and_consume():
            response = controller.request_scan(max_windows=2,allowed=lambda:True)
            assert response.code == "SCAN_STARTED",response
            scanner._thread.join(8)
            assert not scanner._thread.is_alive()
            assert scanner.read().code == "READY",scanner.read()
            outcome = controller.consume_scan(max_windows=2,allowed=lambda:True)
            return outcome,scanner.read().snapshot

        first, first_snapshot = scan_and_consume()
        assert first.code=="LIST_CHANGED"
        assert tuple(w.hwnd for w in first_snapshot.windows)==source_hwnds
        report["two_real_hwnds_verified_by_native_Win32"] = True
        report["bounded_native_Tk_raw_titles"] = raw_native_titles[:]

        actual_w,actual_h = root.winfo_screenwidth(),root.winfo_screenheight()
        report["actual_desktop"] = [actual_w,actual_h]
        if verified_detached_region(actual_w, actual_h) is None:
            refused = host.open(first_snapshot,max_windows=2,allowed=lambda:True)
            report["short_actual_desktop_refused"] = (
                refused.code=="NO_USABLE_SCREEN_REGION" and host.owner_hwnd==0)
            assert report["short_actual_desktop_refused"]
        else:
            report["short_actual_desktop_refused"]="NOT_APPLICABLE"

        positive_w = max(actual_w,1600)
        positive_h = max(actual_h,1000)
        report["positive_test_uses_virtual_Tk_metrics"] = (
            positive_w!=actual_w or positive_h!=actual_h)
        root.winfo_screenwidth = lambda:positive_w
        root.winfo_screenheight = lambda:positive_h
        region = verified_detached_region(positive_w,positive_h)
        opened = host.open(first_snapshot,max_windows=2,allowed=lambda:True)
        owner = host.owner_hwnd
        report["real_topmost_owner_measured"] = (
            opened.code=="HOST_OPEN" and owner>0
            and backend.is_window(owner) and backend.process_id(owner)==pid
            and _native_is_topmost(owner)
            and backend.window_rect(owner)==(
                region.x,region.y,region.x+region.width,region.y+region.height))
        assert report["real_topmost_owner_measured"],opened

        # TEST-ONLY coordinates measured to fit the region, not alleged
        # original C14 detached x/y/spacing algorithm.
        places = tuple(PreviewPlacement(
            h,pid,owner,15+i*215,780,197,110)
            for i,h in enumerate(source_hwnds))
        rendered = host.render(first_snapshot,max_windows=2,
                               placements=places,allowed=lambda:True)
        report["two_real_native_DWM_thumbnails"] = (
            rendered.code=="DETACHED_DWM_VISIBLE"
            and host.active_hwnds==source_hwnds
            and len([e for e in events if e[0]=="register"])==2)
        assert report["two_real_native_DWM_thumbnails"],rendered

        same, _ = scan_and_consume()
        report["identical_new_scan_preserves_real_DWM_host"] = (
            same.code=="UNCHANGED" and host.owner_hwnd==owner
            and host.active_hwnds==source_hwnds
            and not any(e[0]=="destroy_host" for e in events))
        assert report["identical_new_scan_preserves_real_DWM_host"]

        sources[1].destroy()
        root.update_idletasks()
        root.update()
        assert not backend.is_window(source_hwnds[1])
        changed, remaining = scan_and_consume()
        report["real_native_destroy_triggers_detached_close"] = (
            changed.code=="LIST_CHANGED" and len(remaining.windows)==1
            and remaining.windows[0].hwnd==source_hwnds[0]
            and host.owner_hwnd==0 and not host.active_hwnds
            and not backend.is_window(owner))
        assert report["real_native_destroy_triggers_detached_close"],changed

        unregisters = [i for i,e in enumerate(events)
                       if e[0]=="unregister"]
        destroys = [i for i,e in enumerate(events)
                    if e[0]=="destroy_destination"]
        host_destroy = [i for i,e in enumerate(events)
                        if e[0]=="destroy_host"]
        report["all_native_DWM_cleared_before_owner_destroy"] = (
            len(unregisters)==2 and len(destroys)==2
            and len(host_destroy)==1
            and max(unregisters + destroys)<host_destroy[0])
        assert report["all_native_DWM_cleared_before_owner_destroy"],events
        assert controller.shutdown().code=="CLOSED"
        report["shutdown_permanent_no_auto_reopen"]=(
            scanner.read().code=="CLOSED" and host.owner_hwnd==0)
        assert report["shutdown_permanent_no_auto_reopen"]
        report["status"]="PASS_NATIVE_S74_EXPLICIT_C14_HOST_CLOSE_ON_HWND_CHANGE_TEST_ONLY"
    except Exception as exc:
        report["status"]="FAIL_NATIVE_S74"
        report["error_type"]=type(exc).__name__
        report["error_text"]=str(exc)[:300]
        report["traceback"]=traceback.format_exc(limit=15)
    finally:
        if controller is not None:
            try:controller.shutdown()
            except Exception:pass
        elif scanner is not None:
            try:scanner.shutdown()
            except Exception:pass
        if host is not None:
            try:host.shutdown()
            except Exception:pass
        if root is not None:
            try:root.destroy()
            except Exception:pass
        REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),
                          encoding="utf-8")
        for k,v in report.items():
            if k!="traceback":
                print("S74_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if report["status"]==\
        "PASS_NATIVE_S74_EXPLICIT_C14_HOST_CLOSE_ON_HWND_CHANGE_TEST_ONLY" else 1

if __name__=="__main__":
    raise SystemExit(run())
