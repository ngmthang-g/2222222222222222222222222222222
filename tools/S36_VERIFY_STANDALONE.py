"""S36: verify an actual PyInstaller Windows diagnostic build stays fail-closed.

This is a post-build QA runner, NOT a product installer or game automation.
It executes ONLY our clearly named diagnostic EXE with no credentials, no
Info server, no emulator or game process. A pass asserts a real Windows x64
PE was packaged and exits 2 with the existing original-source guard text;
it does not assert any TLMTool runtime/GUI parity.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Sequence

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))

from login_launch_inputs import inspect_x64_pe

DIAGNOSTIC_NAME="S36_DIAGNOSTIC_FAIL_CLOSED_NOT_PRODUCT"
GUARD_SENTENCE="genuine InfoTab/server authorization has not been reconstructed; no GUI started."
DIAGNOSTIC_SUCCESS="PASS_NATIVE_S36_PACKAGED_DIAGNOSTIC_FAIL_CLOSED_NOT_PRODUCT"


def assess_blocked_run(exit_code: int, stdout: str, stderr: str) -> str:
    """Process exit is not a grant; accept only exact fail-closed semantics."""
    if type(exit_code) is not int or type(stdout) is not str or type(stderr) is not str:
        return "MALFORMED_PROCESS_RESULT"
    if exit_code != 2:
        return "NOT_FAIL_CLOSED_EXIT_2"
    if GUARD_SENTENCE not in stderr or "S01 BLOCKED:" not in stderr:
        return "MISSING_EXPLICIT_AUTH_REFUSAL"
    if GUARD_SENTENCE in stdout:
        return "GUARD_NOT_ON_STDERR"
    return "EXPLICITLY_BLOCKED_NO_GUI"


def inspect_diagnostic_path(folder: str | Path) -> tuple[Path | None, str]:
    """Exact non-product name, directory form and x64 PE, never game EXE."""
    target=Path(folder)
    exe=target/DIAGNOSTIC_NAME/(DIAGNOSTIC_NAME+".exe")
    if not exe.is_file():
        return None, "DIAGNOSTIC_EXE_MISSING"
    if (exe.parent/("TLMTool.exe")).exists() or (exe.parent/("TLMTool_2.1.2_REBUILT.exe")).exists():
        return None, "MISLEADING_PRODUCT_FILENAME"
    pe=inspect_x64_pe(exe,dll_required=False)
    if not pe.valid:
        return None, "DIAGNOSTIC_PE_INVALID_"+pe.reason
    return exe, "STRUCTURAL_X64_PE_NOT_SIGNATURE_PROOF"


def run_diagnostic(exe: Path, args: Sequence[str]=()) -> dict:
    """Run in TEST-owned empty cwd; no PYTHONPATH or source checkout needed."""
    with tempfile.TemporaryDirectory(prefix="S36_RUN_NO_GAME_") as temp:
        env=os.environ.copy()
        # Test a packaged EXE without relying on local src modules.
        env.pop("PYTHONPATH",None)
        env.pop("PYTHONHOME",None)
        command=[str(exe.resolve()),*args]
        try:
            proc=subprocess.run(
                command,cwd=temp,env=env,
                capture_output=True,text=True,encoding="utf-8",errors="replace",
                timeout=40,check=False,
            )
        except subprocess.TimeoutExpired:
            return {"status":"DIAGNOSTIC_TIMEOUT","returncode":None,
                    "args":list(args)}
        except OSError as exc:
            return {"status":"WINDOWS_EXECUTION_FAILED","returncode":None,
                    "args":list(args),"error":type(exc).__name__}
        return {"status":assess_blocked_run(proc.returncode,proc.stdout,proc.stderr),
                "returncode":proc.returncode,"args":list(args),
                "guard_seen_on_stderr":GUARD_SENTENCE in proc.stderr,
                "stdout":proc.stdout[-1200:],"stderr":proc.stderr[-1200:]}


def verify(folder: str | Path) -> dict:
    """Only successful for a Windows EXE that really executes and blocks."""
    report={
        "task":"S36","kind":"WINDOWS_PACKAGED_DIAGNOSTIC_NOT_PRODUCT",
        "status":"NOT_RUN","actual_game":"NOT_RUN","signed_Info":"NOT_AVAILABLE",
        "real_gui":"NOT_STARTED","product_exe":"NOT_BUILT",
        "license_grants":0,"game_launches":0,"proxy_runtime":"EXCLUDED",
        "test_claims_inserted":False,
    }
    if os.name!="nt" or sys.maxsize <= 2**32:
        report["status"]="NOT_WINDOWS_X64"
        return report
    exe,status=inspect_diagnostic_path(folder)
    report["pe_classification"]=status
    if exe is None:
        report["status"]="FAIL_S36_"+status
        return report
    report["size_bytes"]=exe.stat().st_size
    report["sha256"]=hashlib.sha256(exe.read_bytes()).hexdigest()
    report["exe_name"]=exe.name
    report["running_from_unrelated_temp_directory"]=True
    normal=run_diagnostic(exe)
    forced=run_diagnostic(exe,("--S36-unverified-bypass-attempt",))
    report["normal_run"]=normal
    report["unverified_commandline_attempt"]=forced
    if (normal["status"]!="EXPLICITLY_BLOCKED_NO_GUI"
            or forced["status"]!="EXPLICITLY_BLOCKED_NO_GUI"):
        report["status"]="FAIL_S36_GUARD_MISMATCH"
    else:
        report["status"]=DIAGNOSTIC_SUCCESS
    return report


def main() -> int:
    if len(sys.argv)!=3:
        print("Usage: python tools/S36_VERIFY_STANDALONE.py <dist-root> <report-path>",
              file=sys.stderr)
        return 2
    target=Path(sys.argv[2])
    target.parent.mkdir(parents=True,exist_ok=True)
    report=verify(sys.argv[1])
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",
                      encoding="utf-8")
    for key,value in report.items():
        if key not in {"normal_run","unverified_commandline_attempt"}:
            print("S36_"+key.upper()+"="+json.dumps(value,ensure_ascii=True))
    for key in ("normal_run","unverified_commandline_attempt"):
        result=report.get(key,{"status":"NOT_RUN"})
        print("S36_"+key.upper()+"_STATUS="+json.dumps(result["status"]))
        print("S36_"+key.upper()+"_RETURN_CODE="+json.dumps(result.get("returncode")))
    return 0 if report["status"]==DIAGNOSTIC_SUCCESS else 1


if __name__=="__main__":
    raise SystemExit(main())
