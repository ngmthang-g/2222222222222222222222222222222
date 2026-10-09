"""S26 native Windows F05 PID-HWND discovery + S25 EXE path preflight.

Uses live Win32 EnumWindows, IsWindowVisible, GetClassNameW, PID and a
150ms-bounded title read via existing S08 backend. Test-owned Tk windows
only. It launches NO game/EXE and does no DLL work.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import sys
import tempfile
import traceback

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/"src"))
OUTPUT=BASE/"artifacts"/"s26"
OUTPUT.mkdir(parents=True,exist_ok=True)
REPORT=OUTPUT/"native_f05_preflight_pid.json"


def run():
    data={"task":"S26","status":"NOT_RUN","real_game":"NOT_RUN",
          "signed_Info":"NOT_AVAILABLE","launch_calls":0,
          "injected_processes":0,"account_logins":0,
          "Proxy_runtime":"EXCLUDED","product_exe":"NOT_BUILT",
          "Windows_test_only_windows":True}
    root=None
    try:
        if os.name!="nt":raise RuntimeError("Windows native test required")
        import tkinter as tk
        import ctypes
        from ctypes import wintypes
        from login_path import EXE_NAME,resolve_game_dir,GameDirectoryStore
        from login_launch_preflight import (check_open_game_preflight,
                                           find_main_window_by_pid)
        from permission_guard import PermissionGuard,VerifiedClaims
        from start_windows import NativeWin32Backend, TITLE_TIMEOUT_MS

        with tempfile.TemporaryDirectory(prefix="S26_TEST_ONLY_") as td:
            base=Path(td)
            directory=base/"Installer"/"Game"
            directory.mkdir(parents=True)
            (directory/EXE_NAME).write_bytes(b"S26 TEST OWNED PLACEHOLDER - NOT EXE")
            cfg=base/"AppData"/"TLMTool"/"settings.ini"
            store=GameDirectoryStore(cfg)
            store.save(resolve_game_dir(base/"Installer"))
            game=store.load()
            guard=PermissionGuard()
            denied=check_open_game_preflight(
                guard.snapshot,game,running_windows=0)
            data["unverified_denied"]=not denied.allowed and denied.executable is None
            assert data["unverified_denied"]
            assert guard.receive_token("S26_TEST_ONLY",lambda _:VerifiedClaims(
                permissions=frozenset({"login_tab","info_tab"}),
                plan_status="TEST_ONLY",max_windows=2))
            snap=guard.snapshot
            pre=check_open_game_preflight(snap,game,running_windows=1)
            data["extra_one_last_slot_allowed"]=(
                pre.allowed and pre.executable==directory/EXE_NAME and
                pre.max_windows==2)
            assert data["extra_one_last_slot_allowed"]
            blocked=check_open_game_preflight(snap,game,running_windows=2)
            data["extra_one_over_limit_denied"]=(
                not blocked.allowed and blocked.reason=="ACCOUNT_LIMIT_EXTRA_ONE")
            assert data["extra_one_over_limit_denied"]
            guard.clear()
            data["revoked_license_denied"]=not check_open_game_preflight(
                guard.snapshot,game,running_windows=1).allowed
            assert data["revoked_license_denied"]

            root=tk.Tk()
            root.withdraw()
            ordinary=tk.Toplevel(root)
            ordinary.title("S26 TEST OWNED ordinary view")
            ordinary.geometry("300x150+30+30")
            preferred=tk.Toplevel(root)
            preferred.title("Thần Long — S26 TEST OWNED title only")
            preferred.geometry("300x150+350+30")
            root.update_idletasks()
            root.update()

            native=NativeWin32Backend()
            u32=ctypes.WinDLL("user32",use_last_error=True)
            get_ancestor=u32.GetAncestor
            get_ancestor.argtypes=[wintypes.HWND,wintypes.UINT]
            get_ancestor.restype=wintypes.HWND
            def top(widget):
                return int(get_ancestor(int(widget.winfo_id()),2))
            h_ordinary,h_preferred=top(ordinary),top(preferred)
            pid=os.getpid()
            data["hwnd_native_real"]=(
                h_ordinary>0 and h_preferred>0 and h_ordinary!=h_preferred and
                native.is_window(h_ordinary) and native.is_window(h_preferred))
            data["native_pid_owned"]=(
                native.process_id(h_ordinary)==pid and
                native.process_id(h_preferred)==pid and
                native.is_visible(h_ordinary) and
                native.is_visible(h_preferred))
            assert data["hwnd_native_real"] and data["native_pid_owned"]

            # Exclude unrelated CI runner windows; this wrapper only narrows
            # the enumeration to exactly two real test-owned HWNDs.
            class NativeTestSubset:
                def enumerate_top_level(self):
                    existing=set(native.enumerate_top_level())
                    return tuple(h for h in (h_ordinary,h_preferred) if h in existing)
                def is_window(self,h):return native.is_window(h)
                def is_visible(self,h):return native.is_visible(h)
                def process_id(self,h):return native.process_id(h)
                def window_class(self,h):return native.window_class(h)
                def title_with_timeout(self,h,t):
                    assert t==TITLE_TIMEOUT_MS
                    return native.title_with_timeout(h,t)
            scope=NativeTestSubset()
            data["actual_titles"]=[
                native.title_with_timeout(h_ordinary,TITLE_TIMEOUT_MS),
                native.title_with_timeout(h_preferred,TITLE_TIMEOUT_MS)]
            data["actual_classes"]=[
                native.window_class(h_ordinary),native.window_class(h_preferred)]
            assert "Thần Long" in data["actual_titles"][1]
            data["pid_prefers_titled_hwnd"]=(
                find_main_window_by_pid(pid,scope)==h_preferred)
            data["foreign_pid_does_not_use_title"]=(
                find_main_window_by_pid(pid+1,scope) is None)
            assert data["pid_prefers_titled_hwnd"] and data["foreign_pid_does_not_use_title"]

            preferred.destroy()
            root.update_idletasks()
            root.update()
            data["closed_hwnd_falls_back_to_owned"]=(
                not native.is_window(h_preferred) and
                find_main_window_by_pid(pid,scope)==h_ordinary)
            assert data["closed_hwnd_falls_back_to_owned"]
            ordinary.destroy()
            root.update_idletasks()
            root.update()
            data["none_after_all_windows_closed"]=(
                find_main_window_by_pid(pid,scope) is None)
            assert data["none_after_all_windows_closed"]
            root.destroy()
            root=None
            data["status"]="PASS_NATIVE_S26_F05_EXTRA_ONE_PID_HWND_FALLBACK_REUSE_GUARD"
    except Exception as exc:
        data["status"]="FAIL_NATIVE_S26"
        data["error"]=type(exc).__name__+": "+str(exc)
        data["traceback"]=traceback.format_exc(limit=14)
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        REPORT.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
        for key,val in data.items():
            if key!="traceback":
                print("S26_"+key.upper()+"="+json.dumps(val,ensure_ascii=True))
    return int(data["status"]!="PASS_NATIVE_S26_F05_EXTRA_ONE_PID_HWND_FALLBACK_REUSE_GUARD")


if __name__=="__main__":
    raise SystemExit(run())
