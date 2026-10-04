#!/usr/bin/env python3
"""D03 static dependency evidence extractor for frozen TLMTool.

Does not execute packaged code. It reads GNU strings from the inner EXE,
uses the D01 canonical TSV/TSV.GZ inventory, reports package version literals
from known version modules, and counts conservative TLM->dependency references.
"""
from __future__ import annotations
import argparse, csv, gzip, json, re, subprocess
from pathlib import Path

MARKER = re.compile(r"u?<module ([^>]+)>")
VERSION = re.compile(r"^\d+(?:\.\d+){1,4}(?:[-+._A-Za-z0-9]*)?$")

VERSION_MODULES = {
    "requests": "requests.__version__",
    "urllib3": "urllib3._version",
    "Pillow/PIL": "PIL._version",
    "cryptography": "cryptography.__about__",
    "idna": "idna.package_data",
    "certifi": "certifi",
    "PyAutoGUI": "pyautogui",
    "pyperclip": "pyperclip",
    "PyScreeze": "pyscreeze",
    "PyTweening": "pytweening",
    "PyMsgBox": "pymsgbox",
    "PyGetWindow": "pygetwindow",
    "six": "six",
}
FAMILY_PREFIXES = {
    "requests": ("requests",), "urllib3": ("urllib3",), "frida": ("frida",),
    "psutil": ("psutil",), "PIL": ("PIL",), "pynput": ("pynput",),
    "pyautogui": ("pyautogui",), "pyperclip": ("pyperclip",),
    "keyboard": ("keyboard",), "mouse": ("mouse",),
    "typing_extensions": ("typing_extensions",), "win32con": ("win32con",),
    "win32api": ("win32api",), "win32gui": ("win32gui",),
    "win32process": ("win32process",), "win32ui": ("win32ui",),
}

def open_text(path: Path):
    return gzip.open(path, "rt", encoding="utf-8") if path.suffix == ".gz" else path.open("r", encoding="utf-8")

def load_inventory(path: Path):
    rows=[]
    with open_text(path) as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if r.get("confidence") != "REJECTED":
                rows.append(r)
    return rows

def read_strings(exe: Path):
    out=subprocess.check_output(["strings","-a","-n","3","-t","x",str(exe)],text=True,errors="ignore")
    rows=[]
    for line in out.splitlines():
        m=re.match(r"^\s*([0-9a-fA-F]+)\s+(.*)$",line)
        if m: rows.append((int(m.group(1),16),m.group(2).strip()))
    return rows

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("dist",type=Path)
    ap.add_argument("d01_inventory",type=Path)
    ap.add_argument("--out",type=Path,default=Path("D03_RAW_DEPENDENCIES.json"))
    args=ap.parse_args()
    exe=args.dist.resolve()/"TLMTool.exe"
    inv=load_inventory(args.d01_inventory)
    internal={r["name"] for r in inv if r["category"]=="TLM_INTERNAL" and r.get("confidence")=="HIGH"}
    strings=read_strings(exe)
    markers=[]
    for off,v in strings:
        m=MARKER.fullmatch(v)
        if m and "%" not in m.group(1) and not any(ch.isspace() for ch in m.group(1)):
            markers.append((off,m.group(1)))

    versions={}
    for family,mod in VERSION_MODULES.items():
        hits=[o for o,n in markers if n==mod]
        if not hits: continue
        center=hits[0]
        near=[(o,v) for o,v in strings if center-5000 <= o <= center+500]
        candidates=[]
        for i,(o,v) in enumerate(near):
            vv=v[1:] if v[:1] in "auw" else v
            if VERSION.fullmatch(vv):
                # Stronger if __version__ appears nearby.
                if any("__version__" in x[1] for x in near[max(0,i-4):min(len(near),i+5)]):
                    candidates.append({"version":vv,"offset_hex":hex(o)})
        if candidates: versions[family]=candidates[-1]

    usage={k:set() for k in FAMILY_PREFIXES}
    for idx,(start,src) in enumerate(markers):
        if src not in internal: continue
        end=markers[idx+1][0] if idx+1<len(markers) else 10**18
        for off,raw in strings:
            if off <= start: continue
            if off >= end: break
            vals=[raw]
            if raw and raw[0] in "auw" and len(raw)>1: vals.append(raw[1:])
            for value in vals:
                for fam,prefixes in FAMILY_PREFIXES.items():
                    if any(value==p or value.startswith(p+".") for p in prefixes):
                        usage[fam].add(src)

    result={
        "versions":versions,
        "direct_tlm_reference_sources":{k:sorted(v) for k,v in usage.items() if v},
        "relation_status":"STATIC_REFERENCE_NOT_IMPORT_PROOF",
    }
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(args.out)

if __name__=="__main__":
    main()
