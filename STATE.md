# STATE — TLMTool 2.1.2

## STATUS
IN_PROGRESS

## COMPLETED
- A01 DONE
- A02 VERIFIED
- A03 VERIFIED
- A04 VERIFIED_WITH_EXPLICIT_UNKNOWN

## A04 KEY RESULTS
- Python runtime: CPython 3.10.11 x64.
- CPython build compiler: MSC v.1929 / MSVC 19.29.
- Nuitka use: VERIFIED from direct runtime/compiler markers.
- Inner `TLMTool.dist/TLMTool.exe`: Nuitka standalone build VERIFIED.
- Exact Nuitka version: UNKNOWN; no unsupported guess was made.
- Native compiler for inner TLM/Nuitka binary: GCC 15.2.0, MinGW-W64 x86_64-msvcrt-posix-seh, Brecht Sanders r6.
- Inner PE linker header value: 2.46.
- Tcl/Tk runtime: 8.6.12 / 8.6.12.
- Distribution contains 0 `.py`, 0 `.pyc`, 0 `.pyo` files.
- Root `TLMTool.exe`, `bootstrap.exe`, `update.exe` carry AutoHotkey 1.1.37.02 compiler/runtime markers; behavior deferred to A05/A06.

## CURRENT_TASK
A05 — Xác minh launcher ngoài và EXE trong `.dist`.

## BLOCKERS
None for A05.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md.
2. Read STATE.md.
3. Execute A05 only.
4. Statistically verify the relationship between root `TLMTool.exe` and `TLMTool.dist/TLMTool.exe`, using embedded AHK script/resource/static evidence without executing package binaries.
5. Record VERIFIED / UNKNOWN separately.
6. Persist A05 report/evidence to GitHub.
7. Advance NEXT_ACTION to A06 only after A05 is verified.
