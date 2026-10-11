"""S137 export EXACT original 2.1.2 item metadata, offline, no game.

Example:
 python tools/S137_EXPORT_ORIGINAL_CATALOG.py TLMTool_2.1.2.zip \\
   --output artifacts/original_item_catalog.json.gz --lookup 10100000
Only explicit original ZIP and explicit output path; never modifies ZIP.
"""
from __future__ import annotations

import argparse
from collections import Counter
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from original_item_catalog import load_original_archive, EXE_SHA256


def canonical_digests(catalog):
    lines = (
        f"{item_id}\t{meta.name}\t{meta.icon}\t{meta.src}\t{meta.equip_type or ''}\n"
        for item_id,meta in sorted(catalog.entries.items())
    )
    m=hashlib.sha256()
    for line in lines:
        m.update(line.encode("utf8"))
    w=hashlib.sha256(("\n".join(str(v) for v in sorted(catalog.weapon_ids))+"\n").encode("ascii"))
    return m.hexdigest(), w.hexdigest()


def export_catalog(catalog, output: Path) -> None:
    """Deterministic gzip JSON. Do not let this affect original runtime."""
    body={
        "source":"OFFLINE_EXACT_ORIGINAL_TLMTOOL_2_1_2",
        "original_exe_sha256":catalog.source_exe_sha256,
        "game_runtime_verified":False,
        "item_schema":["itemID","name","icon","src","type"],
        "entries":[
            [i,m.name,m.icon,m.src,m.equip_type]
            for i,m in sorted(catalog.entries.items())
        ],
        "weapon_ids":sorted(catalog.weapon_ids),
        "weapon_types":list(catalog.weapon_types),
    }
    data=json.dumps(body,ensure_ascii=False,separators=(",",":")).encode("utf8")
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open("wb") as handle:
        with gzip.GzipFile(filename="",mode="wb",compresslevel=9,mtime=0,fileobj=handle) as gz:
            gz.write(data)


def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument("original_zip",type=Path)
    ap.add_argument("--output",type=Path,
                    help="Explicit JSON.gz output path for complete canonical source data")
    ap.add_argument("--lookup",type=int,help="Optional original template ItemID lookup")
    args=ap.parse_args(argv)
    catalog=load_original_archive(args.original_zip)
    if len(catalog.entries)!=29983 or len(catalog.weapon_ids)!=5477:
        raise SystemExit("S137_ORIGINAL_CATALOG_COUNTS_CHANGED")
    digest,digest_weapon=canonical_digests(catalog)
    summary={
        "status":"PASS_S137_ORIGINAL_PINNED_METADATA_OFFLINE",
        "original_exe_sha256":EXE_SHA256,
        "metadata_count":len(catalog.entries),
        "weapons_count":len(catalog.weapon_ids),
        "metadata_by_source":dict(sorted(Counter(m.src for m in catalog.entries.values()).items())),
        "sorted_metadata_sha256":digest,
        "sorted_weapon_ids_sha256":digest_weapon,
        "real_game_attached":False,
        "signed_info_issued":False,
        "game_action_sent":False,
        "read_bag_parity_verified":False
    }
    if args.lookup is not None:
        entry=catalog.lookup(args.lookup)
        summary["lookup"]=(
            {"itemID":entry.item_id,"name":entry.name,"icon":entry.icon,
             "src":entry.src,"type":entry.equip_type,
             "weapon_membership":catalog.weapon_membership(entry.item_id)}
            if entry is not None else None)
    if args.output:
        export_catalog(catalog,args.output)
        summary["exported_path"]=str(args.output)
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    return 0


if __name__=="__main__":
    sys.exit(main())
