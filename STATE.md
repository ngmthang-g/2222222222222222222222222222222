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

## B11 VERIFIED RESULTS
- Used binary-first workflow.
- Original compiled markers recovered: `toiuu_tab.py`, related `cpu_monitor.py`.
- Two Tối ưu screenshots are byte-identical; SHA-256 `653110b20120e26d115f11e64cb61b23af686b77432cf211b28be51a40364933`.
- Tối ưu selected bridge at y=56: x=336..378.
- `Giám sát CPU/GPU`: x=13..436, y=69..285.
  - detached-monitor button measured
  - visible CPU = 15%
  - CPU canvas/line measured
  - visible GPU = N/A because nvidia-smi unavailable
  - GPU canvas measured
- Original module documents 1-second sampling and nvidia-smi GPU query.
- Detached monitor title `CPU / GPU`; detached state persists via `toiuu_monitor_open`.
- `Danh sách tài khoản`: x=13..436, y=301..983; empty-list state; scrollbar track/arrows visible, no thumb.
- Static mode mapping recovered:
  - medium → Thấp vừa
  - low → Cực thấp
  - max → Cực đại
  - config labels also include Không
- Static state vocabulary/colors recovered: Đã dừng / Đang chạy / Treo tick.
- All-account mode buttons measured.
- bottom `Bắt đầu` measured.
- Original module also contains saved running set, DLL/perf command flow, stale-running reconciliation and hang-watch/recovery hooks; runtime parity remains deferred.
- Related `cpu_monitor.py` is recorded as a separate high-CPU warning component, not merged into the visible Tối ưu baseline.

## B11 FILES
- `docs/tasks/B11.md`
- `docs/ui/B11_TOIUU_GEOMETRY.tsv`
- `docs/ui/B11_TOIUU_VISIBLE_STATE.json`
- `docs/ui/B11_TOIUU_STATIC_EVIDENCE.tsv`
- `docs/ui/B11_SCREENSHOT_EVIDENCE.tsv`
- `docs/UI_BASELINE_TLM.md`

## CURRENT_TASK
B12 — Baseline i.

## BLOCKERS
None for B12. A direct i-selected screenshot was supplied and staged earlier.

## WORKFLOW
For remaining Gate B tabs:
1. inspect corresponding compiled module/static original evidence first;
2. then use screenshot evidence to lock pixels/current visible state;
3. do not ask screenshots to rediscover recoverable binary structure;
4. do not invent pixels for controls absent/hidden in screenshots.

## DO_NOT_TOUCH
- Preserve Gate A forensic baseline unchanged.
- Keep B11 runtime/performance/recovery behavior deferred.
- Keep final shared font/color/button metrics for B13.

## NEXT_ACTION
On CONTINUE:
1. Read `PLAN.md`.
2. Read `STATE.md`.
3. Execute **B12 only**.
4. Inspect compiled `info_tab.py` static evidence first.
5. Then measure the staged direct i-selected screenshot.
6. Persist B12 evidence/report to GitHub and update `docs/UI_BASELINE_TLM.md`.
7. Advance to B13 only after B12 is verified.
