# STATE — TLMTool 2.1.2

## STATUS
IN_PROGRESS

## COMPLETED
- A01 VERIFIED
- A02 VERIFIED
- A03 VERIFIED
- A04 VERIFIED_WITH_EXPLICIT_UNKNOWN

## RECOVERY / REPAIR
- A01 artifacts were missing from GitHub even though A01 had been completed.
- A01 was re-verified from the supplied original ZIP.
- Restored to GitHub:
  - `docs/tasks/A01.md`
  - `original_manifest/A01_SUMMARY.json`
  - `original_manifest/A01_FILE_TREE.txt.gz`

## A01 VERIFIED RESULTS
- ZIP entries: 1,050
- Files: 1,002
- Directories: 48
- Uncompressed file bytes: 260,061,035
- Unsafe paths: 0
- Duplicate names: 0
- Symlinks: 0
- Extraction size mismatches: 0
- Complete tree lines: 1,050

## A04 KEY RESULTS
- Python runtime: CPython 3.10.11 x64.
- CPython build compiler: MSC v.1929 / MSVC 19.29.
- Nuitka use: VERIFIED.
- Inner `TLMTool.dist/TLMTool.exe`: Nuitka standalone build VERIFIED.
- Exact Nuitka version: UNKNOWN.
- Native compiler: GCC 15.2.0 / MinGW-W64 x86_64-msvcrt-posix-seh.
- Tcl/Tk runtime: 8.6.12 / 8.6.12.
- Root `TLMTool.exe`, `bootstrap.exe`, `update.exe` carry AutoHotkey 1.1.37.02 markers.

## CURRENT_TASK
A05 — Xác minh launcher ngoài và EXE trong `.dist`.

## BLOCKERS
None for A05.

## NEXT_ACTION
On CONTINUE:
1. Read `PLAN.md`.
2. Read `STATE.md`.
3. Execute A05 only.
4. Statistically verify the relationship between root `TLMTool.exe` and `TLMTool.dist/TLMTool.exe` using embedded AHK script/resource/static evidence without executing package binaries.
5. Record VERIFIED / UNKNOWN separately.
6. Persist A05 report/evidence to GitHub.
7. Advance NEXT_ACTION to A06 only after A05 is verified.
