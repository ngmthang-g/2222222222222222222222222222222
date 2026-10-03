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

## B09 VERIFIED RESULTS
- Used binary-first workflow.
- Original compiled markers recovered: `donvang_tab.py`, `don_logic.py`.
- Two Đồn screenshots are byte-identical; SHA-256 `dffb4da895d21dea87dd72a6601c29104f519dca89c2f716f5a7445bcbe4421a`.
- Đồn selected bridge at y=56: x=278..309.
- `Cấu hình Về thành`: x=11..438, y=69..178.
  - Theo chu kỳ selected; 30 minutes
  - priority `Phù 1 / Phù 2 / Phù 3 / Ngựa`
- `Cấu hình Train`: x=11..438, y=192..326.
  - respawn unchecked
  - stop-on-disconnect unchecked
  - unstuck checked
  - pickup-no-gourd unchecked
  - keep mode `Tất cả`
  - heal-after-death unchecked
  - heal coordinate `Trị liệu Tô Châu`
- `Cấu hình tọa độ lưu sẵn`: x=11..438, y=340..427.
  - visible current row: `Tọa độ 1 | Đại Lý | 0 | 0 | Train`
  - add/hide/delete controls measured
- `Danh sách tài khoản`: x=11..438, y=441..983.
  - shared `Tọa độ dồn` combo blank in capture
  - Acc nhận 1/2 blank
  - + Thêm acc nhận measured
  - scrollbar arrows/track visible, no thumb
- Static dồn coordinate options recovered:
  - Dồn Lạc Dương
  - Dồn Đại Lý
  - Dồn Tô Châu
  - Dồn Lâu Lan
- Binary explicitly documents shared dồn coordinate across receiver rows.
- Receiver rows are dynamic; missing config defaults to one row; delete keeps at least one.
- All-account controls measured: `Tới nơi nhận / Tới chỗ bán / Tới nơi train`.
- bottom `Bắt đầu` measured.
- Static populated account-row structure/state vocabulary recovered without invented pixels.
- `don_logic.py` contains concrete donor/receiver transaction and synchronization logic; runtime parity remains deferred.

## B09 FILES
- `docs/tasks/B09.md`
- `docs/ui/B09_DON_GEOMETRY.tsv`
- `docs/ui/B09_DON_VISIBLE_STATE.json`
- `docs/ui/B09_DON_STATIC_EVIDENCE.tsv`
- `docs/ui/B09_SCREENSHOT_EVIDENCE.tsv`
- `docs/UI_BASELINE_TLM.md`

## CURRENT_TASK
B10 — Baseline Rao.

## BLOCKERS
None for B10. A Rao-selected screenshot is already present.

## WORKFLOW
For remaining Gate B tabs:
1. inspect corresponding compiled module/static original evidence first;
2. then use screenshot evidence to lock pixels/current visible state;
3. do not ask screenshots to rediscover recoverable binary structure;
4. do not invent pixels for controls absent/hidden in screenshots.

## DO_NOT_TOUCH
- Preserve Gate A forensic baseline unchanged.
- Keep B09 runtime/dồn behavior deferred.
- Treat screenshot coordinate/receiver selections as current/persisted state, not automatically clean defaults.
- Keep final shared font/color/button metrics for B13.
- The staged `i` screenshot remains reserved for B12.

## NEXT_ACTION
On CONTINUE:
1. Read `PLAN.md`.
2. Read `STATE.md`.
3. Execute **B10 only**.
4. Inspect compiled `rao_tab.py` static evidence first.
5. Then measure the supplied Rao-selected screenshot.
6. Persist B10 evidence/report to GitHub and update `docs/UI_BASELINE_TLM.md`.
7. Advance to B11 only after B10 is verified.
