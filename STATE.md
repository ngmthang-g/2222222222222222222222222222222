# STATE — TLMTool 2.1.2 reconstruction

_Last checkpoint: 2026-10-12 Asia/Bangkok. Authority: PLAN.md + SCOPE_LOCK.md; append-only history: PROJECT_STATUS.md._

## S147 IMPLEMENTED — C12 authorization-provider exception fail-closed; WIN64 CI NOT YET VERIFIED

### Resumed baseline
- Read LIVE PLAN.md / STATE.md S146 NEXT_ACTION S147 / PROJECT_STATUS.md, docs/tasks/S146.md and C12 original evidence, and current Start/C12 sources.
- Independently SHA256 verified uploaded frozen original ZIP `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; inner original EXE `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`. Both READ ONLY.
- C12 original-specific show at (0,0) versus generic saved-position restore conflict still unresolved; no Start Hiện hết toggle wired. Original game build, authentic signed Info, F06 RGB/pixel reference and runtime remain unverified.

### Actual changes made
- Narrow `src/window_hide.py` S146 `C12HideAll.show_documented_origin` authorization checks only: an unexpected `allowed()` provider exception is now a denial on entry/before EACH window/after ALL moved. The existing `stop("CANCELLED")` records PARTIAL if any Win32 movement occurred, instead of erroneously allowing HIDDEN state to persist when callback throws. No change to `hide()`, coordinates, SetWindowPos, Win32 backend or UI.
- Added 3 `tests/test_s146.py` regressions: callback throws before first native move, mid-batch after first, after last; no false success, correct PARTIAL/no silent retry.
- Extended existing true two-Tk-HWND Windows smoke `tools/S146_WINDOWS_C12_SHOW_ORIGIN_SMOKE.py` with 3 native readback checks: hide two, move one at (0,0), exception before second, verify mixed real geometry/size and PARTIAL denial of subsequent retry. Test-owned adapter only, NOT actual game.
- NEW `docs/tasks/S147.md`, `docs/memory/S147_C12_AUTH_EXCEPTION_EVIDENCE.json`. `PLAN.md`, `SCOPE_LOCK.md`, original ZIP, B04/S59 assets, reference DATA-2222 and Proxy untouched. Prior S01–S145 production source preserved.
- Existing S146 Windows workflow watches all three changed files. **No current S147 native CI result claimed.** Expected full unit suite >=2314 (prior verified 2311 + 3), >=376 compiled and 97 production modules, native C12 >=14 checks (prior 11 + 3). Independent S36 diagnostic and Stage S must also pass before S147 can be marked VERIFIED.

### Last established green baseline (S146, not S147)
- S146 full Win64 run 38163848439: 2311/2311, 376 compiled, 11/11 C12 native real TEST-OWNED Tk checks, inherited S145–S116 passed; signed Info still BLOCKED.
- Independent S36 38163848387 and Stage S 38163848465 SUCCESS, but S36 EXE DIAGNOSTIC ONLY.
- S147 source/tests/docs commits exist. **Windows CI outcome for S147 PENDING/UNVERIFIED.**

### Remaining blockers
- Original released C12 show previous-rectangle vs (0,0) behavior is UNKNOWN; no UI toggle.
- No authorized signed Info provider/heartbeat; real client GameAssembly/RoleData/Bag not verified; login pixel x/y/RGB/tolerance unknown; C07 auto geometry/C14 detached tiles and other tabs incomplete.
- No real-game runtime parity or complete TLMTool product EXE. DATA reference repository READ ONLY; no Proxy scope.

## NEXT_ACTION S148
1. Check actual current S147 GitHub Win64 S146 workflow run for >=2314 full Python tests, >=376 compiled, 14 C12 true native two-HWND assertions and inherited S145–S116 native. Also check independent S36 diagnostic and Stage S at the S147 commit; do not reuse S146's older green claim.
2. If tests fail, fix the exact failing condition only and re-run. If all pass, mark S147 VERIFIED and append exact native Windows run IDs/results in STATE.md and PROJECT_STATUS.md.
3. Resume original-backed meaningful visible Start/Login/Windows parity. Do not manufacture original C12 restore route, Info permissions, F06 login pixels, DLL hooks, Proxy or new UI. Keep `NEXT_ACTION S149` after S148 milestone, with precise changes/blockers.
