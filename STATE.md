# STATE — TLMTool 2.1.2

## STATUS
IN_PROGRESS

## COMPLETED
- A01 VERIFIED
- A02 VERIFIED
- A03 VERIFIED
- A04 VERIFIED_WITH_EXPLICIT_UNKNOWN
- A05 VERIFIED
- A06 VERIFIED
- A07 VERIFIED

## A07 VERIFIED RESULTS
- Authoritative `ORIGINAL_MANIFEST.tsv` contains exactly **1002** data rows.
- Manifest bytes: **158973**.
- Manifest SHA-256: `c906b837c1c804984f26a262ebc563300076981e4008ce36b0c768a18513f4ee`.
- A02 and A03 path sets join exactly: missing 0.
- A02/A03 size mismatches: 0.
- A07 independently re-hashed all 1002 ZIP members against A02: 0 SHA-256 mismatches and 0 size mismatches.
- Classification totals remain EXE 7, DLL 12, PYD 32, DATA 23, RESOURCE 928.
- Robust PE remains 58: 57 x64 and 1 x86.
- Exact Nuitka version remains explicitly UNKNOWN.
- Both uploaded ZIP copies are byte-identical with archive SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`.

## A07 AUTHORITATIVE FILES
- `original_manifest/ORIGINAL_MANIFEST.tsv`
- `original_manifest/ORIGINAL_MANIFEST_SUMMARY.json`
- `original_manifest/ORIGINAL_MANIFEST.md`
- `original_manifest/ORIGINAL_MANIFEST_SHA256.txt`
- `docs/tasks/A07.md`

## CURRENT_TASK
A08 — Tạo bản copy forensic chỉ đọc.

## BLOCKERS
None for A08.

## NEXT_ACTION
On CONTINUE:
1. Read `PLAN.md`.
2. Read `STATE.md`.
3. Execute A08 only.
4. Create a forensic read-only copy/archive of the verified original package baseline without modifying package contents.
5. Record hashes for the forensic artifact and source archive.
6. Persist A08 report/evidence to GitHub.
7. Mark Gate A complete only after A08 is verified.
