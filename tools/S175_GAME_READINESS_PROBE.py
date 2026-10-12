"""S175 — REAL read-only Thần Long client readiness probe for independent tool.

This is NOT a game controller, TLM license emulator, memory reader, IPC
injector or replacement for runtime integration. Reuses existing S08 Win32
read-only HWND/PID enumeration. Optionally hashes user-explicit build
files with the existing S139 identity code; never loads/executes them.
Every original-game action readiness flag ALWAYS remains false because
RoleName, MapID and game-input transport are not verified.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from start_windows import GameWindow,NativeWin32Backend,discover_game_windows
from game_build_identity import inspect_explicit_game_build,public_report

MAX_REPORTED_WINDOWS=64
FORMAT_VERSION="S175_READ_ONLY_V1"
READY_FALSE={
    "real_role_name_reader":False,
    "real_map_id_reader":False,
    "runtime_game_input_transport":False,
    "runtime_train_actions":False,
    "runtime_login_actions":False,
    "runtime_lsv_actions":False,
    "full_original_gameplay_parity":False,
}


def scan_and_report(backend, *, gameassembly: str | Path | None = None,
                    metadata: str | Path | None = None) -> dict[str,Any]:
    """One synchronous Win32 READ-ONLY snapshot, no passwords/paths exposed.

    A verified candidate GameWindow still only attests process/window
    metadata, NOT an authenticated in-game character or usable game IPC.
    """
    if gameassembly is None and metadata is not None:
        raise ValueError("METADATA_REQUIRES_EXPLICIT_GAMEASSEMBLY")
    status="WINDOW_SCAN_COMPLETED"
    windows:tuple[GameWindow,...]=()
    try:
        windows=discover_game_windows(backend)
    except Exception as exc:
        status="WINDOW_SCAN_FAILED_"+type(exc).__name__.upper()
    # Existing S08 guarantees HWND+PID validated; no process/title/full
    # executable path exposed in public output.
    items=[{"hwnd":w.hwnd,"pid":w.pid} for w in windows[:MAX_REPORTED_WINDOWS]]
    result={
        "schema":FORMAT_VERSION,
        "scan_status":status,
        "verified_candidate_count":len(windows) if status=="WINDOW_SCAN_COMPLETED" else None,
        "windows":items,
        "window_list_truncated":len(windows)>MAX_REPORTED_WINDOWS,
        "candidate_identity_limit":"HWND_PID_EXE_CLASS_TITLE_ONLY_NOT_IN_GAME_ROLE",
        "game_action_ready":False,
        "capabilities":dict(READY_FALSE),
        "game_build": (
            public_report(inspect_explicit_game_build(gameassembly,metadata))
            if gameassembly is not None else
            {"status":"NO_EXPLICIT_BUILD_FILES_SUPPLIED",
             "ready_for_game_actions":False}
        ),
        "next_evidence":{
            "game_window":"Run the probe while the authorized Thần Long client is open; HWND/PID alone is not a RoleName.",
            "game_build":"For optional offline SHA-256 evidence, explicitly supply GameAssembly.dll and global-metadata.dat; never upload passwords or tokens.",
            "runtime_role":"A verified character RoleName/MapID reader bound to the exact live HWND/PID and game build is still required.",
            "input_transport":"A separately validated, permission-appropriate game action interface and real-game acceptance are still required.",
        },
        "safety":{
            "read_only":True,
            "original_license_issuer_used":False,
            "process_memory_read":False,
            "game_input_sent":False,
            "game_files_modified":False,
            "account_secrets_collected":False,
        },
    }
    return result


def run_native(*, gameassembly=None,metadata=None):
    if os.name!="nt":
        return {
            "schema":FORMAT_VERSION,
            "scan_status":"REQUIRES_WINDOWS",
            "verified_candidate_count":None,
            "windows":[],
            "window_list_truncated":False,
            "game_action_ready":False,
            "capabilities":dict(READY_FALSE),
            "safety":{"read_only":True,"game_input_sent":False,
                      "process_memory_read":False},
        }
    try:
        return scan_and_report(
            NativeWin32Backend(),gameassembly=gameassembly,metadata=metadata)
    except OSError as exc:
        return {
            "schema":FORMAT_VERSION,
            "scan_status":"WIN32_BACKEND_UNAVAILABLE_"+type(exc).__name__.upper(),
            "verified_candidate_count":None,
            "windows":[],
            "window_list_truncated":False,
            "game_action_ready":False,
            "capabilities":dict(READY_FALSE),
            "safety":{"read_only":True,"game_input_sent":False,
                      "process_memory_read":False},
        }


def main(argv=None) -> int:
    parser=argparse.ArgumentParser(
        description="Read-only game integration readiness evidence; no game actions.")
    parser.add_argument("--gameassembly",help="Optional EXPLICIT GameAssembly.dll path to inspect/hash only")
    parser.add_argument("--metadata",help="Optional EXPLICIT global-metadata.dat path to hash only")
    parser.add_argument("--output",type=Path,
                        help="Optional NEW report JSON path; refuses overwriting existing files")
    args=parser.parse_args(argv)
    if args.metadata and not args.gameassembly:
        parser.error("--metadata requires --gameassembly")
    result=run_native(gameassembly=args.gameassembly,metadata=args.metadata)
    report=json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    if args.output is not None:
        # Avoid clobbering existing user diagnostics or configuration.
        try:
            with args.output.open("x",encoding="utf-8") as f:
                f.write(report)
        except OSError as exc:
            print("REPORT_WRITE_REFUSED:"+type(exc).__name__,file=sys.stderr)
            return 3
    print(report,end="")
    return 0 if result["scan_status"]=="WINDOW_SCAN_COMPLETED" else 2


if __name__=="__main__":
    raise SystemExit(main())
