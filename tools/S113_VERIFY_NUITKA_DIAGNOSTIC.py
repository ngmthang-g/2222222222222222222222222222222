"""S113: verify a real Nuitka standalone Windows folder, TEST/DIAGNOSTIC ONLY.

Do not claim TLM functional/visual parity, authentic Info authorization, or
working game. Must run a *compiled* Nuitka diagnostic from an unrelated cwd,
with actual .dist runtime dependencies, and exit 2 with the existing guard.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from login_launch_inputs import inspect_x64_pe

BINARY = "S113_NUITKA_DIAGNOSTIC_NOT_PRODUCT.exe"
FOLDER = "TLMTool.dist"
REQUIRED_GUARD = "S01 BLOCKED: genuine InfoTab/server authorization has not been reconstructed; no GUI started."
PASS = "PASS_NATIVE_S113_NUITKA_STANDALONE_FOLDER_FAIL_CLOSED_NOT_PRODUCT"


def diagnose_structure(dist: Path) -> tuple[Path | None, str]:
    if not isinstance(dist, Path):
        return None, "INVALID_PATH_TYPE"
    if dist.name != FOLDER:
        return None, "NOT_EXPECTED_NUITKA_DIST_FOLDER"
    exe = dist / BINARY
    if not exe.is_file():
        return None, "DIAGNOSTIC_BINARY_MISSING"
    if (dist / "TLMTool.exe").exists() or (dist / "TLMTool_2.1.2_REBUILT.exe").exists():
        return None, "FORBIDDEN_PRODUCT_FILENAME"
    runtime = dist / "python310.dll"
    if not runtime.is_file():
        return None, "CPYTHON_310_RUNTIME_MISSING"
    pe = inspect_x64_pe(exe, dll_required=False)
    if not pe.valid:
        return None, "INVALID_X64_PE_" + pe.reason
    return exe, "X64_NUITKA_STANDALONE_STRUCTURE_VALID"


def run_from_unrelated_cwd(exe: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix="S113_NO_SOURCE_CWD_") as temp:
        env = dict(os.environ)
        env.pop("PYTHONPATH", None)
        env.pop("PYTHONHOME", None)
        try:
            p = subprocess.run(
                [str(exe.resolve())], cwd=temp, env=env,
                capture_output=True, text=True, encoding="utf-8",
                errors="replace", timeout=45, check=False)
        except subprocess.TimeoutExpired:
            return {"status": "NATIVE_EXE_TIMEOUT"}
        except OSError:
            return {"status": "NATIVE_EXE_LOAD_FAILURE"}
        if p.returncode != 2:
            return {"status": "DID_NOT_REFUSE_EXIT_2", "returncode": p.returncode}
        if REQUIRED_GUARD not in p.stderr or REQUIRED_GUARD in p.stdout:
            return {"status": "AUTH_GUARD_MISSING_OR_WRONG_STREAM", "returncode": p.returncode}
        return {"status": "EXPLICITLY_BLOCKED_NO_GUI", "returncode": 2}


def verify(dist: Path) -> dict:
    report = dict(task="S113", kind="NUITKA_STANDALONE_DIAGNOSTIC_ONLY",
                  product="NOT_BUILT", actual_game="NOT_RUN",
                  original_nuitka_version="UNKNOWN", proxy="EXCLUDED",
                  signed_info="NOT_AVAILABLE", status="NOT_RUN")
    if os.name != "nt" or sys.maxsize <= 2**32:
        report["status"] = "WINDOWS_X64_REQUIRED"
        return report
    exe, structure = diagnose_structure(dist)
    report["structure"] = structure
    if exe is None:
        report["status"] = "FAIL_" + structure
        return report
    report["file_size_bytes"] = exe.stat().st_size
    report["exe_sha256"] = hashlib.sha256(exe.read_bytes()).hexdigest()
    report["dist_file_count"] = sum(1 for p in dist.rglob("*") if p.is_file())
    report["runtime_dll_present"] = (dist / "python310.dll").is_file()
    report["run"] = run_from_unrelated_cwd(exe)
    report["status"] = PASS if report["run"]["status"] == "EXPLICITLY_BLOCKED_NO_GUI" else "FAIL_DIAGNOSTIC_RUN"
    return report


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python tools/S113_VERIFY_NUITKA_DIAGNOSTIC.py <TLMTool.dist> <report.json>", file=sys.stderr)
        return 2
    dest = Path(sys.argv[2])
    dest.parent.mkdir(parents=True, exist_ok=True)
    report = verify(Path(sys.argv[1]))
    dest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for k, v in report.items():
        if k != "run":
            print("S113_" + k.upper() + "=" + json.dumps(v, ensure_ascii=True))
    if "run" in report:
        print("S113_RUN_STATUS=" + report["run"]["status"])
    return 0 if report["status"] == PASS else 1


if __name__ == "__main__":
    raise SystemExit(main())
