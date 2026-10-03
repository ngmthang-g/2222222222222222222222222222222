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

## B06 VERIFIED RESULTS
- Used corrected binary-first workflow.
- Original Train-LSV module markers recovered from inner EXE: `train_lsv_tab.py`, `<module train_lsv_tab>`.
- Four Train-LSV screenshots are byte-identical; SHA-256 `9e3b57671a2ff165ea31264a1c2fb19493f861a7bdadc4dc993a55bd130f5d29`.
- Train LSV selected bridge at y=56: x=136..193.
- `Cấu hình Train LSV`: x=11..438, y=69..253.
  - respawn/reconnect/heal-at-Lạc-Dương-LSV unchecked
  - pickup mode `Tất cả` selected
- Fixed `Dạ Minh Châu` row measured:
  - checked-square visual x=20..32, y=203..215
  - key `1`
  - duration `0 ph 5 giây`
  - add-row button measured
- Original binary documents Dạ Minh Châu as fixed/no-delete/always-active and normal buff hotkeys F1-F10 + 1/2/3.
- Static LSV map-name set recovered:
  - Tần Hoàng Địa Cung Tầng 1–4
  - Phàm Liên Trại
  - Thanh Liên Trại
  - Khô Vinh Đạo
- `Cấu hình tọa độ lưu sẵn`: x=11..438, y=267..330.
  - headers `Tên | Map | X | Y | Áp dụng | Xóa`
  - no saved row visible
  - add/hide buttons measured
- `Danh sách tài khoản`: x=11..438, y=344..983.
  - headers `Nhân vật | Tọa độ Train`
  - empty-list state
  - scrollbar arrows/track visible; no thumb
- Static populated-row structure recovered: `▶`, `⬤`, `Đã dừng`, Train-coordinate combobox, row action methods, extra tracking text.
- All-account controls measured:
  - Tới LSV
  - Tới chỗ train
  - Đánh
  - Rời LSV
- bottom `Bắt đầu`: x=16..433, y=988..1017.

## B06 FILES
- `docs/tasks/B06.md`
- `docs/ui/B06_TRAIN_LSV_GEOMETRY.tsv`
- `docs/ui/B06_TRAIN_LSV_VISIBLE_STATE.json`
- `docs/ui/B06_TRAIN_LSV_STATIC_EVIDENCE.tsv`
- `docs/ui/B06_SCREENSHOT_EVIDENCE.tsv`
- `docs/UI_BASELINE_TLM.md`

## CURRENT_TASK
B07 — Baseline Phó Bản.

## BLOCKERS
None for B07. A Phó Bản-selected screenshot is already present.

## WORKFLOW
For remaining Gate B tabs:
1. inspect corresponding compiled module/static original evidence first;
2. then use screenshot evidence to lock pixels/current visible state;
3. never ask screenshots to rediscover labels/structure already recoverable from the original binary;
4. never invent pixels for controls not visible in screenshot evidence.

## DO_NOT_TOUCH
- Preserve Gate A forensic baseline unchanged.
- Keep B06 runtime behavior deferred.
- Do not treat visible Dạ Minh Châu key/time values as clean-package defaults unless later evidence proves that.
- Keep final shared font/color/button metrics for B13.
- The staged `i` screenshot remains reserved for B12.

## NEXT_ACTION
On CONTINUE:
1. Read `PLAN.md`.
2. Read `STATE.md`.
3. Execute **B07 only**.
4. Inspect compiled `phoban_tab.py` / related dungeon static evidence first.
5. Then measure the supplied Phó Bản-selected screenshot.
6. Persist B07 static + visual evidence to GitHub and update `docs/UI_BASELINE_TLM.md`.
7. Advance to B08 only after B07 is verified.
