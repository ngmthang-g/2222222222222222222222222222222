"""S139 actual Win64 file identity smoke using Windows' OWN python310.dll.

Copies the real Windows x64 CPython DLL into an explicitly test-owned
temporary GameAssembly.dll filename to test non-synthetic PE/header/hash IO.
That file is NOT a Than Long client or valid game build. Never loads/starts.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from game_build_identity import inspect_explicit_game_build,public_report

def main():
    if os.name!="nt" or sys.maxsize <= 2**32:
        raise SystemExit("S139_REAL_WIN64_REQUIRED")
    source=Path(sys.base_prefix)/"python310.dll"
    if not source.is_file():
        source=Path(sys.executable).parent/"python310.dll"
    if not source.is_file():
        raise SystemExit("S139_NATIVE_PYTHON310_DLL_NOT_FOUND")
    with tempfile.TemporaryDirectory(prefix="S139_SELF_OWNED_") as folder:
        dst=Path(folder)/"GameAssembly.dll"
        md=Path(folder)/"global-metadata.dat"
        shutil.copyfile(source,dst)
        md.write_bytes(b"S139_TEST_OWNED_EXPLICIT_METADATA_NOT_REAL_UNITY")
        result=inspect_explicit_game_build(dst,md)
        absent=inspect_explicit_game_build(dst)
        out=public_report(result)
        checks={
            "real_win64_dll_pe_structural_read":
                out["dll_x64_pe_structure"] and
                result.candidate_dll.sha256==hashlib.sha256(source.read_bytes()).hexdigest(),
            "real_file_metadata_sha_read":
                result.candidate_metadata.sha256==hashlib.sha256(md.read_bytes()).hexdigest(),
            "missing_metadata_requires_explicit_path":
                absent.candidate_metadata is None,
            "positive_only_candidate_fingerprint":
                result.status=="UNATTESTED_DLL_AND_METADATA_FINGERPRINTS_ONLY",
            "does_not_claim_actual_game":
                not result.is_authoritatively_known_game_build
                and not result.game_process_attached
                and not result.real_roledata_read
                and not result.original_tlm_pointer_offsets_compatible
                and not result.ready_for_game_actions
                and not result.signed_info_verified,
            "no_private_filepaths_in_output":
                folder not in json.dumps(out),
        }
    p=ROOT/"artifacts"/"s139"
    p.mkdir(parents=True,exist_ok=True)
    report={"status":"PASS_S139_REAL_WINDOWS_READ_ONLY_FILE_FINGERPRINT_NOT_GAME",
            "test_owned_real_windows_system_dll":True,
            "actual_game_build":False,
            "signed_info_validated":False,
            "all":checks}
    (p/"native.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf8")
    print(json.dumps(report))
    if not all(checks.values()):
        raise SystemExit("S139_NATIVE_FINGERPRINT_FAILED")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
