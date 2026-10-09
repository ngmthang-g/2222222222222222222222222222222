"""S31 native Windows runner: offline ADB captured-text identity and S29 Win32.

No invocation of adb.exe or frida, no ADB server start, app/game process,
guest network requests, injection, entitlement or Proxy.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile
import time
import traceback

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s31"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"native_offline_adb_identity_evidence.json"


def run():
    out={"task":"S31","status":"NOT_RUN","real_adb_executed":False,
         "adb_server_started":False,"real_emulator":"NOT_RUN",
         "real_game":"NOT_RUN","signed_Info":"NOT_AVAILABLE",
         "Proxy_runtime":"EXCLUDED","game_launches":0,"product_exe":"NOT_BUILT"}
    try:
        if os.name != "nt":raise RuntimeError("Native Windows required")
        from adb_identity_evidence import (
            GuestIdentityHint,inspect_captured_adb_devices,
            identify_possible_serial_rebinds,
        )
        from running_count_evidence import NativeWin32ProcessBackend,find_named_process_pids
        from login_path import EXE_NAME,GameDirectoryResult
        from login_launch_preflight import check_open_game_preflight
        from permission_guard import PermissionSnapshot

        now=time.monotonic()
        sample=("List of devices attached\n"
                "127.0.0.1:5555\tdevice product:ld-model\n"
                "127.0.0.1:5557\tdevice product:ld-model\n"
                "emulator-5558\toffline\n")
        hints={
            "127.0.0.1:5555":GuestIdentityHint(
                android_id="CLONE_AID",hwid="CLONE_HWID",guest_ipv4="172.18.0.2",
                guest_game_pid=123),
            "127.0.0.1:5557":GuestIdentityHint(
                android_id="CLONE_AID",hwid="CLONE_HWID",guest_ipv4="172.18.0.3",
                guest_game_pid=123),
        }
        e=inspect_captured_adb_devices(sample,captured_at=now,hints_by_serial=hints)
        out["captured_transport_rows"]=len(e.transports)
        out["two_online_one_offline"]=(
            len(e.observed_online_serials)==2 and "offline" in e.unknown_states)
        out["clone_androidid_and_hwid_collision_detected"]=(
            e.duplicate_aids==("CLONE_AID",) and
            e.duplicate_hwids==("CLONE_HWID",))
        out["clone_ip_individually_resolves"]=(
            e.unique_serial_for("guest_ipv4","172.18.0.3",time.monotonic())
            =="127.0.0.1:5557")
        out["ambiguous_aid_cannot_choose_target"]=(
            e.unique_serial_for("android_id","CLONE_AID",time.monotonic())
            is None)
        out["guest_pid_not_account_total"]=(
            e.emulator_account_count is None and e.combined_running_count is None
            and not e.is_authoritative_account_total)

        duplicate=inspect_captured_adb_devices(
            "List of devices attached\nx device\nx device\n",captured_at=now)
        out["duplicate_transport_serial_rejected"]=(
            duplicate.status=="AMBIGUOUS_DUPLICATE_SERIAL"
            and not duplicate.observed_online_serials)
        out["stale_device_capture_rejected"]=(
            e.freshness(now+31)=="STALE_CAPTURE"
            and e.unique_serial_for("guest_ipv4","172.18.0.2",now+31) is None)

        # Native Toolhelp proof is distinct from synthetically captured ADB:
        # current Python PID is NOT a Windows emulator-account process.
        processes=NativeWin32ProcessBackend()
        python_pids=find_named_process_pids(processes,Path(sys.executable).name)
        out["genuine_native_windows_host_pid_observed"]=os.getpid() in python_pids
        out["no_windows_emulator_count_inferred"]=e.emulator_account_count is None
        with tempfile.TemporaryDirectory(prefix="S31_TEST_ONLY_") as td:
            root=Path(td);(root/EXE_NAME).write_bytes(b"S31 NOT A GAME")
            snap=PermissionSnapshot(
                has_verified_payload=True,permissions=frozenset({"login_tab"}),
                plan_status="TEST_ONLY",max_windows=3)
            denial=check_open_game_preflight(snap,GameDirectoryResult(root,""),
                                              running_windows=e.combined_running_count)
            out["partial_count_still_blocks_login"]=(
                not denial.allowed and denial.reason=="RUNNING_WINDOW_COUNT_UNKNOWN")
        assert all(out[k] for k in (
            "two_online_one_offline","clone_androidid_and_hwid_collision_detected",
            "clone_ip_individually_resolves","ambiguous_aid_cannot_choose_target",
            "guest_pid_not_account_total","duplicate_transport_serial_rejected",
            "stale_device_capture_rejected","genuine_native_windows_host_pid_observed",
            "no_windows_emulator_count_inferred","partial_count_still_blocks_login",
        ))
        out["status"]="PASS_NATIVE_S31_OFFLINE_ADB_CLONE_IDENTITY_NO_COUNT_GRANT"
    except Exception as exc:
        out["status"]="FAIL_NATIVE_S31"
        out["error"]=type(exc).__name__+": "+str(exc)
        out["traceback"]=traceback.format_exc(limit=14)
    finally:
        REPORT.write_text(json.dumps(out,ensure_ascii=False,indent=2),
                          encoding="utf-8")
        for k,v in out.items():
            if k!="traceback":
                print("S31_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return int(out["status"]!="PASS_NATIVE_S31_OFFLINE_ADB_CLONE_IDENTITY_NO_COUNT_GRANT")


if __name__=="__main__":
    raise SystemExit(run())
