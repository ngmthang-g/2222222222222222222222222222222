# STATE — TLMTool 2.1.2

## STATUS
BLOCKED_ON_REQUIRED_VISUAL_EVIDENCE

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

## CURRENT_TASK
B04 — Baseline Party — **BLOCKED_VISUAL_EVIDENCE**

## B04 PARTIAL RESULTS
- Re-checked the entire supplied 12-screenshot set.
- There is no Party-selected screenshot.
- `TLMTool_fTpCsm0auQ(2).png` is VERIFIED as `▶ / Start / Xếp lưới`, not Party:
  - selected white bridge at y=56 is x=6..30;
  - Party span remains under the inactive separator;
  - compiled `start_tab.py` contains the exact visible Xếp-lưới/sync/preview labels.
- `TLMTool_rARyQTv9Ta(2).png` is the same Start tab in Auto / Điều khiển nhanh mode.
- Static original `party_tab.py` structure was recovered:
  - Bắt đầu
  - Sau khi party: Chờ / Train / Train LSV / Dồn vàng / Phó bản
  - Cấu hình tổ đội
  - Danh sách acc sẵn sàng:
  - Cấu hình nhóm
  - Nhóm
  - Trưởng nhóm:
  - + Thêm nhóm
  - 6 accounts per cluster, 2 rows × 3 comboboxes
  - documented toggles Theo sau đội trưởng / Tự nhặt đồ
- Party pixel geometry remains UNKNOWN and is not copied from Phó Bản.

## CORRECTION
B02 focus-state evidence was corrected:
- selected tab does not always show a dotted focus rectangle;
- dotted rectangle is focus state, not required selection state.
- B02 screenshot hash for TLMTool_3MXfXQKSHN was also corrected.

## BLOCKERS
A full-window **Party-selected screenshot** is required to finish B04 pixel baseline and advance to B05.

Preferred evidence:
- full TLMTool window;
- Party tab visibly selected;
- same 452 × 1032 capture size if possible;
- do not crop the title bar, tab bar, bottom controls, or page edges.

## FILES_CHANGED
- `docs/tasks/B04.md`
- `docs/ui/B04_PARTY_STATIC_EVIDENCE.tsv`
- `docs/ui/B04_PARTY_STATIC_STRUCTURE.json`
- `docs/UI_BASELINE_TLM.md`
- corrected `docs/tasks/B02.md`
- corrected `docs/ui/B02_COMMON_STYLE.json`
- corrected `docs/ui/B02_SCREENSHOT_ACTIVE_TAB.tsv`
- `STATE.md`
- `PROJECT_STATUS.md`

## DO_NOT_TOUCH
- Do not advance to B05 while B04 visual geometry is unverified.
- Do not substitute Start/Xếp-lưới screenshot for Party.
- Do not copy Phó Bản pixel coordinates into Party merely because static text says the UI is similar.
- Preserve Gate A forensic baseline unchanged.

## NEXT_ACTION
On CONTINUE:
1. Read `PLAN.md`.
2. Read `STATE.md`.
3. Re-check conversation files for a new full-window Party-selected screenshot.
4. If present, measure Party pixel geometry, finish B04, update `UI_BASELINE_TLM.md`, and advance to B05.
5. If absent, keep B04 BLOCKED and do not fabricate/skip the visual gate.
