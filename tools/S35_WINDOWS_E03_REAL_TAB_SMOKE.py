"""S35 native Windows: real E03 Notebook + existing Login chooser and Start.

All test-owned: a dummy FILE named game EXE for path resolution, a native
Win32 Tk top-level HWND for read-only discovery, and a TEST ONLY decoded
permission snapshot. No real game/Info server/Proxy/injection/product EXE.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile
import traceback

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s35"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"e03_native_available_start_login_integration.json"

def run():
    report={
        "task":"S35","status":"NOT_RUN",
        "real_game":"NOT_RUN","real_info_server":"NOT_AVAILABLE",
        "signed_info":"NOT_AVAILABLE","test_claims_only":True,
        "game_launches":0,"game_logins":0,"proxy_runtime":"EXCLUDED",
        "product_exe":"NOT_BUILT",
        "pixel_parity":"NOT_VERIFIED",
    }
    root=None
    source_hwnd=None
    try:
        if os.name!="nt":
            raise RuntimeError("S35 real Windows Tk required")
        import tkinter as tk
        from tkinter import ttk
        from source_backed_tab_builders import source_backed_tab_builders
        from shell import TLMMainApp
        from info_tab import TLMInfoTab
        from permission_guard import PermissionGuard,VerifiedClaims
        from start_tab import TLMStartTab
        from login_tab import TLMLoginPathTab
        from login_path import EXE_NAME,GameDirectoryStore
        from start_windows import NativeWin32Backend
        from start_polling import StartWindowProducer

        with tempfile.TemporaryDirectory(prefix="S35_TEST_ONLY_") as td:
            base=Path(td)
            game=base/"ThanLong TEST"/"Game"
            game.mkdir(parents=True)
            (game/EXE_NAME).write_bytes(b"TEST_PLACEHOLDER_NOT_GAME_EXE")
            cfg=base/"AppData"/"TLMTool"/"settings.ini"
            cfg.parent.mkdir(parents=True)
            cfg.write_text("[Settings]\ngrid_rows = 4\n[Unrelated]\nkeep = yes\n",
                           encoding="utf-8")
            selected=[]; factories=[]
            def chooser(**kwargs):
                selected.append(kwargs["title"])
                return str(game.parent)
            root=tk.Tk()
            root.title("S35 TEST-only notebook shell")
            root.geometry("680x820+0+0")
            other=tk.Toplevel(root)
            other.title("S35 OWNED non-game Win32 HWND")
            other.geometry("180x130+700+50")
            root.update()
            native=NativeWin32Backend()
            import ctypes
            from ctypes import wintypes
            u32=ctypes.WinDLL("user32",use_last_error=True)
            ancestor=u32.GetAncestor
            ancestor.argtypes=[wintypes.HWND,wintypes.UINT]
            ancestor.restype=wintypes.HWND
            source_hwnd=int(ancestor(int(other.winfo_id()),2))
            report["actual_non_game_hwnd_in_native_enumeration"]=(
                native.is_window(source_hwnd)
                and native.process_id(source_hwnd)==os.getpid()
                and source_hwnd in native.enumerate_top_level())
            assert report["actual_non_game_hwnd_in_native_enumeration"]

            def info_factory(frame):
                instance=TLMInfoTab(frame)
                factories.append(("info",instance))
                return instance
            # Start producer always invokes REAL Windows native HWND discovery,
            # which correctly ignores the python.exe test-owned window.
            producer=StartWindowProducer(NativeWin32Backend)
            builders=source_backed_tab_builders(
                info_factory, settings_file=cfg, start_producer=producer,
                choose_directory=chooser,
                show_error=lambda title,text:selected.append("ERROR:"+title))
            app=TLMMainApp(root,builders)
            root.update()
            report["info_only_before_verified_claims"]=(
                app.lifecycle.visible=={"info_tab"}
                and set(app.lifecycle._instances)=={"info_tab"}
                and all(app.notebook.tab(app._tab_frames[k],"state")=="hidden"
                        for k in ("login_tab","start_tab")))
            assert report["info_only_before_verified_claims"]

            guard=PermissionGuard()
            assert guard.receive_token("S35_TEST_ONLY",lambda _:
                VerifiedClaims(permissions=frozenset({
                    "info_tab","start_tab","login_tab"}),
                    plan_status="TEST_ONLY",max_windows=2))
            app.apply_info_snapshot(guard.snapshot)
            root.update()
            report["verified_test_claims_show_real_tabs"]=(
                {"info_tab","start_tab","login_tab"}==app.lifecycle.visible)
            report["still_lazy_no_early_login_or_start"]=(
                set(app.lifecycle._instances)=={"info_tab"})
            assert report["verified_test_claims_show_real_tabs"]
            assert report["still_lazy_no_early_login_or_start"]

            app.notebook.select(app._tab_frames["login_tab"])
            root.update()
            login=app.lifecycle._instances["login_tab"]
            report["actual_login_tab_and_tk_button"]=(
                isinstance(login,TLMLoginPathTab)
                and isinstance(login.btn_choose,tk.Button)
                and login.btn_choose.cget("text")=="Chọn thư mục game")
            assert report["actual_login_tab_and_tk_button"]
            login.btn_choose.invoke()  # actual native Tk button command
            report["native_button_resolves_and_persists_selected_game_dir"]=(
                GameDirectoryStore(cfg).load().directory==game
                and login.get_exe_path()==game/EXE_NAME)
            report["original_game_file_name_exact_two_spaces"]=EXE_NAME=="Thần Long  Mobile.exe"
            assert report["native_button_resolves_and_persists_selected_game_dir"]
            assert report["original_game_file_name_exact_two_spaces"]

            app.notebook.select(app._tab_frames["start_tab"])
            root.update()
            start=app.lifecycle._instances["start_tab"]
            report["actual_start_tab_and_native_background_producer"]=(
                isinstance(start,TLMStartTab)
                and start.poller.producer is producer
                and start.poller.active and producer.active)
            # No source title may be interpreted as a genuine game PID.
            snap=producer.read_snapshot()
            report["no_test_python_window_mislabeled_as_game"]=(
                not any(w.hwnd==source_hwnd for w in snap.windows))
            assert report["actual_start_tab_and_native_background_producer"]
            assert report["no_test_python_window_mislabeled_as_game"]

            guard.clear()
            app.apply_info_snapshot(guard.snapshot)
            root.update()
            report["revoke_falls_back_info_and_stops_start"]=(
                app.lifecycle.current=="info_tab"
                and app.lifecycle.visible=={"info_tab"}
                and not start.poller.active
                and not producer.active
                and app.notebook.tab(app._tab_frames["start_tab"],"state")=="hidden"
                and app.notebook.tab(app._tab_frames["login_tab"],"state")=="hidden")
            assert report["revoke_falls_back_info_and_stops_start"]
            report["existing_grid_config_untouched"]=(
                "grid_rows = 4" in cfg.read_text(encoding="utf-8")
                and "keep = yes" in cfg.read_text(encoding="utf-8"))
            assert report["existing_grid_config_untouched"]
            app.shutdown()
            root.destroy()
            root=None
            report["real_tk_cleanup"]=app._closed and start._closed and login._closed
            assert report["real_tk_cleanup"]
            report["status"]="PASS_NATIVE_S35_E03_SOURCE_BACKED_START_LOGIN_LAZY_AUTH"
    except Exception as exc:
        report["status"]="FAIL_NATIVE_S35"
        report["error"]=type(exc).__name__+": "+str(exc)
        report["traceback"]=traceback.format_exc(limit=18)
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),
                          encoding="utf-8")
        for k,v in report.items():
            if k!="traceback":
                print("S35_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return int(report["status"]!="PASS_NATIVE_S35_E03_SOURCE_BACKED_START_LOGIN_LAZY_AUTH")

if __name__=="__main__":
    raise SystemExit(run())
