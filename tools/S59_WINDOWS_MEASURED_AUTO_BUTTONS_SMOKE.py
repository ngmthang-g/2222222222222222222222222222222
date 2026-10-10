"""S59 native Windows Tk: live source-backed Start C10/C11 worker lifecycle.

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
OUT=ROOT/"artifacts"/"s59"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"native_measured_auto_buttons.json"

def run():
    result={
        "task":"S59","status":"NOT_RUN",
        "real_game":"NOT_RUN","real_license":"NOT_AVAILABLE",
        "original_auto_ui_pixel_parity":"NOT_VERIFIED",
        "actual_auto_buttons":"C10_C11_ONLY",
        "real_game_launches":0,"real_account_logins":0,
        "proxy_runtime":"EXCLUDED","product_exe":"NOT_PRODUCT",
    }
    root=None;app=None;start=None;other=[]
    hold=threading.Event()
    try:
        if os.name!="nt":raise RuntimeError("S59_WINDOWS_REQUIRED")
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
        from grid_master import GridSettingsStore

        with tempfile.TemporaryDirectory(prefix="S59_TEST_ONLY_") as td:
            cfg=Path(td)/"grid_settings.ini"
            root=tk.Tk()
            root.title("S59 TEST-ONLY NOTEBOOK")
            root.geometry("600x900+650+70")
            root.update()
            for i in range(2):
                w=tk.Toplevel(root)
                w.title("S59 TEST OWNED NOT A GAME")
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

            class S59TestIdentity:
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
            backend=S59TestIdentity()
            fixture_rows=tuple(GameWindow(h,pid,GAME_TITLE,UNITY_WINDOW_CLASS,GAME_PROCESS) for h in ids)
            fixture_snapshot=WindowSnapshot(3,fixture_rows,True)
            def pump_native_worker(thread,limit=3.0):
                # Native SetWindowPos on Tk-owned HWND can require messages
                # dispatched by the UI thread. Never join() while Tk is idle.
                deadline=time.monotonic()+limit
                while thread.is_alive() and time.monotonic()<deadline:
                    root.update()
                    time.sleep(.01)
                if thread.is_alive(): return False
                thread.join(timeout=0)
                return True
            producer=StartWindowProducer(NativeWin32Backend)
            builders={
                "info_tab":lambda parent:TLMInfoTab(parent),
                "start_tab":lambda parent:TLMStartTab(
                    parent,producer=producer,grid_settings_store=GridSettingsStore(cfg),
                    stack_service_factory=lambda:C10C11WindowStacker(backend))}
            app=TLMMainApp(root,builders)
            app.position_window_top_right()
            root.update()
            result["original_e03_info_only_before_test_grant"]=(
                app.lifecycle.visible=={"info_tab"})
            guard=PermissionGuard()
            assert guard.receive_token(
                "S59_TEST_ONLY",lambda _:VerifiedClaims(
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
            import hashlib
            from PIL import ImageGrab
            reference=ROOT/"docs/ui/original/START_AUTO.png"
            result["original_b14_sha_verified"]=hashlib.sha256(reference.read_bytes()).hexdigest()=="4f1b126ea4ba0034889545653046f552a226d5f0033d2329a8693342184c28cd"
            relative=[]
            for button in (start.btn_stack_tight,start.btn_stack_diagonal):
                relative.append((button.winfo_rootx()-start.container.winfo_rootx(),
                                 button.winfo_rooty()-start.container.winfo_rooty(),
                                 button.winfo_width(),button.winfo_height()))
            result["actual_button_bounds_relative_to_tab"]=relative
            result["measured_bounds_match_original"]=relative==[(169,78,78,21),(249,78,78,21)]
            result["original_button_labels"]=(start.btn_stack_tight.cget("text")=="Xếp gọn" and start.btn_stack_diagonal.cget("text")=="Xếp chéo")
            result["no_unverified_toggle_or_mode"]=(not hasattr(start,"btn_hide_windows") and not hasattr(start,"mode_var"))
            root.update()
            x,y=start.container.winfo_rootx(),start.container.winfo_rooty()
            ImageGrab.grab(bbox=(x,y,x+start.container.winfo_width(),y+244)).save(OUT/"measured_auto_fragment.png")
            begun=time.monotonic()
            result["quick_tk_dispatch_returns_without_join"]=bool(int(start.btn_stack_diagonal.invoke()))
            result["dispatch_no_tk_block"]=(time.monotonic()-begun)<.25
            worker=start._stack_thread
            first_joined=pump_native_worker(worker)
            result["first_worker_completed_with_tk_pumping"]=first_joined
            result["first_stack_outcome"]=getattr(start._stack_last_result,"code","MISSING")
            after={h:native.window_rect(h) for h in ids}
            result["actual_c11_native_diagonal_master_first"]=(
                not worker.is_alive()
                and start._stack_last_result.code=="STACK_DIAGONAL_APPLIED"
                and after[ids[1]][:2]==(0,0) and after[ids[0]][:2]==(50,50)
                and all((after[h][2]-after[h][0],after[h][3]-after[h][1])==widths[h] for h in ids))
            self_before=time.monotonic()
            result["actual_c10_dispatch_returns_quickly"]=bool(int(start.btn_stack_tight.invoke()))
            result["second_dispatch_nonblocking"]=(time.monotonic()-self_before)<.25
            worker=start._stack_thread
            second_joined=pump_native_worker(worker)
            result["second_worker_completed_with_tk_pumping"]=second_joined
            result["second_stack_outcome"]=getattr(start._stack_last_result,"code","MISSING")
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
            assert bool(int(start.btn_stack_diagonal.invoke()))
            assert entered.wait(1)
            result["duplicate_live_dispatch_rejected"]=not bool(int(start.btn_stack_tight.invoke()))
            result["grid_rejected_during_stack"]=(
                not bool(int(start.btn_layout.invoke())) and not start.layout_active)
            guard.clear()
            app.apply_info_snapshot(guard.snapshot)
            root.update()
            result["native_tk_revocation_nonblocking"]=(time.monotonic()-self_before)<.45
            hold.set()
            worker=start._stack_thread
            stopped=pump_native_worker(worker)
            result["revoked_before_movement_does_not_move"]=(
                stopped and not worker.is_alive()
                and all(native.window_rect(h)[:2]==(0,0) for h in ids)
                and start._stack_last_result is None and not bool(int(start.btn_stack_tight.invoke()))
                and not start.poller.active and app.lifecycle.visible=={"info_tab"})
            app.shutdown()
            root.destroy();root=None
            result["app_shutdown_and_worker_cleanup"]=app._closed and not worker.is_alive()
            result["no_extra_settings_game_files"]=not cfg.exists()
            checked=(
                "original_b14_sha_verified",
                "measured_bounds_match_original",
                "original_button_labels",
                "no_unverified_toggle_or_mode",
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
                "grid_rejected_during_stack",
                "native_tk_revocation_nonblocking",
                "revoked_before_movement_does_not_move",
                "app_shutdown_and_worker_cleanup",
                "no_extra_settings_game_files",
            )
            assert all(result.get(k) is True for k in checked),"S59_NATIVE_ASSERTION_FAILED"
            result["status"]="PASS_NATIVE_S59_MEASURED_BUTTONS_REAL_MOVEMENT"
    except Exception as exc:
        result["status"]="FAIL_NATIVE_S59"
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
            print("S59_"+key.upper()+"="+json.dumps(value,ensure_ascii=True))
    return int(result["status"]!="PASS_NATIVE_S59_MEASURED_BUTTONS_REAL_MOVEMENT")

if __name__=="__main__":raise SystemExit(run())
