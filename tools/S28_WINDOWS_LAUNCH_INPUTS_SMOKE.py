"""S28 Windows native: test-owned synthetic PE32+ input structural safety.

No source game binary, process start, injection, DLL loading or Proxy runtime.
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
sys.path.insert(0,str(ROOT/"tools"))
from login_launch_inputs import inspect_x64_pe, build_audited_windows_env, prepare_launch_inputs
from login_launch_preflight import check_open_game_preflight
from login_path import EXE_NAME,resolve_game_dir
from permission_guard import PermissionGuard,VerifiedClaims
from S28_TEST_PE_FIXTURE import write_test_pe

OUT=ROOT/"artifacts"/"s28"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"safe_env_x64_pe_preflight.json"


def run():
    evidence={
        "task":"S28","status":"NOT_RUN","real_game":"NOT_RUN",
        "signed_Info":"NOT_AVAILABLE","process_spawned":0,
        "injection_attempts":0,"loaded_dlls":0,
        "proxy_runtime":"EXCLUDED","product_exe":"NOT_BUILT",
        "synthetic_PE_is_real_executable":False,
        "original_windows_whitelist":"UNKNOWN",
    }
    try:
        if os.name!="nt":
            raise RuntimeError("Native Windows environment required")
        with tempfile.TemporaryDirectory(prefix="S28_TEST_ONLY_") as td:
            base=Path(td)
            game=write_test_pe(base/"game"/EXE_NAME,dll=False)
            payload=write_test_pe(base/"tool"/"data"/"resources.dat",dll=True)
            local_env=dict(os.environ)
            systemroot=next((k for k in local_env if k.casefold()=="systemroot"),None)
            assert systemroot is not None and local_env[systemroot]
            safe=build_audited_windows_env(
                profile_index=2,source_env=local_env,
                essential_keys=(systemroot,))
            evidence["test_owned_allowlist_requires_systemroot"]=(
                safe=={systemroot:local_env[systemroot],"TLM_PROFILE":"2"})
            assert evidence["test_owned_allowlist_requires_systemroot"]

            guard=PermissionGuard()
            denied=check_open_game_preflight(
                guard.snapshot,resolve_game_dir(game.parent),running_windows=0)
            evidence["original_auth_blocked"]=not denied.allowed
            assert evidence["original_auth_blocked"]
            assert guard.receive_token("S28_TEST_ONLY",lambda _:VerifiedClaims(
                permissions=frozenset({"login_tab","info_tab"}),
                plan_status="TEST_ONLY",max_windows=1))
            allowed=check_open_game_preflight(
                guard.snapshot,resolve_game_dir(game.parent),running_windows=0)
            result=prepare_launch_inputs(
                allowed,package_root=base/"tool",profile_index=2,
                source_env=local_env,essential_keys=(systemroot,))
            evidence["native_test_synthetic_x64_pe_headers"]=(
                result.prepared and result.game_pe.valid and result.payload_pe.valid
                and not result.game_pe.dll and result.payload_pe.dll)
            evidence["only_active_resources_dat"]=result.payload==payload
            evidence["no_python_or_proxy_env_injection"]=(
                set(x.casefold() for x in result.environment)==
                {systemroot.casefold(),"tlm_profile"})
            assert all(evidence[x] for x in (
                "native_test_synthetic_x64_pe_headers",
                "only_active_resources_dat",
                "no_python_or_proxy_env_injection"))
            payload.write_bytes(b"MZ"+bytes(100))
            rejected=prepare_launch_inputs(allowed,package_root=base/"tool",
                profile_index=2,source_env=local_env,essential_keys=(systemroot,))
            evidence["truncated_payload_refused"]=not rejected.prepared
            assert evidence["truncated_payload_refused"]
            write_test_pe(payload,dll=True,machine=0x14c)
            rejected=prepare_launch_inputs(allowed,package_root=base/"tool",
                profile_index=2,source_env=local_env,essential_keys=(systemroot,))
            evidence["x86_payload_refused"]=rejected.reason=="PAYLOAD_NOT_AMD64"
            assert evidence["x86_payload_refused"]
            guard.clear()
            revoked=check_open_game_preflight(
                guard.snapshot,resolve_game_dir(game.parent),running_windows=0)
            evidence["revoked_rights_refused"]=not prepare_launch_inputs(
                revoked,package_root=base/"tool",profile_index=2,
                source_env=local_env,essential_keys=(systemroot,)).prepared
            assert evidence["revoked_rights_refused"]
            evidence["status"]="PASS_NATIVE_S28_F05_ENV_X64_PE_INPUTS_NO_LAUNCH"
    except Exception as exc:
        evidence["status"]="FAIL_NATIVE_S28"
        evidence["error"]=type(exc).__name__+": "+str(exc)
        evidence["traceback"]=traceback.format_exc(limit=14)
    finally:
        REPORT.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")
        for key,val in evidence.items():
            if key!="traceback":
                print("S28_"+key.upper()+"="+json.dumps(val,ensure_ascii=True))
    return int(evidence["status"]!="PASS_NATIVE_S28_F05_ENV_X64_PE_INPUTS_NO_LAUNCH")


if __name__=="__main__":
    raise SystemExit(run())
