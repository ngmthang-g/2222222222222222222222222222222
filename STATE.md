# STATE — TLMTool 2.1.2

## STATUS
IN_PROGRESS

## COMPLETED
- A01 VERIFIED
- A02 VERIFIED
- A03 VERIFIED
- A04 VERIFIED_WITH_EXPLICIT_UNKNOWN
- A05 VERIFIED

## RECOVERY / REPAIR
- A01 artifacts were missing from GitHub even though A01 had been completed.
- A01 was re-verified from the supplied original ZIP and restored to GitHub.
- Restored:
  - `docs/tasks/A01.md`
  - `original_manifest/A01_SUMMARY.json`
  - `original_manifest/A01_FILE_TREE.txt.gz`

## A05 VERIFIED RESULTS
- Root `TLMTool.exe` is an AutoHotkey 1.1.37.02 launcher wrapper.
- If not elevated: `Run, *RunAs %A_ScriptFullPath%` then `ExitApp`.
- Inner target is exactly `A_ScriptDir\TLMTool.dist\TLMTool.exe`.
- Inner working directory is exactly `A_ScriptDir\TLMTool.dist`.
- Launcher checks `FileExist(exePath)` before launch.
- Launch action is `Run, %exePath%, %workDir%`.
- Missing inner target produces: `Không tìm thấy file: %exePath%`.
- Outer launcher does not use `RunWait`.
- No command-line argument forwarding is present in the recovered launcher script.
- Relationship is VERIFIED: outer launcher → elevated outer launcher when needed → inner Nuitka TLMTool.exe.

## FILES WRITTEN TO GITHUB IN A05
- `docs/tasks/A05.md`
- `original_manifest/A05_OUTER_LAUNCHER_SCRIPT.txt`
- `original_manifest/A05_RELATIONSHIP.json`
- `original_manifest/A05_EVIDENCE.tsv`

## CURRENT_TASK
A06 — Phân tích bootstrap/update.

## BLOCKERS
None for A06.

## NEXT_ACTION
On CONTINUE:
1. Read `PLAN.md`.
2. Read `STATE.md`.
3. Execute A06 only.
4. Recover and analyze the embedded AutoHotkey logic in `bootstrap.exe` and `update.exe` statically.
5. Separate VERIFIED behavior from UNKNOWN.
6. Persist A06 report/evidence to GitHub.
7. Advance NEXT_ACTION to A07 only after A06 is verified.
