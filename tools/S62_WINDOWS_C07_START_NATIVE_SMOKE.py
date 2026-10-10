"""S62 real TEST-ONLY Info-gated Tk Start C07 native Win32 reset lifecycle.

Test local process HWNDs ONLY. Does NOT simulate real game runtime or a user
license; trusted TEST_ONLY claims exist exclusively in this CI harness.
"""
from __future__ import annotations
import ctypes,json,os,sys,tempfile,threading,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s62"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"s62_real_tk_owned_c07_reset.json"

def run():
    evidence={"task":"S62","status":"NOT_RUN","actual_game":"NOT_RUN",
              "actual_license":"NOT_CONNECTED","product_exe":"NOT_PRODUCT",
              "proxy_runtime":"EXCLUDED"}
    root=None
    app=None
    release=threading.Event()
    try:
        if os.name!="nt":raise RuntimeError("S62 requires real Windows")
        import tkinter as tk
        from info_tab import TLMInfoTab
        from shell import TLMMainApp
        from permission_guard import PermissionGuard,VerifiedClaims
        from start_tab import TLMStartTab
        from start_polling import WindowSnapshot,StartWindowProducer
        from start_windows import (
            GameWindow,GAME_PROCESS,GAME_TITLE,UNITY_WINDOW_CLASS,NativeWin32Backend)
        from window_auto_reset import C07AutoReset,NativeC07Backend
        from grid_master import GridSettingsStore

        with tempfile.TemporaryDirectory(prefix="S62_TEST_ONLY_") as temp:
            cfg=Path(temp)/"grid.ini"
            root=tk.Tk()
            root.title("S62 TEST SHELL")
            root.geometry("600x900+650+80")
            root.maxsize(2000,1400)
            other=[]
            for index in range(2):
                w=tk.Toplevel(root)
                w.title("S62 TEST OWNED")
                w.geometry(f"310x210+{180+index*380}+{170+index*80}")
                w.maxsize(2000,1400)
                other.append(w)
            root.update_idletasks();root.update()
            user32=ctypes.WinDLL("user32",use_last_error=True)
            ancestor=user32.GetAncestor
            ancestor.argtypes=[ctypes.c_void_p,ctypes.c_uint]
            ancestor.restype=ctypes.c_void_p
            ids=tuple(int(ancestor(w.winfo_id(),2)) for w in other)
            native=NativeC07Backend()
            pid=os.getpid()
            evidence["two_real_test_owned_python_hwnds"]=(
                len(set(ids))==2 and
                native.process_executable(pid).lower().endswith(
                    ("python.exe","pythonw.exe","python3.exe"))
                and all(native.is_window(h) and native.process_id(h)==pid for h in ids))
            before={h:native.window_rect(h) for h in ids}

            class OwnedOnly:
                def enumerate_top_level(self):
                    return tuple(h for h in native.enumerate_top_level() if h in ids)
                def is_window(self,h):
                    return h in ids and native.is_window(h)
                def is_visible(self,h):
                    return h in ids and native.is_visible(h)
                def process_id(self,h):
                    return native.process_id(h) if h in ids else 0
                def process_executable(self,p):
                    return GAME_PROCESS if p==pid else ""
                def window_class(self,h):
                    return UNITY_WINDOW_CLASS if h in ids else ""
                def title_with_timeout(self,h,ms):
                    return GAME_TITLE if h in ids else ""
                def window_rect(self,h):
                    return native.window_rect(h)
                def resize_no_move(self,h,w,height):
                    return native.resize_no_move(h,w,height) if h in ids else False
                def move_no_resize(self,h,x,y):
                    return native.move_no_resize(h,x,y) if h in ids else False

            rows=tuple(GameWindow(h,pid,GAME_TITLE,UNITY_WINDOW_CLASS,GAME_PROCESS)
                      for h in ids)
            snapshot=WindowSnapshot(62,rows,True)
            producer=StartWindowProducer(NativeWin32Backend)
            app=TLMMainApp(root,{
                "info_tab":lambda parent:TLMInfoTab(parent),
                "start_tab":lambda parent:TLMStartTab(
                    parent,producer=producer,
                    grid_settings_store=GridSettingsStore(cfg),
                    auto_reset_service_factory=lambda:C07AutoReset(OwnedOnly()))
            })
            app.position_window_top_right()
            root.update()
            evidence["info_only_before_test_permission"]=app.lifecycle.visible=={"info_tab"}
            guard=PermissionGuard()
            assert guard.receive_token("S62_TEST_ONLY",lambda _:
                VerifiedClaims(frozenset({"start_tab","info_tab"}),"TEST_ONLY",2))
            app.apply_info_snapshot(guard.snapshot)
            root.update()
            app.notebook.select(app._tab_frames["start_tab"])
            root.update()
            start=app.lifecycle._instances["start_tab"]
            producer.read_snapshot=lambda:snapshot
            start.layout_master_hwnd=ids[1]
            evidence["gated_start_selected_with_test_only_claim"]=(
                start.poller.active and start.container.winfo_viewable()
                and start.layout_max_windows==2)

            def pump(worker,limit=5):
                deadline=time.monotonic()+limit
                while worker.is_alive() and time.monotonic()<deadline:
                    root.update()
                    time.sleep(.01)
                if worker.is_alive():return False
                worker.join(timeout=0)
                return True

            t=time.monotonic()
            evidence["internal_reset_started"]=start._dispatch_auto_reset()
            evidence["tk_callback_nonblocking"]=(time.monotonic()-t)<.3
            worker=start._auto_reset_thread
            evidence["native_worker_completed"]=pump(worker)
            evidence["native_result_code"]=getattr(start._auto_reset_last_result,"code","NONE")
            after={h:native.window_rect(h) for h in ids}
            evidence["real_1366x768_reset_master_first"]=(
                not worker.is_alive() and
                start._auto_reset_last_result.code=="AUTO_RESET_APPLIED"
                and start._auto_reset_last_result.resized==(ids[1],ids[0])
                and all(after[h]==(0,0,1366,768) for h in ids)
                and all(native.process_id(h)==pid for h in ids))
            entered=threading.Event()
            class BlockReset:
                def apply(self,snapshot,*,max_windows,master_hwnd,allowed):
                    entered.set()
                    release.wait(3)
                    return C07AutoReset(OwnedOnly()).apply(
                        snapshot,max_windows=max_windows,
                        master_hwnd=master_hwnd,allowed=allowed)
            start._auto_reset_service_factory=BlockReset
            assert start._dispatch_auto_reset()
            assert entered.wait(1)
            evidence["competing_real_stack_and_grid_blocked"]=(
                not start._stack_diagonal_cmd()
                and not start._stack_tight_cmd()
                and not start._toggle_layout()
                and not start.layout_active)
            guard.clear()
            app.apply_info_snapshot(guard.snapshot)
            root.update()
            evidence["authorization_revoked_without_join"]=(
                start.layout_max_windows==0 and not start.poller.active
                and app.lifecycle.visible=={"info_tab"})
            release.set()
            worker=start._auto_reset_thread
            evidence["revoked_worker_exits_cleanly"]=pump(worker)
            evidence["revoked_worker_late_state_is_discarded"]=(
                start._auto_reset_last_result is None
                and not start._dispatch_auto_reset()
                and all(native.window_rect(h)==(0,0,1366,768) for h in ids))
            app.shutdown()
            root.destroy();root=None
            evidence["test_shell_shutdown"]=app._closed
            evidence["did_not_create_settings_file"]=not cfg.exists()
            checks=(
                "two_real_test_owned_python_hwnds",
                "info_only_before_test_permission",
                "gated_start_selected_with_test_only_claim",
                "internal_reset_started",
                "tk_callback_nonblocking",
                "native_worker_completed",
                "real_1366x768_reset_master_first",
                "competing_real_stack_and_grid_blocked",
                "authorization_revoked_without_join",
                "revoked_worker_exits_cleanly",
                "revoked_worker_late_state_is_discarded",
                "test_shell_shutdown",
                "did_not_create_settings_file",
            )
            assert all(evidence.get(k) is True for k in checks),evidence
            evidence["status"]="PASS_NATIVE_S62_C07_START_WORKER_TEST_OWNED"
    except Exception as exc:
        evidence["status"]="FAIL_NATIVE_S62"
        evidence["error_type"]=type(exc).__name__
        evidence["error_text"]=str(exc)[:260]
    finally:
        release.set()
        if app is not None:
            try:app.shutdown()
            except Exception:pass
        if root is not None:
            try:root.destroy()
            except Exception:pass
        REPORT.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),
                          encoding="utf-8")
        for k,v in evidence.items():
            print("S62_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if evidence["status"]=="PASS_NATIVE_S62_C07_START_WORKER_TEST_OWNED" else 1
if __name__=="__main__":
    raise SystemExit(run())
