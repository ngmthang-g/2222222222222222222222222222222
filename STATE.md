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

## B07 VERIFIED RESULTS
- Used binary-first workflow.
- Original compiled markers recovered: `phoban_tab.py`, `phoban_dungeons.py`.
- Two Phó Bản screenshots are byte-identical; SHA-256 `8b62070b04231f762dc080f4432cbc178f020ae0614540dc0e9c293d16987fb8`.
- Phó Bản selected bridge at y=56: x=192..245.
- `Cấu hình tổ đội`: border x=13..436, y=69..110; no ready-account entry visible.
- `Cấu hình phó bản`: border x=13..436, y=124..206.
  - all visible toggles unchecked
  - exact static labels recovered from binary
  - follow-leader checkbox is cursor-occluded at pixel-border level, so no false precision is claimed.
- Original binary creates a hidden `Cấu hình tọa độ bán đồ` block and then `pack_forget`; it is not part of the visible B07 baseline.
- `Cấu hình lịch trình`: border x=13..436, y=220..979.
- Nhóm 1 frame: x=18..423, y=240..372.
  - leader `(chưa chọn)`
  - six blank comboboxes = 2 rows × 3
  - delete-group button measured
  - schedule header checkbox unchecked
  - no schedule row visible
- Toolbar measured: + Thêm Lịch trình / Tắt auto PB / Bắt đầu lịch trình.
- Static activities recovered: `Phó bản`, `Train`.
- Train map value recovered: `Về train theo thiết lập sẵn`.
- Eight dungeon names recovered, including `Sát Tinh - Thử nghiệm`.
- Static progress states recovered: `Chưa / Đang / Xong`.
- Static runner-state strings recovered: `Bắt đầu lịch trình / Dừng lịch trình / Đang dừng lịch trình... / Dừng lại`.
- Legacy `Bán đồ` schedule config is explicitly marked removed/ignored in the original binary.
- `+ Thêm nhóm` and bottom `Bắt đầu` measured.

## B07 FILES
- `docs/tasks/B07.md`
- `docs/ui/B07_PHOBAN_GEOMETRY.tsv`
- `docs/ui/B07_PHOBAN_VISIBLE_STATE.json`
- `docs/ui/B07_PHOBAN_STATIC_EVIDENCE.tsv`
- `docs/ui/B07_SCREENSHOT_EVIDENCE.tsv`
- `docs/UI_BASELINE_TLM.md`

## CURRENT_TASK
B08 — Baseline Daily.

## BLOCKERS
None for B08. Daily-selected screenshots are already present.

## WORKFLOW
For remaining Gate B tabs:
1. inspect corresponding compiled module/static original evidence first;
2. then use screenshot evidence to lock pixels/current visible state;
3. do not ask screenshots to rediscover recoverable binary structure;
4. do not invent pixels for controls absent/hidden in screenshots.

## DO_NOT_TOUCH
- Preserve Gate A forensic baseline unchanged.
- Keep B07 runtime/dungeon behavior deferred.
- Do not expose hidden sale-coordinate UI as visible just because it exists statically.
- Keep final shared font/color/button metrics for B13.
- The staged `i` screenshot remains reserved for B12.

## NEXT_ACTION
On CONTINUE:
1. Read `PLAN.md`.
2. Read `STATE.md`.
3. Execute **B08 only**.
4. Inspect compiled `daily_tab.py` static evidence first.
5. Then measure supplied Daily-selected screenshot evidence.
6. Persist B08 evidence/report to GitHub and update `docs/UI_BASELINE_TLM.md`.
7. Advance to B09 only after B08 is verified.
