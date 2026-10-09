"""S18 native C05/C08: functional radios, grid +/- and persisted grid.

Uses only real TEST-OWNED native Tk HWNDs, isolated settings.ini, verified
test-only PermissionSnapshot. No real game or C19 input-sync.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import traceback
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s18"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"native_grid_master_settings.json"


def run():
    report={
        "task":"S18", "status":"NOT_RUN",
        "source_type":"FOUR_REAL_TEST_OWNED_WIN32_TK_HWND_NOT_GAME",
        "real_game":"NOT_RUN","real_server":"NOT_RUN",
        "product_exe":"NOT_BUILT","input_sync":"NOT_IMPLEMENTED",
        "exact_original_grid_math":"UNKNOWN",
        "exact_original_worker_cadence":"UNKNOWN",
        "proxy":"NOT_DEVELOPED",
    }
    root=None
    app=None
    sources=[]
    extra=None
    sandbox_ini=None
    try:
        if os.name!="nt":
            raise RuntimeError("Windows required")
        import ctypes
        from ctypes import wintypes
        import tkinter as tk
        from info_tab import TLMInfoTab
        from shell import TLMMainApp
        from permission_guard import PermissionGuard,VerifiedClaims
        from start_tab import TLMStartTab
        from start_windows import GAME_PROCESS,GAME_TITLE,UNITY_WINDOW_CLASS,GameWindow
        from start_polling import WindowSnapshot
        from dwm_preview import NativeDwmBackend
        from layout_windows import C18LayoutSync,NativeLayoutBackend
        from grid_master import GridSettingsStore,GridSettings

        root=tk.Tk()
        root.title("S17 native test tool - not a game")
        root.geometry("920x760+70+35")
        for i in range(4):
            src=tk.Toplevel(root)
            src.title(f"S17 ONLY TEST NATIVE HWND #{i}")
            src.geometry(f"160x120+{55+i*190}+{210+(i%2)*145}")
            tk.Label(src,text=f"TEST OWNED SOURCE {i}").pack(fill="both",expand=True)
            sources.append(src)
        extra=tk.Toplevel(root)
        extra.title("S17 NOT TARGET, MUST NEVER MOVE")
        extra.geometry("130x90+500+500")
        tk.Label(extra,text="UNRELATED WINDOW").pack(fill="both",expand=True)
        root.update()
        native=NativeLayoutBackend()
        ancestor=NativeDwmBackend()
        targets=tuple(int(ancestor._ancestor(int(src.winfo_id()),2)) for src in sources)
        extra_hwnd=int(ancestor._ancestor(int(extra.winfo_id()),2))
        pid=os.getpid()
        assert len(set(targets))==4 and extra_hwnd not in targets
        assert all(native.is_window(h) and native.process_id(h)==pid for h in targets)
        rows=tuple(GameWindow(h,pid,GAME_TITLE,UNITY_WINDOW_CLASS,GAME_PROCESS) for h in targets)
        start_positions={h:native.window_rect(h) for h in targets}
        unrelated_before=native.window_rect(extra_hwnd)
        report["real_test_hwnds"]=targets
        report["unrelated_hwnd"]=extra_hwnd
        report["starting_rects"]=start_positions

        # ONLY TEST fixture provides pretend game identity to original S08
        # candidate gate. Production code uses actual native process identity.
        class SafeTestNativeBackend:
            moves=[]
            def __init__(self):
                self.native=NativeLayoutBackend()
            def __getattr__(self,name):
                return getattr(self.native,name)
            def process_executable(self,process_id):
                return GAME_PROCESS if process_id==pid else ""
            def window_class(self,hwnd):
                return UNITY_WINDOW_CLASS if hwnd in targets else "TkTop"
            def title_with_timeout(self,hwnd,timeout_ms):
                assert timeout_ms==150
                return GAME_TITLE if hwnd in targets else "OTHER WINDOW"
            def move_no_resize(self,hwnd,x,y):
                assert hwnd in targets,("NON_TEST_OWNED_MOVE_BLOCKED",hwnd)
                self.moves.append((hwnd,x,y))
                return self.native.move_no_resize(hwnd,x,y)

        guarded_backend=SafeTestNativeBackend()
        class TestOnlyCache:
            def __init__(self):
                self.active=False
                self.revision=0
                self.windows=rows
            def start(self):
                self.active=True
                self.revision+=1
                return True
            def stop(self):
                self.active=False
                self.revision+=1
            def read_snapshot(self):
                return WindowSnapshot(self.revision,self.windows if self.active else (),self.active)
        cache=TestOnlyCache()
        sandbox_ini=tempfile.TemporaryDirectory(prefix="s18_settings_test_")
        store=GridSettingsStore(Path(sandbox_ini.name)/"TLMTool"/"settings.ini")
        built=[]
        def make_start(frame):
            item=TLMStartTab(frame,producer=cache,
                layout_service_factory=lambda:C18LayoutSync(guarded_backend),
                grid_settings_store=store)
            built.append(item)
            return item
        app=TLMMainApp(root,{"info_tab":lambda f:TLMInfoTab(f),"start_tab":make_start})
        app.position_window_top_right()
        root.geometry("930x800+25+25")
        root.update()
        report["info_only_until_verified"]=app.lifecycle.visible=={"info_tab"} and not built
        assert report["info_only_until_verified"]

        guard=PermissionGuard()
        def grant(limit):
            assert guard.receive_token("S18_TEST_ONLY_VERIFIER",lambda _:
                VerifiedClaims(permissions=frozenset({"info_tab","start_tab"}),
                               plan_status="TEST_ONLY",max_windows=limit))
            app.apply_info_snapshot(guard.snapshot)
            root.update()
        def pump(ms=200):
            root.after(ms,root.quit)
            root.mainloop()

        grant(3)
        app.notebook.select(app._tab_frames["start_tab"])
        root.update()
        pump(240)
        tab=built[0]
        report["initial_grid_defaults"]=(tab.grid_cols,tab.grid_rows)==(3,4)
        assert report["initial_grid_defaults"]
        report["radio_count_4"]=len(tab._master_radio_buttons)==4
        assert report["radio_count_4"]
        # Actual buttons: 3x4 to 2x2; persistence uses E05 settings.ini.
        tab.btn_decrease_cols.invoke()
        tab.btn_decrease_rows.invoke()
        tab.btn_decrease_rows.invoke()
        report["actual_grid_buttons_2x2"]=(tab.grid_cols,tab.grid_rows)==(2,2)
        report["initial_settings_saved"]=store.load()==GridSettings(2,2)
        assert report["actual_grid_buttons_2x2"]
        assert report["initial_settings_saved"]
        report["label_updated"]=(tab.grid_cols_label.cget("text")=="Cột: 2"
                                   and tab.grid_rows_label.cget("text")=="Hàng: 2")
        assert report["label_updated"]
        report["limit3_passed_to_start"]=tab.layout_max_windows==3
        assert report["limit3_passed_to_start"]
        report["over_limit_refuses_to_start"]=not tab._toggle_layout() and not guarded_backend.moves
        assert report["over_limit_refuses_to_start"]

        grant(4)
        pump(140)
        report["limit4_verified"]=tab.layout_max_windows==4
        assert report["limit4_verified"]
        # S18: C05 radio is a genuine HWND/PID selector; do not bypass UI.
        assert len(tab._master_radio_buttons)==4
        tab._master_radio_buttons[2].invoke()
        assert tab.layout_master_hwnd==targets[2]
        report["initial_state_off"]=not tab.layout_active
        assert report["initial_state_off"]
        assert tab.btn_layout.cget("text")=="Đồng bộ các cửa sổ"
        tab.btn_layout.invoke()
        report["button_enabled_real_worker"]=tab.layout_active and tab.sync_layout_running
        assert report["button_enabled_real_worker"]
        for i in range(14):
            pump(180)
            if tab._layout_last_result and tab._layout_last_result.code=="GRID_APPLIED":
                break
        report["first_worker_result"]=getattr(tab._layout_last_result,"code","NO_RESULT")
        assert report["first_worker_result"]=="GRID_APPLIED"
        assert len(guarded_backend.moves)>0
        actual={h:native.window_rect(h) for h in targets}
        master_rect=actual[targets[2]]
        w=master_rect[2]-master_rect[0]
        expected={
            targets[2]:(0,0),
            targets[0]:(w+8,0),
            targets[1]:(0,master_rect[3]-master_rect[1]+8),
            targets[3]:(w+8,master_rect[3]-master_rect[1]+8),
        }
        report["actual_layout_xy"]={str(h):actual[h][:2] for h in targets}
        report["expected_local_layout_xy"]={str(h):xy for h,xy in expected.items()}
        assert all(actual[h][:2]==xy for h,xy in expected.items())
        report["preserved_source_sizes"]=all(
            (actual[h][2]-actual[h][0],actual[h][3]-actual[h][1])==
            (start_positions[h][2]-start_positions[h][0],
             start_positions[h][3]-start_positions[h][1]) for h in targets)
        assert report["preserved_source_sizes"]
        assert native.window_rect(extra_hwnd)==unrelated_before
        report["unrelated_window_untouched"]=True

        # Adjust column and row count WHILE native sync is active; worker
        # must cancel old-generation geometry and re-layout from actual GUI.
        tab.btn_increase_cols.invoke()
        tab.btn_increase_rows.invoke()
        assert (tab.grid_cols,tab.grid_rows)==(3,3)
        assert store.load()==GridSettings(3,3)
        expected_after={
            targets[2]:(0,0),
            targets[0]:(w+8,0),
            targets[1]:(2*(w+8),0),
            targets[3]:(0,master_rect[3]-master_rect[1]+8),
        }
        for _ in range(18):
            pump(190)
            if all(native.window_rect(h)[:2]==xy for h,xy in expected_after.items()):
                break
        report["regrid_from_button_while_running"]=all(
            native.window_rect(h)[:2]==xy for h,xy in expected_after.items())
        assert report["regrid_from_button_while_running"]

        # Real RADIO invocation changes native grid index0 master. No
        # character-name guess or test-only property injection.
        tab._master_radio_buttons[1].invoke()
        assert tab.layout_master_hwnd==targets[1]
        master_next={
            targets[1]:(0,0),
            targets[0]:(w+8,0),
            targets[2]:(2*(w+8),0),
            targets[3]:(0,master_rect[3]-master_rect[1]+8),
        }
        for _ in range(18):
            pump(190)
            if all(native.window_rect(h)[:2]==xy for h,xy in master_next.items()):
                break
        report["real_radio_changes_native_master"]=all(
            native.window_rect(h)[:2]==xy for h,xy in master_next.items())
        assert report["real_radio_changes_native_master"]
        report["master_identity_pid_safe"]=(tab.master_selection.selected==(targets[1],pid))
        assert report["master_identity_pid_safe"]
        report["persisted_grid_after_changes"]=store.load()==GridSettings(3,3)
        assert report["persisted_grid_after_changes"]

        # External manual move; existing S13 housekeeping triggers worker
        # *again* using cached source list. No invented original C18 timer.
        target=targets[0]
        assert native.move_no_resize(target,510,330)
        assert native.window_rect(target)[:2]==(510,330)
        for i in range(16):
            pump(200)
            if native.window_rect(target)[:2]==master_next[target]:
                break
        report["layout_sync_restored_external_move"]=(
            native.window_rect(target)[:2]==master_next[target])
        assert report["layout_sync_restored_external_move"]
        report["native_move_count"]=len(guarded_backend.moves)

        # Revoke grant while active and verify no further native moves.
        guard.clear()
        app.apply_info_snapshot(guard.snapshot)
        root.update()
        pump(160)
        report["revoked_info_fallback"]=(app.lifecycle.current=="info_tab")
        report["revoked_stopped_layout"]=(not tab.layout_active and
                                          not tab.sync_layout_running and
                                          not tab._layout_allow.is_set() and
                                          tab.layout_max_windows==0)
        assert report["revoked_info_fallback"] and report["revoked_stopped_layout"]
        saved=len(guarded_backend.moves)
        assert native.move_no_resize(target,480,320)
        pump(1300)
        report["revocation_no_late_moves"]=(len(guarded_backend.moves)==saved and
                                            native.window_rect(target)[:2]==(480,320))
        assert report["revocation_no_late_moves"]
        report["master_not_persisted_to_ini"]="master" not in store.path.read_text(encoding="utf-8").lower()
        assert report["master_not_persisted_to_ini"]
        report["no_input_or_game_events"]=True
        report["status"]="PASS_NATIVE_S18_REAL_GRID_BUTTONS_RADIOS_PERSISTENCE_AND_REVOKE"
    except Exception as exc:
        report["status"]="FAIL_NATIVE_S18_GRID_MASTER"
        report["error"]=f"{type(exc).__name__}: {exc}"
        report["traceback"]=traceback.format_exc(limit=17)
    finally:
        if app is not None:
            try:app.shutdown()
            except Exception as exc:
                report["cleanup_error"]=str(exc)
                report["status"]="FAIL_CLEANUP"
        for src in sources:
            try:src.destroy()
            except Exception:pass
        if extra is not None:
            try:extra.destroy()
            except Exception:pass
        if root is not None:
            try:root.destroy()
            except Exception as exc:
                report["destroy_error"]=str(exc)
                report["status"]="FAIL_CLEANUP"
        if sandbox_ini is not None:
            sandbox_ini.cleanup()
        REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
        for k,v in report.items():
            if k!="traceback":
                print("S18_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if report["status"]=="PASS_NATIVE_S18_REAL_GRID_BUTTONS_RADIOS_PERSISTENCE_AND_REVOKE" else 1


if __name__=="__main__":
    raise SystemExit(run())
