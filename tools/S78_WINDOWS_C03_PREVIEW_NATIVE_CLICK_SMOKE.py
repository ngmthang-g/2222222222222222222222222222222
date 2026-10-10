"""S78 genuine native Win32 DWM overlay WndProc left click -> source focus.

TEST-OWNED Python/Tk source HWNDs ONLY; real DWM register and overlay
WndProc receives genuine user32.SendMessageW 513/514/515. Activation uses
real ShowWindow/SetForegroundWindow, but Windows foreground policy may
reject foreground assignment: assert *attempt*, not forced focus success.
No game automation, mouse injection, signed Info or product EXE.
"""
from __future__ import annotations
import json
import os
import sys
import traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"tests")]
OUT=ROOT/"artifacts"/"s78"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"native_c03_click_activation.json"

def run():
    report={"task":"S78","status":"NOT_RUN",
            "source":"TWO_REAL_TEST_OWNED_TK_HWND_NOT_GAME",
            "original_C03_click_messages":[513,514,515],
            "real_game":"NOT_EXECUTED","signed_info":"NOT_CONNECTED",
            "product_exe":"NOT_PRODUCT"}
    root=None
    preview=None
    try:
        if os.name!="nt":raise RuntimeError("WINDOWS_REQUIRED")
        import tkinter as tk
        import ctypes
        from ctypes import wintypes as w
        from dwm_preview import NativeDwmBackend,ReadOnlyDwmPreviews,PreviewPlacement,_DWM_CLICK_TARGETS
        root=tk.Tk()
        root.title("S78 real native DWM click, NOT GAME")
        root.geometry("490x235+90+55")
        sources=[]
        for i in range(2):
            win=tk.Toplevel(root)
            win.title(f"S78 source HWND {i+1} TEST ONLY")
            win.geometry(f"225x170+{30+i*245}+430")
            tk.Label(win,text="TEST SOURCE NO GAME").pack()
            sources.append(win)
        root.update_idletasks()
        root.update()
        events=[]
        class NativeActivationSpy(NativeDwmBackend):
            def __init__(self):
                super().__init__()
                self.destinations=[]
            def create_destination(self,*args):
                dest=super().create_destination(*args)
                self.destinations.append(dest)
                return dest
            def activate_source(self,hwnd):
                # This spy records actual Win32 invocation; the method still
                # makes real ShowWindow/SetForegroundWindow calls.
                events.append(("activate_attempt",int(hwnd)))
                return super().activate_source(hwnd)
        backend=NativeActivationSpy()
        ancestor=backend._ancestor
        owner=int(ancestor(int(root.winfo_id()),2))
        hwnds=tuple(int(ancestor(int(src.winfo_id()),2)) for src in sources)
        pid=os.getpid()
        assert len(set(hwnds))==2
        assert all(backend.source_matches(h,pid) for h in hwnds)
        preview=ReadOnlyDwmPreviews(backend)
        places=tuple(PreviewPlacement(h,pid,owner,25+i*230,40,185,104)
                     for i,h in enumerate(hwnds))
        result=preview.sync(places)
        assert result.rendered==hwnds and not result.errors,result
        dests=tuple(backend.destinations)
        report["real_two_DWM_slots_and_source_PIDs"] = (
            len(dests)==2 and all(backend._is_window(d) for d in dests)
            and all(backend.source_matches(h,pid) for h in hwnds))
        assert report["real_two_DWM_slots_and_source_PIDs"]
        report["native_dst_handles"] = [int(d) for d in dests]
        report["native_source_hwnds"] = [int(h) for h in hwnds]
        report["native_click_mapping_readback"] = {
            str(d): {
                "exists": d in _DWM_CLICK_TARGETS,
                "source": _DWM_CLICK_TARGETS[d][1]
                          if d in _DWM_CLICK_TARGETS else None,
                "pid": _DWM_CLICK_TARGETS[d][2]
                       if d in _DWM_CLICK_TARGETS else None,
            } for d in dests
        }
        report["real_destination_click_mapping_registered"]=all(
            _DWM_CLICK_TARGETS.get(d,())[1:]==(h,pid)
            for d,h in zip(dests,hwnds))
        assert report["real_destination_click_mapping_registered"]
        get_style=backend.user32.GetWindowLongW
        get_style.argtypes=(w.HWND,ctypes.c_int)
        get_style.restype=ctypes.c_long
        report["native_owner_overlay_hit_test_not_WS_EX_TRANSPARENT"]=all(
            not (int(get_style(d,-20)) & backend.WS_EX_TRANSPARENT)
            for d in dests)
        assert report["native_owner_overlay_hit_test_not_WS_EX_TRANSPARENT"]

        send=backend.user32.SendMessageW
        send.argtypes=(w.HWND,w.UINT,w.WPARAM,w.LPARAM)
        send.restype=ctypes.c_ssize_t
        for msg in (513,514,515):
            send(dests[0],msg,0,0)
        send(dests[1],513,0,0)
        report["real_native_WndProc_dispatched_all_left_messages"]=events==[
            ("activate_attempt",hwnds[0])]*3+[("activate_attempt",hwnds[1])]
        assert report["real_native_WndProc_dispatched_all_left_messages"],events

        count=len(events)
        send(dests[0],0x0204,0,0)  # WM_RBUTTONDOWN is NOT C03 activate
        report["right_button_never_activates_source"]=len(events)==count
        assert report["right_button_never_activates_source"]

        sources[1].destroy()
        root.update_idletasks()
        root.update()
        assert not backend._is_window(hwnds[1])
        send(dests[1],513,0,0)  # mapped but stale source
        report["destroyed_source_never_activates_again"]=len(events)==count
        assert report["destroyed_source_never_activates_again"]

        preview.clear()
        report["native_cleanup_removes_all_click_mappings"]=(
            not preview.active_hwnds
            and all(not backend._is_window(d) for d in dests)
            and all(d not in _DWM_CLICK_TARGETS for d in dests))
        assert report["native_cleanup_removes_all_click_mappings"]
        report["status"]="PASS_NATIVE_S78_C03_REAL_WNDPROC_LEFT_CLICK_HWND_PID_GUARDED"
    except Exception as exc:
        report["status"]="FAIL_NATIVE_S78"
        report["error_type"]=type(exc).__name__
        report["error_text"]=str(exc)[:300]
        report["traceback"]=traceback.format_exc(limit=15)
    finally:
        if preview is not None:
            try:preview.shutdown()
            except Exception:pass
        if root is not None:
            try:root.destroy()
            except Exception:pass
        REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),
                          encoding="utf-8")
        for k,v in report.items():
            if k!="traceback":
                print("S78_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if report["status"]==        "PASS_NATIVE_S78_C03_REAL_WNDPROC_LEFT_CLICK_HWND_PID_GUARDED" else 1

if __name__=="__main__":raise SystemExit(run())
