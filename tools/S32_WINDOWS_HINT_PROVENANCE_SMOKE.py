"""S32 Windows smoke: offline individually timed ADB hints and transitions.

Native Toolhelp is only used to confirm THIS TEST's real python.exe PID;
ADB input is a fixed synthetic captured transcript. No adb subprocess,
server start, Frida, game/emulator process, Proxy or injection.
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
OUT=ROOT/"artifacts"/"s32"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"native_hint_freshness_reconnect_safety.json"

def run():
    evidence={"task":"S32","status":"NOT_RUN","actual_adb_invoked":False,
              "adb_daemon_started":False,"real_ldplayer":"NOT_RUN",
              "real_game":"NOT_RUN","signed_Info":"NOT_AVAILABLE",
              "proxy_runtime":"EXCLUDED","product_exe":"NOT_BUILT"}
    try:
        if os.name!="nt":raise RuntimeError("Windows-only native check")
        from adb_identity_evidence import GuestIdentityHint,inspect_captured_adb_devices
        from adb_hint_provenance import (
            HintTimes,with_hint_times,compare_adb_lifecycle,
        )
        from running_count_evidence import (
            NativeWin32ProcessBackend,find_named_process_pids,
        )
        from login_path import EXE_NAME,GameDirectoryResult
        from login_launch_preflight import check_open_game_preflight
        from permission_guard import PermissionSnapshot

        now=time.monotonic()
        transcript=("List of devices attached\n"
                    "127.0.0.1:5555\tdevice\n"
                    "127.0.0.1:5557\tdevice\n"
                    "emulator-5558\toffline\n")
        hints={
            "127.0.0.1:5555":GuestIdentityHint(
                android_id="CLONE_AID",guest_ipv4="172.18.0.2",
                hwid="CLONE_HWID",guest_game_pid=101),
            "127.0.0.1:5557":GuestIdentityHint(
                android_id="CLONE_AID",guest_ipv4="172.18.0.3",
                hwid="CLONE_HWID",guest_game_pid=102),
        }
        capture=inspect_captured_adb_devices(transcript,captured_at=now,
                                             hints_by_serial=hints)
        timed=with_hint_times(capture,{
            "127.0.0.1:5555":HintTimes(android_id_at=now-2,hwid_at=now-2,
                                       guest_ipv4_at=now-2,guest_game_pid_at=now-2),
            "127.0.0.1:5557":HintTimes(android_id_at=now-45,hwid_at=now-45,
                                       guest_ipv4_at=now-2,guest_game_pid_at=now-2),
        })
        evidence["stale_androidid_even_when_capture_fresh"]=(
            timed.assess("127.0.0.1:5557","android_id",time.monotonic()).code
            =="STALE_HINT")
        evidence["fresh_guest_ip_on_same_serial"]=(
            timed.assess("127.0.0.1:5557","guest_ipv4",time.monotonic()).is_fresh_diagnostic)
        evidence["clone_collision_not_automatically_selected"]=(
            timed.unique_serial_for("android_id","CLONE_AID",time.monotonic())
            is None)
        evidence["fresh_distinct_ip_diagnostic_only"]=(
            timed.unique_serial_for("guest_ipv4","172.18.0.3",time.monotonic())
            =="127.0.0.1:5557")
        evidence["offline_not_targetable"]=(
            timed.unique_serial_for("guest_ipv4","emulator-5558",time.monotonic())
            is None)

        prev=with_hint_times(inspect_captured_adb_devices(
            "List of devices attached\na offline\n",captured_at=now),
            {})
        curr=with_hint_times(inspect_captured_adb_devices(
            "List of devices attached\na device\n",captured_at=now+1),
            {})
        delta=compare_adb_lifecycle(prev,curr,now=now+2)
        evidence["offline_to_online_unverified_transition"]=(
            len(delta.transitions)==1 and
            delta.transitions[0].code=="OFFLINE_TO_ONLINE"
            and not delta.is_authoritative_rebinding)

        p=NativeWin32ProcessBackend()
        own=find_named_process_pids(p,Path(sys.executable).name)
        evidence["native_windows_python_pid_seen"]=os.getpid() in own
        evidence["game_emulator_count_still_unknown"]=(
            timed.combined_running_count is None
            and timed.emulator_account_count is None
            and not timed.is_authoritative_account_total)
        with tempfile.TemporaryDirectory(prefix="S32_TEST_ONLY_") as td:
            d=Path(td);(d/EXE_NAME).write_bytes(b"S32 NOT GAME EXE")
            snapshot=PermissionSnapshot(has_verified_payload=True,
                permissions=frozenset({"login_tab"}),max_windows=10,
                plan_status="TEST_ONLY")
            blocked=check_open_game_preflight(snapshot,GameDirectoryResult(d,""),
                                              running_windows=timed.combined_running_count)
            evidence["s26_rejects_unknown_total"]=(
                not blocked.allowed and blocked.reason=="RUNNING_WINDOW_COUNT_UNKNOWN")
        assert all(evidence[k] for k in (
            "stale_androidid_even_when_capture_fresh",
            "fresh_guest_ip_on_same_serial","clone_collision_not_automatically_selected",
            "fresh_distinct_ip_diagnostic_only","offline_not_targetable",
            "offline_to_online_unverified_transition","native_windows_python_pid_seen",
            "game_emulator_count_still_unknown","s26_rejects_unknown_total"))
        evidence["status"]="PASS_NATIVE_S32_INDEPENDENT_HINT_TTL_RECONNECT_NO_AUTH"
    except Exception as exc:
        evidence["status"]="FAIL_NATIVE_S32"
        evidence["error"]=type(exc).__name__+": "+str(exc)
        evidence["traceback"]=traceback.format_exc(limit=12)
    finally:
        REPORT.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),
                          encoding="utf-8")
        for k,v in evidence.items():
            if k!="traceback":
                print("S32_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return int(evidence["status"]!="PASS_NATIVE_S32_INDEPENDENT_HINT_TTL_RECONNECT_NO_AUTH")

if __name__=="__main__":
    raise SystemExit(run())
