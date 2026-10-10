"""S82 native Windows: source-stable master radios across C09/C15 Tk actions.

ACTUAL Windows Tk radiobuttons, preview grids 1x/2x/3x and real DWM
thumb destination registration, based on three TEST-OWNED Python HWNDs.
No original game, signed real Info, RoleName or product EXE.
"""
from __future__ import annotations
import json, os, sys, tempfile, traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s82"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"native_master_radio_grid_refresh.json"

def run():
    result={"task":"S82","status":"NOT_RUN",
            "windows":"THREE_REAL_TEST_OWNED_TK_HWND_NOT_GAME",
            "grant":"EXPLICIT_LOCAL_TEST_LIMIT_NOT_REAL_INFO",
            "game":"NOT_EXECUTED","role_name":"NOT_READ",
            "product_exe":"DIAGNOSTIC_NOT_PRODUCT"}
    root=None; start=None
    try:
        if os.name!="nt":raise RuntimeError("S82_WINDOWS_REQUIRED")
        import tkinter as tk
        from dwm_preview import NativeDwmBackend, _DWM_CLICK_TARGETS
        from start_tab import TLMStartTab
        from start_windows import GameWindow,NativeWin32Backend
        from start_polling import StartWindowProducer,WindowSnapshot
        from grid_master import GridSettingsStore
        root=tk.Tk()
        root.title("S82 TEST Start C05 C09 C15 not game")
        root.geometry("930x940+10+10")
        sources=[]
        for i in range(3):
            w=tk.Toplevel(root)
            w.title(f"S82 TEST source {i+1} NOT GAME")
            w.geometry(f"190x145+{15+230*i}+430")
            tk.Label(w,text="TEST OWNED NOT GAME").pack()
            sources.append(w)
        root.update_idletasks()
        root.update()
        class ObservedDWM(NativeDwmBackend):
            def __init__(self):
                super().__init__()
                self.registered=[]
                self.released=[]
            def register(self,dst,source):
                t=super().register(dst,source)
                self.registered.append((int(dst),int(source),t))
                return t
            def unregister(self,thumbnail):
                self.released.append(int(thumbnail))
                return super().unregister(thumbnail)
        backend=ObservedDWM()
        hwnds=tuple(int(backend._ancestor(int(w.winfo_id()),2)) for w in sources)
        pid=os.getpid()
        assert len(set(hwnds))==3
        assert all(backend.source_matches(h,pid) for h in hwnds)
        rows=tuple(GameWindow(h,pid,f"S82 NATIVE TEST {i+1}",
                              "TEST_OWNED","NOT_GAME.exe")
                   for i,h in enumerate(hwnds))
        cache=WindowSnapshot(82,rows,True)
        with tempfile.TemporaryDirectory(prefix="S82_NATIVE_") as folder:
            start=TLMStartTab(root,producer=StartWindowProducer(NativeWin32Backend),
                             preview_backend_factory=lambda:backend,
                             grid_settings_store=GridSettingsStore(Path(folder)/"grid.ini"))
            root.update()
            start.set_layout_max_windows(3)
            start._start_refresh()
            root.update()
            start.poller.producer.read_snapshot=lambda:cache
            start._sync_tiles(rows)
            root.update()
            start._refresh_dwm()
            root.update()
            assert start._preview_controller is not None
            result["three_real_DWM_source_slots"]=(
                start._preview_controller.active_hwnds==hwnds
                and len(backend.registered)==3)
            assert result["three_real_DWM_source_slots"]
            radios=tuple(start._master_radio_buttons)
            assert len(radios)==3
            result["three_real_Tk_master_radios"]=all(
                bool(w.winfo_exists()) for w in radios)
            assert result["three_real_Tk_master_radios"]

            # Simulate a real user clicking master radio #2 (not just
            # assigning a synthetic StringVar selection).
            radios[1].invoke()
            root.update()
            assert start.master_selection.selected==(hwnds[1],pid)
            permuted=(rows[2],rows[0],rows[1])
            start._sync_tiles(permuted)
            root.update()
            result["same_HWND_set_permutation_does_not_destroy_radio"]=(
                tuple(start._master_radio_buttons)==radios
                and all(w.winfo_exists() for w in radios)
                and start.master_selection.selected==(hwnds[1],pid)
                and start._master_var.get()==f"{hwnds[1]}:{pid}")
            assert result["same_HWND_set_permutation_does_not_destroy_radio"]

            # Rename the source label in the cache, without making a new
            # numeric HWND. Captions must stay mapped by HWND/PID.
            renamed=(
                GameWindow(hwnds[2],pid,"CHANGED THIRTY","TEST_OWNED","NOT_GAME.exe"),
                GameWindow(hwnds[0],pid,"CHANGED TEN","TEST_OWNED","NOT_GAME.exe"),
                GameWindow(hwnds[1],pid,"CHANGED TWENTY","TEST_OWNED","NOT_GAME.exe"))
            start._sync_tiles(renamed)
            root.update()
            result["same_radios_labels_follow_HWND_not_cache_index"]=(
                tuple(start._master_radio_buttons)==radios
                and [w.cget("text") for w in radios]==[
                    f"CHANGED TEN [HWND {hwnds[0]}]",
                    f"CHANGED TWENTY [HWND {hwnds[1]}]",
                    f"CHANGED THIRTY [HWND {hwnds[2]}]"])
            assert result["same_radios_labels_follow_HWND_not_cache_index"]

            def positions():
                return {w.hwnd:(
                    int(start._tile_items[(w.hwnd,pid)][0].grid_info()["row"]),
                    int(start._tile_items[(w.hwnd,pid)][0].grid_info()["column"]))
                    for w in rows}
            # Explicit user's 1x/3x choices affect only preview columns;
            # C17 manual HWND order and C05 master selection are separate.
            start.preview_grid_var.set("1x")
            assert start._set_manual_preview_grid()
            root.update()
            one=positions()
            result["real_Tk_grid_1x_one_column"]=(sorted(v[0] for v in one.values())==[0,1,2]
                                                    and all(v[1]==0 for v in one.values()))
            assert result["real_Tk_grid_1x_one_column"]
            start.preview_grid_var.set("3x")
            assert start._set_manual_preview_grid()
            root.update()
            three=positions()
            result["real_Tk_grid_3x_three_columns"]=(sorted(v[1] for v in three.values())==[0,1,2]
                                                      and all(v[0]==0 for v in three.values()))
            assert result["real_Tk_grid_3x_three_columns"]
            result["C05_master_unchanged_by_C09_grid"]=(
                start.master_selection.selected==(hwnds[1],pid)
                and tuple(start._master_radio_buttons)==radios)
            assert result["C05_master_unchanged_by_C09_grid"]

            # Manual C17 order change persists after full C15 DWM teardown
            # / rebuild, not just while an old preview tile is cached.
            assert start._move_preview_item(hwnds[2],pid,-1)
            expected=tuple(w.hwnd for w in start._active_windows)
            cache=WindowSnapshot(83,renamed,True)
            released_before=len(backend.released)
            first_tiles=tuple(start._tile_items.values())
            first_surface_hwnds=[x[2].winfo_id() for x in first_tiles]
            assert start.refresh_window_preview_list()
            root.update()
            start._refresh_dwm()
            root.update()
            result["C15_refresh_destroys_old_Tk_preview_tiles"]=all(
                not item[0].winfo_exists() for item in first_tiles)
            result["C15_refresh_releases_and_reregisters_real_DWM"]=(
                len(backend.released)-released_before==3
                and len(backend.registered)>=6
                and start._preview_controller.active_hwnds==tuple(
                    w.hwnd for w in start._active_windows))
            result["C17_manual_order_survives_C15_refresh"]=(
                tuple(w.hwnd for w in start._active_windows)==expected)
            result["C05_master_radios_stable_across_C15_full_refresh"]=(
                tuple(start._master_radio_buttons)==radios
                and start.master_selection.selected==(hwnds[1],pid))
            for k in ("C15_refresh_destroys_old_Tk_preview_tiles",
                      "C15_refresh_releases_and_reregisters_real_DWM",
                      "C17_manual_order_survives_C15_refresh",
                      "C05_master_radios_stable_across_C15_full_refresh"):
                assert result[k],k
            start.shutdown();start=None
            root.destroy();root=None
            result["normal_Tk_shutdown_after_DWM_rebuild"]=True
        result["status"]="PASS_NATIVE_S82_C05_C09_C15_REAL_TK_DWM_MASTER_RETAINED"
    except Exception as exc:
        result["status"]="FAIL_NATIVE_S82"
        result["error_type"]=type(exc).__name__
        result["error_text"]=str(exc)[:400]
        result["traceback"]=traceback.format_exc(limit=17)
    finally:
        if start is not None:
            try:start.shutdown()
            except Exception:pass
        if root is not None:
            try:root.destroy()
            except Exception:pass
        REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2),
                          encoding="utf-8")
        for k,v in result.items():
            if k!="traceback":
                print("S82_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if result["status"]=="PASS_NATIVE_S82_C05_C09_C15_REAL_TK_DWM_MASTER_RETAINED" else 1
if __name__=="__main__":
    raise SystemExit(run())
