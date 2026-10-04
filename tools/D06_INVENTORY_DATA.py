#!/usr/bin/env python3
"""D06 static packaged data/config inventory.

Reads the original ZIP and inner EXE printable strings. It does not execute any
packaged program or DLL. Output is descriptive evidence only.
"""
from __future__ import annotations
import argparse, csv, hashlib, math, re, subprocess, zipfile
from collections import Counter
from pathlib import Path

def entropy(data: bytes) -> float:
    if not data: return 0.0
    c=Counter(data); n=len(data)
    return -sum((v/n)*math.log2(v/n) for v in c.values())

def exe_strings(exe: Path) -> list[str]:
    return subprocess.check_output(["strings","-a","-n","3",str(exe)],text=True,errors="ignore").splitlines()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("archive",type=Path)
    ap.add_argument("inner_exe",type=Path)
    ap.add_argument("--out",type=Path,default=Path("D06_PACKAGE_DATA_REPRO.tsv"))
    args=ap.parse_args()
    strings=exe_strings(args.inner_exe)
    with zipfile.ZipFile(args.archive) as z:
        candidates=[]
        for name in z.namelist():
            if name.endswith("/"): continue
            rel=name.split("/",1)[1] if "/" in name else name
            if "/data/" in rel or rel.endswith(("proxy_working.txt","version.dat","ppx/Default.ppx","emu_client.js","ld_remote.js")):
                data=z.read(name)
                base=Path(rel).name
                candidates.append({
                    "path":rel,
                    "size_bytes":len(data),
                    "sha256":hashlib.sha256(data).hexdigest(),
                    "magic_hex":data[:16].hex(),
                    "entropy":f"{entropy(data):.3f}",
                    "name_ref_count":sum(base in s for s in strings),
                })
    fields=["path","size_bytes","sha256","magic_hex","entropy","name_ref_count"]
    with args.out.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter="\t")
        w.writeheader(); w.writerows(candidates)
    print(f"{len(candidates)} rows -> {args.out}")

if __name__=="__main__":
    main()
