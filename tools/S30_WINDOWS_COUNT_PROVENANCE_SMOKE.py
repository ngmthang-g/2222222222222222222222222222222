"""S30 Windows native provenance: actual Toolhelp and HWND snapshots, no emu guess.

Two Toolhelp snapshots around native S08 EnumWindows. Test-owned Tk windows
are genuine python.exe and NEVER masquerade as original game processes.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile
import time
import traceback

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/"src"))
OUT=BASE/"artifacts"/"s30"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"native_non_authoritative_process_provenance.json"


def run():
    evidence={
        "task":"S30","status":"NOT_RUN","real_game":"NOT_RUN",
        "signed_Info":"NOT_AVAILABLE","emulator_exe_count":"UNKNOWN",
        "original_emulator_image_rules":"NOT_PROVEN",
        "game_launches":0,"proxy_runtime":"EXCLUDED","product_exe":"NOT_BUILT",
    }
    root=None
    try:
        if os.name!="nt":raise RuntimeError("Requires genuine Windows")
        import tkinter as tk
        from login_path import EXE_NAME,GameDirectoryResult
        from login_launch_preflight import check_open_game_preflight
        from permission_guard import PermissionSnapshot
        from running_count_evidence import (
            NativeWin32ProcessBackend, find_named_process_pids,
        )
        from running_count_provenance import observe_running_provenance
        from start_windows import NativeWin32Backend
        import ctypes
        from ctypes import wintypes

        root=tk.Tk()
        root.withdraw()
        w=tk.Toplevel(root)
        w.title("Thần Long — S30 TEST-OWNED python.exe HWND")
        w.geometry("230x130+40+40")
        root.update()
        backend=NativeWin32Backend()
        u32=ctypes.WinDLL("user32",use_last_error=True)
        ancestor=u32.GetAncestor
        ancestor.argtypes=[wintypes.HWND,wintypes.UINT]
        ancestor.restype=wintypes.HWND
        hwnd=int(ancestor(int(w.winfo_id()),2))
        evidence["real_test_hwnd_visible_same_pid"]=(
            backend.is_window(hwnd) and backend.is_visible(hwnd)
            and backend.process_id(hwnd)==os.getpid())
        assert evidence["real_test_hwnd_visible_same_pid"]

        processes=NativeWin32ProcessBackend()
        own_image=Path(sys.executable).name
        matching=find_named_process_pids(processes,own_image)
        evidence["native_toolhelp_host_pid_present"]=os.getpid() in matching
        assert evidence["native_toolhelp_host_pid_present"]

        observation=observe_running_provenance(
            processes=processes,windows=backend)
        evidence["two_actual_process_snapshots"]=(
            observation.process_pids_before is not None and
            observation.process_pids_after is not None)
        evidence["real_native_hwnd_scan"]=observation.visible_windows is not None
        evidence["test_titled_python_not_a_game"]=(
            not any(item.hwnd==hwnd for item in observation.visible_windows or ()))
        evidence["no_authoritative_total"]=(
            observation.emulator_count is None and
            observation.combined_running_count is None and
            not observation.is_authoritative_account_total)
        freshness=observation.diagnostic_freshness(time.monotonic())
        evidence["diagnostic_freshness"]=freshness
        evidence["fresh_or_transient_observation"]=freshness in (
            "FRESH_DIAGNOSTIC_ONLY","INCOMPLETE_OR_CHANGING")
        assert all(evidence[k] for k in (
            "two_actual_process_snapshots","real_native_hwnd_scan",
            "test_titled_python_not_a_game","no_authoritative_total",
            "fresh_or_transient_observation"))

        old=observation.diagnostic_freshness(
            observation.completed_at+3.0)
        evidence["stale_after_3_seconds"]=(
            old in ("STALE_DIAGNOSTIC","INCOMPLETE_OR_CHANGING"))
        assert evidence["stale_after_3_seconds"]
        with tempfile.TemporaryDirectory(prefix="S30_TEST_ONLY_") as td:
            d=Path(td);(d/EXE_NAME).write_bytes(b"TEST NOT GAME")
            verified_test_claims=PermissionSnapshot(
                has_verified_payload=True,
                permissions=frozenset({"login_tab"}),
                plan_status="TEST_ONLY",max_windows=3)
            result=check_open_game_preflight(
                verified_test_claims,GameDirectoryResult(d,""),
                running_windows=observation.combined_running_count)
            evidence["partial_total_refused_for_launch"]=(
                not result.allowed and
                result.reason=="RUNNING_WINDOW_COUNT_UNKNOWN")
            assert evidence["partial_total_refused_for_launch"]

        w.destroy();root.destroy();root=None
        evidence["status"]="PASS_NATIVE_S30_DOUBLE_PROCESS_SCAN_STALE_SAFE_GATE"
    except Exception as exc:
        evidence["status"]="FAIL_NATIVE_S30"
        evidence["error"]=type(exc).__name__+": "+str(exc)
        evidence["traceback"]=traceback.format_exc(limit=14)
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        REPORT.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),
                          encoding="utf-8")
        for k,v in evidence.items():
            if k!="traceback":
                print("S30_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return int(evidence["status"]!="PASS_NATIVE_S30_DOUBLE_PROCESS_SCAN_STALE_SAFE_GATE")


if __name__=="__main__":
    raise SystemExit(run())
