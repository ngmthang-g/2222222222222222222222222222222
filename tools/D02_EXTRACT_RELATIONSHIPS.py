#!/usr/bin/env python3
"""D02 static relationship extractor.

This script never executes the packaged application. It consumes:
- the frozen inner executable;
- the D01 row-level inventory (TSV or TSV.GZ).

For each exact-marker TLM internal source block it records exact accepted
module names that occur as tagged string constants. The resulting edge is
STATIC_REFERENCE_NOT_IMPORT_PROOF; it is not promoted to Python import syntax.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import re
import subprocess
from pathlib import Path

MARKER = re.compile(r"u?<module ([^>]+)>")


def open_text(path: Path):
    if path.suffix == ".gz":
        return gzip.open(path, "rt", encoding="utf-8")
    return path.open("r", encoding="utf-8")


def load_inventory(path: Path):
    accepted = {}
    with open_text(path) as f:
        for row in csv.DictReader(f, delimiter="\t"):
            if row["confidence"] == "REJECTED":
                continue
            accepted[row["name"]] = row["category"]
    return accepted


def read_strings(exe: Path):
    output = subprocess.check_output(
        ["strings", "-a", "-n", "3", "-t", "d", str(exe)],
        text=True,
        errors="ignore",
    )
    rows = []
    for line in output.splitlines():
        m = re.match(r"^\s*(\d+)\s+(.*)$", line)
        if m:
            rows.append((int(m.group(1)), m.group(2).strip()))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dist", type=Path)
    ap.add_argument("d01_inventory", type=Path)
    ap.add_argument("--out", type=Path, default=Path("D02_RELATIONSHIP_EVIDENCE.tsv"))
    args = ap.parse_args()

    exe = args.dist.resolve() / "TLMTool.exe"
    accepted = load_inventory(args.d01_inventory)
    internal = {name for name, cat in accepted.items() if cat == "TLM_INTERNAL"}
    strings = read_strings(exe)

    markers = []
    for off, value in strings:
        m = MARKER.fullmatch(value)
        if not m:
            continue
        name = m.group(1)
        if "%" in name or any(ch.isspace() for ch in name):
            continue
        markers.append((off, name))

    edges = []
    for index, (start, source) in enumerate(markers):
        if source not in internal:
            continue
        end = markers[index + 1][0] if index + 1 < len(markers) else 10**18
        seen = set()
        for off, raw in strings:
            if off <= start:
                continue
            if off >= end:
                break
            candidates = [raw]
            if raw and raw[0] in "auw" and len(raw) > 1:
                candidates.append(raw[1:])
            for target in candidates:
                if target == source or target not in accepted:
                    continue
                key = (source, target)
                if key in seen:
                    continue
                seen.add(key)
                edges.append({
                    "source": source,
                    "target": target,
                    "target_category": accepted[target],
                    "source_marker_offset_dec": start,
                    "reference_offset_dec": off,
                    "raw_string": raw,
                    "evidence": "TAGGED_NAME_IN_COMPILED_MODULE_BLOCK",
                    "relation_status": "STATIC_REFERENCE_NOT_IMPORT_PROOF",
                })

    edges.sort(key=lambda x: (x["source"], x["target_category"], x["target"].lower()))
    fields = [
        "source", "target", "target_category",
        "source_marker_offset_dec", "reference_offset_dec",
        "raw_string", "evidence", "relation_status",
    ]
    with args.out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        w.writeheader()
        w.writerows(edges)

    print(f"{len(edges)} relationship rows -> {args.out}")


if __name__ == "__main__":
    main()
