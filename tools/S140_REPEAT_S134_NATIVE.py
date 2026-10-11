"""S140 — Repeat REAL Win64 self-owned S134 pointer regression after flaky fix.

Tests the existing S134 original _resolve_chain contract many independent
process lifetimes. No game, no Info credentials, no memory injection.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"tools"/"S134_WINDOWS_ROLE_CHAIN_FIXTURE_SMOKE.py"
OUT=ROOT/"artifacts"/"s140"
RUNS=12


def main() -> int:
    if os.name!="nt" or sys.maxsize<=2**32:
        print("S140_WINDOWS_X64_REQUIRED")
        return 2
    OUT.mkdir(parents=True,exist_ok=True)
    samples=[]
    for i in range(RUNS):
        completed=subprocess.run(
            [sys.executable,str(SCRIPT)],cwd=ROOT,capture_output=True,
            text=True,timeout=40,check=False)
        # The S134 child writes this artifact, but only status/booleans are
        # recorded, never arbitrary raw process stdout or paths/account data.
        child=ROOT/"artifacts"/"s134"/"win64_owned_pointer_chain.json"
        try:
            evidence=json.loads(child.read_text(encoding="utf8"))
        except (OSError,UnicodeError,ValueError):
            evidence={}
        result={
            "iteration":i+1,
            "exit_code":completed.returncode,
            "native_pointer_chain":evidence.get("status")==
                "PASS_S134_NATIVE_READONLY_SELF_OWNED_ROLE_POINTER_FIXTURE",
            "exact_native_address_trace":evidence.get(
                "O02_returns_object_before_last_offset") is True,
            "readback_is_self_owned":evidence.get(
                "real_Windows_RPM_reads_self_owned_64bit_pointer") is True,
            "real_game_attached":False,"signed_info_authenticated":False,
        }
        samples.append(result)
        if not (result["exit_code"]==0
                and result["native_pointer_chain"]
                and result["exact_native_address_trace"]
                and result["readback_is_self_owned"]):
            break
    passed=(len(samples)==RUNS and all(
        x["exit_code"]==0 and x["native_pointer_chain"]
        and x["exact_native_address_trace"] and x["readback_is_self_owned"]
        for x in samples))
    output={
        "status":"PASS_S140_REPEATED_REAL_WIN64_TEST_OWNED_CHAIN_NOT_GAME"
                if passed else "FAIL_S140_NATIVE_POINTER_CHAIN",
        "requested":RUNS,"completed":len(samples),
        "all_native_results_passed":passed,
        "actual_game_process_access":False,
        "original_info_verified":False,
        "samples":samples,
    }
    (OUT/"s134_repeatability.json").write_text(
        json.dumps(output,indent=2)+"\n",encoding="utf8")
    print(json.dumps({k:v for k,v in output.items() if k!="samples"}))
    return 0 if passed else 1


if __name__=="__main__":
    raise SystemExit(main())
