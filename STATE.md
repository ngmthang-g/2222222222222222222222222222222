# STATE — TLMTool 2.1.2

## STATUS
IN_PROGRESS

## GATE A
**COMPLETE / VERIFIED**

## GATE B
**COMPLETE / VERIFIED**

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
- B14 VERIFIED

## B14 VERIFIED RESULTS
- Built the Gate-B pixel-comparison contract from B01–B13.
- Defined six comparison classes:
  - S0 STRICT_RASTER
  - S1 STRICT_GEOMETRY_NATIVE_RENDER
  - T1 TEXT_ENVELOPE
  - D1 DYNAMIC_CONTENT_MASK
  - C1 CURSOR_MASK
  - N0 NONCLIENT_EXCLUDED
- Strict structural coordinates use 0 px drift.
- Exact locked flat-fill RGB is required in S0 regions.
- Native ttk glyph anti-aliasing may vary within ±1 px envelope while outer geometry remains strict.
- Text uses Segoe UI role/weight + ±1 px bbox envelope; ClearType fringe RGB is not hardcoded.
- Dynamic/server/device/live regions are masked without relaxing their container geometry/style.
- Party's 451×1035 raw capture is handled with B04 raw measured regions and an outer-framing exclusion.
- Start is covered by two direct whole-client references:
  - Auto / Điều khiển nhanh
  - Xếp lưới
- Direct screenshot reference coverage now spans all baseline page families and all 11 selected tab labels.
- Per-page checklist covers Login, Party, Train, Train LSV, Phó Bản, Daily, Đồn, Rao, Tối ưu, i and Start reference states.
- No unresolved visual blocker remains in the PLAN-defined Gate-B baseline scope.
- Gate B closed as COMPLETE / VERIFIED.

## B14 FILES
- `docs/tasks/B14.md`
- `docs/ui/B14_PIXEL_COMPARISON_CHECKLIST.tsv`
- `docs/ui/B14_COMPARISON_POLICY.json`
- `docs/ui/B14_SCREENSHOT_BASELINES.tsv`
- `docs/ui/B14_DYNAMIC_MASKS.tsv`
- `docs/UI_BASELINE_TLM.md`

## CURRENT_TASK
C01 — TLM tìm cửa sổ game thế nào.

## BLOCKERS
None known for C01. Gate A and Gate B are complete.

## DO_NOT_TOUCH
- Preserve Gate A forensic baseline unchanged.
- Preserve Gate B geometry/palette/checklist as the visual contract.
- Do not begin C02 before C01 is verified.
- Do not infer HWND discovery mechanism from UI appearance; inspect original binary/static/runtime evidence as required by PLAN.

## NEXT_ACTION
On CONTINUE:
1. Read `PLAN.md`.
2. Read `STATE.md`.
3. Execute **C01 only**.
4. Inspect original binary/module evidence for how TLM discovers game windows.
5. Identify APIs, window-class/title/process filters, refresh cadence and exclusion rules only where evidence supports them.
6. Persist C01 evidence/report and start/update `WINDOW_BEHAVIOR_MATRIX.md`.
7. Advance to C02 only after C01 is verified.
