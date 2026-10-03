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

## B08 VERIFIED RESULTS
- Used binary-first workflow.
- Original Daily compiled marker recovered: `daily_tab.py`.
- Two Daily screenshots are 452 × 1032 and show the same UI state; their 265-pixel difference is localized to mouse-cursor placement.
- Daily selected bridge at y=56: x=244..279.
- `Trừng ác`: x=13..436, y=69..279.
  - duration 15
  - Ngựa selected; Định vị phù unselected
  - teleport-hotkey combobox blank; original static values 1/2/3
  - heal checked, Tô Châu label
  - discard unchecked
  - reconnect checked
  - respawn checked
  - brown apply-all button measured
- `Tàng bảo đồ`: x=13..436, y=295..408.
  - tomb duration 30
  - heal unchecked
  - heal location Tô Châu
  - reconnect checked
  - respawn checked
  - brown apply-all button measured
- Original config keys/default fallback evidence recorded separately from visible persisted screenshot state.
- `Danh sách tài khoản`: x=13..436, y=424..983; empty-list state; scrollbar track/arrows visible, no thumb.
- Static populated-row structure recovered: ▶, activity combobox Trừng ác/Tàng bảo đồ, status dot, Đã dừng, per-row Tới bổ đầu/Trị liệu.
- All-account `Tới bổ đầu` / `Trị liệu` controls measured.
- Static target facts preserved for later behavior work:
  - bổ đầu: Tô Châu map 4, 224,285
  - trị liệu: Tô Châu map 4, 155,252
- bottom `Bắt đầu` measured; later static state strings include `Dừng lại` and `Đang dừng...`.

## B08 FILES
- `docs/tasks/B08.md`
- `docs/ui/B08_DAILY_GEOMETRY.tsv`
- `docs/ui/B08_DAILY_VISIBLE_STATE.json`
- `docs/ui/B08_DAILY_STATIC_EVIDENCE.tsv`
- `docs/ui/B08_SCREENSHOT_EVIDENCE.tsv`
- `docs/UI_BASELINE_TLM.md`

## CURRENT_TASK
B09 — Baseline Đồn.

## BLOCKERS
None for B09. A Đồn-selected screenshot is already present.

## WORKFLOW
For remaining Gate B tabs:
1. inspect corresponding compiled module/static original evidence first;
2. then use screenshot evidence to lock pixels/current visible state;
3. do not ask screenshots to rediscover recoverable binary structure;
4. do not invent pixels for controls absent/hidden in screenshots.

## DO_NOT_TOUCH
- Preserve Gate A forensic baseline unchanged.
- Keep B08 runtime behavior deferred.
- Keep screenshot state distinct from clean fallback/default config where they differ.
- Keep final shared font/color/button metrics for B13.
- The staged `i` screenshot remains reserved for B12.

## NEXT_ACTION
On CONTINUE:
1. Read `PLAN.md`.
2. Read `STATE.md`.
3. Execute **B09 only**.
4. Inspect compiled Đồn module/static evidence first (`don_logic.py`, `donvang_tab.py` as applicable).
5. Then measure the supplied Đồn-selected screenshot.
6. Persist B09 evidence/report to GitHub and update `docs/UI_BASELINE_TLM.md`.
7. Advance to B10 only after B09 is verified.
