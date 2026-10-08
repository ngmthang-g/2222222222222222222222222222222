# CODE / BUILD AUDIT — 2026-10-08 (reconstruction TLMTool 2.1.2)

## 1. Verified GitHub baseline
- Main HEAD before audit `00f95aea9acf1c24f4dcae710fc229ce5cc20004`: complete recursive tree 756 entries, no truncation; 173 docs/tasks A01–O05, P01 absent.
- Read PLAN.md, STATE.md, PROJECT_STATUS.md, README.md, SCOPE_LOCK.md, exact source of all seven `tools/D01..D07` Python scripts and `tools/A08_VERIFY_FORENSIC.sh`.
- Existing repository contained **seven forensic `.py` scripts** and **one shell verifier**. It did NOT contain executable TLMTool application source (`main.py`, rebuilt UI modules, a `.csproj`, etc.), nor `pyproject`, requirements/build spec or GitHub Actions Windows build workflow.
- This is an actual **BUILD BLOCKER (SOURCE_MISSING)**, not a diagnosed compiler error; the original executable in user ZIP is not an EXE generated from this GitHub repository.

## 2. Code scripts reviewed (no accidental rewrite)
| File | Role | Current qualification |
|---|---|---|
| D01_EXTRACT_MODULES.py | Nuitka compiled module markers | Python static review; original EXE file and GNU strings required |
| D02_EXTRACT_RELATIONSHIPS.py | Static module-string references | Evidence only, not Python import runtime proof; possible quadratic performance pattern unbenchmarked |
| D03_EXTRACT_DEPENDENCIES.py | Dependency/version strings | Reference graph only; possible high scanning cost unbenchmarked |
| D04_BUILD_INTERNAL_GRAPH.py | Architecture from TSV evidence | Input schema must be supplied; not a product app |
| D05_EXTRACT_MODULE_STRINGS.py | Module-local string offsets and classifications | Static heuristic, not recovered source AST |
| D06_INVENTORY_DATA.py | Original ZIP resource hash/entropy | Read-only original package inspector |
| D07_ANALYZE_HELPERS.py | Original JS/helper metadata hashes | Reads bundled helper files; documenting Proxy is allowed, developing it is not |
| A08_VERIFY_FORENSIC.sh | ZIP SHA-256/CRC/file inventory | **Shell syntax and direct execution PASS when given actual original ZIP path** |

All seven Python files were read at source level. Their current GitHub versions were **not materialized and individually executed/py-compiled as a complete suite** in this audit. Do not label all D01–D07 PASS; no actual product build is possible.

## 3. Tests performed on original/read-only tools
- Original ZIP SHA256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, 1050 archive entries and full CRC/inventory verified by A08; result PASS. Inner original EXE SHA256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22` and size 47,450,112 bytes verified.
- Standalone `O04_AUDIT_EMBEDDED_ITEM_DATA.py` was `py_compile`-checked and executed read-only on the pinned ZIP: 29,983 META entries, 5,477 unique weapon ItemIDs and 0 missing/set mismatch. That script was **missing from GitHub**; fixed via preceding dedicated commit `fe23b809d55641351fa7dcd69a70e0b767b47799` adding `tools/O04_AUDIT_EMBEDDED_ITEM_DATA.py` only.
- Original packaged `emu_client.js` passed `node --check` (only JavaScript syntax); `ld_remote.js` contains AutoX XML-style `<frame>` UI layout, which standard Node parser does not support. The Node error **does not establish a bug** in the intended AutoX runtime.

## 4. Problems and risks — no invented runtime bugs
1. **BLOCKER:** No Stage-S rebuilt app source or Stage-T Windows EXE workflow, so product cannot currently be built from GitHub. Mark `BUILD_BLOCKED_SOURCE_MISSING`, not PASS.
2. **Confirmed missing reproducibility tool:** O04 verifier not in repository; fixed by adding tested existing script without touching O04 docs or original ZIP.
3. **Unmeasured source risk:** D02/D03 scan compiled strings per module in nested loops; potential high CPU on large EXE, but no timing regression measured and no change made.
4. **Unverified runtime risk:** emulator reader/ADB/Frida, remote listener and dummy/ACK-only endpoints not tested. Do not enable listener or expose hidden tabs merely because modules exist.
5. **No confirmed rebuilt-app crash:** no rebuilt product code/runtime exists from which such a crash can be observed.

## 5. Correct next work and build gates
- Original research A–O stays intact; O05 is static-complete (61 evidence items, 27 planned checks NOT_RUN). `STATE.md` next task was P01. P01 researched original emulator active/dormant gating, not a placeholder UI.
- Stage S must eventually create real app source from established feature contracts; Stage T must then create a reproducible Windows build, package required assets, and run smoke tests. This cannot truthfully be guaranteed today.
- `SOURCE`: BLOCKED_SOURCE_MISSING; `BUILD`: NOT_APPLICABLE; `WINDOWS_PARITY`: NOT_RUN; `RESEARCH_FORENSIC_ZIP`: VERIFIED; `O04_SCRIPT`: VERIFIED_READ_ONLY.
- Phase Q Proxy development remains excluded, existing permissions/scope are unchanged. Never claim build success on the basis of newly added documentation or forensic scripts.

Audit verdict: **RESEARCH_REPOSITORY_CONSISTENT / PRODUCT_BUILD_BLOCKED_SOURCE_MISSING**.
