#!/usr/bin/env python3
"""D07 static helper analyzer.

Never executes packaged helpers. Reads source-text JS and printable strings from
helper executables, hashes them, and extracts Frida RPC / HTTP endpoint surfaces.
"""
from __future__ import annotations
import argparse, hashlib, json, re, subprocess
from pathlib import Path

def sha256(p: Path) -> str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1<<20), b""): h.update(b)
    return h.hexdigest()

def strings(p: Path) -> list[str]:
    return subprocess.check_output(["strings","-a","-n","4",str(p)],text=True,errors="ignore").splitlines()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("dist",type=Path)
    ap.add_argument("--out",type=Path,default=Path("D07_HELPER_ANALYSIS.json"))
    args=ap.parse_args()
    d=args.dist.resolve()
    emu=(d/"emu_client.js").read_text(encoding="utf-8-sig")
    ld=(d/"ld_remote.js").read_text(encoding="utf-8-sig")
    rpc=re.findall(r"^\s*([A-Za-z0-9_]+):\s*function\s*\(",emu,re.M)
    endpoints=sorted(set(re.findall(r'["\'](/(?:emu_[A-Za-z0-9_]+|maps|ping)(?:\?[^"\']*)?)["\']',ld)))
    helpers=["forwarder.exe","bootstrap.exe","update.exe","tools/7z.exe","ppx/ProxifierSetup.exe"]
    result={
        "js":{
            "emu_client.js":{"sha256":sha256(d/"emu_client.js"),"lines":len(emu.splitlines()),"rpc_exports":rpc},
            "ld_remote.js":{"sha256":sha256(d/"ld_remote.js"),"lines":len(ld.splitlines()),"http_paths":endpoints},
        },
        "helpers":{},
    }
    for rel in helpers:
        p=d/rel
        result["helpers"][rel]={
            "sha256":sha256(p),
            "selected_strings":[s for s in strings(p) if any(k.lower() in s.lower() for k in (
                "SOCKS5 Forwarder","forwarder_mode.txt","UpdaterVersion","bootstrap.exe",
                "TLMTool.exe","7z.exe","Proxifier","127.0.0.1"
            ))][:100]
        }
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(args.out)

if __name__=="__main__":
    main()
