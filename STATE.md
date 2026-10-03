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

## A06 VERIFIED RESULTS
- Recovered exact embedded AutoHotkey payloads from `bootstrap.exe` and `update.exe` without executing them.
- `bootstrap.exe`: 350-byte / 24-line script; waits for new file then retries `FileMove` overwrite every 500 ms until success; no timeout.
- `update.exe`: 9,030-byte / 284-line updater script, internal version 1.2.
- Update sources: Pixeldrain or Google Drive; invalid/missing argument falls back to compiled default Drive file ID.
- Drive/default ZIP password is `1`; Pixeldrain ZIP password is empty.
- Download uses generated hidden PowerShell, TLS 1.2, `HttpWebRequest`, and a 65,536-byte buffer.
- Explicit download acceptance before extraction: ZIP exists and size >= 10,000 bytes.
- No cryptographic hash or digital-signature verification of downloaded ZIP is present in recovered AHK script.
- Extraction prefers bundled `tools\7z.exe`, falls back to `C:\Program Files\7-Zip\7z.exe`.
- Extraction success requires both `EXITCODE=0` and `Everything is Ok` in unzip log.
- Update package selector: first extracted directory matching `TLMTool*`, then its `TLMTool.dist`.
- New `TLMTool.dist` contents are copied into current `A_ScriptDir` (current installed `TLMTool.dist`) excluding `update.exe`.
- Outer root `TLMTool.exe` is not copied by the recovered update flow.
- New updater is staged as `update\update.exe`; bootstrap replaces current `update.exe` after it becomes movable.
- Final relaunch is `A_ScriptDir\TLMTool.exe`, which is the inner TLM executable because updater itself is located in `TLMTool.dist`.

## CURRENT_TASK
A07 — Lập `ORIGINAL_MANIFEST`.

## BLOCKERS
None for A07.

## NEXT_ACTION
On CONTINUE:
1. Read `PLAN.md`.
2. Read `STATE.md`.
3. Execute A07 only.
4. Consolidate A01 tree + A02 SHA-256 + A03 classification + A04 runtime facts + A05 launcher relation + A06 bootstrap/update evidence into the authoritative `ORIGINAL_MANIFEST` set.
5. Verify counts/hashes and preserve UNKNOWN values explicitly.
6. Persist A07 artifacts to GitHub.
7. Advance NEXT_ACTION to A08 only after A07 verification.
