"""S29 native Windows: real read-only Toolhelp process + HWND counts.

Uses current TEST runner python.exe PID and TEST-OWNED Tk top-level windows.
Never relabels python.exe as a game, never grants account limits, no injection.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import traceback

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/"src"))
OUT=BASE/"artifacts"/"s29"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"native_partial_process_window_evidence.json"


def run():
    evidence={"task":"S29","status":"NOT_RUN","real_game":"NOT_RUN",
              "signed_Info":"NOT_AVAILABLE","real_game_launches":0,
              "process_spawned":0,"injects":0,"proxy_runtime":"EXCLUDED",
              "product_exe":"NOT_BUILT","emulator_count":"UNKNOWN"}
    root=None
    try:
        if os.name!="nt":raise RuntimeError("Windows native test required")
        import ctypes
        from ctypes import wintypes
        import tkinter as tk
        from login_path import EXE_NAME,GameDirectoryResult
        from login_launch_preflight import check_open_game_preflight
        from permission_guard import PermissionGuard,VerifiedClaims
        from running_count_evidence import (
            NativeWin32ProcessBackend,find_named_process_pids,
            observe_running_game_evidence,visible_hwnds_for_pid,
        )
        from start_windows import NativeWin32Backend

        processes=NativeWin32ProcessBackend()
        windows=NativeWin32Backend()
        current_pid=os.getpid()
        real_image_name=Path(sys.executable).name
        native_python_pids=find_named_process_pids(processes,real_image_name)
        evidence["native_toolhelp_own_python_pid_found"]=(
            current_pid in native_python_pids)
        evidence["native_toolhelp_own_python_image"]=real_image_name
        assert evidence["native_toolhelp_own_python_pid_found"]

        root=tk.Tk()
        root.withdraw()
        first=tk.Toplevel(root)
        first.title("Thần Long — S29 TEST ONLY python.exe window")
        first.geometry("260x130+50+50")
        second=tk.Toplevel(root)
        second.title("S29 another TEST OWNED HWND")
        second.geometry("260x130+400+50")
        root.update_idletasks()
        root.update()
        u32=ctypes.WinDLL("user32",use_last_error=True)
        ancestor=u32.GetAncestor
        ancestor.argtypes=[wintypes.HWND,wintypes.UINT]
        ancestor.restype=wintypes.HWND
        hwnds=(int(ancestor(int(first.winfo_id()),2)),
               int(ancestor(int(second.winfo_id()),2)))
        evidence["real_two_hwnds_same_pid"]=(
            len(set(hwnds))==2 and
            all(windows.is_window(h) and windows.is_visible(h) and
                windows.process_id(h)==current_pid for h in hwnds))
        assert evidence["real_two_hwnds_same_pid"]

        # Real native Win32 snapshot: NEVER claim python.exe is Thần Long.
        owned=visible_hwnds_for_pid(windows,current_pid)
        evidence["native_pid_scoped_hwnds_both_visible"]=set(hwnds)<=set(owned)
        assert evidence["native_pid_scoped_hwnds_both_visible"]
        snap=observe_running_game_evidence(processes=processes,windows=windows)
        evidence["process_scan_valid"]=snap.process_scan_valid
        evidence["window_scan_valid"]=snap.window_scan_valid
        evidence["visible_game_hwnd_count"]=snap.visible_hwnd_count
        evidence["game_exe_name_count"]=snap.game_process_count
        evidence["test_python_hwnds_never_mislabeled_game"]=(
            not any(w.hwnd in hwnds for w in snap.game_windows))
        evidence["game_account_combined_count_unknown"]=(
            snap.combined_running_count is None and
            snap.emulator_process_count is None and
            not snap.is_authoritative_account_total)
        assert (evidence["process_scan_valid"] and evidence["window_scan_valid"] and
                evidence["test_python_hwnds_never_mislabeled_game"] and
                evidence["game_account_combined_count_unknown"])

        guard=PermissionGuard()
        assert guard.receive_token("S29_TEST_ONLY",lambda _:VerifiedClaims(
            permissions=frozenset({"login_tab","info_tab"}),
            plan_status="TEST_ONLY",max_windows=2))
        # The E04 incomplete count CANNOT be converted into a guessed zero
        # even though a test-only snapshot happens to be available.
        with __import__("tempfile").TemporaryDirectory(prefix="S29_TEST_ONLY_") as td:
            d=Path(td);(d/EXE_NAME).write_bytes(b"NOT A REAL GAME EXE")
            denied=check_open_game_preflight(
                guard.snapshot,GameDirectoryResult(d,""),
                running_windows=snap.combined_running_count)
            evidence["incomplete_count_blocks_S26_launch_preflight"]=(
                not denied.allowed and denied.reason=="RUNNING_WINDOW_COUNT_UNKNOWN")
            assert evidence["incomplete_count_blocks_S26_launch_preflight"]
        second.destroy()
        root.update()
        remaining=visible_hwnds_for_pid(windows,current_pid)
        evidence["destroyed_test_hwnd_removed"]=(
            not windows.is_window(hwnds[1]) and hwnds[1] not in remaining and
            hwnds[0] in remaining)
        assert evidence["destroyed_test_hwnd_removed"]
        first.destroy()
        root.destroy();root=None
        evidence["status"]="PASS_NATIVE_S29_TOOLHELP_PROCESS_VS_VISIBLE_HWND_INCOMPLETE_GATE"
    except Exception as exc:
        evidence["status"]="FAIL_NATIVE_S29"
        evidence["error"]=type(exc).__name__+": "+str(exc)
        evidence["traceback"]=traceback.format_exc(limit=14)
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        REPORT.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),
                          encoding="utf-8")
        for k,v in evidence.items():
            if k!="traceback":print("S29_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return int(evidence["status"]!="PASS_NATIVE_S29_TOOLHELP_PROCESS_VS_VISIBLE_HWND_INCOMPLETE_GATE")


if __name__=="__main__":
    raise SystemExit(run())
