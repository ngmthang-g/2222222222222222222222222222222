"""S138: package the EXACT original metadata into a portable offline diagnostic.

No EXE, no account data, no game reader, no authorization bypass, no Proxy.
Requires the S137 exact SHA-pinned original 193,833-byte export explicitly
provided by the user. The 90 MB original TLMTool ZIP is NEVER bundled.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))

from original_item_catalog_resource import (
    EXPORTED_GZIP_SHA256, load_verified_export,
)

RESOURCE_NAME="assets/original_item_catalog.json.gz"
FILES = (
    ("src/original_item_catalog.py",ROOT/"src/original_item_catalog.py"),
    ("src/original_item_catalog_resource.py",ROOT/"src/original_item_catalog_resource.py"),
    ("tools/S138_CATALOG_LOOKUP.py",ROOT/"tools/S138_CATALOG_LOOKUP.py"),
)
WINDOWS_LAUNCHER = (
    "@echo off\r\n"
    "cd /d \"%~dp0\"\r\n"
    "py -3 tools\\S138_CATALOG_LOOKUP.py --item-id %1\r\n"
    "exit /b %errorlevel%\r\n"
)
README = """S138 — OFFLINE TLMTool 2.1.2 ORIGINAL ITEM CATALOG

This is a diagnostic/research lookup tool, NOT TLMTool, NOT an EXE and NOT
a working game tool. Windows: install Python 3.10+ if needed, then run
lookup_item_windows.cmd 10100000. Alternatively run:
  python tools/S138_CATALOG_LOOKUP.py --item-id 10100000

Includes exactly 29,983 original ItemID metadata records and 5,477
original weapon ItemIDs from frozen TLMTool 2.1.2. SHA256 of the
compressed metadata is locked in original_item_catalog_resource.py.
The full original 90 MB ZIP, login/configs, account data and game
executables are not included. NO game process, network, packet, Info
authorization, Farm or Bag Site10 functionality is used. An ItemID not
present in this frozen catalog is UNKNOWN, not automatically harmless.
"""


def _add_bytes(zf: zipfile.ZipFile, name: str, content: bytes) -> None:
    entry=zipfile.ZipInfo("S138_ORIGINAL_ITEM_CATALOG_OFFLINE/"+name)
    entry.date_time=(2020,1,1,0,0,0)
    entry.compress_type=zipfile.ZIP_DEFLATED
    entry.create_system=3
    entry.external_attr=0o644 << 16
    zf.writestr(entry,content,compresslevel=9)


def build_offline_bundle(input_resource: str | Path, output_zip: str | Path) -> dict:
    source=Path(input_resource).resolve()
    target=Path(output_zip).resolve()
    if source == target:
        raise ValueError("S138_INPUT_OUTPUT_MUST_DIFFER")
    catalog=load_verified_export(source)
    resource_bytes=source.read_bytes()
    manifest={
        "status":"OFFLINE_AUTHENTIC_ORIGINAL_METADATA_ONLY_NOT_PRODUCT",
        "origin_exe_sha256":catalog.source_exe_sha256,
        "resource_sha256":EXPORTED_GZIP_SHA256,
        "metadata_count":len(catalog.entries),
        "weapon_item_id_count":len(catalog.weapon_ids),
        "real_game_reader":False,
        "runtime_read_bag":False,
        "signed_info_authorization":False,
        "game_actions":False,
        "contains_original_game_executable":False
    }
    sources={name:path.read_bytes() for name,path in FILES}
    manifest_bytes=(json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+"\n").encode()
    payloads={
        **sources,
        "README_OFFLINE.txt":README.encode("utf-8"),
        "lookup_item_windows.cmd":WINDOWS_LAUNCHER.encode("utf-8"),
        "manifest.json":manifest_bytes,
        RESOURCE_NAME:resource_bytes,
    }
    target.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(target,"w",compression=zipfile.ZIP_DEFLATED) as zf:
        for name in sorted(payloads):
            _add_bytes(zf,name,payloads[name])
    with zipfile.ZipFile(target) as zf:
        if zf.testzip() is not None:
            raise ValueError("S138_BUNDLE_CRC_FAILED")
        expect={"S138_ORIGINAL_ITEM_CATALOG_OFFLINE/"+name for name in payloads}
        if set(zf.namelist()) != expect:
            raise ValueError("S138_BUNDLE_FILE_MANIFEST_MISMATCH")
        if zf.read("S138_ORIGINAL_ITEM_CATALOG_OFFLINE/"+RESOURCE_NAME) != resource_bytes:
            raise ValueError("S138_BUNDLE_EXPORTED_CATALOG_CHANGED")
    manifest["bundle_sha256"]=hashlib.sha256(target.read_bytes()).hexdigest()
    manifest["bundle_bytes"]=target.stat().st_size
    return manifest


def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument("verified_gzip",type=Path)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args(argv)
    try:
        report=build_offline_bundle(args.verified_gzip,args.output)
    except (ValueError,OSError) as exc:
        print(f"S138_BLOCKED: {exc}",file=sys.stderr)
        return 2
    print(json.dumps(report,indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
