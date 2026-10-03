# STATE — TLMTool 2.1.2

## STATUS
IN_PROGRESS

## GATE A
**COMPLETE / VERIFIED**

## COMPLETED
- A01 VERIFIED
- A02 VERIFIED
- A03 VERIFIED
- A04 VERIFIED_WITH_EXPLICIT_UNKNOWN
- A05 VERIFIED
- A06 VERIFIED
- A07 VERIFIED
- A08 VERIFIED

## A08 VERIFIED RESULTS
- Created byte-for-byte forensic archive copy: `TLMTool_2.1.2_ORIGINAL_READONLY.zip`.
- Source and forensic copy size: 93,715,901 bytes.
- Source and forensic SHA-256: `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`.
- `cmp` source vs forensic: IDENTICAL.
- Forensic copy permission mode: 0444.
- Forensic directory has no write bits (mode 2555; inherited setgid).
- ZIP integrity recheck: PASS.
- ZIP inventory remains 1050 entries = 1002 files + 48 directories; 260,061,035 uncompressed file bytes.
- Authoritative ORIGINAL_MANIFEST.tsv SHA-256 remains `c906b837c1c804984f26a262ebc563300076981e4008ce36b0c768a18513f4ee`.

## CURRENT_MILESTONE
GIAI ĐOẠN B — Khóa giao diện.

## CURRENT_TASK
B01 — Chốt kích thước cửa sổ chính.

## BLOCKERS
None for B01.

## DO_NOT_TOUCH
- Preserve Gate A forensic baseline unchanged.
- Do not modify the forensic original archive.
- Do not replace UNKNOWN values from Gate A with guesses.
- Do not begin behavior implementation while only UI baseline evidence is being measured.

## NEXT_ACTION
On CONTINUE:
1. Read `PLAN.md`.
2. Read `STATE.md`.
3. Execute **B01 only**.
4. Use the supplied TLM screenshots as baseline evidence to determine/record the main-window dimensions and measurement confidence.
5. Do not infer hidden dimensions that screenshots do not support; mark them UNKNOWN if necessary.
6. Persist B01 report/evidence to GitHub.
7. Advance to B02 only after B01 is verified.
