"""S152 real Win64/Tk/DWM C14 Info-provider exception after registered preview.

True TEST-OWNED three HWNDs and DwmRegisterThumbnail; no actual game,
original signed Info, product UI or authorization bypass. Hosted 1024x768
may not have an original C14 region, so positive case uses clearly TEST-ONLY
overridden Tk desktop metrics while native HWND/DWM handles are real.
"""
from __future__ import annotations
import json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s152"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"c14_auth_exception_real_win64.json"

def fail_provider():
    raise AssertionError("S152_TEST_ONLY_INFO_PROVIDER_EXCEPTION")

def run():
    report={"status":"NOT_RUN","task":"S152",
            "sources":"THREE_TEST_OWNED_TK_REAL_WIN64_NOT_GAME",
            "original_c14_ui_complete":False,"real_info_connected":False,
            "product_exe_verified":False,"game_input_count":0}
    root=None
    manager=None
    try:
        if os.name!="nt":raise RuntimeError("WINDOWS_REQUIRED")
        import tkinter as tk
        from layout_windows import NativeLayoutBackend
        from dwm_preview import NativeDwmBackend,PreviewPlacement
        from detached_preview import C14DetachedDwmSession,verified_detached_region
        from detached_host import C14DetachedHost,_native_is_topmost
        from start_windows import GameWindow,GAME_PROCESS,GAME_TITLE,UNITY_WINDOW_CLASS
        from start_polling import WindowSnapshot

        events=[]
        native=NativeLayoutBackend()
        class TracedDwm(NativeDwmBackend):
            def register(self,*args):
                t=super().register(*args)
                events.append(("register",int(t)))
                return t
            def unregister(self,token):
                events.append(("unregister",int(token)))
                return super().unregister(token)
            def destroy_destination(self,hwnd):
                events.append(("destroy_destination",int(hwnd)))
                return super().destroy_destination(hwnd)
        dwm=TracedDwm()
        root=tk.Tk()
        root.title("S152 owned Tk root TEST NO GAME")
        root.geometry("380x220+250+80")
        sources=[]
        for i in range(3):
            t=tk.Toplevel(root)
            t.title("S152 test source NOT Thần Long")
            t.geometry(f"230x150+{20+i*240}+{40+i*20}")
            tk.Label(t,text="S152 REAL TEST HWND - NOT GAME").pack(expand=True,fill="both")
            sources.append(t)
        root.update_idletasks();root.update()
        pid=os.getpid()
        hwnds=tuple(int(dwm._ancestor(int(t.winfo_id()),2)) for t in sources)
        assert len(set(hwnds))==3
        assert all(dwm.source_matches(h,pid) for h in hwnds)

        class TestOwnedGameIdentity:
            def enumerate_top_level(self):return native.enumerate_top_level()
            def is_window(self,h):return native.is_window(h)
            def is_visible(self,h):return native.is_visible(h)
            def process_id(self,h):return native.process_id(h)
            def window_rect(self,h):return native.window_rect(h)
            def process_executable(self,p):return GAME_PROCESS if p==pid else ""
            def window_class(self,h):
                return UNITY_WINDOW_CLASS if h in hwnds else "TkTop"
            def title_with_timeout(self,h,ms):
                assert ms==150
                return GAME_TITLE if h in hwnds else "S152 TEST HOST"
        identity=TestOwnedGameIdentity()
        rows=tuple(GameWindow(h,pid,GAME_TITLE,UNITY_WINDOW_CLASS,GAME_PROCESS)
                   for h in hwnds)
        snapshot=WindowSnapshot(152,rows,True)

        class TracedHost(tk.Toplevel):
            def destroy(self):
                events.append(("destroy_host",int(dwm._ancestor(int(self.winfo_id()),2))))
                return super().destroy()
        manager=C14DetachedHost(
            root,windows_backend=identity,
            toplevel_factory=lambda tkroot:TracedHost(tkroot),
            session_factory=lambda:C14DetachedDwmSession(dwm,identity))

        aw,ah=root.winfo_screenwidth(),root.winfo_screenheight()
        report["actual_desktop_dimensions"]=[aw,ah]
        report["original_region_available_on_actual_desktop"]=(
            verified_detached_region(aw,ah) is not None)
        # Physical CI desktop may end at 768; never claim original product
        # usability of an off-screen test-only 1600x1000 coordinate fixture.
        fw,fh=max(1600,aw),max(1000,ah)
        report["test_only_tk_virtual_desktop_metrics"]=[fw,fh]
        root.winfo_screenwidth=lambda:fw
        root.winfo_screenheight=lambda:fh
        region=verified_detached_region(fw,fh)
        opened=manager.open(snapshot,max_windows=3,allowed=lambda:True)
        owner=manager.owner_hwnd
        report["true_native_topmost_host_and_C14_region"]=(
            opened.code=="HOST_OPEN" and owner>0 and _native_is_topmost(owner)
            and native.window_rect(owner)==(0,768,region.width,768+region.height))
        assert report["true_native_topmost_host_and_C14_region"]
        places=tuple(PreviewPlacement(h,pid,owner,12+210*i,780,197,110)
                     for i,h in enumerate(hwnds))
        rendered=manager.render(snapshot,max_windows=3,
                                placements=places,allowed=lambda:True)
        report["real_three_DWM_registered_before_authorization_exception"]=(
            rendered.code=="DETACHED_DWM_VISIBLE"
            and rendered.rendered==hwnds
            and len([e for e in events if e[0]=="register"])==3)
        assert report["real_three_DWM_registered_before_authorization_exception"]
        destinations=tuple(manager._session._previews._slots[h].destination for h in hwnds)

        rejected=manager.render(snapshot,max_windows=3,placements=places,
                                allowed=fail_provider)
        report["provider_exception_revokes_real_DWM_without_game_close"]=(
            rejected.code=="CANCELLED" and manager.owner_hwnd==0
            and not native.is_window(owner)
            and all(not native.is_window(h) for h in destinations)
            and all(native.is_window(h) and native.process_id(h)==pid for h in hwnds)
            and len([e for e in events if e[0]=="unregister"])==3
            and len([e for e in events if e[0]=="destroy_destination"])==3)
        report["C13_DWM_cleanup_before_detached_host_destroy"]=(
            max(i for i,e in enumerate(events)
                if e[0] in ("unregister","destroy_destination")) <
            next(i for i,e in enumerate(events) if e[0]=="destroy_host"))
        assert report["provider_exception_revokes_real_DWM_without_game_close"]
        assert report["C13_DWM_cleanup_before_detached_host_destroy"]

        reopened=manager.open(snapshot,max_windows=3,allowed=fail_provider)
        report["provider_still_denied_no_new_native_host"]=(
            reopened.code=="CANCELLED"
            and manager.owner_hwnd==0
            and len([e for e in events if e[0]=="register"])==3)
        assert report["provider_still_denied_no_new_native_host"]
        report["status"]="PASS_NATIVE_S152_C14_PROVIDER_EXCEPTION_CLEANUP_TEST_OWNED_NOT_PRODUCT"
    except Exception as exc:
        report["status"]="FAIL_NATIVE_S152"
        report["error_type"]=type(exc).__name__
    finally:
        if manager is not None:
            try:manager.shutdown()
            except Exception:pass
        if root is not None:
            try:root.destroy()
            except Exception:pass
        REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",
                          encoding="utf-8")
        print(json.dumps(report,ensure_ascii=False))
    return 0 if report["status"].startswith("PASS_") else 1

if __name__=="__main__":raise SystemExit(run())
