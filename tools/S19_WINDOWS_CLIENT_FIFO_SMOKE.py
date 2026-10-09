"""S19 native Windows: genuine GetClientRect, FIFO and TEST-OWNED Tk sink.

Never PostMessageW a game, never install input hooks, never lock actual
keyboard/mouse. The only synthetic Tk events are sent to Toplevel windows
created by this test itself. Actual source/slave client geometry comes from
Win32 GetClientRect and current HWND/PID, not inferred screenshot sizes.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import traceback

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s19"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"native_client_geometry_fifo.json"


def run():
    report={
        "task":"S19","status":"NOT_RUN",
        "windows":"THREE_REAL_TEST_OWNED_WIN32_TK_TOPLEVEL_HWND_NOT_GAME",
        "real_thanh_long_game":"NOT_RUN","actual_native_input_post":"NOT_IMPLEMENTED",
        "input_hooks":"NOT_IMPLEMENTED","dll_slave_lock":"NOT_IMPLEMENTED",
        "keyboard_payload":"UNKNOWN_NOT_INVENTED","product_exe":"NOT_BUILT",
        "test_only_tk_events":True,"proxy":"NOT_DEVELOPED"
    }
    root=None
    sources=[]
    unrelated=None
    try:
        if os.name!="nt":
            raise OSError("S19 native test requires Windows")
        import tkinter as tk
        from dwm_preview import NativeDwmBackend
        from input_sync_core import (
            InputSyncModel,NativeClientRectReader,scale_client_point)
        from permission_guard import PermissionGuard,VerifiedClaims
        from start_windows import (
            GameWindow,GAME_PROCESS,GAME_TITLE,UNITY_WINDOW_CLASS,
            NativeWin32Backend)
        from start_polling import WindowSnapshot

        root=tk.Tk()
        root.title("S19 native safe input-model ONLY - NOT GAME")
        root.geometry("320x130+20+20")
        sizes_in_tk=((280,190),(410,260),(360,310))
        for i,(w,h) in enumerate(sizes_in_tk):
            top=tk.Toplevel(root)
            top.title(f"S19 REAL HWND {i}: TEST CREATED ONLY")
            top.geometry(f"{w}x{h}+{50+i*355}+{200+(i%2)*210}")
            tk.Label(top,text=f"S19 test owned {i}").pack()
            sources.append(top)
        unrelated=tk.Toplevel(root)
        unrelated.title("S19 unrelated - never receive synthetic event")
        unrelated.geometry("180x130+1350+350")
        root.update()

        win=NativeWin32Backend()
        ancestor=NativeDwmBackend()
        handles=tuple(int(ancestor._ancestor(int(t.winfo_id()),2)) for t in sources)
        foreign=int(ancestor._ancestor(int(unrelated.winfo_id()),2))
        pid=os.getpid()
        assert len(set(handles))==3 and foreign not in handles
        assert all(win.is_window(h) and win.process_id(h)==pid for h in handles)
        rows=tuple(GameWindow(h,pid,GAME_TITLE,UNITY_WINDOW_CLASS,GAME_PROCESS)
                   for h in handles)
        identities=tuple((h,pid) for h in handles)
        read=NativeClientRectReader()
        metrics={ident:read.size(*ident) for ident in identities}
        assert all(dim.width > 100 and dim.height > 100 for dim in metrics.values())
        assert len({(dim.width,dim.height) for dim in metrics.values()})==3
        report["owned_hwnds"]=handles
        report["unrelated_hwnd"]=foreign
        report["actual_native_client_sizes"]={
            str(h):[metrics[h,pid].width,metrics[h,pid].height] for h in handles}
        report["all_client_sizes_distinct"]=True

        guard=PermissionGuard()
        assert guard.receive_token("S19_TEST_ONLY_VERIFIER",lambda _:
            VerifiedClaims(permissions=frozenset({"info_tab","start_tab"}),
                           plan_status="TEST_ONLY",max_windows=3))
        def authorized():
            snap=guard.snapshot
            return (snap.has_verified_payload and not snap.blocked
                    and "start_tab" in snap.authorized_keys
                    and snap.max_windows >= 3)

        pipeline=InputSyncModel()
        assert authorized()
        assert pipeline.start(WindowSnapshot(7,rows,True),identities[0],
                              max_windows=guard.snapshot.max_windows)
        received=[]
        foreign_received=[]
        unrelated.bind("<ButtonPress-1>",
                       lambda e:foreign_received.append(("down",e.x,e.y)),add="+")
        unrelated.bind("<ButtonRelease-1>",
                       lambda e:foreign_received.append(("up",e.x,e.y)),add="+")

        for i in (1,2):
            top=sources[i]
            top.bind("<ButtonPress-1>",
                lambda e,index=i:received.append((index,"down",e.x,e.y)),add="+")
            top.bind("<ButtonRelease-1>",
                lambda e,index=i:received.append((index,"up",e.x,e.y)),add="+")
        destination={handles[1]:sources[1],handles[2]:sources[2]}
        native_sends=[]
        # ONLY TEST-OWNED Tk events: no actual mouse/keyboard system injection.
        def test_only_sink(event):
            assert event.target[0] in destination, (
                "S19_BLOCKED_NON_TEST_HWND",event.target)
            assert event.target[1]==pid
            assert event.source==identities[0]
            kind=("<ButtonPress-1>" if event.action=="down"
                  else "<ButtonRelease-1>")
            destination[event.target[0]].event_generate(
                kind,x=event.x,y=event.y,when="tail")
            native_sends.append((event.target[0],event.action,event.x,event.y))
            root.update()

        def live_ok(h,p):
            return (h in handles and p==pid
                    and win.is_window(h) and win.process_id(h)==pid)

        master_size=metrics[identities[0]]
        x,y=master_size.width//3,master_size.height//4
        assert pipeline.queue_mouse(x,y,button="left",pressed=True,
                                    sizes=metrics,now=100.0)==2
        assert pipeline.queue_mouse(x,y,button="left",pressed=False,
                                    sizes=metrics,now=101.0)==2
        report["not_dispatched_during_queue"]=not received
        assert report["not_dispatched_during_queue"]
        processed=[]
        while pipeline.pending:
            evt=pipeline.dispatch_one(sink=test_only_sink,identity_ok=live_ok,
                                      permission_ok=authorized)
            assert evt is not None
            processed.append(evt.sequence)
        root.update()
        report["delivered_exact_order"]=received
        expected=[]
        for action in ("down","up"):
            for i in (1,2):
                xx,yy=scale_client_point(x,y,master_size,metrics[identities[i]])
                expected.append((i,action,xx,yy))
        report["expected_scaled_client_events"]=expected
        report["real_tk_callbacks_fifo_scaled"]=received==expected
        assert report["real_tk_callbacks_fifo_scaled"]
        report["strict_sequence_indices"]=processed==[1,2,3,4]
        assert report["strict_sequence_indices"]
        assert not foreign_received
        report["unrelated_receives_zero_events"]=True

        # Permission revocation destroys queued clicks and logical press
        # tracking BEFORE any new test-only dispatch.
        assert pipeline.queue_mouse(x,y,button="right",pressed=True,
                                    sizes=metrics,now=108)==2
        before=len(received)
        guard.clear()
        attempt=pipeline.dispatch_one(sink=test_only_sink,
                                      identity_ok=live_ok,permission_ok=authorized)
        report["revocation_refuses_queued_input"]=(
            attempt is None and not pipeline.active
            and pipeline.pending==0 and len(received)==before)
        assert report["revocation_refuses_queued_input"]

        # New test-only verified session, but destroyed slave HWND must
        # be rejected before the next event reaches its test sink.
        assert guard.receive_token("S19_TEST_ONLY_VERIFIER",lambda _:
            VerifiedClaims(permissions=frozenset({"info_tab","start_tab"}),
                           plan_status="TEST_ONLY",max_windows=3))
        assert pipeline.start(WindowSnapshot(8,rows,True),identities[0],
                              max_windows=3)
        assert pipeline.queue_mouse(x,y,button="left",pressed=True,
                                    sizes=metrics,now=200)==2
        # do not actually destroy a game: close only a test-created HWND
        sources[2].destroy()
        root.update()
        delivered_before=len(received)
        # First FIFO to still-live test source is okay.
        ok=pipeline.dispatch_one(sink=test_only_sink,
                                 identity_ok=live_ok,permission_ok=authorized)
        assert ok is not None and len(received)==delivered_before+1
        denied=pipeline.dispatch_one(sink=test_only_sink,
                                     identity_ok=live_ok,permission_ok=authorized)
        report["stale_hwnd_pid_rejected"]=(
            denied is None and not pipeline.active and pipeline.pending==0)
        assert report["stale_hwnd_pid_rejected"]

        # Watchdog models C19 release after 10 seconds; NEVER claims OS DLL
        # input locks were taken/unlocked (none exists in S19).
        still_live=(rows[0],rows[1])
        assert pipeline.start(WindowSnapshot(9,still_live,True),
                              identities[0],max_windows=3)
        current={k:v for k,v in metrics.items() if k!=identities[2]}
        assert pipeline.queue_mouse(x,y,button="middle",pressed=True,
                                    sizes=current,now=300)==1
        assert not pipeline.watchdog(309.99)
        assert pipeline.watchdog(310.0)
        report["watchdog_cleared_pending_logical_down"]=(
            not pipeline.active and pipeline.pending==0
            and not pipeline.planned_buttons)
        assert report["watchdog_cleared_pending_logical_down"]
        pipeline.master_changed(identities[1])
        report["master_change_no_auto_restart"]=not pipeline.active
        assert report["master_change_no_auto_restart"]
        report["no_real_game_input_emitted"]=True
        report["status"]="PASS_NATIVE_S19_WIN32_CLIENTRECT_TEST_OWNED_FIFO_REVOKE"
    except Exception as exc:
        report["status"]="FAIL_NATIVE_S19_WIN32_CLIENTRECT_FIFO"
        report["error"]=f"{type(exc).__name__}: {exc}"
        report["traceback"]=traceback.format_exc(limit=18)
    finally:
        for top in sources:
            try:top.destroy()
            except Exception:pass
        if unrelated is not None:
            try:unrelated.destroy()
            except Exception:pass
        if root is not None:
            try:root.destroy()
            except Exception:pass
        REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),
                          encoding="utf-8")
        for k,v in report.items():
            if k!="traceback":
                print("S19_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if report["status"]=="PASS_NATIVE_S19_WIN32_CLIENTRECT_TEST_OWNED_FIFO_REVOKE" else 1


if __name__=="__main__":
    raise SystemExit(run())
