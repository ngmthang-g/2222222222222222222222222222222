"""S85 C14 genuine native DWM close-then-reopen refresh with external placements.

All game-like source identity adaptation is isolated to this TEST-ONLY file.
Positive overlay test labels the 1600x1000 Tk screen-method override as a
VIRTUAL TEST FIXTURE, NEVER as a usable real desktop or original UI parity.
"""
from __future__ import annotations
import ctypes,json,os,sys,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s85"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"native_C14_refresh_only_with_verified_placements.json"

def run():
    report={"task":"S85","status":"NOT_RUN",
            "test_sources":"3_OWNED_REAL_PYTHON_TK_HWND_NOT_GAME",
            "original_TLM_visual_parity":"NOT_RUN",
            "actual_game":"NOT_RUN","signed_info":"NOT_CONNECTED",
            "product_exe":"NOT_PRODUCT",
            "detached_auto_open_runtime":"NOT_WIRED"}
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

        b=NativeLayoutBackend()
        events=[]
        class CountedNative(NativeDwmBackend):
            def register(self,*args):
                token=super().register(*args)
                events.append(("register",int(token)))
                return token
            def unregister(self,token):
                events.append(("unregister",int(token)))
                return super().unregister(token)
            def destroy_destination(self,hwnd):
                events.append(("destroy_destination",int(hwnd)))
                return super().destroy_destination(hwnd)
        dwm=CountedNative()
        root=tk.Tk()
        root.title("S85 owned root NO GAME")
        root.geometry("460x320+280+100")
        sources=[]
        for i in range(3):
            s=tk.Toplevel(root)
            s.title("S85 owned source %d test ONLY"%(i+1))
            s.geometry(f"220x170+{10+225*i}+{20+25*i}")
            tk.Label(s,text="TEST HWND - NOT GAME").pack(fill="both",expand=True)
            sources.append(s)
        root.update_idletasks()
        root.update()
        source_hwnds=tuple(int(dwm._ancestor(int(x.winfo_id()),2))
                           for x in sources)
        pid=os.getpid()
        assert all(dwm.source_matches(h,pid) for h in source_hwnds)
        assert len(set(source_hwnds))==3

        class TestOnlyIdentity:
            def enumerate_top_level(self):return b.enumerate_top_level()
            def is_window(self,h):return b.is_window(h)
            def is_visible(self,h):return b.is_visible(h)
            def process_id(self,h):return b.process_id(h)
            def window_rect(self,h):return b.window_rect(h)
            def process_executable(self,p):
                return GAME_PROCESS if p==pid else ""
            def window_class(self,h):
                return UNITY_WINDOW_CLASS if h in source_hwnds else "TkTop"
            def title_with_timeout(self,h,ms):
                assert ms==150
                return GAME_TITLE if h in source_hwnds else "TEST HOST"
        adapter=TestOnlyIdentity()
        rows=tuple(GameWindow(h,pid,GAME_TITLE,UNITY_WINDOW_CLASS,GAME_PROCESS)
                   for h in source_hwnds)
        snap=WindowSnapshot(70,rows,True)

        class TracedHost(tk.Toplevel):
            def destroy(self):
                events.append(("destroy_host",int(dwm._ancestor(int(self.winfo_id()),2))))
                return super().destroy()
        def factory(root_widget):
            return TracedHost(root_widget)

        manager=C14DetachedHost(root,windows_backend=adapter,
             toplevel_factory=factory,
             session_factory=lambda:C14DetachedDwmSession(dwm,adapter))

        physical_w,physical_h=root.winfo_screenwidth(),root.winfo_screenheight()
        report["actual_physical_desktop"]=[physical_w,physical_h]
        original=verified_detached_region(physical_w,physical_h)
        report["original_C14_real_screen_sufficient"]=original is not None
        if original is None:
            denied=manager.open(snap,max_windows=3,allowed=lambda:True)
            report["actual_short_screen_refused_no_owner"]=(
                denied.code=="NO_USABLE_SCREEN_REGION"
                and manager.owner_hwnd==0
                and not any(e[0]=="destroy_host" for e in events))
            assert report["actual_short_screen_refused_no_owner"]
        else:
            report["actual_short_screen_refused_no_owner"]="NOT_APPLICABLE_REAL_REGION_EXISTS"

        # TEST-ONLY Tk desktop metrics fixture, explicit and readback-proven.
        # We do NOT mutate system resolution or claim production user-screen
        # compatibility. Windows native windows are nevertheless real.
        effective_w=max(1600,physical_w)
        effective_h=max(1000,physical_h)
        report["positive_native_test_uses_virtual_desktop_fixture"]=(
            effective_w!=physical_w or effective_h!=physical_h)
        root.winfo_screenwidth=lambda:effective_w
        root.winfo_screenheight=lambda:effective_h
        region=verified_detached_region(effective_w,effective_h)
        fresh=manager.open(snap,max_windows=3,allowed=lambda:True)
        report["host_open_status"]=fresh.code
        host=manager.owner_hwnd
        report["native_topmost_host_created_verified"]=(
            fresh.code=="HOST_OPEN" and host>0 and b.is_window(host)
            and b.process_id(host)==pid and _native_is_topmost(host)
            and b.window_rect(host)==(
                region.x,region.y,region.x+region.width,region.y+region.height))
        assert report["native_topmost_host_created_verified"],report
        places=tuple(PreviewPlacement(
            h,pid,host,12+i*210,780,197,110)
            for i,h in enumerate(source_hwnds))
        status=manager.render(snap,max_windows=3,placements=places,
                               allowed=lambda:True)
        report["three_real_DWM_destinations_while_host_alive"]=(
            status.code=="DETACHED_DWM_VISIBLE" and
            status.rendered==source_hwnds and
            manager.active_hwnds==source_hwnds)
        assert report["three_real_DWM_destinations_while_host_alive"],status

        # S85 originally proved C14 refresh = CLOSE THEN REOPEN. Each
        # placement exists ONLY in this TEST-ONLY caller; production NEVER
        # invents tile spacing or original C14 detached rows/cols.
        prev_owner=host
        native_tokens_before=tuple(e[1] for e in events if e[0]=="register")
        def test_only_verified_placements(region, owner, current):
            return tuple(PreviewPlacement(
                w.hwnd,w.pid,owner,12+i*210,780,197,110)
                for i,w in enumerate(current.windows))
        state=manager.refresh(
            snap,max_windows=3,allowed=lambda:True,
            placements_for_owner=test_only_verified_placements)
        reopened_owner=manager.owner_hwnd
        report["native_original_close_then_reopen_visible"]=(
            state.code=="DETACHED_DWM_REFRESHED"
            and set(state.rendered)==set(source_hwnds)
            and reopened_owner>0 and b.is_window(reopened_owner)
            and _native_is_topmost(reopened_owner)
            and manager.active_hwnds==source_hwnds)
        assert report["native_original_close_then_reopen_visible"],state
        first_destroy=next(i for i,e in enumerate(events) if e[0]=="destroy_host")
        # OLD owner DWM destinations are destroyed BEFORE old owner goes;
        # second batch registers only AFTER the old owner is destroyed.
        report["real_native_refresh_teardown_before_new_DWM"]=(
            sum(e[0]=="unregister" for e in events)==3
            and sum(e[0]=="destroy_destination" for e in events)==3
            and sum(e[0]=="register" for e in events)==6
            and max(i for i,e in enumerate(events[:first_destroy])
                    if e[0] in ("unregister","destroy_destination")) < first_destroy
            and min(i for i,e in enumerate(events)
                    if e[0]=="register" and e[1] not in native_tokens_before)
                    > first_destroy)
        assert report["real_native_refresh_teardown_before_new_DWM"],events
        report["all_three_source_HWNDs_alive_during_refresh"]=all(
            b.is_window(h) and b.process_id(h)==pid for h in source_hwnds)
        assert report["all_three_source_HWNDs_alive_during_refresh"]
        # Preserve the existing real user-facing S84 C13 close button.
        close_btn=manager._close_view_button
        assert close_btn is not None and close_btn.cget("text")=="Đóng xem"
        close_btn.invoke()
        root.update_idletasks()
        report["C13_close_still_real_after_native_C14_refresh"]=(
            manager.owner_hwnd==0
            and not manager.active_hwnds
            and not b.is_window(reopened_owner))
        assert report["C13_close_still_real_after_native_C14_refresh"]
        report["real_owner_destroyed_after_DWM_unregister"]=(
            not b.is_window(reopened_owner)
            and not manager.active_hwnds
            and events[-1][0]=="destroy_host"
            and len([e for e in events if e[0]=="unregister"])==6
            and len([e for e in events if e[0]=="destroy_destination"])==6
            and max(i for i,e in enumerate(events)
                    if e[0] in ("unregister","destroy_destination"))
                < max(i for i,e in enumerate(events)
                       if e[0]=="destroy_host"))
        assert report["real_owner_destroyed_after_DWM_unregister"],events
        report["placement_provider_is_explicit_test_only"]=True
        manager.shutdown()
        assert manager.open(snap,max_windows=3,allowed=lambda:True).code=="CLOSED"
        report["host_shutdown_permanent"]=True
        report["status"]="PASS_NATIVE_S85_C14_REFRESH_CLOSE_REOPEN_VERIFIED_PLACEMENTS_TEST_ONLY"
    except Exception as exc:
        report["status"]="FAIL_NATIVE_S85"
        report["error_type"]=type(exc).__name__
        report["error_text"]=str(exc)[:300]
        report["traceback"]=traceback.format_exc(limit=12)
    finally:
        if manager is not None:
            try:manager.shutdown()
            except Exception:pass
        if root is not None:
            try:root.destroy()
            except Exception:pass
        REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),
                          encoding="utf-8")
        for k,v in report.items():
            if k!="traceback":print("S85_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if report["status"]=="PASS_NATIVE_S85_C14_REFRESH_CLOSE_REOPEN_VERIFIED_PLACEMENTS_TEST_ONLY" else 1

if __name__=="__main__":raise SystemExit(run())
