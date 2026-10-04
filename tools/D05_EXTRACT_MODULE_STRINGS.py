#!/usr/bin/env python3
"""D05 map printable constants/strings to exact-marker TLM module blocks.

Static-only: never executes TLMTool. The module block is defined from an exact
Nuitka <module NAME> marker to the next exact module marker, matching the D02
evidence model. Full and high-signal TSV outputs retain absolute EXE offsets.
"""
from __future__ import annotations
import argparse, csv, gzip, re, subprocess
from pathlib import Path

MARKER = re.compile(r"u?<module ([^>]+)>$")
API = re.compile(r"^(?:Get|Set|Create|Open|Read|Write|Close|Post|Send|Enum|Find|Show|Destroy|Dwm|Process|Virtual|Wait|Terminate|Client|Screen|Window|Is|Load|Free)[A-Z][A-Za-z0-9_]*$")
URL = re.compile(r"^(?:https?://|ws://|wss://)", re.I)
PATHISH = re.compile(r"(?:\.ini|\.json|\.txt|\.dll|\.exe|\.dat|\.js|\.ppx|\\\\|/)", re.I)

def normalize(raw: str) -> str:
    # Nuitka printable constants often expose one leading type/tag byte.
    return raw[1:] if raw and raw[0] in "auw" and len(raw) > 1 else raw

def categories(raw: str) -> list[str]:
    s=normalize(raw)
    if len(s)<3:
        return []
    out=[]
    if URL.search(s): out.append("URL")
    if PATHISH.search(s): out.append("PATH_FILE")
    if API.match(s) or s.startswith(("WM_","SWP_","SM_","DWM_")): out.append("API_CONST")
    if ("[" in s or "]" in s or any(k in s.upper() for k in ("ERROR","WARN","MODE","LAYOUT","SYNC","AUTO","HWND","PID"))) and len(s)>=4:
        out.append("LOG_UI")
    if s.startswith("_") and len(s)>=5 and re.fullmatch(r"_[A-Za-z0-9_]+",s):
        out.append("SYMBOL")
    elif "_" in s and len(s)>=8 and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]+",s):
        verbs=("toggle","refresh","update","start","stop","load","save","send","read","write","click","window","preview","sync","train","farm","login","map","item","memory","party","inject","permission","config","proxy","close","open","hide","show","move","coord","role","health","process","capture","detach","layout","arrange")
        if any(v in s.lower() for v in verbs): out.append("SYMBOL")
    if len(s)>=6 and (" " in s or any(ch in s for ch in ":;,.!?()[]{}")):
        out.append("UI_TEXT")
    return sorted(set(out))

def read_strings(exe: Path):
    txt=subprocess.check_output(["strings","-a","-n","3","-t","x",str(exe)],text=True,errors="ignore")
    rows=[]
    for line in txt.splitlines():
        m=re.match(r"^\s*([0-9a-fA-F]+)\s+(.*)$",line)
        if m: rows.append((int(m.group(1),16),m.group(2).strip()))
    return rows

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("dist",type=Path)
    ap.add_argument("internal_names",type=Path,help="D01_TLM_INTERNAL.json")
    ap.add_argument("--out",type=Path,default=Path("D05_MODULE_STRINGS.tsv.gz"))
    ap.add_argument("--high-signal-out",type=Path,default=Path("D05_HIGH_SIGNAL_STRINGS.tsv.gz"))
    args=ap.parse_args()
    import json
    names=set(json.loads(args.internal_names.read_text(encoding="utf-8"))["names"])
    strings=read_strings(args.dist.resolve()/"TLMTool.exe")
    markers=[]
    for off,val in strings:
        m=MARKER.fullmatch(val)
        if m and "%" not in m.group(1) and not any(ch.isspace() for ch in m.group(1)):
            markers.append((off,m.group(1)))
    fields=["module","marker_offset_hex","string_offset_hex","normalized","raw","categories"]
    full=[]; signal=[]
    pos=0
    for i,(start,name) in enumerate(markers):
        if name not in names: continue
        end=markers[i+1][0] if i+1<len(markers) else 1<<63
        while pos<len(strings) and strings[pos][0] <= start: pos+=1
        j=pos
        while j<len(strings) and strings[j][0] < end:
            off,raw=strings[j]
            cats=categories(raw)
            row={"module":name,"marker_offset_hex":hex(start),"string_offset_hex":hex(off),"normalized":normalize(raw),"raw":raw,"categories":"|".join(cats)}
            full.append(row)
            if cats: signal.append(row)
            j+=1
    for path,data in ((args.out,full),(args.high_signal_out,signal)):
        opener=gzip.open if path.suffix==".gz" else open
        with opener(path,"wt",encoding="utf-8",newline="") as f:
            w=csv.DictWriter(f,fieldnames=fields,delimiter="\t")
            w.writeheader(); w.writerows(data)
    print(f"full={len(full)} high_signal={len(signal)}")

if __name__=="__main__":
    main()
