#!/usr/bin/env bash
set -euo pipefail
EXPECTED='c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd'
FILE="${1:-./TLMTool_2.1.2_ORIGINAL_READONLY.zip}"
ACTUAL="$(sha256sum "$FILE" | awk '{print $1}')"
if [[ "$ACTUAL" != "$EXPECTED" ]]; then
  echo "FAIL: SHA-256 mismatch"
  echo "expected=$EXPECTED"
  echo "actual=$ACTUAL"
  exit 1
fi
python3 - "$FILE" <<'PY'
import sys, zipfile
p=sys.argv[1]
with zipfile.ZipFile(p,'r') as z:
    bad=z.testzip()
    infos=z.infolist()
    files=sum(not i.is_dir() for i in infos)
    dirs=sum(i.is_dir() for i in infos)
    total=sum(i.file_size for i in infos if not i.is_dir())
if bad is not None:
    raise SystemExit(f"FAIL: ZIP CRC error at {bad}")
if (len(infos),files,dirs,total)!=(1050,1002,48,260061035):
    raise SystemExit(f"FAIL: ZIP inventory mismatch: {(len(infos),files,dirs,total)}")
print("PASS: SHA-256 and ZIP inventory verified")
PY
