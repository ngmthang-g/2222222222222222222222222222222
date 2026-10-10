"""S83 real Windows: invoking already selected C05 master radio must not abort active native C10/C11 worker.

Two actual TEST-OWNED Python/Tk HWNDs. Full original-backed Start view
and real ttk.Radiobutton.invoke. Native SetWindowPos moves ONLY a test
window when an in-progress worker stays authorized; a real DIFFERENT
master selection while a second worker is running must cancel it.
NO original TLM game or signed license, no source input injection.
"""
from __future__ import annotations
import json,os,sys,tempfile,threading,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s83"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"native_c05_same_master_worker_idempotence.json"

def run():
    report={"task":"S83","status":"NOT_RUN",
        "sources":"TWO_ACTUAL_TEST_OWNED_NATIVE_TK_HWNDS",
        "license":"TEST_ONLY_LOCAL_MAX_WINDOWS_NOT_AUTHENTICATED",
        "game":"NOT_EXECUTED","exe":"NOT_PRODUCT"}
    root=None;start=None
    releases=[threading.Event(),threading.Event()]
    try:
        if os.name!="nt":raise RuntimeError("S83_WINDOWS_REQUIRED")
        import tkinter as tk
        import ctypes
        from start_tab import TLMStartTab
        from start_polling import StartWindowProducer,WindowSnapshot
        from start_windows import NativeWin32Backend,GameWindow
        from layout_windows import NativeLayoutBackend
        from grid_master import GridSettingsStore
        from window_stacking import StackResult

        root=tk.Tk()
        root.title("S83 TEST native Tk selected master radio")
        root.geometry("870x920+10+10")
        sources=[]
        for i in range(2):
            w=tk.Toplevel(root)
            w.title(f"S83 TEST-OWNED source #{i+1}")
            w.geometry(f"220x150+{30+i*255}+430")
            tk.Label(w,text="S83 TEST ONLY NOT GAME").pack()
            sources.append(w)
        root.update_idletasks();root.update()
        backend=NativeLayoutBackend()
        api=ctypes.WinDLL("user32",use_last_error=True)
        anc=api.GetAncestor
        anc.argtypes=[ctypes.c_void_p,ctypes.c_uint]
        anc.restype=ctypes.c_void_p
        hwnds=tuple(int(anc(int(w.winfo_id()),2)) for w in sources)
        pid=os.getpid()
        assert len(set(hwnds))==2
        assert all(backend.is_window(h) and backend.process_id(h)==pid for h in hwnds)
        rows=tuple(GameWindow(h,pid,"S83 NATIVE TEST NOT GAME",
                              "TEST_OWNED","NOT_GAME.exe") for h in hwnds)
        snapshot=WindowSnapshot(83,rows,True)
        entered=[threading.Event(),threading.Event()]
        n=[0]
        native_moves=[]
        class ControlledNativeStack:
            def apply(self,snap,*,mode,max_windows,master_hwnd,allowed):
                idx=n[0]
                n[0]+=1
                assert idx in (0,1),idx
                entered[idx].set()
                releases[idx].wait(4)
                if not allowed():
                    return StackResult("TEST_C05_WORKER_CANCELLED")
                # A real HWND SetWindowPos attempt, ONLY on a TEST-OWNED Tk
                # window. If the first radio click wrongly invalidated the
                # generation this movement would not happen.
                native_moves.append((idx,backend.move_no_resize(
                    hwnds[1],87+idx*50,67+idx*30)))
                return StackResult("TEST_C05_WORKER_COMPLETED")

        with tempfile.TemporaryDirectory(prefix="S83_NATIVE_") as td:
            start=TLMStartTab(root,producer=StartWindowProducer(NativeWin32Backend),
                stack_service_factory=ControlledNativeStack,
                grid_settings_store=GridSettingsStore(Path(td)/"settings.ini"))
            root.update()
            start.set_layout_max_windows(2)
            start._start_refresh()
            root.update()
            start.poller.producer.read_snapshot=lambda:snapshot
            start._sync_tiles(rows)
            root.update()
            radios=tuple(start._master_radio_buttons)
            assert len(radios)==2
            assert start.master_selection.selected==(hwnds[0],pid)
            before=backend.window_rect(hwnds[1])
            assert start._dispatch_auto_stack("tight")
            assert entered[0].wait(3), "WORKER_FIRST_NOT_STARTED"
            first_worker=start._stack_thread
            first_allowed=start._stack_allow
            first_generation=start._stack_generation
            radios[0].invoke() # REAL CURRENTLY SELECTED ttk.Radiobutton
            root.update()
            report["real_same_radio_invoke_retains_native_event_and_generation"]=(
                first_allowed.is_set()
                and start._stack_generation==first_generation
                and start.master_selection.selected==(hwnds[0],pid))
            assert report["real_same_radio_invoke_retains_native_event_and_generation"]
            releases[0].set()
            deadline=time.monotonic()+4
            while first_worker.is_alive() and time.monotonic()<deadline:
                root.update()
                time.sleep(.01)
            assert not first_worker.is_alive(),"WORKER_ONE_NOT_JOINED"
            first_worker.join(timeout=0)
            moved=backend.window_rect(hwnds[1])
            report["same_master_click_preserves_real_native_test_HWND_move"]=(
                moved[:2]==(87,67)
                and (before[2]-before[0],before[3]-before[1])
                 ==(moved[2]-moved[0],moved[3]-moved[1])
                and native_moves==[(0,True)]
                and getattr(start._stack_last_result,"code",None)
                   =="TEST_C05_WORKER_COMPLETED")
            assert report["same_master_click_preserves_real_native_test_HWND_move"]
            # Real CHANGED master radio must still CANCEL second operation.
            assert start._dispatch_auto_stack("diagonal")
            assert entered[1].wait(3),"WORKER_TWO_NOT_STARTED"
            second_worker=start._stack_thread
            second_allowed=start._stack_allow
            second_generation=start._stack_generation
            radios[1].invoke()
            root.update()
            report["different_master_real_radio_cancels_native_worker"]=(
                not second_allowed.is_set()
                and start._stack_generation>second_generation
                and start.master_selection.selected==(hwnds[1],pid))
            assert report["different_master_real_radio_cancels_native_worker"]
            releases[1].set()
            deadline=time.monotonic()+4
            while second_worker.is_alive() and time.monotonic()<deadline:
                root.update()
                time.sleep(.01)
            assert not second_worker.is_alive(),"WORKER_TWO_NOT_JOINED"
            second_worker.join(timeout=0)
            report["new_master_prevents_stale_second_real_SetWindowPos"]=(
                backend.window_rect(hwnds[1])==moved
                and native_moves==[(0,True)]
                and start._stack_last_result is None)
            assert report["new_master_prevents_stale_second_real_SetWindowPos"]
            start.shutdown();start=None
            root.destroy();root=None
            report["normal_native_Tk_owner_shutdown"]=True
        report["status"]="PASS_NATIVE_S83_C05_IDENTICAL_RADIO_KEEPS_NATIVE_STACK"
    except Exception as exc:
        report["status"]="FAIL_NATIVE_S83"
        report["error_type"]=type(exc).__name__
        report["error_text"]=str(exc)[:320]
        report["traceback"]=traceback.format_exc(limit=15)
    finally:
        for e in releases:e.set()
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
                print("S83_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if report["status"]=="PASS_NATIVE_S83_C05_IDENTICAL_RADIO_KEEPS_NATIVE_STACK" else 1
if __name__=="__main__":
    raise SystemExit(run())
