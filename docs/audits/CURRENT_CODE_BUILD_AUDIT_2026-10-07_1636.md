# Current code/build audit — 2026-10-07 16:36 +07

## Purpose

This audit was run before continuing K08, per user instruction:

- inspect the whole current repository first;
- identify what is already complete, what is missing, and any current errors;
- do not rewrite correct work;
- continue only from the first unfinished task;
- do not claim a build result that cannot actually be executed.

## Repository state

- default branch: `main`
- recursive tree entries: **577**
- current Phase K state before K08:
  - K01–K07: VERIFIED
  - K08: NEXT
- latest continuity commit before this audit: `4daaa0d9dc7724cb1c319fd72cc9560e525348c3`
  (`K07: verify recovery audit and advance to K08`).

No K08 task artifact or K08 completion commit existed before this audit.

## Current code-bearing files

The repository currently contains exactly **7 Python forensic/research scripts** and **1 shell verification script**:

- `tools/D01_EXTRACT_MODULES.py`
- `tools/D02_EXTRACT_RELATIONSHIPS.py`
- `tools/D03_EXTRACT_DEPENDENCIES.py`
- `tools/D04_BUILD_INTERNAL_GRAPH.py`
- `tools/D05_EXTRACT_MODULE_STRINGS.py`
- `tools/D06_INVENTORY_DATA.py`
- `tools/D07_ANALYZE_HELPERS.py`
- `tools/A08_VERIFY_FORENSIC.sh`

All eight files were fetched in full during this audit. No reconstructed application source tree exists yet.

### Static code review result

No blocking source defect was found in the current forensic scripts.

The scripts use Python standard-library modules plus external command-line `strings`; the shell verifier uses `sha256sum`, `awk`, and `python3`.

One non-blocking cleanliness issue exists:
- `tools/D04_BUILD_INTERNAL_GRAPH.py` imports `defaultdict` but does not use it.

This is not a runtime/build failure and was **not changed**, because the instruction is not to rewrite code that is already working.

## Build-system audit

The current repository contains **none** of the following:

- application `src/` tree;
- reconstructed `TLMTool.py` / tab source modules;
- `pyproject.toml`;
- `setup.py` / `setup.cfg`;
- `requirements*.txt`;
- Nuitka `.spec` build target;
- `Makefile` / `CMakeLists.txt`;
- GitHub Actions workflow under `.github/workflows/`.

The latest commit also has:
- **0 combined CI statuses**
- **0 GitHub Actions workflow runs**.

Therefore the reconstructed product cannot honestly be “built” yet. This is **not a regression**: PLAN.md explicitly locks application reconstruction to Stage S and Nuitka build to Stage T.

Current product build classification:

`NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED`

Do not create placeholder source/build files merely to manufacture a green build.

## Frozen-original integrity check

The newly supplied `TLMTool_2.1.2(7).zip` was verified locally against the repository's forensic contract:

- SHA-256: `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`
- ZIP CRC check: PASS
- entries: **1050**
- files: **1002**
- directories: **48**
- total uncompressed file bytes: **260,061,035**

This exactly matches `tools/A08_VERIFY_FORENSIC.sh`.

## Completed work that must not be rewritten

Phase K verified work:
- K01 — Daily authority/UI/dependency boundary
- K02 — shared account roster/session coordination
- K03 — Trừng Ác config/start/loop ownership
- K04 — NPC return / quest / 30-of-30 / cancel recovery
- K05 — item 40004000 / target / travel / summon
- K06 — combat / auto-train / timing / drift boundary
- K07 — heal / reconnect / death / Địa-phủ recovery

No contradiction found that requires reopening K01–K07.

## First unfinished work

The first unfinished PLAN/STATE task is exactly:

**K08 — Trừng Ác discard worker / equipment filtering and discard lifecycle audit.**

This audit therefore authorizes continuing K08 only.

## Errors/blockers

Current blockers are environmental/phase-related, not a broken source tree:

1. no reconstructed app source/build target yet by PLAN;
2. no Windows + live Thần Long runtime for end-to-end parity;
3. no CI workflow exists, so there is no CI build result to inspect.

No newly introduced code regression was found before K08.
