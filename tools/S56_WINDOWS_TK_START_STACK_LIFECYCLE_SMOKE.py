"""S56 native Windows Tk: live source-backed Start C10/C11 worker lifecycle.

The only tested HWNDs are synthetic Tk top-level windows created by this test.
A TEST-ONLY identity adapter cannot change the real native discovery backend.
No game window, license server, Login, Proxy, credential or OS side effect.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s56"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"native_tk_start_c10_c11_dispatch.json"

def run():
    result={
        "task":"S56","status":"NOT_RUN",
        "real_game":"NOT_RUN","real_license":"NOT_AVAILABLE",
        "original_auto_ui_pixel_parity":"NOT_VERIFIED",
        "actual_auto_buttons":"NOT_WIRED",
        "real_game_launches":0,"real_account_logins":0,
        "proxy_runtime":"EXCLUDED","product_exe":"NOT_PRODUCT",
    }
    root=None;app=None;start=None;other=[]
    hold=threading.Event()
    try:
        if os.name!="nt":raise RuntimeError("S56_WINDOWS_REQUIRED")
        import ctypes
        import tkinter as tk
        from info_tab import TLMInfoTab
        from shell import TLMMainApp
        from permission_guard import PermissionGuard,VerifiedClaims
        from start_tab import TLMStartTab
        from start_polling import WindowSnapshot,StartWindowProducer
        from start_windows import (
            GameWindow,GAME_PROCESS,GAME_TITLE,UNITY_WINDOW_CLASS,
            NativeWin32Backend)
        from layout_windows import NativeLayoutBackend
        from window_stacking import C10C11WindowStacker,StackResult

        with tempfile.TemporaryDirectory(prefix="S56_TEST_ONLY_") as td:
            cfg=Path(td)/"grid_settings.ini"
            root=tk.Tk()
            root.title("S56 TEST-ONLY NOTEBOOK")
            root.geometry("600x900+650+70")
            root.update()
            for i in range(2):
                w=tk.Toplevel(root)
                w.title("S56 TEST OWNED NOT A GAME")
                w.geometry(f"230x145+{250+i*270}+340")
                other.append(w)
            root.update()
            u32=ctypes.WinDLL("user32",use_last_error=True)
            ancestor=u32.GetAncestor
            ancestor.argtypes=[ctypes.c_void_p,ctypes.c_uint]
            ancestor.restype=ctypes.c_void_p
            ids=tuple(int(ancestor(w.winfo_id(),2)) for w in other)
            native=NativeLayoutBackend()
            pid=os.getpid()
            result["two_real_test_windows_not_game"]=(
                len(set(ids))==2 and all(native.is_window(h) and native.process_id(h)==pid for h in ids)
                and native.process_executable(pid).lower().endswith(("python.exe","pythonw.exe","python3.exe")))
            before={h:native.window_rect(h) for h in ids}
            widths={h:(before[h][2]-before[h][0],before[h][3]-before[h][1]) for h in ids}

            class S56TestIdentity:
                def enumerate_top_level(self):
                    return tuple(h for h in native.enumerate_top_level() if h in ids)
                def is_window(self,h):return h in ids and native.is_window(h)
                def is_visible(self,h):return h in ids and native.is_visible(h)
                def process_id(self,h):return native.process_id(h) if h in ids else 0
                def process_executable(self,p):return GAME_PROCESS if p==pid else ""
                def window_class(self,h):return UNITY_WINDOW_CLASS if h in ids else ""
                def title_with_timeout(self,h,_ms):return GAME_TITLE if h in ids else ""
                def window_rect(self,h):return native.window_rect(h)
                def move_no_resize(self,h,x,y):
                    return native.move_no_resize(h,x,y) if h in ids else False
            backend=S56TestIdentity()
            fixture_rows=tuple(GameWindow(h,pid,GAME_TITLE,UNITY_WINDOW_CLASS,GAME_PROCESS) for h in ids)
            fixture_snapshot=WindowSnapshot(3,fixture_rows,True)
            producer=StartWindowProducer(NativeWin32Backend)
            builders={
                "info_tab":lambda parent:TLMInfoTab(parent),
                "start_tab":lambda parent:TLMStartTab(
                    parent,producer=producer,grid_settings_store=None,
                    stack_service_factory=lambda:C10C11WindowStacker(backend))}
            app=TLMMainApp(root,builders)
            app.position_window_top_right()
            root.update()
            result["original_e03_info_only_before_test_grant"]=(
                app.lifecycle.visible=={"info_tab"})
            guard=PermissionGuard()
            assert guard.receive_token(
                "S56_TEST_ONLY",lambda _:VerifiedClaims(
                    frozenset({"start_tab","info_tab"}),"TEST_ONLY",2))
            app.apply_info_snapshot(guard.snapshot)
            root.update()
            app.notebook.select(app._tab_frames["start_tab"])
            root.update()
            start=app.lifecycle._instances["start_tab"]
            producer.read_snapshot=lambda:fixture_snapshot
            start.layout_master_hwnd=ids[1]
            result["real_tk_start_active_with_test_claims"]=(
                start.poller.active and start.container.winfo_viewable()
                and start.layout_max_windows==2)
            begun=time.monotonic()
            result["quick_tk_dispatch_returns_without_join"]=start._stack_diagonal_cmd()
            result["dispatch_no_tk_block"]=(time.monotonic()-begun)<.25
            worker=start._stack_thread
            worker.join(2)
            after={h:native.window_rect(h) for h in ids}
            result["actual_c11_native_diagonal_master_first"]=(
                not worker.is_alive()
                and start._stack_last_result.code=="STACK_DIAGONAL_APPLIED"
                and after[ids[1]][:2]==(0,0) and after[ids[0]][:2]==(50,50)
                and all((after[h][2]-after[h][0],after[h][3]-after[h][1])==widths[h] for h in ids))
            self_before=time.monotonic()
            result["actual_c10_dispatch_returns_quickly"]=start._stack_tight_cmd()
            result["second_dispatch_nonblocking"]=(time.monotonic()-self_before)<.25
            worker=start._stack_thread
            worker.join(2)
            after_tight={h:native.window_rect(h) for h in ids}
            result["actual_c10_native_tight_stack_preserves_dimensions"]=(
                not worker.is_alive()
                and start._stack_last_result.code=="STACK_TIGHT_APPLIED"
                and all(after_tight[h][:2]==(0,0) and
                        (after_tight[h][2]-after_tight[h][0],after_tight[h][3]-after_tight[h][1])==widths[h]
                        for h in ids))
            entered=threading.Event()
            class BlockingStack:
                def apply(self,snapshot,*,mode,max_windows,master_hwnd,allowed):
                    entered.set()
                    hold.wait(3)
                    return C10C11WindowStacker(backend).apply(
                        snapshot,mode=mode,max_windows=max_windows,
                        master_hwnd=master_hwnd,allowed=allowed)
            start._stack_service_factory=BlockingStack
            self_before=time.monotonic()
            assert start._stack_diagonal_cmd()
            assert entered.wait(1)
            result["duplicate_live_dispatch_rejected"]=not start._stack_tight_cmd()
            guard.clear()
            app.apply_info_snapshot(guard.snapshot)
            root.update()
            result["native_tk_revocation_nonblocking"]=(time.monotonic()-self_before)<.45
            hold.set()
            worker=start._stack_thread
            worker.join(2)
            result["revoked_before_movement_does_not_move"]=(
                not worker.is_alive()
                and all(native.window_rect(h)[:2]==(0,0) for h in ids)
                and start._stack_last_result is None and not start._stack_tight_cmd()
                and not start.poller.active and app.lifecycle.visible=={"info_tab"})
            app.shutdown()
            root.destroy();root=None
            result["app_shutdown_and_worker_cleanup"]=app._closed and not worker.is_alive()
            result["no_extra_settings_game_files"]=not cfg.exists()
            checked=(
                "two_real_test_windows_not_game",
                "original_e03_info_only_before_test_grant",
                "real_tk_start_active_with_test_claims",
                "quick_tk_dispatch_returns_without_join",
                "dispatch_no_tk_block",
                "actual_c11_native_diagonal_master_first",
                "actual_c10_dispatch_returns_quickly",
                "second_dispatch_nonblocking",
                "actual_c10_native_tight_stack_preserves_dimensions",
                "duplicate_live_dispatch_rejected",
                "native_tk_revocation_nonblocking",
                "revoked_before_movement_does_not_move",
                "app_shutdown_and_worker_cleanup",
                "no_extra_settings_game_files",
            )
            assert all(result.get(k) is True for k in checked),"S56_NATIVE_ASSERTION_FAILED"
            result["status"]="PASS_NATIVE_S56_START_C10_C11_ASYNC_LIFETIME"
    except Exception as exc:
        result["status"]="FAIL_NATIVE_S56"
        result["error_type"]=type(exc).__name__
        result["error_text"]=str(exc)[:220]
    finally:
        hold.set()
        if app is not None:
            try:app.shutdown()
            except Exception:pass
        if root is not None:
            try:root.destroy()
            except Exception:pass
        REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
        for key,value in result.items():
            print("S56_"+key.upper()+"="+json.dumps(value,ensure_ascii=True))
    return int(result["status"]!="PASS_NATIVE_S56_START_C10_C11_ASYNC_LIFETIME")

if __name__=="__main__":raise SystemExit(run())
