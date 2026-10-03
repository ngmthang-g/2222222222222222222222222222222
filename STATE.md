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

## B10 VERIFIED RESULTS
- Used binary-first workflow.
- Original compiled marker recovered: `rao_tab.py`.
- Two Rao screenshots are byte-identical; SHA-256 `341f2b4653f31f5a0ee4a3f29d3cf9245edbf43c0ca140ac09a859925d8a2319`.
- Rao selected bridge at y=56: x=308..337.
- `Cấu hình rao tự động`: x=13..436, y=69..154.
  - one visible row: `Rao 1 | blank content | Thế giới | 30 | ✕`
  - add-Rao and delete controls measured
- Static channel list recovered:
  - Thế giới
  - Bang hội
  - Môn phái
  - Tổ đội
  - Liên minh
  - Quân đoàn
  - Lân cận
- Original default channel: `Thế giới`.
- Automatic Rao naming and digits-only repeat validation recovered from original module.
- `Danh sách tài khoản`: x=13..436, y=170..983; empty screenshot state; scrollbar arrows/track visible, no thumb.
- Static populated account-row structure recovered:
  - ▶
  - character name
  - initial `Đã dừng`
  - 4 Rao-content combobox slots per account
- Original module documents maximum four independent Rao loops per account and account-list refresh every five seconds.
- Static backend evidence preserved for later behavior: memory_items.send_chat / Network.SendPacket CMD_CLIENT_CHAT, background without opening chat panel.
- bottom `Bắt đầu` measured; static running strings include `Đang rao X/4 nhóm...` and `Dừng lại`.

## B10 FILES
- `docs/tasks/B10.md`
- `docs/ui/B10_RAO_GEOMETRY.tsv`
- `docs/ui/B10_RAO_VISIBLE_STATE.json`
- `docs/ui/B10_RAO_STATIC_EVIDENCE.tsv`
- `docs/ui/B10_SCREENSHOT_EVIDENCE.tsv`
- `docs/UI_BASELINE_TLM.md`

## CURRENT_TASK
B11 — Baseline Tối ưu.

## BLOCKERS
None for B11. A Tối ưu-selected screenshot is already present.

## WORKFLOW
For remaining Gate B tabs:
1. inspect corresponding compiled module/static original evidence first;
2. then use screenshot evidence to lock pixels/current visible state;
3. do not ask screenshots to rediscover recoverable binary structure;
4. do not invent pixels for controls absent/hidden in screenshots.

## DO_NOT_TOUCH
- Preserve Gate A forensic baseline unchanged.
- Keep B10 send/loop behavior deferred.
- Treat screenshot Rao values as visible/current state; only values separately confirmed as defaults may be called defaults.
- Keep final shared font/color/button metrics for B13.
- The staged `i` screenshot remains reserved for B12.

## NEXT_ACTION
On CONTINUE:
1. Read `PLAN.md`.
2. Read `STATE.md`.
3. Execute **B11 only**.
4. Inspect compiled `toiuu_tab.py` / monitoring static evidence first.
5. Then measure the supplied Tối ưu-selected screenshot.
6. Persist B11 evidence/report to GitHub and update `docs/UI_BASELINE_TLM.md`.
7. Advance to B12 only after B11 is verified.
