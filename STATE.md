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

## B05 VERIFIED RESULTS
- Used corrected binary-first workflow.
- Original FarmTab markers recovered from inner EXE: `farm_tab.py`, `<module farm_tab>`.
- Train captures (1)/(2) are byte-identical; SHA-256 `17d98f6b6a263daa5857224d100355379672eae7bd7c72794323f31417d8bc53`.
- Train selected bridge at y=56: x=102..137.
- `Cấu hình Về thành`: x=11..438, y=69..133; `Theo chu kỳ (phút)` selected; value 30; lower town body collapsed.
- Binary explicitly documents lower town block as default-hidden and reveals its hidden labels/options without requiring screenshot guessing.
- `Cấu hình Train`: x=11..438, y=147..329.
  - respawn/reconnect/pickup/heal unchecked
  - treatment coordinate `Trị liệu Tô Châu`
  - keep mode `Tất cả`
  - no buff row visible
- Static buff-row structure supports F1-F10 + 1/2/3.
- `Cấu hình tọa độ lưu sẵn`: x=11..438, y=343..406; no saved row visible; add/hide buttons measured.
- Static coordinate-row structure contains Bán / Train / ✕.
- `Danh sách tài khoản`: x=11..438, y=420..983; empty-list state; headers and scrollbar measured.
- Static populated-account row structure recovered but no pixel geometry invented.
- All-account controls measured: Tới bán đồ / Bán đồ / Tới bãi train / Đánh.
- bottom `Bắt đầu`: x=16..433, y=988..1017.

## B05 FILES
- `docs/tasks/B05.md`
- `docs/ui/B05_TRAIN_GEOMETRY.tsv`
- `docs/ui/B05_TRAIN_VISIBLE_STATE.json`
- `docs/ui/B05_TRAIN_STATIC_EVIDENCE.tsv`
- `docs/ui/B05_SCREENSHOT_EVIDENCE.tsv`
- `docs/UI_BASELINE_TLM.md`

## CURRENT_TASK
B06 — Baseline Train LSV.

## BLOCKERS
None for B06. Train LSV selected screenshot evidence is already present.

## WORKFLOW
For remaining Gate B tabs:
1. inspect corresponding compiled module/static original evidence first;
2. then use screenshot evidence to lock pixels/current visible state;
3. never ask screenshots to rediscover labels/structure already recoverable from the original binary;
4. never invent pixels for controls not visible in screenshot evidence.

## DO_NOT_TOUCH
- Preserve Gate A forensic baseline unchanged.
- Keep B05 runtime behavior deferred.
- Do not assign pixels to hidden/collapsed Train controls without direct visual evidence.
- Keep final shared font/color/button metrics for B13.
- The staged `i` screenshot remains reserved for B12.

## NEXT_ACTION
On CONTINUE:
1. Read `PLAN.md`.
2. Read `STATE.md`.
3. Execute **B06 only**.
4. Inspect compiled `train_lsv_tab.py` evidence first.
5. Then measure the supplied Train LSV-selected screenshot(s).
6. Persist B06 static + visual evidence to GitHub and update `docs/UI_BASELINE_TLM.md`.
7. Advance to B07 only after B06 is verified.
