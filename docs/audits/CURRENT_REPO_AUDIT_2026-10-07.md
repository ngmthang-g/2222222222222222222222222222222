# Current repository audit — 2026-10-07

## Why this audit was run

The continuation appeared stalled, so the repository was checked from the current GitHub state before doing any more K05 work.

Rule used: **do not rewrite work that is already complete and correct; continue only from the first unfinished task.**

## 1. Exact current milestone

Authoritative files agree:

- `PLAN.md`: research-first reconstruction; Stage S implementation is later.
- `STATE.md`: K01–K04 complete, **K05 is NEXT**.
- `PROJECT_STATUS.md`: K01–K04 verified, **K05 is current**.

GitHub search found **no K05 artifact and no K05 completion commit**.

Therefore the correct continuation point is exactly:

**K05 — Trừng Ác Lệnh bag/use target extraction / travel / stuck-target accounting / summon audit.**

No K01–K04 artifact needs to be rewritten.

## 2. What is complete

Repository-wide research status already frozen in STATE/PROJECT_STATUS:

- A01–A08 complete.
- B01–B14 complete.
- C01–C20 static/visual complete, runtime parity deferred where documented.
- D01–D08 complete.
- E01–E10 complete.
- F01–F11 complete research handoff.
- G01–G12 complete.
- H01–H15 static handoff complete.
- I01–I12 static handoff complete.
- J01–J14 static research closed; live Windows/game parity deferred.
- K01 Daily authority/surface complete.
- K02 shared Daily roster/session/coordinator complete.
- K03 Trừng Ác config/outer loop complete.
- K04 NPC/quest/30-of-30/stuck-cancel complete.

K04 was previously recovered from a partial commit state; its missing evidence artifact has already been added and STATE/PROJECT_STATUS now agree. It is not pending work anymore.

## 3. Repository content / code reality

Current GitHub tree contains **563 entries**.

The repository currently consists primarily of:
- research handoff documents under `docs/`;
- original-package manifests under `original_manifest/`;
- seven static forensic Python tools under `tools/`;
- PLAN/STATE/status/scope files.

Static Python tools currently present:
1. `tools/D01_EXTRACT_MODULES.py`
2. `tools/D02_EXTRACT_RELATIONSHIPS.py`
3. `tools/D03_EXTRACT_DEPENDENCIES.py`
4. `tools/D04_BUILD_INTERNAL_GRAPH.py`
5. `tools/D05_EXTRACT_MODULE_STRINGS.py`
6. `tools/D06_INVENTORY_DATA.py`
7. `tools/D07_ANALYZE_HELPERS.py`

No reconstructed application source tree exists yet.

Specifically, the current tree has no recovered implementation/build entry such as:
- `src/`;
- application package/source directory;
- `pyproject.toml`;
- `setup.py`;
- `requirements*.txt`;
- PyInstaller/Nuitka `.spec` for the reconstructed app;
- `.github/workflows/` build workflow.

This is consistent with PLAN: **Stage S implementation has not started yet.**

## 4. Buildability status

### Original TLM specimen

The frozen original remains the research authority:

- archive SHA-256: `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`
- inner EXE SHA-256: `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`
- inner EXE size: **47,450,112 bytes**.

### Reconstructed application build

**NOT_APPLICABLE_YET / NO BUILD TARGET EXISTS.**

There is no reconstructed app source/build system in the repository yet, so it would be false to claim that the reconstructed product was rebuilt successfully.

This is **not a new build break**. It is the expected state before Stage S.

### Research tooling

The static-analysis tools remain present and unchanged. This audit did not modify those scripts.

No GitHub Actions workflow exists, so there is no CI build result to report.

## 5. Errors/regressions found by this audit

No evidence of a code regression was found because the reconstructed application code has not started.

The actual continuity problem was procedural:
- the user-visible continuation appeared stalled;
- K05 had not been persisted;
- the correct response is to resume K05, not restart earlier Daily work and not jump to Stage S.

No completed K01–K04 file is being rewritten as part of this recovery.

## 6. Scope lock

Do **not** create a placeholder application/build system merely to make a green build before Stage S.

Doing so would violate:
- `PLAN.md`;
- `SCOPE_LOCK.md`;
- the user's “không viết lại phần đã đúng” rule.

The safe build-preserving action during K05 is docs/evidence-only changes.

## 7. Next action

Proceed with K05 only:
- Trừng Ác Lệnh item ID and bag lookup;
- internal use-item retries;
- target extraction from GameDialog with UseItemData fallback;
- travel ownership;
- repeated target-failure state;
- summon dialog/button behavior.

After K05, update STATE/PROJECT_STATUS and advance to K06 only if K05 is verified.
