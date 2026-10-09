"""S33: test-owned offline epoch transitions + genuine Windows host PID.

NO adb.exe execution, ADB server, LDPlayer/Frida/game, Proxy, injected
binary or actual entitlement. Evidence is offline fixtures only.
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
OUT=ROOT/"artifacts"/"s33"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"native_offline_adb_connection_epoch_evidence.json"


def run():
    result={"task":"S33","status":"NOT_RUN","actual_adb_invoked":False,
            "adb_server_started":False,"real_ldplayer":"NOT_RUN",
            "real_game":"NOT_RUN","signed_Info":"NOT_AVAILABLE",
            "product_exe":"NOT_BUILT","proxy_runtime":"EXCLUDED"}
    try:
        if os.name!="nt":
            raise RuntimeError("Native Windows required")
        from adb_identity_evidence import GuestIdentityHint,inspect_captured_adb_devices
        from adb_hint_provenance import HintTimes,with_hint_times
        from adb_serial_epochs import advance_serial_epochs
        from running_count_evidence import NativeWin32ProcessBackend,find_named_process_pids
        from login_path import EXE_NAME,GameDirectoryResult
        from login_launch_preflight import check_open_game_preflight
        from permission_guard import PermissionSnapshot

        now=time.monotonic()
        H="List of devices attached\n"
        def snap(rows, at, *, hints=None, times=None):
            return with_hint_times(inspect_captured_adb_devices(
                H+rows,captured_at=at,hints_by_serial=hints),
                {} if times is None else times)
        first=advance_serial_epochs(None,snap("127.0.0.1:5555 device\n",now))
        before=advance_serial_epochs(first,snap(
            "127.0.0.1:5555 device\n",now+1,
            hints={"127.0.0.1:5555":GuestIdentityHint(android_id="AID")},
            times={"127.0.0.1:5555":HintTimes(android_id_at=now+.5)}))
        result["fresh_second_capture_hint"]=before.assess(
            "127.0.0.1:5555","android_id",now+2).is_fresh_diagnostic
        offline=advance_serial_epochs(before,snap(
            "127.0.0.1:5555 offline\n",now+3))
        reconnect=advance_serial_epochs(offline,snap(
            "127.0.0.1:5555 device\n",now+4,
            hints={"127.0.0.1:5555":GuestIdentityHint(android_id="AID")},
            times={"127.0.0.1:5555":HintTimes(android_id_at=now+.5)}))
        result["offline_reconnect_invalidates_old_aid"]=(
            reconnect.assess("127.0.0.1:5555","android_id",now+5).code
            == "HINT_NOT_AFTER_EPOCH"
            and reconnect.generation_by_serial["127.0.0.1:5555"]==2)
        reboot=advance_serial_epochs(before,snap(
            "127.0.0.1:5555 device\n",now+3,
            hints={"127.0.0.1:5555":GuestIdentityHint(android_id="AID")},
            times={"127.0.0.1:5555":HintTimes(android_id_at=now+.5)}),
            observed_reboots=("127.0.0.1:5555",))
        result["observed_reboot_invalidates_same_serial"]=(
            reboot.assess("127.0.0.1:5555","android_id",now+4).code
            == "HINT_NOT_AFTER_EPOCH")
        result["same_aid_never_implies_rebind"]=(
            reconnect.unique_serial_for("android_id","AID",now+5) is None)
        result["epoch_is_not_authoritative_account_count"]=(
            reconnect.combined_running_count is None
            and not reconnect.is_authoritative_account_total)
        result["native_windows_test_python_pid_observed"]=(
            os.getpid() in find_named_process_pids(
                NativeWin32ProcessBackend(),Path(sys.executable).name))
        with tempfile.TemporaryDirectory(prefix="S33_TEST_ONLY_") as td:
            d=Path(td);(d/EXE_NAME).write_bytes(b"S33 NOT AN EXE")
            perm=PermissionSnapshot(has_verified_payload=True,
                permissions=frozenset({"login_tab"}),
                max_windows=3,plan_status="TEST_ONLY")
            denial=check_open_game_preflight(perm,GameDirectoryResult(d,""),
                                              running_windows=reconnect.combined_running_count)
            result["s26_rejects_unverified_emulator_count"]=(
                not denial.allowed and denial.reason=="RUNNING_WINDOW_COUNT_UNKNOWN")
        assert all(result[k] for k in (
            "fresh_second_capture_hint","offline_reconnect_invalidates_old_aid",
            "observed_reboot_invalidates_same_serial","same_aid_never_implies_rebind",
            "epoch_is_not_authoritative_account_count",
            "native_windows_test_python_pid_observed",
            "s26_rejects_unverified_emulator_count"))
        result["status"]="PASS_NATIVE_S33_OFFLINE_EPOCH_RECONNECT_REBOOT_NO_GRANT"
    except Exception as exc:
        result["status"]="FAIL_NATIVE_S33"
        result["error"]=type(exc).__name__+": "+str(exc)
        result["traceback"]=traceback.format_exc(limit=14)
    finally:
        REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2),
                          encoding="utf-8")
        for k,v in result.items():
            if k!="traceback":
                print("S33_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return int(result["status"]!="PASS_NATIVE_S33_OFFLINE_EPOCH_RECONNECT_REBOOT_NO_GRANT")

if __name__=="__main__":
    raise SystemExit(run())
