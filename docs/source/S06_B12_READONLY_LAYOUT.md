# S06 — Native Windows original-backed read-only Info geometry

## Scope, inputs and immutability
Resumed from S05 `STATE.md` NEXT_ACTION. Read `PLAN.md`, `STATE.md`, `PROJECT_STATUS.md`, B12 screenshot-locked original Info geometry, `src/info_tab.py`, `src/info_binding.py`, S03/S04 tests and S05 native Tk smoke. Verified `docs/tasks/S06.md` absent at start. Prior S01–S05 source/tests and frozen original ZIP were not overwritten; S06 only updates the partial Info layout and creates new tests/CI. User correction **Dồn** remains unchanged. Phase Q Proxy remains excluded.

## Original evidence-backed visual targets
B12 measured original screenshot `TLMTool_f8iidp8FS8.png` (SHA256 `e536e081c653c72991344bfe505dd79cbcbf5fa52c9befa63214eb9d1516e4bc`). Original client 450×1000 on its capture desktop, full raster 452×1032. Info frame local anchor y≈59.

| S06 element | Original B12 screenshot | Rebuilt anchor relative to Info frame | Native Windows |
|---|---|---|---|
| Status border | x17 y110 width416 height44 | x3,y51,w416,h44 | **PASS** |
| Version value surface | x121 y165 w312 h19 | x107,y105,w312,h19 | **PASS** |
| Device code + Key surfaces | x121 y190/y215 w256 h19 | x107,y130/155,w256,h19 | **PASS** |
| License/windows/validity | x121 y240/265/290 w312 h19 | x107,y180/205/230,w312,h19 | **PASS** |
| Changelog text+bar region | x17 y354 to x432 y462 | x3,y295,w416,h109 | **PASS** |
| Status color | Development blue-purple is one *conditional* original state | Uses the original blue "checking" palette `#D1ECF1/#0C5460` because no trusted server state | **SAFE PARTIAL** |
| Changelog contents | Server-fed original live text | Explicit `Chưa xác minh`, editable only internally; widget state disabled | **SAFE PARTIAL** |

**Coordinate caveat:** original screenshot pixels include titlebar/outer border and were captured at 450×1000; S06 checks positions in the reconstructed Info frame. Matching relative anchors is not full screenshot parity, font/rendering parity, or proof of exact original layout expression.

## Actual source change
Updated `src/info_tab.py` **in place**, preserving `InfoDisplay` and `display_from_info_state` exactly from S03 (no new permissions/license grant behavior).
- Real native ttk/Tk page uses a 416×44 status bordered panel, blue-safe unverified status, B12-measured value rows, distinct widths 256 and 312, blank action slots where Copy and Nhập will eventually appear **only after real handlers exist**.
- Replaced passive changelog label with native `tk.Text` in `state='disabled'`, paired with a real vertical `ttk.Scrollbar`; original server data is not hardcoded.
- Stable structural members `_status`, `_values`, `_changelog`, `refresh_readonly` maintained for S03/S04 callers. Fake ttk adapters from old tests still have a documented non-native fallback without claiming native scroller parity.
- No fake actions, no login or RPC calls, no Proxy, no arbitrary server prices, no fake defaults for FREE/VIP. Normal `src/TLMTool.py` still intentionally exits 2.

New `tests/test_s06.py` provides six headless tests for B12 anchor constants, all six values, safe unknown/default view, visible absence of fake actions, planned scroll area and failure revocation.
New `tools/S06_WINDOWS_INFO_LAYOUT.py` runs **native Windows Tk**, measures each actual widget relative to the Info tab frame, checks exact expected rectangles and 25px row pitch, asserts the Text/Scrollbar and fail-closed Info-only state, checks shutdown, captures current client PNG, saves structured JSON. Does NOT access license server, game or original EXE.
New `.github/workflows/s06-native-info-layout.yml` runs these on Windows Python 3.10 with all Stage-S tests and uploads PNG+JSON.

## Verified source + live Windows test result
**[Actions run 37869205674](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37869205674)**, head SHA `09302f5c241d302c5ebfe68c282b2bfaeeba438b`, job `113623105567`, **COMPLETED SUCCESS**. The actual job log was fetched:
- Compile-all `src tests tools/S06_WINDOWS_INFO_LAYOUT.py`: **PASS**.
- Combined S01–S06 headless test suite: **37/37 PASS** (`Ran 37 tests in 0.018s`), consisting S01=7, S02=8, S03=6, S04=10, S06=6. No S05 unit module (S05 native Windows smoke instead).
- Native Windows S06 layout script: **`PASS_NATIVE_READONLY_LAYOUT_ANCHORS`**. Root client 450×688 on 1024×768 runner, as S05 (not full B12 450×1000 environment).
- Actual status rectangle `[3,51,416,44]`; first value `[107,105,312,19]`; device/key `[107,130/155,256,19]`; license/windows/validity `[107,180/205/230,312,19]`; changelog `[3,295,416,109]`; live vertical scrollbar present **TRUE**, `Text` disabled, exact safe unknown license fields.
- Real client PNG created, and root destroy callback marked binding closed **TRUE**. Actions uploaded `s06-native-b12-info-layout` artifact ID **11589915070** with PNG+JSON (link in job/log). Native Windows screenshot capture succeeded; original B12 pixel diff **NOT_RUN**.
- Earlier `src/info_tab.py` prior to S06 displayed only plain status/changelog labels with vertical 23px pitch; this is now an actual measured improvement, not repeating S05.

## Open gaps (do not inflate parity)
- B12 screenshot 11 visible tabs with Info at the right, while reconstructed safe Info-only state shows only Info (15 potential registered slots). Production permission engine/real feature constructors still missing.
- Original Info app code/device fingerprint, key, license type, max window view, expiry, server changelog, price/contact/catalog cannot be fabricated. The current safe `Chưa xác minh` value is a **reconstruction placeholder, not original screenshot content**.
- Original B12 status panel development purple fill appears only with a verified actual version/server status; S06 intentionally keeps checking blue. Exact fonts, Tk DPI, theme, outer raster and pixel diff remain unverified.
- Main entrypoint still returns exit 2; no authentic license RPC/heartbeat, functional game controls, Stage-T Nuitka EXE build, original EXE runtime or Proxy work occurred.

**S06 STATUS = NATIVE_WINDOWS_B12_INFO_ANCHORS_37_TESTS_PASS / FULL_UI_AND_GAME_PARITY_BLOCKED.**

## NEXT_ACTION S07
Read PLAN.md/STATE.md/current source first. Continue the **remaining B12 verified passive content sections** (server-dependent pricing placeholder, support/contact labels, system catalog placeholder and correct separators) only where original static/screenshot evidence supports; do not invent prices, endpoints or clickable handlers, and do not undo the now-verified Info status/row/scroll geometry. Add tests and native Windows Tk measurements, preserve Info-only authorization and report actual source build blocker. After that, prioritize original-backed functional Start/Login slices instead of repeated cosmetic work.
