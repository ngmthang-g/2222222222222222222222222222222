"""S139 opt-in audit of file identity for an actual locally installed client.

Usage:
  py -3 tools/S139_GAME_BUILD_FILE_AUDIT.py --gameassembly "C:\\...\\GameAssembly.dll" --metadata "C:\\...\\global-metadata.dat"
The second path is OPTIONAL and must be explicitly supplied; no discovery.
Records only basename, size, SHA-256 and UNATTESTED status. Never uploads.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from game_build_identity import inspect_explicit_game_build,public_report

def main(argv=None) -> int:
    parser=argparse.ArgumentParser(
        description="Offline, read-only candidate GameAssembly build identity; NOT authentication"
    )
    parser.add_argument("--gameassembly",type=Path,required=True,
                        help="Explicit path to a candidate GameAssembly.dll")
    parser.add_argument("--metadata",type=Path,
                        help="Optional explicit path to global-metadata.dat")
    args=parser.parse_args(argv)
    report=public_report(inspect_explicit_game_build(args.gameassembly,args.metadata))
    print(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2))
    return (0 if report["status"] in {
        "UNATTESTED_DLL_AND_METADATA_FINGERPRINTS_ONLY",
        "UNATTESTED_X64_GAMEASSEMBLY_CANDIDATE_METADATA_NOT_SUPPLIED"
    } else 2)

if __name__=="__main__":
    raise SystemExit(main())
