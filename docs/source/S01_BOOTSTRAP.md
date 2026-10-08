# S01 — First real Stage-S source bootstrap (NOT a playable cloned app)

## Scope and authority
Resumed from R01 final NEXT_ACTION. Re-read current PLAN.md, STATE.md, PROJECT_STATUS.md, SCOPE_LOCK.md; checked current GitHub absent `docs/tasks/S01.md`, `src/TLMTool.py` and source/test paths before creating them. Original contracts used: E01 main lifecycle, E02 Tk geometry, E03 15 potential-tab order & Info gate, E04 shared ownership, E05 settings.ini, B01/B02 screenshot baseline, A05 outer launcher CWD and R01 immutable resources. No previously completed source/docs rewritten. Proxy Phase Q remains no-development.

**New real Python source**:
1. `src/TLMTool.py`: explicit runnable Python entrypoint and `run_with_info_factory()` integration seam. `main()` **returns code 2 and does not start Tk**, because real InfoTab/authorization/heartbeat is not yet reconstructed; it prints a precise blocker. This is intentional fail-closed, not an EXE parity claim.
2. `src/shell.py`: real `TLMMainApp` constructs Tk/ttk Notebook on demand with 15 ordered potential original tab slots; starts every slot hidden except Info. Actual widgets/tabs are built **only when their real factory is injected**; without Info factory construction raises `MissingFeatureError`. No dummy controls. Real `TabLifecycle` selects from trusted caller-supplied granted keys; missing factory is always hidden. Dev-only keys stay hidden unless separately authorized; losing a visible tab or version/plan block falls back to Info. One-time lazy tab construction and old-selected refresh stop/new-selected refresh start/close cleanup tested. Root uses title TLMTool, transient `250x20`, withdraw/topmost, default Segoe UI 9, Notebook pack fill/expand margins 5; screen-anchored top-right dimensions modeled from E02 as 450 width, screenheight-80, screenwidth-450-10, y=0. **Exact geometry arithmetic remains high-confidence reconstruction, not recovered source expression.** Browser/screenshots not substituted for original contracts.
3. `src/settings_store.py`: real `%APPDATA%/TLMTool/settings.ini` service, `configparser.RawConfigParser(strict=False)` duplicate-last-wins, shared synchronized access, UTF-8, same-dir temporary file and `os.replace` atomic commit. E05's dated `settings.YYYYMMDD.ini` prior-file backup is preserved; **original backup-retention count UNKNOWN**, so S01 deletes **no backups**. Exact original control-character sanitizer scope and concrete lock class UNKNOWN; S01 uses a documented compatible RLock choice, not source-equivalent claim. Central `config.ini` intentionally unimplemented in this task.
4. `tests/test_s01.py`: seven headless stdlib `unittest` cases with fake Tk Notebook adapters (NOT actual Windows widget parity), permission/constructor gating, dev entitlement, one-time build, refresh start/stop + Info fallback, root layout model, duplicate-key + backup + atomic write, and fail-closed CLI.

User's approved terminology correction is implemented: tab label **Dồn**, never **Đồn**. The historical Gate-B screenshot and E03 record `Đồn`; current source intentionally uses the later user correction, without modifying original manifest/evidence.

## Actual local verification
- `python -m compileall -q src tests` — **PASS**.
- `python -m unittest discover -s tests -v` — **PASS 7/7** (after the backup implementation and the Dồn correction).
- GitHub was re-fetched for exact source paths, and UTF-8 byte lengths checked against the locally tested working tree. 4 files match: TLMTool.py=1074 B; shell.py=7564 B; settings_store.py=2292 B; tests/test_s01.py=5665 B. Source name/permission/backup guards directly inspected in returned GitHub content.
- **NOT RUN:** Tk actual window using X server/Windows, real InfoTab API/heartbeat/permissions, DLL/resource injection, game account management, screenshot parity, GitHub Actions, Nuitka Windows EXE build.

## Residual blockers — do NOT inflate status
- No genuine `TLMInfoTab` factory, login/startup server, permission_guard validation or heartbeat; therefore default `python src/TLMTool.py` is **intentionally not a functional GUI**. This makes it impossible to present a false functional interface.
- No other tab implementation: 15 original slots are a registration skeleton, not 15 finished features. The supplied Gate-B 11-tab visible state requires verified server authorization and corresponding real tab factories; default visible Info-only is the original fail-safe permission state, not final screenshot parity.
- Original single-instance Win32 mutex, splash, crash/tee logs, CPU monitor, forced quit, exact per-tab scroll and selected refresh ticks, full account-limit enforcement, icon.ico selection, Windows CWD/launcher and Stage-T Nuitka standalone packaging are not rebuilt in S01.
- Settings backup pruning and sanitization exact logic are not source-proof; test covers our implemented compatible behavior only.
- The previous `BUILD_BLOCKED_SOURCE_MISSING` blocker changes **now that real source exists** to **`SOURCE_PARTIAL_APP_STARTUP_BLOCKED_INFO_AUTH_AND_WINDOWS_BUILD_WORKFLOW_MISSING`**. Do not keep claiming the repository contains no application source. There is still **NO BUILT EXE** and no functional or visual parity certification.

## Files created/changed in S01
- New `src/TLMTool.py`, `src/shell.py`, `src/settings_store.py`, `tests/test_s01.py`.
- New `docs/source/S01_BOOTSTRAP.md`, `docs/source/S01_MODEL.json`, `docs/tasks/S01.md`.
- Append-only checkpoint `STATE.md` and `PROJECT_STATUS.md`.
- Existing Gate A–R, PLAN, SCOPE_LOCK and original archive unchanged. No Proxy behavior developed.

## NEXT_ACTION = S02
Read original InfoTab and permission_guard evidence (E01/E04/E05/E07, Info core/tabs docs) and existing source first. Implement the **smallest genuine Info startup/authentication state slice** with test doubles and explicit fail-closed permission decisions; do not invent server endpoints, grant permissions without response, show unsupported tabs or claim a usable game tool. Wire into S01 only where source contract supports it, then update state, tests and identify Windows UI build prerequisites.
