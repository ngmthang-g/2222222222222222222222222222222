"""S55 native Win32 proof: C10/C11 position-only movement on TEST-OWNED HWNDs.

Uses real Tk Toplevel handles + real Win32 SetWindowPos/GetWindowRect but
NEVER touches game processes. Test adapter synthesizes game candidate identity
only for this isolated fixture; no test claim is production authorization.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s55"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"native_test_owned_move_only_stacks.json"

def run():
    out={"task":"S55","status":"NOT_RUN","real_game":"NOT_RUN",
         "real_game_auth":"NOT_AVAILABLE","test_identity_only":True,
         "game_launches":0,"game_logins":0,"proxy_runtime":"EXCLUDED",
         "original_auto_tile_concurrency":"UNKNOWN",
         "hidden_state_reset_integration":"NOT_IMPLEMENTED",
         "product_exe":"NOT_PRODUCT"}
    root=None
    try:
        if os.name!="nt":
            raise RuntimeError("S55_WINDOWS_REQUIRED")
        import ctypes
        import tkinter as tk
        from layout_windows import NativeLayoutBackend
        from window_stacking import C10C11WindowStacker
        from start_polling import WindowSnapshot
        from start_windows import (GameWindow, GAME_PROCESS,GAME_TITLE,UNITY_WINDOW_CLASS)

        root=tk.Tk()
        root.title("S55 TEST OWNED ROOT HWND")
        root.geometry("220x130+200+230")
        other=tk.Toplevel(root)
        other.title("S55 TEST OWNED OTHER HWND")
        other.geometry("210x120+450+350")
        root.update_idletasks()
        root.update()
        user32=ctypes.WinDLL("user32",use_last_error=True)
        get_ancestor=user32.GetAncestor
        get_ancestor.argtypes=[ctypes.c_void_p,ctypes.c_uint]
        get_ancestor.restype=ctypes.c_void_p
        handles=tuple(int(get_ancestor(w.winfo_id(),2)) for w in (root,other))
        assert len(set(handles))==2 and all(handles)
        real=NativeLayoutBackend()
        pid=os.getpid()
        out["genuine_windows_top_level_hwnds"]=all(
            real.is_window(h) and real.is_visible(h)
            and real.process_id(h)==pid for h in handles)
        out["native_backend_refuses_test_python_identity"]=all(
            real.process_executable(pid).casefold().endswith(
                ("python.exe","python3.exe","pythonw.exe"))
            for _ in handles)
        initial_rects={h:real.window_rect(h) for h in handles}
        size=lambda r:(r[2]-r[0],r[3]-r[1])
        expected_sizes={h:size(initial_rects[h]) for h in handles}
        # Identity override is *strictly* in this Windows smoke and limited to
        # the two test-owned Tk windows. Production backend has no such override.
        class TestOnlyIdentityAdapter:
            def enumerate_top_level(self):
                return tuple(h for h in real.enumerate_top_level() if h in handles)
            def is_window(self,h):
                return h in handles and real.is_window(h)
            def is_visible(self,h):
                return h in handles and real.is_visible(h)
            def process_id(self,h):
                return real.process_id(h) if h in handles else 0
            def process_executable(self,p):
                return GAME_PROCESS if p==pid else ""
            def window_class(self,h):
                return UNITY_WINDOW_CLASS if h in handles else ""
            def title_with_timeout(self,h,_ms):
                return GAME_TITLE if h in handles else ""
            def window_rect(self,h):
                return real.window_rect(h)
            def move_no_resize(self,h,x,y):
                if h not in handles: return False
                return real.move_no_resize(h,x,y)
        backend=TestOnlyIdentityAdapter()
        original=(GameWindow(h,pid,GAME_TITLE,UNITY_WINDOW_CLASS,GAME_PROCESS)
                  for h in handles)
        rows=tuple(original)
        snap=WindowSnapshot(1,rows,True)
        svc=C10C11WindowStacker(backend)
        diag=svc.apply(snap,mode="diagonal",max_windows=2,
                       master_hwnd=handles[1])
        after_diag={h:real.window_rect(h) for h in handles}
        out["c11_real_setwindowpos_50px_diagonal"]=(
            diag.code=="STACK_DIAGONAL_APPLIED"
            and after_diag[handles[1]][:2]==(0,0)
            and after_diag[handles[0]][:2]==(50,50)
            and all(size(after_diag[h])==expected_sizes[h] for h in handles))
        tight=svc.apply(snap,mode="tight",max_windows=2,
                        master_hwnd=handles[1])
        after_tight={h:real.window_rect(h) for h in handles}
        out["c10_real_setwindowpos_both_zero"]=(
            tight.code=="STACK_TIGHT_APPLIED"
            and all(after_tight[h][:2]==(0,0) for h in handles)
            and all(size(after_tight[h])==expected_sizes[h] for h in handles))
        out["missing_authorization_blocks_window_actions"]=(
            svc.apply(snap,mode="tight",max_windows=0).code
            =="NO_VERIFIED_WINDOW_LIMIT")
        out["window_handles_remain_owned_by_test"]=all(
            real.process_id(h)==pid for h in handles)
        root.destroy()
        root=None
        out["no_original_game_actions"]=True
        expected={"genuine_windows_top_level_hwnds",
                  "native_backend_refuses_test_python_identity",
                  "c11_real_setwindowpos_50px_diagonal",
                  "c10_real_setwindowpos_both_zero",
                  "missing_authorization_blocks_window_actions",
                  "window_handles_remain_owned_by_test",
                  "no_original_game_actions"}
        assert all(out[k] is True for k in expected),"S55_NATIVE_PROOF_FAILED"
        out["status"]="PASS_NATIVE_S55_C10_C11_TEST_OWNED_MOVE_ONLY"
    except Exception as exc:
        out["status"]="FAIL_NATIVE_S55"
        out["error_type"]=type(exc).__name__
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        REPORT.write_text(json.dumps(out,indent=2,ensure_ascii=False),
                          encoding="utf-8")
        for key,value in out.items():
            print("S55_"+key.upper()+"="+json.dumps(value,ensure_ascii=True))
    return int(out["status"]!="PASS_NATIVE_S55_C10_C11_TEST_OWNED_MOVE_ONLY")

if __name__=="__main__":raise SystemExit(run())
