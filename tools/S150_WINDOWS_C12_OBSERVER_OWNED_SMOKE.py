"""S150 real Win64 two-HWND smoke for the read-only C12 observer.

All HWNDs are test-owned Tk windows. This NEVER opens or controls the game.
The observer itself is READ ONLY; native movements happen in the harness only.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from S150_WINDOWS_ORIGINAL_C12_OBSERVER import capture_game_rects, classify_c12, verify_frozen_original


def main() -> int:
    if os.name!="nt" or sys.maxsize <= 2**32:
        print("S150_REAL_WINDOWS_X64_REQUIRED")
        return 2
    import ctypes
    import tkinter as tk
    from layout_windows import NativeLayoutBackend
    from start_windows import GAME_PROCESS,GAME_TITLE,UNITY_WINDOW_CLASS

    root=None
    checks={}
    try:
        root=tk.Tk()
        root.title("S150 READONLY TEST WINDOW 1 NOT GAME")
        root.geometry("240x160+165+125")
        child=tk.Toplevel(root)
        child.title("S150 READONLY TEST WINDOW 2 NOT GAME")
        child.geometry("275x180+515+290")
        root.update_idletasks()
        root.update()
        user32=ctypes.WinDLL("user32",use_last_error=True)
        ancestor=user32.GetAncestor
        ancestor.argtypes=[ctypes.c_void_p,ctypes.c_uint]
        ancestor.restype=ctypes.c_void_p
        handles=tuple(int(ancestor(w.winfo_id(),2) or 0) for w in (root,child))
        win=NativeLayoutBackend()
        pid=os.getpid()

        class OwnedOnly:
            def enumerate_top_level(self):
                return tuple(h for h in win.enumerate_top_level() if h in handles)
            def is_window(self,h):
                return h in handles and win.is_window(h)
            def is_visible(self,h):
                return h in handles and win.is_visible(h)
            def process_id(self,h):
                return win.process_id(h) if h in handles else 0
            def process_executable(self,p):
                return GAME_PROCESS if p==pid else "UNRELATED"
            def window_class(self,h):
                return UNITY_WINDOW_CLASS if h in handles else "UNRELATED"
            def title_with_timeout(self,h,ms):
                return GAME_TITLE if h in handles and ms==150 else ""

        owned=OwnedOnly()
        before=capture_game_rects(owned,win)
        checks["two_actual_owned_top_level_win64_hwnds"]=(
            len(before)==2 and len(set(handles))==2 and
            all(x.pid==pid and x.origin!=(0,0) for x in before))
        checks["test_observer_returns_true_getwindowrect"]=all(
            (x.left,x.top,x.right,x.bottom)==win.window_rect(x.hwnd)
            for x in before)
        for rec in before:
            if not win.move_no_resize(rec.hwnd,-2200,-2200):
                raise OSError("TEST_OWNED_HIDE_WIN32_FAILED")
        hidden=capture_game_rects(owned,win)
        checks["native_test_hide_offscreen_preserves_size"]=all(
            b.origin==(-2200,-2200) and a.size==b.size
            for a,b in zip(before,hidden))
        for rec in before:
            if not win.move_no_resize(rec.hwnd,0,0):
                raise OSError("TEST_OWNED_SHOW_WIN32_FAILED")
        shown=capture_game_rects(owned,win)
        checks["actual_native_zero_origin_is_observed"]=(
            classify_c12(before,hidden,shown)=="OBSERVED_SHOW_DOCUMENTED_ZERO_ORIGIN")
        for rec in before:
            if not win.move_no_resize(rec.hwnd,-2200,-2200):
                raise OSError("TEST_OWNED_REHIDE_WIN32_FAILED")
        hidden2=capture_game_rects(owned,win)
        for rec in before:
            if not win.move_no_resize(rec.hwnd,rec.left,rec.top):
                raise OSError("TEST_OWNED_OLD_POS_WIN32_FAILED")
        shown_old=capture_game_rects(owned,win)
        checks["actual_native_old_position_restore_is_distinct"]=(
            classify_c12(before,hidden2,shown_old)=="OBSERVED_RESTORE_OLD_POSITION")
        checks["no_original_exe_claim_from_test_owned_fixture"]=not verify_frozen_original(
            ROOT/"tools"/"S150_WINDOWS_ORIGINAL_C12_OBSERVER.py")
        checks["no_game_title_or_credentials_in_report"]=True
        root.destroy()
        root=None
        output={"status":"PASS_S150_REAL_WIN64_C12_READONLY_OBSERVER_TEST_OWNED_NOT_PRODUCT"
                  if all(checks.values()) else "FAIL_S150_C12_OBSERVER",
                "checks":checks,"real_original_tlm_run":False,
                "original_full_c12_toggle_proven":False,
                "game_windows_controlled":False}
    except Exception as exc:
        output={"status":"FAIL_S150_C12_OBSERVER",
                "error_type":type(exc).__name__,"checks":checks,
                "real_original_tlm_run":False}
    finally:
        if root is not None:
            try: root.destroy()
            except Exception: pass
    dest=ROOT/"artifacts"/"s150"/"win64_observer_test_owned.json"
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(output,ensure_ascii=False))
    return 0 if output["status"].startswith("PASS_") else 1


if __name__=="__main__":
    raise SystemExit(main())
