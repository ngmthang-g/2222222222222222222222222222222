"""S77 real Windows Win32+DWM test-owned HWNDs: E08 release after error.

Two explicit scenarios (leaving Start; app shutdown) with native DWM
register/unregister/destroy, test-owned Python/Tk HWND sources and REAL
Tk frames. One native unregister throws AFTER the actual Windows call.
No TLM/game executable, signed server payload, or product runtime.
"""
from __future__ import annotations
import json
import os
import sys
import traceback
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"), str(ROOT/"tests")]
OUT=ROOT/"artifacts"/"s77"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"native_e08_stop_shutdown_cleanup.json"


def run():
    report={"task":"S77","status":"NOT_RUN",
            "native_sources":"TWO_REAL_TEST_OWNED_TK_HWNDS_NOT_GAME",
            "fault":"TEST_ONLY_AFTER_REAL_NATIVE_DWM_UNREGISTER",
            "original_game":"NOT_EXECUTED","signed_info":"NOT_CONNECTED",
            "full_product_exe":"NOT_PRODUCT"}
    root=None
    try:
        if os.name!="nt":
            raise RuntimeError("WINDOWS_REQUIRED")
        import tkinter as tk
        from dwm_preview import NativeDwmBackend,ReadOnlyDwmPreviews,PreviewPlacement
        from start_windows import GameWindow
        from test_s15 import prepared
        from start_tab import StartReadOnlyState

        root=tk.Tk()
        root.title("S77 owner root NO GAME")
        root.geometry("460x230+130+55")
        sources=[]
        for i in range(2):
            w=tk.Toplevel(root)
            w.title("S77 native owned source %d NO GAME"%(i+1))
            w.geometry(f"210x160+{15+i*230}+425")
            tk.Label(w,text="TEST ONLY NO GAME").pack()
            sources.append(w)
        root.update_idletasks()
        root.update()
        import ctypes
        from ctypes import wintypes as w
        user32=ctypes.WinDLL("user32",use_last_error=True)
        ancestor=user32.GetAncestor
        ancestor.argtypes=(w.HWND,w.UINT)
        ancestor.restype=w.HWND
        hwnds=tuple(int(ancestor(int(s.winfo_id()),2)) for s in sources)
        owner=int(ancestor(int(root.winfo_id()),2))
        pid=os.getpid()
        assert len(set(hwnds))==2

        for mode in ("stop","shutdown"):
            events=[]
            class InjectedRealDwm(NativeDwmBackend):
                def __init__(self):
                    super().__init__()
                    self.native_unregs=0
                    self.destinations=[]
                def create_destination(self,*args):
                    h=super().create_destination(*args)
                    self.destinations.append(h)
                    events.append(("destination_new",h))
                    return h
                def unregister(self,t):
                    super().unregister(t)
                    self.native_unregs+=1
                    events.append(("native_unregister",int(t)))
                    if self.native_unregs==1:
                        raise OSError("S77_POST_NATIVE_SUCCESS_FAULT")
                def destroy_destination(self,h):
                    events.append(("destroy_destination",int(h)))
                    return super().destroy_destination(h)
            backend=InjectedRealDwm()
            assert all(backend.source_matches(h,pid) for h in hwnds)
            rows=tuple(GameWindow(h,pid,"S77 TEST NOT GAME",
                                  "TEST_TK_ONLY","NOT_GAME.exe") for h in hwnds)
            preview=ReadOnlyDwmPreviews(backend)
            placements=tuple(PreviewPlacement(h,pid,owner,
                               28+i*225,50,184,105)
                             for i,h in enumerate(hwnds))
            rendered=preview.sync(placements)
            assert rendered.rendered==hwnds and not rendered.errors
            assert all(backend._is_window(h) for h in backend.destinations)
            obj=prepared(rows)
            obj._preview_controller=preview
            class Frame(tk.Frame):
                def destroy(self):
                    events.append(("tk_tile_destroy",int(self.winfo_id())))
                    return super().destroy()
            frames=tuple(Frame(root) for _ in hwnds)
            obj._tile_items={(h,pid):(frame,None,None)
                             for h,frame in zip(hwnds,frames)}
            obj._cancel_auto_reset_worker=lambda:events.append(("cancel_auto",0))
            obj._cancel_stack_worker=lambda:events.append(("cancel_stack",0))
            obj._stop_sync_loop=lambda:events.append(("stop_sync",0))
            class Maintenance:
                def stop(self):events.append(("maintenance_stop",0))
                def shutdown(self):events.append(("maintenance_shutdown",0))
            obj.maintenance=Maintenance()
            obj.poller._stop_refresh=lambda:events.append(("poller_stop",0))
            obj.poller.shutdown=lambda:events.append(("poller_shutdown",0))
            class Host:
                def unbind(self,sequence,binding):
                    events.append(("unbind",sequence))
            obj._top=Host()
            obj._top_handlers=[("<Map>","map"),("<Unmap>","unmap")]
            def destroy_tiles(empty):
                assert empty == ()
                for frame in frames:
                    if frame.winfo_exists():
                        frame.destroy()
                obj._tile_items.clear()
                obj._active_windows=()
                obj._observed_windows=()
            obj._sync_tiles=destroy_tiles
            obj._render=lambda state:setattr(obj,"_state",state)

            if mode=="stop":
                obj._stop_refresh()
                assert obj._state.code=="STOPPED"
                assert obj._preview_cleanup_faulted
                assert "DWM" in obj.preview_status.value
                assert ("poller_stop",0) in events
                assert all(not f.winfo_exists() for f in frames)
            else:
                try:
                    obj.shutdown()
                    raise AssertionError("shutdown must report native failure")
                except OSError as exc:
                    assert "S77_POST_NATIVE_SUCCESS_FAULT" in str(exc)
                assert obj._closed and obj._preview_cleanup_faulted
                assert ("poller_shutdown",0) in events
                assert ("maintenance_shutdown",0) in events
                assert ("unbind","<Map>") in events
                assert ("unbind","<Unmap>") in events
                assert obj._top_handlers==[]
                assert all(f.winfo_exists() for f in frames)
                # Actual Tk root's Destroy event owns descendant widget cleanup.
                for frame in frames:
                    frame.destroy()

            report[mode+"_two_native_DWM_registers"]=len(backend.destinations)==2
            report[mode+"_native_unregs_all_attempted"]=backend.native_unregs==2
            report[mode+"_native_destinations_removed"]=all(
                not backend._is_window(h) for h in backend.destinations)
            report[mode+"_DWM_teardown_before_Tk_frame_destroy"]=(
                len([e for e in events if e[0]=="tk_tile_destroy"])==2
                and max(i for i,e in enumerate(events)
                        if e[0] in ("native_unregister","destroy_destination"))
                  < min(i for i,e in enumerate(events)
                        if e[0]=="tk_tile_destroy"))
            assert all(report[mode+"_"+k] for k in (
                "two_native_DWM_registers","native_unregs_all_attempted",
                "native_destinations_removed","DWM_teardown_before_Tk_frame_destroy"))
            preview.shutdown()
        report["status"]="PASS_NATIVE_S77_E08_ALL_OWNERS_AFTER_DWM_FAULT_TEST_ONLY"
    except Exception as exc:
        report["status"]="FAIL_NATIVE_S77"
        report["error_type"]=type(exc).__name__
        report["error_text"]=str(exc)[:300]
        report["traceback"]=traceback.format_exc(limit=14)
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),
                          encoding="utf-8")
        for k,v in report.items():
            if k!="traceback":
                print("S77_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if report["status"]=="PASS_NATIVE_S77_E08_ALL_OWNERS_AFTER_DWM_FAULT_TEST_ONLY" else 1

if __name__=="__main__":
    raise SystemExit(run())
