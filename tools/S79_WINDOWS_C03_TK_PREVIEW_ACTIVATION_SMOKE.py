"""S79 real Tk C03 header/surface activation of two REAL TEST-OWNED HWNDs.

The source windows and permission claims are TEST ONLY, NEVER original game.
Genuine Tk widgets/events, Win32 GetAncestor/PID and real DWM thumbnail
registrations are used, and the native ShowWindow/SetForegroundWindow call is
made by S78. OS foreground policy may deny focus: verify invocation, not
force focus. No injected user input, game memory, Proxy or product EXE.
"""
from __future__ import annotations
import json
import os
import sys
import tempfile
import traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s79"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"native_c03_tk_header_activation.json"

def run():
    report={
      "task":"S79","status":"NOT_RUN",
      "sources":"TWO_REAL_TEST_OWNED_PYTHON_TK_HWNDS_NOT_GAME",
      "permission":"IN_MEMORY_TEST_ONLY_CLAIMS_NOT_SERVER",
      "real_game":"NOT_EXECUTED","original_overlay_pixel_parity":"NOT_RUN",
      "product_exe":"NOT_PRODUCT",
    }
    root=None;app=None
    try:
        if os.name!="nt":raise RuntimeError("WINDOWS_REQUIRED")
        import tkinter as tk
        from dwm_preview import NativeDwmBackend
        from grid_master import GridSettingsStore
        from info_tab import TLMInfoTab
        from shell import TLMMainApp
        from permission_guard import PermissionGuard,VerifiedClaims
        from start_polling import WindowSnapshot,StartWindowProducer
        from start_tab import TLMStartTab
        from start_windows import (GameWindow,GAME_PROCESS,GAME_TITLE,
                                    UNITY_WINDOW_CLASS,NativeWin32Backend)
        with tempfile.TemporaryDirectory(prefix="S79_TK_PREVIEW_") as folder:
            events=[]
            root=tk.Tk()
            root.title("S79 test-owned Tk shell, NOT TLM game")
            root.geometry("800x910+10+15")
            sources=[]
            for idx in range(2):
                source=tk.Toplevel(root)
                source.title("S79 TEST-owned source, not game")
                source.geometry(f"185x130+{50+idx*230}+375")
                tk.Label(source,text="TEST-ONLY HWND").pack()
                sources.append(source)
            root.update_idletasks()
            root.update()
            class ObservedDwm(NativeDwmBackend):
                def __init__(self):
                    super().__init__()
                    self.activation_attempts=[]
                def activate_source(self,hwnd):
                    self.activation_attempts.append(int(hwnd))
                    events.append(("native_activate",int(hwnd)))
                    return super().activate_source(hwnd)
            dwm=ObservedDwm()
            hwnds=tuple(int(dwm._ancestor(int(win.winfo_id()),2))
                        for win in sources)
            pid=os.getpid()
            assert len(set(hwnds))==2
            assert all(dwm.source_matches(hwnd,pid) for hwnd in hwnds)
            report["two_real_native_test_HWNDS_and_PID"]=True
            test_rows=tuple(GameWindow(hwnd,pid,
                "S79 TEST-OWNED NOT GAME",UNITY_WINDOW_CLASS,GAME_PROCESS)
                for hwnd in hwnds)
            snap=WindowSnapshot(79,test_rows,True)
            producer=StartWindowProducer(NativeWin32Backend)
            builders={
                "info_tab":lambda parent:TLMInfoTab(parent),
                "start_tab":lambda parent:TLMStartTab(
                    parent,producer=producer,
                    preview_backend_factory=lambda:dwm,
                    grid_settings_store=GridSettingsStore(
                        Path(folder)/"grid_settings.ini")),
            }
            app=TLMMainApp(root,builders)
            app.position_window_top_right()
            root.update()
            report["original_info_only_before_test_permission"]=(
                app.lifecycle.visible=={"info_tab"})
            assert report["original_info_only_before_test_permission"]
            guard=PermissionGuard()
            assert guard.receive_token("S79_LOCAL_TEST_ONLY",
                lambda _:VerifiedClaims(
                  frozenset({"start_tab","info_tab"}),"TEST_ONLY",2))
            app.apply_info_snapshot(guard.snapshot)
            root.update()
            app.notebook.select(app._tab_frames["start_tab"])
            root.update()
            start=app.lifecycle._instances["start_tab"]
            producer.read_snapshot=lambda:snap
            root.geometry("805x890+20+15")
            root.update()
            assert start.poller.active and start.layout_max_windows==2
            assert start.container.winfo_viewable()
            start._sync_tiles(test_rows)
            root.update()
            start._refresh_dwm()
            root.update()
            controller=start._preview_controller
            report["genuine_live_DWM_bound_to_same_two_HWNDS"]=(
                controller is not None and controller.active_hwnds==hwnds
                and start.layout_max_windows==2)
            assert report["genuine_live_DWM_bound_to_same_two_HWNDS"]
            first=start._tile_items[(hwnds[0],pid)]
            second=start._tile_items[(hwnds[1],pid)]
            def click(widget):
                widget.event_generate("<Button-1>",x=7,y=7)
                root.update_idletasks()
            for widget,expected in (
                (first[1],hwnds[0]), # visible title label
                (second[2],hwnds[1]),# Tk preview surface behind DWM overlay
                (first[0],hwnds[0]), # tile background
            ):
                before=len(dwm.activation_attempts)
                click(widget)
                assert dwm.activation_attempts[before:]==[expected],(
                    widget,expected,dwm.activation_attempts)
            report["real_tk_label_surface_tile_events_activate_expected_source"]=True

            count=len(dwm.activation_attempts)
            first[3].invoke() # C17 left arrow, no native activation
            first[4].invoke() # C17 right arrow, no native activation
            root.update_idletasks()
            report["c17_arrows_do_not_activate_game_source"]=(
                len(dwm.activation_attempts)==count)
            assert report["c17_arrows_do_not_activate_game_source"]

            producer.read_snapshot=lambda:WindowSnapshot(
                80,(test_rows[0],GameWindow(
                    hwnds[1],pid+999,"TEST-PID-REUSED",
                    UNITY_WINDOW_CLASS,GAME_PROCESS)),True)
            click(second[1])
            report["reused_pid_snapshot_blocks_old_Tk_closure"]=(
                len(dwm.activation_attempts)==count)
            assert report["reused_pid_snapshot_blocks_old_Tk_closure"]
            producer.read_snapshot=lambda:snap

            # A native HWND can die before the next Start cache poll.
            sources[1].destroy()
            root.update()
            before=len(dwm.activation_attempts)
            click(second[1])
            report["destroyed_real_HWND_never_activated_again"]=(
                len(dwm.activation_attempts)==before)
            assert report["destroyed_real_HWND_never_activated_again"]

            guard.clear()
            app.apply_info_snapshot(guard.snapshot)
            root.update()
            report["Info_revocation_closes_Tk_DWM_source_callbacks"]=(
                not start.poller.active
                and not start._active_windows
                and start._preview_controller is None
                and start._activate_preview_source(hwnds[0],pid) is False)
            assert report["Info_revocation_closes_Tk_DWM_source_callbacks"]
            app.shutdown()
            root.destroy();root=None
            report["normal_owner_shutdown_after_revocation"]=True
            report["status"]="PASS_NATIVE_S79_C03_TK_CLICK_REAL_WIN32_SOURCE_TEST_ONLY"
    except Exception as exc:
        report["status"]="FAIL_NATIVE_S79"
        report["error_type"]=type(exc).__name__
        report["error_text"]=str(exc)[:300]
        report["traceback"]=traceback.format_exc(limit=17)
    finally:
        if app is not None:
            try:app.shutdown()
            except Exception:pass
        if root is not None:
            try:root.destroy()
            except Exception:pass
        REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),
                          encoding="utf-8")
        for k,v in report.items():
            if k!="traceback":
                print("S79_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if report["status"]==        "PASS_NATIVE_S79_C03_TK_CLICK_REAL_WIN32_SOURCE_TEST_ONLY" else 1

if __name__=="__main__":raise SystemExit(run())
