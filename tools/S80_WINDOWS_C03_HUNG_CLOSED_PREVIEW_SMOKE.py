"""S80 real Win32 C03 per-tile HUNG vs CLOSED messages (TEST WINDOWS ONLY).

Actual native Tk widgets and 2 DWM thumbnails on two TEST-OWNED Python
source HWNDs. Native IsWindow/GetWindowThreadProcessId are real, and a
test-only IsHungAppWindow adapter simulates HUNG for one valid source.
A destroyed native HWND must show CLOSED instead. No real game or license.
"""
from __future__ import annotations
import json
import os
import sys
import traceback
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s80"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"native_c03_hung_closed_preview.json"

def run():
    result={
       "task":"S80","status":"NOT_RUN",
       "source_windows":"TWO_REAL_TEST_OWNED_TK_HWND_NOT_GAME",
       "native_state":"REAL_WIN32_ISWINDOW_AND_PID",
       "hung_state":"EXPLICIT_TEST_ONLY_ISHUNGAPPWINDOW_ADAPTER",
       "actual_game":"NOT_EXECUTED","signed_info":"NOT_CONNECTED",
       "product_exe":"NOT_PRODUCT",
    }
    root=None
    start=None
    try:
        if os.name!="nt":raise RuntimeError("S80_WINDOWS_REQUIRED")
        import tkinter as tk
        from dwm_preview import NativeDwmBackend,THUMB_WIDTH,THUMB_HEIGHT
        from start_polling import WindowSnapshot
        from start_tab import TLMStartTab
        from start_windows import GameWindow
        root=tk.Tk()
        root.title("S80 native C03 per-tile status NOT GAME")
        root.geometry("535x335+170+40")
        sources=[]
        for idx in range(2):
            w=tk.Toplevel(root)
            w.title(f"S80 TEST source {idx+1} NOT GAME")
            w.geometry(f"210x146+{40+idx*230}+460")
            tk.Label(w,text="TEST ONLY NO GAME").pack()
            sources.append(w)
        root.update_idletasks()
        root.update()
        backend=NativeDwmBackend()
        native_hwnds=tuple(int(backend._ancestor(int(w.winfo_id()),2))
                           for w in sources)
        pid=os.getpid()
        assert len(set(native_hwnds))==2
        assert all(backend.source_matches(h,pid) for h in native_hwnds)
        rows=tuple(GameWindow(h,pid,f"S80 TEST {i+1} NOT GAME",
                               "TEST_OWNED","NOT_GAME.exe")
                   for i,h in enumerate(native_hwnds))
        # The actual existing Start _refresh_dwm method owns real DWM
        # controller/overlay creation; minimal owner fixture avoids any
        # pretend authenticated production Start tab.
        start=object.__new__(TLMStartTab)
        start._closed=False
        start._preview_cleanup_faulted=False
        start._preview_after=None
        start._preview_controller=None
        start._preview_backend_factory=lambda:backend
        start.poller=SimpleNamespace(active=True)
        start.container=tk.Frame(root)
        start.container.pack(fill="both",expand=True)
        start.preview_status=tk.Label(start.container,text="")
        start.preview_status.pack(fill="x")
        tiles={}
        for index,row in enumerate(rows):
            tile=tk.Frame(start.container,width=210,height=152,relief="solid",borderwidth=1)
            tile.pack(side="left",padx=9,pady=10)
            tile.pack_propagate(False)
            label=tk.Label(tile,text=row.title)
            label.place(x=3,y=2,width=195,height=19)
            surface=tk.Frame(tile,bg="#000000",width=THUMB_WIDTH,height=THUMB_HEIGHT)
            surface.place(x=4,y=25,width=THUMB_WIDTH,height=THUMB_HEIGHT)
            error=tk.Label(surface,text="",bg="#000000",fg="#ff5555",
                           wraplength=THUMB_WIDTH-8)
            tiles[(row.hwnd,row.pid)]=(tile,label,surface,None,None,error)
        start._tile_items=tiles
        start._active_windows=rows
        root.update_idletasks()
        root.update()

        start._refresh_dwm()
        assert start._preview_controller is not None
        result["two_real_native_DWM_slots"]=(
            start._preview_controller.active_hwnds==native_hwnds
            and all(not t[5].winfo_manager() for t in tiles.values()))
        assert result["two_real_native_DWM_slots"]
        result["native_correct_LIVE_status"]=all(
            backend.source_status(h,pid)=="LIVE" for h in native_hwnds)
        assert result["native_correct_LIVE_status"]

        # Test-only Win32 hung adapter, not a hang heuristic or actual
        # intentionally deadlocked game/OS thread.
        native_hung=backend._hung
        backend._hung=lambda h: h==native_hwnds[1] or native_hung(h)
        assert backend.source_status(native_hwnds[1],pid)=="HUNG"
        start._refresh_dwm()
        error=tiles[(native_hwnds[1],pid)][5]
        result["actual_Tk_red_hung_exact_original_text"]=(
            error.winfo_manager()=="place"
            and error.cget("text")=="Cửa sổ không phản hồi"
            and error.cget("fg")=="#ff5555"
            and not tiles[(native_hwnds[0],pid)][5].winfo_manager())
        assert result["actual_Tk_red_hung_exact_original_text"]
        result["real_native_hung_slot_DWM_unregistered"]=(
            start._preview_controller.active_hwnds==(native_hwnds[0],))
        assert result["real_native_hung_slot_DWM_unregistered"]

        backend._hung=native_hung
        start._refresh_dwm()
        result["real_hung_to_live_recovery_hides_error"]=(
            start._preview_controller.active_hwnds==native_hwnds
            and not error.winfo_manager()
            and backend.source_status(native_hwnds[1],pid)=="LIVE")
        assert result["real_hung_to_live_recovery_hides_error"]

        sources[1].destroy()
        root.update_idletasks()
        root.update()
        result["native_destroyed_is_CLOSED_not_HUNG"]=(
            backend.source_status(native_hwnds[1],pid)=="CLOSED"
            and not backend._is_window(native_hwnds[1]))
        assert result["native_destroyed_is_CLOSED_not_HUNG"]
        start._refresh_dwm()
        result["actual_Tk_red_closed_prefix_not_hung"]=(
            error.winfo_manager()=="place"
            and error.cget("text").startswith("Đã đóng cửa sổ: ")
            and "không phản hồi" not in error.cget("text")
            and error.cget("fg")=="#ff5555")
        assert result["actual_Tk_red_closed_prefix_not_hung"]
        result["native_destroyed_slot_DWM_unregistered"]=(
            start._preview_controller.active_hwnds==(native_hwnds[0],))
        assert result["native_destroyed_slot_DWM_unregistered"]
        result["no_original_game_or_new_game_inputs"]=True
        result["status"]="PASS_NATIVE_S80_REAL_C03_HUNG_CLOSED_PER_ITEM"
    except Exception as exc:
        result["status"]="FAIL_NATIVE_S80"
        result["error_type"]=type(exc).__name__
        result["error_text"]=str(exc)[:350]
        result["traceback"]=traceback.format_exc(limit=17)
    finally:
        if start is not None and start._preview_controller is not None:
            try:start._preview_controller.shutdown()
            except Exception:pass
        if root is not None:
            try:root.destroy()
            except Exception:pass
        REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
        for key,val in result.items():
            if key!="traceback":
                print("S80_"+key.upper()+"="+json.dumps(val,ensure_ascii=True))
    return 0 if result["status"]=="PASS_NATIVE_S80_REAL_C03_HUNG_CLOSED_PER_ITEM" else 1

if __name__=="__main__":
    raise SystemExit(run())
