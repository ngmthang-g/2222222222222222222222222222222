#!/usr/bin/env python3
"""D01 static module-name extractor for the frozen TLMTool distribution.

This script does not execute any package binary. It extracts:
- exact Nuitka-style module markers from printable strings;
- exact module-like .py filename references;
- physical .pyd extension-module names;
- the SHA-256 of the inspected inner executable.

Category/provenance policy is documented in docs/tasks/D01.md.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

MODULE_MARKER = re.compile(r"u?<module ([^>]+)>")
PY_PATH = re.compile(r"^[A-Za-z0-9_.-]+(?:[\\/][A-Za-z0-9_.-]+)*\.py$")


def module_from_path(value: str) -> str:
    value = value.replace("\\", "/")
    if value.endswith("/__init__.py"):
        value = value[:-12]
    elif value.endswith(".py"):
        value = value[:-3]
    return value.replace("/", ".")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("dist", type=Path, help="Path to TLMTool.dist")
    ap.add_argument("--out", type=Path, default=Path("D01_RAW_MODULE_NAMES.json"))
    args = ap.parse_args()

    dist = args.dist.resolve()
    exe = dist / "TLMTool.exe"
    if not exe.is_file():
        raise SystemExit(f"Missing inner executable: {exe}")

    sha256 = hashlib.sha256(exe.read_bytes()).hexdigest()
    text = subprocess.check_output(
        ["strings", "-a", "-n", "3", str(exe)],
        text=True,
        errors="ignore",
    )
    lines = [line.strip() for line in text.splitlines()]

    exact_markers = []
    rejected_markers = []
    seen = set()
    for line in lines:
        m = MODULE_MARKER.fullmatch(line)
        if not m:
            continue
        name = m.group(1)
        if name in seen:
            continue
        seen.add(name)
        if any(ch.isspace() for ch in name) or "%" in name or "'" in name:
            rejected_markers.append(name)
        else:
            exact_markers.append(name)

    source_refs = {}
    for line in lines:
        if not PY_PATH.fullmatch(line):
            continue
        name = module_from_path(line)
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.-]*(?:\.[A-Za-z_][A-Za-z0-9_.-]*)*", name):
            source_refs.setdefault(name, line.replace("\\", "/"))

    pyd = []
    for path in sorted(dist.rglob("*.pyd")):
        rel = path.relative_to(dist).as_posix()
        pyd.append({"name": rel[:-4].replace("/", "."), "path": rel})

    result = {
        "inner_exe_sha256": sha256,
        "exact_module_markers": sorted(exact_markers),
        "rejected_marker_strings": sorted(rejected_markers),
        "source_filename_refs": source_refs,
        "physical_pyd_modules": pyd,
    }
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.out)


if __name__ == "__main__":
    main()
