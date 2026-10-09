"""S34 Windows fixture: strict offline intake only, real Toolhelp self PID.

Synthetic captured ADB rows only; NO real ADB/LDPlayer/Frida/game run,
daemon start, Proxy runtime, process injection or account-limit grant.
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
OUT=ROOT/"artifacts"/"s34"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"strict_offline_adb_intake_native.json"


def run():
    evidence={"task":"S34","status":"NOT_RUN","real_adb_invoked":False,
              "adb_daemon_started":False,"real_ldplayer":"NOT_RUN",
              "game_process_launched":False,"signed_Info":"NOT_AVAILABLE",
              "product_exe":"NOT_BUILT","proxy_runtime":"EXCLUDED"}
    try:
        if os.name!="nt":
            raise RuntimeError("Actual Windows required")
        from adb_identity_evidence import GuestIdentityHint
        from adb_hint_provenance import HintTimes
        from adb_offline_intake import CapturedAdbFrame, OfflineAdbIntake
        from running_count_evidence import NativeWin32ProcessBackend,find_named_process_pids
        from login_path import EXE_NAME,GameDirectoryResult
        from login_launch_preflight import check_open_game_preflight
        from permission_guard import PermissionSnapshot

        t=time.monotonic()
        head="List of devices attached\n"
        def f(rows,at,hints=None,times=None):
            return CapturedAdbFrame(head+rows,at,hints,times)
        facade=OfflineAdbIntake()
        init=facade.ingest(f("a device\nb device\n",t),now=t+4)
        h={"a":GuestIdentityHint(android_id="CLONE",guest_ipv4="10.0.0.2"),
           "b":GuestIdentityHint(android_id="CLONE",guest_ipv4="10.0.0.3")}
        times={"a":HintTimes(android_id_at=t+1,guest_ipv4_at=t+1),
               "b":HintTimes(android_id_at=t+1,guest_ipv4_at=t+1)}
        repeat=facade.ingest(f("a device\nb device\n",t+2,h,times),
                             now=t+4)
        evidence["ordered_s31_s32_s33_receipts"]=(
            init.epoch_status=="BASELINE" and
            repeat.epoch_status=="CONSISTENT_HISTORY")
        evidence["clone_android_id_not_unique"]=(
            facade.lookup("android_id","CLONE",now=t+4).serial is None)
        evidence["unique_ip_diagnostic_no_control"]=(
            facade.lookup("guest_ipv4","10.0.0.3",now=t+4).code
            =="UNIQUE_DIAGNOSTIC_ONLY"
            and not facade.lookup("guest_ipv4","10.0.0.3",now=t+4).may_control_device)
        facade.ingest(f("a offline\nb device\n",t+5),now=t+8)
        rejoin=facade.ingest(f("a device\nb device\n",t+7,h,times),now=t+8)
        evidence["offline_reconnect_epoch_invalidates_stale_ip"]=(
            rejoin.status=="ACCEPTED_DIAGNOSTIC_ONLY"
            and facade.lookup("guest_ipv4","10.0.0.3",now=t+8).serial is None)
        missing=facade.ingest(CapturedAdbFrame(None,t+9),now=t+10)
        evidence["lost_capture_clears_epoch"]=(
            missing.detail=="S31_NO_CAPTURE" and
            facade.lookup("guest_ipv4","10.0.0.3",now=t+10).serial is None)
        replay=facade.replay((
            f("a device\n",t+11),
            f("a device\n",t+11)),now=t+12)
        evidence["replayed_timestamp_rejected"]=(
            replay[-1].detail=="S33_NON_INCREASING_CAPTURE_TIME")

        evidence["real_windows_toolhelp_self_python_pid"]=(
            os.getpid() in find_named_process_pids(
                NativeWin32ProcessBackend(),Path(sys.executable).name))
        evidence["emulator_count_still_unverified"]=(
            missing.combined_running_count is None
            and not missing.is_authoritative_account_total)
        with tempfile.TemporaryDirectory(prefix="S34_TEST_ONLY_") as td:
            game=Path(td);(game/EXE_NAME).write_bytes(b"S34 NOT GAME")
            claims=PermissionSnapshot(
                has_verified_payload=True,
                permissions=frozenset({"login_tab"}),
                plan_status="TEST_ONLY",max_windows=5)
            denied=check_open_game_preflight(
                claims,GameDirectoryResult(game,""),
                running_windows=missing.combined_running_count)
            evidence["s26_unknown_account_count_blocked"]=(
                not denied.allowed and denied.reason=="RUNNING_WINDOW_COUNT_UNKNOWN")
        assert all(evidence[k] for k in (
            "ordered_s31_s32_s33_receipts","clone_android_id_not_unique",
            "unique_ip_diagnostic_no_control",
            "offline_reconnect_epoch_invalidates_stale_ip",
            "lost_capture_clears_epoch","replayed_timestamp_rejected",
            "real_windows_toolhelp_self_python_pid",
            "emulator_count_still_unverified","s26_unknown_account_count_blocked"))
        evidence["status"]="PASS_NATIVE_S34_STRICT_OFFLINE_S31_S32_S33_INTAKE_NO_GRANT"
    except Exception as exc:
        evidence["status"]="FAIL_NATIVE_S34"
        evidence["error"]=type(exc).__name__+": "+str(exc)
        evidence["traceback"]=traceback.format_exc(limit=14)
    finally:
        REPORT.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),
                          encoding="utf-8")
        for key,val in evidence.items():
            if key!="traceback":
                print("S34_"+key.upper()+"="+json.dumps(val,ensure_ascii=True))
    return int(evidence["status"]!="PASS_NATIVE_S34_STRICT_OFFLINE_S31_S32_S33_INTAKE_NO_GRANT")


if __name__=="__main__":
    raise SystemExit(run())
