"""S81 native C05 auto master loss cancels pending C10/C11 worker.
Two real TEST-OWNED Win32/Tk source HWNDs, actual Windows position
readback and a blocked genuine Tk Start worker. The stack service is
TEST ONLY and would execute a real Win32 SetWindowPos if not cancelled.
NO actual TLM game/license, background input, Proxy or product EXE.
"""
from __future__ import annotations
import json
import os
import sys
import tempfile
import threading
import time
import traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s81"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"native_c05_master_loss_stack_cancel.json"

def run():
    report={"task":"S81","status":"NOT_RUN",
            "windows":"TWO_NATIVE_TEST_OWNED_TK_HWNDS_NOT_GAME",
            "entitlement":"TEST_ONLY_EXTERNAL_LIMIT",
            "game":"NOT_EXECUTED","product_exe":"NOT_PRODUCT"}
    root=None;start=None;release=threading.Event()
    try:
        if os.name!="nt":raise RuntimeError("WINDOWS_REQUIRED")
        import tkinter as tk
        from start_tab import TLMStartTab
        from start_polling import StartWindowProducer,WindowSnapshot
        from start_windows import NativeWin32Backend,GameWindow
        from grid_master import GridSettingsStore
        from layout_windows import NativeLayoutBackend
        from window_stacking import StackResult
        root=tk.Tk()
        root.title("S81 TEST only C05 master lifecycle")
        root.geometry("850x920+45+30")
        sources=[]
        for i in range(2):
            w=tk.Toplevel(root)
            w.title(f"S81 TEST SOURCE #{i} NOT GAME")
            w.geometry(f"220x165+{90+260*i}+420")
            tk.Label(w,text="TEST OWNED NO GAME").pack()
            sources.append(w)
        root.update()
        backend=NativeLayoutBackend()
        import ctypes
        u32=ctypes.WinDLL("user32",use_last_error=True)
        anc=u32.GetAncestor
        anc.argtypes=[ctypes.c_void_p,ctypes.c_uint]
        anc.restype=ctypes.c_void_p
        hwnds=tuple(int(anc(int(w.winfo_id()),2)) for w in sources)
        pid=os.getpid()
        assert len(set(hwnds))==2
        assert all(backend.is_window(h) and backend.process_id(h)==pid for h in hwnds)
        rows=tuple(GameWindow(h,pid,"S81 TEST NOT GAME",
                               "TEST_ONLY","NOT_GAME.exe") for h in hwnds)
        snap=WindowSnapshot(81,rows,True)
        before=backend.window_rect(hwnds[1])
        entered=threading.Event()
        did_move=[]
        class WaitAndMaybeMove:
            def apply(self,snapshot,*,mode,max_windows,master_hwnd,allowed):
                entered.set()
                release.wait(3.0)
                if allowed():
                    # THIS WOULD PERFORM REAL USER32 SETWINDOWPOS ON A TEST-
                    # OWNED SOURCE IF THE OLD STACK GENERATION REMAINED LIVE.
                    did_move.append(backend.move_no_resize(hwnds[1],40,30))
                    return StackResult("TEST_OLD_WORKER_MOVED")
                return StackResult("STACK_CANCELLED_S81_MASTER_CHANGED")

        with tempfile.TemporaryDirectory(prefix="S81_NATIVE_") as td:
            start=TLMStartTab(root,producer=StartWindowProducer(NativeWin32Backend),
                stack_service_factory=WaitAndMaybeMove,
                grid_settings_store=GridSettingsStore(Path(td)/"settings.ini"))
            root.update()
            start._start_refresh()
            root.update()
            start.poller.producer.read_snapshot=lambda:snap
            start.set_layout_max_windows(2)  # explicitly TEST-ONLY authorized
            start._update_master_combobox(rows)
            report["start_selected_master_first_true_HWND"]=(
                start.master_selection.selected==(hwnds[0],pid))
            assert report["start_selected_master_first_true_HWND"]
            assert start._dispatch_auto_stack("diagonal")
            assert entered.wait(2.0), "TEST_STACK_NOT_STARTED"
            worker=start._stack_thread
            old_event=start._stack_allow
            old_generation=start._stack_generation
            # Actual native HWND is destroyed while native stack is paused.
            sources[0].destroy()
            root.update()
            assert not backend.is_window(hwnds[0])
            assert backend.is_window(hwnds[1])
            start._update_master_combobox((rows[1],))
            report["new_master_is_live_second_HWND"]=(
                start.master_selection.selected==(hwnds[1],pid)
                and start.layout_master_hwnd==hwnds[1])
            report["old_C10_C11_generation_cancelled"]=(
                not old_event.is_set() and start._stack_generation>old_generation)
            assert report["new_master_is_live_second_HWND"]
            assert report["old_C10_C11_generation_cancelled"]
            release.set()
            deadline=time.monotonic()+4.0
            while worker.is_alive() and time.monotonic()<deadline:
                root.update()
                time.sleep(.01)
            assert not worker.is_alive(), "OLD_WORKER_STILL_RUNNING"
            worker.join(timeout=0)
            after=backend.window_rect(hwnds[1])
            report["real_native_remaining_HWND_not_moved_by_stale_worker"]=(
                before==after and not did_move)
            report["cancelled_worker_does_not_publish_success"]=(
                start._stack_last_result is None)
            assert report["real_native_remaining_HWND_not_moved_by_stale_worker"]
            assert report["cancelled_worker_does_not_publish_success"]
            start.shutdown();start=None
            root.destroy();root=None
            report["owner_clean_exit"]=True
        report["status"]="PASS_NATIVE_S81_C05_MASTER_LOSS_CANCELS_C10_C11"
    except Exception as exc:
        report["status"]="FAIL_NATIVE_S81"
        report["error_type"]=type(exc).__name__
        report["error_text"]=str(exc)[:300]
        report["traceback"]=traceback.format_exc(limit=18)
    finally:
        release.set()
        if start is not None:
            try:start.shutdown()
            except Exception:pass
        if root is not None:
            try:root.destroy()
            except Exception:pass
        REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),
                          encoding="utf-8")
        for k,v in report.items():
            if k!="traceback":
                print("S81_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if report["status"]=="PASS_NATIVE_S81_C05_MASTER_LOSS_CANCELS_C10_C11" else 1
if __name__=="__main__":
    raise SystemExit(run())
