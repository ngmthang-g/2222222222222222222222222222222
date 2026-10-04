# STATE — TLMTool 2.1.2

## STATUS
IN_PROGRESS

## GATE A
**COMPLETE / VERIFIED**

## GATE B
**COMPLETE / VERIFIED**

## GATE C
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
- B14 VERIFIED
- C01 VERIFIED_WITH_EXPLICIT_UNKNOWN_BOOLEAN_FORMULA
- C02 VERIFIED_WITH_EXPLICIT_UNKNOWN_FALLBACK_FORMAT
- C03 VERIFIED_WITH_EXPLICIT_UNKNOWN_PROPERTY_BOOLEANS
- C04 VERIFIED_WITH_EXPLICIT_UNKNOWN_BOUNDARY_AND_DETACHED_CADENCE

## C04 VERIFIED RESULTS
- Verified 800/2000ms are **preview maintenance/update cadence**, not DWM image FPS.
- DWM thumbnail image remains compositor-driven; no TLM app-defined DWM FPS was recovered.
- Preview maintenance is Tk `after` scheduled:
  - `_preview_loop_id`
  - `_schedule_preview_loop`
  - respects `_refresh_active`
- Adaptive policy recovered:
  - switch constant = 6
  - short delay = 800ms
  - long delay = 2000ms
  - exact boundary operator (< vs <=) remains explicit UNKNOWN
- Normal update-loop responsibilities recovered:
  - reposition DWM destination HWNDs
  - compare alive HWNDs/current valid preview items
  - conditionally rebuild list
  - refresh cached name/HP
  - refresh slot combobox HWND mapping
  - schedule next cycle
- Update-loop block contains `cache_ts` + exact float 3.0; exact source comparator/use remains explicit UNKNOWN.
- Reposition debounce recovered exactly: **60ms**.
- Timing layers distinguished:
  - Start list poll: 2000ms
  - preview maintenance: 800/2000ms
  - worker EnumWindows + character info: ~3s
  - heavier memory: ~8s
  - DWM composition: live compositor
- Detached preview has separate `_detached_update_loop`:
  - rebuilds when game-window list changes
  - independent of Start tab visibility
  - exact detached timer interval remains explicit UNKNOWN
- Leaving Start stops normal poll/preview scheduled work while detached preview remains active.

## C04 FILES
- `docs/tasks/C04.md`
- `docs/window/C04_PREVIEW_UPDATE_STATIC_EVIDENCE.tsv`
- `docs/window/C04_PREVIEW_TIMING_MODEL.md`
- `docs/window/C04_PREVIEW_TIMING.json`
- `WINDOW_BEHAVIOR_MATRIX.md`

## CURRENT_TASK
C05 — cửa sổ chính.

## BLOCKERS
None known for C05.

## DO_NOT_TOUCH
- Preserve Gate A forensic baseline unchanged.
- Preserve Gate B visual contract unchanged.
- Preserve C01–C04 explicit unknowns.
- Do not mislabel maintenance timers as DWM FPS.
- Do not begin C06 before C05 is verified.

## NEXT_ACTION
On CONTINUE:
1. Read `PLAN.md`.
2. Read `STATE.md`.
3. Execute **C05 only**.
4. Recover how TLM chooses/stores the main/master game window.
5. Determine master-variable semantics, automatic selection/fallback, effect on sorting/sync/layout and stale-window handling only from original evidence.
6. Update `WINDOW_BEHAVIOR_MATRIX.md` and persist C05 evidence/report.
7. Advance to C06 only after C05 is verified.
