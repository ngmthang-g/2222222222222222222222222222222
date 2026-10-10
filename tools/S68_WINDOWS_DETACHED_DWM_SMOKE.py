"""S68 ACTUAL Windows C14 detached DWM overlay lifecycle on TEST-owned HWNDs.

Proof uses Win32 user32 + dwmapi. No actual Thần Long game, account/license,
pixel comparison or guessed `Tách rời` controls. A test-owned virtual desktop
fixture is used only if hosted Windows physical screen height <= 768.
"""
from __future__ import annotations
import ctypes,json,os,sys,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s68"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"c14_real_dwm_detached_owned.json"

def run():
    out={"task":"S68","status":"NOT_RUN",
         "source_kind":"THREE_TEST_OWNED_REAL_TK_HWND_NOT_GAME",
         "real_game":"NOT_RUN","product_exe":"NOT_PRODUCT",
         "real_entitlement":"NOT_CONNECTED","game_input_count":0,
         "exact_detached_tile_spacing":"UNKNOWN_NOT_GUESSED",
         "embedded_visibility_transition":"UNKNOWN_NOT_GUESSED"}
    root=None;host=None;detached=None;embedded=None
    try:
        if os.name!="nt":raise RuntimeError("WINDOWS_REQUIRED")
        import tkinter as tk
        from dwm_preview import NativeDwmBackend,ReadOnlyDwmPreviews,PreviewPlacement
        from detached_preview import C14DetachedDwmSession,verified_detached_region
        from layout_windows import NativeLayoutBackend
        from start_polling import WindowSnapshot
        from start_windows import GameWindow,GAME_PROCESS,GAME_TITLE,UNITY_WINDOW_CLASS

        native=NativeLayoutBackend()
        class CountedDwm(NativeDwmBackend):
            def __init__(self):
                super().__init__()
                self.registered=[];self.unregistered=[];self.created=[];self.destroyed=[]
            def create_destination(self,*args):
                h=super().create_destination(*args)
                self.created.append(h)
                return h
            def register(self,*args):
                h=super().register(*args)
                self.registered.append(h)
                return h
            def unregister(self,h):
                self.unregistered.append(h)
                return super().unregister(h)
            def destroy_destination(self,h):
                self.destroyed.append(h)
                return super().destroy_destination(h)
        dwm=CountedDwm()
        root=tk.Tk()
        root.title("S68 owned root - NO GAME")
        root.geometry("470x360+80+50")
        sources=[]
        for i in range(3):
            win=tk.Toplevel(root)
            win.title("S68 test source %s NO GAME"%(i+1))
            win.geometry(f"235x166+{80+245*i}+{110+30*i}")
            tk.Label(win,text="S68 native HWND %s / NOT GAME"%(i+1)).pack(
                fill="both",expand=True)
            sources.append(win)
        root.update_idletasks();root.update()
        pid=os.getpid()
        hwnds=tuple(int(dwm._ancestor(int(w.winfo_id()),2)) for w in sources)
        root_hwnd=int(dwm._ancestor(int(root.winfo_id()),2))
        assert len(set(hwnds))==3 and all(dwm.source_matches(h,pid) for h in hwnds)
        out["owned_source_hwnd_pid_verified"]=(
            native.process_executable(pid).lower().endswith(
                ("python.exe","pythonw.exe","python3.exe"))
            and all(native.process_id(h)==pid for h in hwnds))
        actual_w,actual_h=root.winfo_screenwidth(),root.winfo_screenheight()
        out["actual_desktop_dimensions"]=[actual_w,actual_h]
        out["original_C14_actual_desktop_region_available"]=(
            verified_detached_region(actual_w,actual_h) is not None)
        # Hosted CI can have a 768px desktop. NEVER claim a usable real
        # full-screen original region when actual_h <=768. This separate
        # test fixture exercises real native DWM at original C14 origin,
        # with clearly labeled virtual geometry only for the test.
        fixture_w=max(1600,actual_w)
        fixture_h=max(1000,actual_h)
        region=verified_detached_region(fixture_w,fixture_h)
        out["test_fixture_desktop_dimensions"]=[fixture_w,fixture_h]
        out["fixture_is_actual_screen"]=(
            fixture_w==actual_w and fixture_h==actual_h)

        host=tk.Toplevel(root)
        host.overrideredirect(True)
        host.attributes("-topmost",True)
        host.geometry(f"{region.width}x{region.height}+{region.x}+{region.y}")
        root.update_idletasks();root.update()
        host_hwnd=int(dwm._ancestor(int(host.winfo_id()),2))
        host_rect=native.window_rect(host_hwnd)
        out["native_detached_host_rect"]=[*host_rect]
        out["original_C14_region_native_host_geometry"]=(
            host_rect==(0,768,region.width,768+region.height)
            and native.process_id(host_hwnd)==pid and native.is_window(host_hwnd))
        assert out["original_C14_region_native_host_geometry"],out["native_detached_host_rect"]
        out["native_host_topmost_flag_requested"]=True

        class TestOwnedIdentity:
            """Only this test adapter represents test HWND as game identity."""
            def enumerate_top_level(self):
                allowed={host_hwnd,*hwnds}
                return tuple(h for h in native.enumerate_top_level() if h in allowed)
            def is_window(self,h):
                return h in {host_hwnd,*hwnds} and native.is_window(h)
            def is_visible(self,h):
                return h in {host_hwnd,*hwnds} and native.is_visible(h)
            def process_id(self,h):
                return native.process_id(h) if h in {host_hwnd,*hwnds} else 0
            def window_rect(self,h):
                return native.window_rect(h)
            def process_executable(self,p):
                return GAME_PROCESS if p==pid else ""
            def window_class(self,h):
                return UNITY_WINDOW_CLASS if h in hwnds else "TkTop"
            def title_with_timeout(self,h,timeout):
                assert timeout==150
                return GAME_TITLE if h in hwnds else "S68 TEST HOST"

        rows=tuple(GameWindow(h,pid,GAME_TITLE,UNITY_WINDOW_CLASS,GAME_PROCESS)
                   for h in hwnds)
        places=tuple(PreviewPlacement(h,pid,host_hwnd,12+i*215,780,197,110)
                     for i,h in enumerate(hwnds))
        owner=TestOwnedIdentity()
        detached=C14DetachedDwmSession(dwm,owner)
        embedded=ReadOnlyDwmPreviews(dwm)
        embed=PreviewPlacement(hwnds[0],pid,root_hwnd,155,110,197,110)
        embedded_result=embedded.sync((embed,))
        assert embedded_result.rendered==(hwnds[0],),embedded_result
        embedded_destination=embedded._slots[hwnds[0]].destination
        detached_open=detached.update(WindowSnapshot(68,rows,True),
                    owner_hwnd=host_hwnd,owner_pid=pid,
                    screen_width=fixture_w,screen_height=fixture_h,
                    max_windows=3,placements=places)
        out["native_3_detached_DWM_register"]=(
            detached_open.code=="DETACHED_DWM_VISIBLE"
            and detached_open.rendered==hwnds and len(detached.active_hwnds)==3)
        destinations=tuple(detached._previews._slots[h].destination for h in hwnds)
        out["native_DWM_destination_rectangles"]=(
            all(native.window_rect(dest)==(p.x,p.y,p.x+p.width,p.y+p.height)
                for dest,p in zip(destinations,places)))
        out["detached_and_embedded_distinct_destinations"]=(
            embedded_destination not in destinations
            and embedded.active_hwnds==(hwnds[0],))
        assert all(out[k] for k in (
            "native_3_detached_DWM_register","native_DWM_destination_rectangles",
            "detached_and_embedded_distinct_destinations")),out

        sources[1].destroy()
        root.update_idletasks();root.update()
        survivors=(rows[0],rows[2])
        p_survive=(places[0],places[2])
        after_close=detached.update(WindowSnapshot(69,survivors,True),
                    owner_hwnd=host_hwnd,owner_pid=pid,
                    screen_width=fixture_w,screen_height=fixture_h,
                    max_windows=3,placements=p_survive)
        out["closed_source_DWM_destroyed_but_survivors_remain"]=(
            after_close.code=="DETACHED_DWM_VISIBLE"
            and set(detached.active_hwnds)=={hwnds[0],hwnds[2]}
            and not native.is_window(destinations[1]))
        out["separate_embedded_DWM_survives_detached_close"]=False
        detached.clear()
        out["separate_embedded_DWM_survives_detached_close"]=(
            not detached.active_hwnds
            and embedded.active_hwnds==(hwnds[0],)
            and native.is_window(embedded_destination))
        out["DWM_resources_balanced_after_shutdown"]=False
        detached.shutdown()
        embedded.shutdown()
        out["DWM_resources_balanced_after_shutdown"]=(
            len(dwm.created)==len(dwm.destroyed)
            and len(dwm.registered)==len(dwm.unregistered))
        out["native_window_game_input_none"]=True
        assert all(out[k] for k in (
            "closed_source_DWM_destroyed_but_survivors_remain",
            "separate_embedded_DWM_survives_detached_close",
            "DWM_resources_balanced_after_shutdown","native_window_game_input_none")),out
        out["status"]="PASS_NATIVE_S68_C14_SEPARATE_DWM_HOST_TEST_ONLY"
    except Exception as exc:
        out["status"]="FAIL_NATIVE_S68"
        out["error_type"]=type(exc).__name__
        out["error_text"]=str(exc)[:300]
        out["traceback"]=traceback.format_exc(limit=10)
    finally:
        for ctrl in (detached,embedded):
            if ctrl is not None:
                try:ctrl.shutdown()
                except Exception:pass
        if root is not None:
            try:root.destroy()
            except Exception:pass
        REPORT.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
        for k,v in out.items():
            if k!="traceback":print("S68_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if out["status"]=="PASS_NATIVE_S68_C14_SEPARATE_DWM_HOST_TEST_ONLY" else 1
if __name__=="__main__":raise SystemExit(run())
