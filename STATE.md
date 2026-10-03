# STATE — TLMTool 2.1.2

## STATUS
IN_PROGRESS

## GATE A
**COMPLETE / VERIFIED**

## GATE B
IN_PROGRESS

## COMPLETED
- A01 VERIFIED
- A02 VERIFIED
- A03 VERIFIED
- A04 VERIFIED_WITH_EXPLICIT_UNKNOWN
- A05 VERIFIED
- A06 VERIFIED
- A07 VERIFIED
- A08 VERIFIED
- B01 VERIFIED
- B02 VERIFIED
- B03 VERIFIED
- B04 VERIFIED
- B05 VERIFIED
- B06 VERIFIED
- B07 VERIFIED
- B08 VERIFIED
- B09 VERIFIED
- B10 VERIFIED
- B11 VERIFIED
- B12 VERIFIED

## B12 VERIFIED RESULTS
- Used binary-first workflow.
- Original compiled `info_tab.py` / `TLMInfoTab` evidence recovered before screenshot measurement.
- Direct i-selected screenshot: `TLMTool_f8iidp8FS8.png`, SHA-256 `e536e081c653c72991344bfe505dd79cbcbf5fa52c9befa63214eb9d1516e4bc`, 452 × 1032.
- i selected bridge at y=56: x=377..402.
- B02 selected-state coverage is now complete: direct screenshots exist for all 11 tabs.
- Header/title and separator measured.
- Current version-status panel measured:
  - `Bạn đang dùng bản phát triển: v2.1.2`
  - #E2E3FF / #4A00E0
- Information rows measured:
  - version 2.1.2
  - runtime/device-derived app ID d9ab65e4e118663e
  - blank key + Nhập
  - FREE
  - 1/1
  - Vĩnh viễn
- Changelog scroll region/current visible content recorded.
- Exact screenshot changelog lines are classified server-fed/current because binary contains placeholder/update path rather than those lines.
- Price block current values recorded and classified server-fed/current via price handling.
- Contact links and support button measured; static Facebook URL and log-support workflow recorded.
- Auto-system current six-title catalog recorded; original module dynamically rebuilds it from server `price_tools`.
- Conditional hidden original UI (manual/auto update, new-features panel, license entry, log popup) recorded without invented pixels.

## B12 FILES
- `docs/tasks/B12.md`
- `docs/ui/B12_INFO_GEOMETRY.tsv`
- `docs/ui/B12_INFO_VISIBLE_STATE.json`
- `docs/ui/B12_INFO_STATIC_EVIDENCE.tsv`
- `docs/ui/B12_SCREENSHOT_EVIDENCE.tsv`
- `docs/UI_BASELINE_TLM.md`
- B02 selected-state evidence updated to 11/11.

## CURRENT_TASK
B13 — Màu/font/button metrics.

## BLOCKERS
None for B13. Gate B now has direct visual coverage for every tab label and per-tab baseline B03–B12.

## WORKFLOW
For B13:
1. consolidate screenshot-measured colors/font/style tokens from B01–B12;
2. cross-check against original binary style strings where available;
3. distinguish exact raster colors from toolkit/theme-dependent borders/anti-aliasing;
4. do not replace screenshot facts with guessed source styling.

## DO_NOT_TOUCH
- Preserve Gate A forensic baseline unchanged.
- Keep B12 server/runtime/update/license behavior deferred.
- Do not hardcode current server-fed changelog/price/tool catalog as permanent package constants.
- B13 may normalize the style inventory but must not alter per-tab geometry.

## NEXT_ACTION
On CONTINUE:
1. Read `PLAN.md`.
2. Read `STATE.md`.
3. Execute **B13 only**.
4. Consolidate exact screenshot colors, font evidence, button fills/borders, entry/combobox surfaces, scrollbar/theme metrics across B01–B12.
5. Cross-check original binary style tokens.
6. Persist B13 metric inventory and update `docs/UI_BASELINE_TLM.md`.
7. Advance to B14 only after B13 is verified.
