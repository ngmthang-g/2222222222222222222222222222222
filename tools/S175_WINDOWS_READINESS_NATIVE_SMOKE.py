"""S175 genuine Win64 native read-only integration readiness probe smoke.

Uses actual Windows EnumWindows/QueryFullProcessImageNameW via S08, not a
fake game metadata backend. A physically test-owned Tk window must NEVER
be misreported as Thần Long. Does not claim a real game was available.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tkinter as tk

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
sys.path.insert(0,str(ROOT/"src"))
import S175_GAME_READINESS_PROBE as probe
from start_windows import NativeWin32Backend

OUT=ROOT/"artifacts"/"s175"
OUT.mkdir(parents=True,exist_ok=True)


def main():
    proof={"status":"NOT_RUN","real_game_attested":False,
           "real_role_name_attested":False,"sent_game_input":False,
           "original_issuer_used":False}
    root=None
    try:
        if os.name!="nt":
            raise RuntimeError("NATIVE_WIN64_REQUIRED")
        root=tk.Tk()
        root.title("S175 test-owned Python Tk fixture, NOT THE GAME")
        root.update()
        native=NativeWin32Backend()
        hwnd=int(root.winfo_id())
        pid=int(os.getpid())
        proof["real_test_owned_win32_hwnd_pid"]=(
            native.is_window(hwnd) and native.process_id(hwnd)==pid)
        raw=probe.scan_and_report(native)
        proof["real_s08_native_enum_completed"]=(
            raw["scan_status"]=="WINDOW_SCAN_COMPLETED")
        proof["test_owned_python_window_not_false_game"]=(
            all(w["hwnd"]!=hwnd for w in raw["windows"]))
        proof["all_runtime_game_actions_remain_unverified"]=(
            raw["game_action_ready"] is False
            and not any(raw["capabilities"].values()))
        proof["readiness_json_contains_no_guess_names"]=(
            all(set(x)=={"hwnd","pid"} for x in raw["windows"])
            and "role_name" not in json.dumps(raw["windows"]))
        proof["actual_scan_count_is_not_synthetic"]=(
            type(raw["verified_candidate_count"]) is int
            and raw["verified_candidate_count"]>=0)
        proof["no_build_files_used_or_touched"]=(
            raw["game_build"]["status"]=="NO_EXPLICIT_BUILD_FILES_SUPPLIED")
        proof["no_game_memory_or_credential_access"]=(
            raw["safety"]["process_memory_read"] is False
            and raw["safety"]["account_secrets_collected"] is False
            and raw["safety"]["game_files_modified"] is False)
        root.destroy();root=None
        checks={k:v for k,v in proof.items() if type(v) is bool
            and k not in ("real_game_attested","real_role_name_attested",
                          "sent_game_input","original_issuer_used")}
        if not all(checks.values()):
            raise RuntimeError("WIN64_PROBE_FAIL:"+",".join(
                k for k,v in checks.items() if not v))
        proof["status"]="PASS_NATIVE_S175_REAL_S08_WIN32_READONLY_GAME_READINESS_NOT_GAME"
    except Exception as exc:
        proof["status"]="FAILED_S175_NATIVE"
        proof["error_type"]=type(exc).__name__
        proof["error_detail"]=str(exc)[:700]
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        (OUT/"native_real_win32_probe.json").write_text(
            json.dumps(proof,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        for k,v in proof.items():
            print("S175_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if proof["status"].startswith("PASS_NATIVE_") else 1

if __name__=="__main__":
    raise SystemExit(main())
