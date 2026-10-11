# STATE — TLMTool 2.1.2 reconstruction

_Last checkpoint: 2026-10-12 Asia/Bangkok. Authority PLAN.md + SCOPE_LOCK.md. Detailed history append-only in PROJECT_STATUS.md._

## S151 VERIFIED — ORIGINAL F01 LOGIN 100-ROW MOUSEWHEEL COVERAGE, REAL WINDOWS TESTED

### Continued authority / no unrelated changes
- Re-read live PLAN.md, STATE.md S150 NEXT_ACTION S151, PROJECT_STATUS, SCOPE_LOCK and docs/tasks/S150.md; original C12 three-phase **real TLM observation still absent**, so old-rectangle vs (0,0) remains explicit UNKNOWN and its full Start UI toggle is not wired. Original ZIP hash `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, 93,715,901 bytes / 1,050 entries; original inner EXE hash `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, unchanged.
- F01 original Login evidence proves 100 Canvas-hosted account rows, real scrollbar and mousewheel in account region; `<Enter>/<Leave>` original binding micro-order UNKNOWN. Existing S37 `src/login_account_rows.py` had bound `<MouseWheel>` to Canvas and row Entry/Button/Combobox widgets, but not the blank inner frame, original header selector or heading Labels. **Real user-visible gap:** wheel over header/empty row area did not scroll.

### Actual S151 narrow user-visible implementation
- EDIT **only** `src/login_account_rows.py`: existing `_scroll_wheel` is bound directly to real `rows_inner` blank area, the original header selection button and all five original header Labels. No modification to scroll delta/direction, UI geometry, accounts selection/masking, save, game Login, native input sync or Proxy. **No global `bind_all` / mouse listener.** Actual original Enter/Leave microsequence NOT invented.
- NEW `tests/test_s151.py` (**12** source/behavior unit tests); NEW `tools/S151_WINDOWS_LOGIN_ACCOUNT_WHEEL_SMOKE.py` (**12** TRUE Tk-on-Win64 user-visible checks on an actual 100-row Canvas, blank/header/button/username wheel, outside no scroll, unchanged dummy `settings.ini` through shutdown); NEW `.github/workflows/s151-login-account-wheel.yml` (Windows full suite/Win32 Tk/inherited S37/S116/S150/C12/Info negative gate). Other original source unchanged.
- [PR #5](https://github.com/ngmthang-g/2222222222222222222222222222222/pull/5) reviewed exact four-file diff, marked ready and **squash merged to main `389fd1d9091205e77f14fb73f05ad0e43dc7544e`** only after all 3 real Windows workflows complete SUCCESS. NEW `docs/tasks/S151.md`, `docs/memory/S151_LOGIN_ACCOUNT_WHEEL_EVIDENCE.json`; updated STATE.md and append-only PROJECT_STATUS.md.

### Proven CURRENT Windows CI on PR head d2fb4aabad70d43b587f4f938d560d1fac08d7b8
- [S151 actual Win64 CI **38168294659**](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38168294659), job **114555354559 COMPLETED SUCCESS**: **2338/2338** Python unit tests, S86 **381 compiled Python files and 97 `src` modules**; native `PASS_NATIVE_S151_REAL_F01_ACCOUNT_CANVAS_WHEEL_TEST_OWNED_NO_GAME` **12/12 true Tk** checks. Inherited S37 original 100 rows/scroll, S116 real 300ms account field saving, S150 observer 7/7 native, S146/S147 C12 14/14 Win64 native all PASS. Signed Info `S151_PRODUCT=EXPLICITLY_BLOCKED_NO_GUI_NOT_PRODUCT`. S151 test-only artifact **11712499710**.
- [Independent S36 Windows package diagnostic **38168294652**](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38168294652), job **114555354565 COMPLETED SUCCESS**: **2338/2338** tests; actual packaged PyInstaller onedir diagnostic run `PASS_NATIVE_S36_PACKAGED_DIAGNOSTIC_FAIL_CLOSED_NOT_PRODUCT`, `S36_PRODUCT_EXE="NOT_BUILT"`; artifact **11712274188** DIAGNOSTIC ONLY, NOT user product.
- [Stage S regression **38168294650**](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38168294650), job **114555354481 COMPLETED SUCCESS**, **2338/2338**.
- DATA-2222 strictly READ ONLY; no changes original ZIP/EXE/PLAN/SCOPE_LOCK/B04/S59 or Proxy features. No user credentials or real game in CI.

### Explicit blockers
- S151 fixes only wheel missing target widgets, not complete 1:1 F01 mouse-enter/mouse-leave micro-order or a full signed account Login pipeline. F02 checkbox serialization and legacy captcha token still UNKNOWN.
- Original C12 show branch conflict and C14 embedded-view visibility lifecycle remain UNKNOWN; signed Info issuer/heartbeat, F05/F06 login game pixels/runtime, C07 and C19 native input hook payload, many tabs and full TLMTool product EXE NOT verified. S36 Windows diagnostic is NOT the product.

## NEXT_ACTION S152
1. Re-read LIVE PLAN.md, STATE.md and docs/tasks/S151.md, latest PROJECT_STATUS.md; inspect source before editing. Do not repeat S151/Login wheel, S149 CI resolution or S150 observer.
2. Investigate **one genuinely original-backed substantive user-visible Start/Login/Windows function**, particularly C14 real DWM detached preview/close with original C13 separate `Đóng xem` and `Hủy tách` behavior. Add only a safe independently source-proven action if missing geometry/embedded-preview lifecycle can be fenced without false parity. Otherwise identify alternate actually missing original functionality; no placeholder buttons, fake auth, game data or guessing.
3. For code changes use PR-native Win64 >=2338 full units / >=381 compiled, S151 native 12/12, S150 7/7, C12 14/14, inherited S37/S116, Stage S, independent S36 packaged diagnostic and signed Info product fail-closed. Keep original ZIP/PLAN/SCOPE_LOCK/B04/S59 and DATA-2222 read-only, Proxy excluded. Update touched files / actual evidence / remaining blockers; append PROJECT_STATUS and advance NEXT_ACTION S153 only after a real milestone.
