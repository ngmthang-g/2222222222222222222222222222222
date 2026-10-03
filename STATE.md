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
- B13 VERIFIED_WITH_EXPLICIT_UNKNOWN_FONT_POINT_SIZE

## B13 VERIFIED RESULTS
- Consolidated screenshot/style evidence across B01–B12.
- Locked exact base raster colors:
  - #F0F0F0 client
  - #FFFFFF selected/input
  - #D9D9D9 notebook separator
  - #DCDCDC LabelFrame border
  - #7A7A7A entry/combobox border
  - #333333 checkbox/radio stroke
  - #A0A0A0 Info separators
  - #CDCDCD scrollbar thumb
- Consolidated semantic action palette:
  - #388E3C, #2E8B57, #2E7D32, #4169E1, #1565C0, #0277BD,
    #C62828, #8E24AA, #795548, #B48608, #808080, #616161,
    #E65100, #F44336.
- Verified classic raised button edge behavior:
  - one-pixel light top/left edge
  - one-pixel black/dark right/bottom edge
  - representative highlight shades recorded.
- Common raster metrics locked:
  - 13×13 checkbox/radio
  - ~21 px ttk combobox
  - ~19–21 px entry/spin
  - 15 px vertical scrollbar
  - ~21–23 px small custom buttons
  - 30 px bottom Start outer / 28 px fill
- Original binary cross-check:
  - Segoe UI occurs 226 times
  - global default_font / *Font
  - Bold.TLabelframe.Label
  - White.TCombobox
  - semantic color tokens corroborated.
- Font raster envelopes recorded.
- Exact numeric Tk source font point sizes remain explicit UNKNOWN because neither compiled readable strings nor screenshot DPI prove them.
- ClearType/native-theme anti-aliasing classified environment-sensitive rather than hardcoded pixel palette.

## B13 FILES
- `docs/tasks/B13.md`
- `docs/ui/B13_STYLE_PALETTE.tsv`
- `docs/ui/B13_CONTROL_METRICS.tsv`
- `docs/ui/B13_FONT_METRICS.tsv`
- `docs/ui/B13_STATIC_STYLE_EVIDENCE.tsv`
- `docs/UI_BASELINE_TLM.md`

## CURRENT_TASK
B14 — Pixel comparison checklist.

## BLOCKERS
None. B01–B13 provide geometry, direct selected-state evidence for all tabs, per-tab baselines, palette and common control metrics.

## DO_NOT_TOUCH
- Preserve Gate A forensic baseline unchanged.
- Do not convert B13's unknown numeric font point size into a claimed fact.
- Do not hardcode ClearType fringe colors.
- B14 is a comparison/checklist task only; do not begin source reconstruction.

## NEXT_ACTION
On CONTINUE:
1. Read `PLAN.md`.
2. Read `STATE.md`.
3. Execute **B14 only**.
4. Build the pixel-comparison checklist from B01–B13.
5. Define strict vs environment-sensitive comparison regions/tolerances.
6. Persist B14 checklist/report and update `docs/UI_BASELINE_TLM.md`.
7. Close Gate B only if the checklist covers all baseline tabs/regions without unresolved visual blockers.
