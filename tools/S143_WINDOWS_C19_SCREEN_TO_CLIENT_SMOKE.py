"""S143 — Native Win64 real C19 screen point + 3 separate TEST-OWNED Tk HWNDs.

Use real user32.WindowFromPoint, GetAncestor, ScreenToClient, GetClientRect,
ClientToScreen on actual Win64 HWND/PIDs. NO native mouse, key, game input.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s143"
OUT.mkdir(parents=True,exist_ok=True)

def main():
    if os.name!="nt" or sys.maxsize<=2**32:
        raise SystemExit("S143_REAL_WIN64_REQUIRED")
    import ctypes
    from ctypes import wintypes
    import tkinter as tk
    from input_sync_core import NativeClientRectReader,InputSyncModel,scale_client_point
    from input_sync_screen_coords import (
        NativeC19MasterPointReader,queue_verified_screen_mouse)
    from start_polling import WindowSnapshot
    from start_windows import GameWindow,GAME_PROCESS,GAME_TITLE,UNITY_WINDOW_CLASS
    checks={}
    root=None
    try:
        root=tk.Tk()
        root.title("S143 root NOT GAME")
        root.geometry("120x80+8+8")
        sources=[]
        for i,x in enumerate((50,360,670)):
            w=tk.Toplevel(root)
            w.geometry(f"200x155+{x}+160")
            w.title(f"S143 SELF OWNED #{i} NOT GAME")
            tk.Label(w,text=f"TEST WIN32 SOURCE {i}").pack(fill="both",expand=True)
            sources.append(w)
        other=tk.Toplevel(root)
        other.geometry("130x100+300+480")
        other.title("UNRELATED TEST HWND")
        root.update()
        u=ctypes.WinDLL("user32",use_last_error=True)
        ancestor=u.GetAncestor
        ancestor.argtypes=[wintypes.HWND,wintypes.UINT]
        ancestor.restype=wintypes.HWND
        to_screen=u.ClientToScreen
        to_screen.argtypes=[wintypes.HWND,ctypes.POINTER(wintypes.POINT)]
        to_screen.restype=wintypes.BOOL
        hwnds=tuple(int(ancestor(w.winfo_id(),2) or 0) for w in sources)
        other_hwnd=int(ancestor(other.winfo_id(),2) or 0)
        pid=os.getpid()
        checks["three_distinct_actual_Win64_HWNDs"]=(
            len(set(hwnds))==3 and min(hwnds)>0 and other_hwnd not in hwnds)
        sizes=NativeClientRectReader()
        dimensions={h:sizes.size(h,pid) for h in hwnds}
        checks["actual_user32_GetClientRect_sizes"]=all(
            sz.width>100 and sz.height>90 for sz in dimensions.values())
        client=wintypes.POINT(55,45)
        checks["actual_user32_ClientToScreen"]=bool(
            to_screen(hwnds[1],ctypes.byref(client)))
        sx,sy=client.x,client.y
        reader=NativeC19MasterPointReader()
        cap=reader.capture(hwnds[1],pid,sx,sy)
        checks["actual_user32_WindowFromPoint_and_ScreenToClient"]=(
            (cap.hwnd,cap.pid,cap.x,cap.y)==(hwnds[1],pid,55,45)
            and (cap.width,cap.height)==
                (dimensions[hwnds[1]].width,dimensions[hwnds[1]].height))
        wrong=wintypes.POINT(30,30)
        assert to_screen(other_hwnd,ctypes.byref(wrong))
        try:
            reader.capture(hwnds[1],pid,wrong.x,wrong.y)
            checks["foreign_window_point_blocked"]=False
        except ValueError:
            checks["foreign_window_point_blocked"]=True
        try:
            reader.capture(hwnds[1],pid+123456,sx,sy)
            checks["stale_master_pid_blocked"]=False
        except ValueError:
            checks["stale_master_pid_blocked"]=True
        # Synthetic game identity exists only inside this TEST-OWNED cache.
        rows=tuple(GameWindow(h,pid,GAME_TITLE,UNITY_WINDOW_CLASS,GAME_PROCESS)
                   for h in hwnds)
        model=InputSyncModel()
        checks["two_slave_model_started_test_only"]=model.start(
            WindowSnapshot(1,rows,True),(hwnds[1],pid),max_windows=3)
        trusted=set(hwnds)
        identity=lambda h,p: h in trusted and p==pid and u.IsWindow(h)!=0
        check_permitted=lambda:True  # ONLY THIS TEST PROCESS, NOT PRODUCT
        count=queue_verified_screen_mouse(
            model,sx,sy,button="left",pressed=True,now=10.0,
            allowed=check_permitted,live_identity=identity,
            point_reader=reader,size_reader=sizes)
        checks["actual_two_slave_native_geometry_queued_only"]=(
            count==2 and model.pending==2)
        queued=[]
        while model.pending:
            event=model.dispatch_one(
                sink=queued.append,identity_ok=identity,
                permission_ok=check_permitted)
            assert event is not None
        expected=[scale_client_point(55,45,dimensions[hwnds[1]],dimensions[h])
                  for h in (hwnds[0],hwnds[2])]
        checks["two_actual_slave_client_rect_ratios"]=(
            [e.target for e in queued]==[(hwnds[0],pid),(hwnds[2],pid)]
            and [(e.x,e.y) for e in queued]==expected)
        model.stop("REVOKED")
        checks["no_queued_input_after_revoke"]=(
            queue_verified_screen_mouse(model,sx,sy,button="left",pressed=True,
             now=12.0,allowed=check_permitted,live_identity=identity,
             point_reader=reader,size_reader=sizes)==0 and model.pending==0)
        sources[1].destroy()
        root.update()
        try:
            reader.capture(hwnds[1],pid,sx,sy)
            checks["destroyed_master_hwnd_blocked"]=False
        except ValueError:
            checks["destroyed_master_hwnd_blocked"]=True
        for w in sources:
            if w.winfo_exists():w.destroy()
        other.destroy()
        root.destroy()
        root=None
        result={"status":"PASS_S143_WIN64_REAL_C19_SCREEN_CLIENT_2_SLAVE_NO_SEND"
                 if all(checks.values()) else "FAIL_S143_C19_NATIVE_GEOMETRY",
                "test_owned_native_windows":3,"original_game_executed":False,
                "actual_win32_input_sent":False,"auth_signed_info":False,
                "original_payload_verified":False,"checks":checks}
    except Exception as exc:
        result={"status":"FAIL_S143_C19_NATIVE_GEOMETRY",
                "error_type":type(exc).__name__,"checks":checks,
                "original_game_executed":False,
                "actual_win32_input_sent":False}
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
    (OUT/"native_c19_point.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(result,ensure_ascii=False))
    return 0 if result["status"].startswith("PASS_S143_") else 1

if __name__=="__main__":
    raise SystemExit(main())
