#!/usr/bin/env python3
"""D04 internal architecture builder.

Consumes the persisted D02 internal relationship table plus D04 contextual
evidence. It never executes the packaged application.

The D02 graph remains STATIC_REFERENCE_NOT_IMPORT_PROOF. Contextual rows are
kept as a separate stronger tier instead of silently rewriting the D02 graph.
"""
from __future__ import annotations
import argparse, csv, gzip, json
from collections import Counter, defaultdict
from pathlib import Path

LAYERS = {
    "shell_orchestration": ["start_tab","party_tab","login_tab","info_tab","splash"],
    "feature_automation": ["farm_tab","farm_data","train_lsv_tab","daily_tab",
        "donvang_tab","don_logic","phoban_tab","phoban_dungeons","rao_tab",
        "toiuu_tab","proxy_tab"],
    "low_level_game_integration": ["memory_reader","memory_items","dll_injector",
        "pixel","pixel_data","coordinate_utils","fast_travel","forwarder"],
    "guard_metadata_support": ["utils","permission_guard","item_meta_data",
        "weapon_ids","local_token_secret","bag_filter"],
    "emulator": ["emu_input","emu_reader","emu_remote","emu_setup","emu_chat",
        "emu_farm_tab","debug_android_tab"],
}
FILENAME_ONLY = ["TLMTool","bag_filter","emu_reader","pixel","proxy_refresh"]

def open_text(path: Path):
    return gzip.open(path, "rt", encoding="utf-8") if path.suffix == ".gz" else path.open("r", encoding="utf-8")

def read_edges(path: Path):
    with open_text(path) as f:
        rows=list(csv.DictReader(f, delimiter="\t"))
    return rows

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("d02_internal", type=Path)
    ap.add_argument("contextual", type=Path)
    ap.add_argument("--out", type=Path, default=Path("D04_ARCHITECTURE_REPRO.json"))
    args=ap.parse_args()

    base=read_edges(args.d02_internal)
    contextual=read_edges(args.contextual)
    incoming=Counter(r["target"] for r in base)
    outgoing=Counter(r["source"] for r in base)
    sources=sorted({r["source"] for r in base})
    targets=sorted({r["target"] for r in base})

    base_pairs={(r["source"],r["target"]) for r in base}
    stronger=[]
    contextual_only=[]
    for r in contextual:
        pair=(r["source"],r["target"])
        if pair in base_pairs:
            stronger.append(r)
        else:
            contextual_only.append(r)

    result={
        "task":"D04",
        "base_graph":{
            "edges":len(base),
            "sources":len(sources),
            "distinct_targets":len(targets),
            "relation_status":"STATIC_REFERENCE_NOT_IMPORT_PROOF",
        },
        "top_incoming":incoming.most_common(20),
        "top_outgoing":outgoing.most_common(20),
        "contextual_rows":len(contextual),
        "contextual_rows_also_in_base":len(stronger),
        "contextual_edges_beyond_base":[f'{r["source"]}->{r["target"]}' for r in contextual_only],
        "layers":LAYERS,
        "filename_only_sources":FILENAME_ONLY,
        "exact_python_import_syntax":"UNKNOWN",
    }
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(args.out)

if __name__=="__main__":
    main()
