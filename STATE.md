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
- C05 VERIFIED_WITH_EXPLICIT_UNKNOWN_AUTO_SELECTION_RULE

## C05 VERIFIED RESULTS
- Master is stored as runtime `hwnd_master`, separate from UI label/name.
- Original state includes:
  - `_prev_hwnd_master`
  - `_master_var`
  - `_master_hwnd_cache`
  - `_hwnd_by_name`
  - `_master_radio_buttons`
  - `_master_initial_selected`
- Master UI is a dynamic Radiobutton list under `Cửa sổ chính:`.
- Master candidate list rebuilds only when HWND list changes.
- Candidate labels use character-info cache; fallback prefix `Cửa sổ ` is present.
- Exact full fallback label format remains UNKNOWN.
- Manual radio selection resolves label → HWND and logs selected master.
- Original exact behavior on changing master while input sync is ON:
  - automatically stop input sync
  - unlock all slaves
  - user re-enables sync after choosing new master
- Master ordering rules verified:
  - stack/offset: index 0
  - auto tile: first
  - grid: index 0/top-left
- Master is the source for click/scroll/move/key sync handlers; other windows are slave targets.
- Watchdog explicitly handles stale slave block after master close/change/exit.
- Recovered Start settings block contains grid/detached fields but no master HWND key; master is classified runtime-derived.
- Automatic initialization is real:
  - `_auto_master_and_sync`
  - `_master_initial_selected`
- Exact automatic HWND-choice rule is still explicit UNKNOWN.
- Exact fallback after selected master disappears is still explicit UNKNOWN.

## C05 FILES
- `docs/tasks/C05.md`
- `docs/window/C05_MASTER_STATIC_EVIDENCE.tsv`
- `docs/window/C05_MASTER_FLOW.md`
- `docs/window/C05_MASTER_MODEL.json`
- `WINDOW_BEHAVIOR_MATRIX.md`

## CURRENT_TASK
C06 — bố trí nhiều cửa sổ.

## BLOCKERS
None known for C06.

## DO_NOT_TOUCH
- Preserve Gate A forensic baseline unchanged.
- Preserve Gate B visual contract unchanged.
- Preserve C01–C05 explicit unknowns.
- Do not claim a "first window wins" automatic master rule without stronger evidence.
- Do not begin C07 before C06 is verified.

## NEXT_ACTION
On CONTINUE:
1. Read `PLAN.md`.
2. Read `STATE.md`.
3. Execute **C06 only**.
4. Recover the common multi-window layout engine before the mode/button-specific tasks C07–C11.
5. Determine screen metrics, cols/rows, tile size, ordering, MoveWindow/SetWindowPos/resize behavior, master-first integration and limit handling only from original evidence.
6. Update `WINDOW_BEHAVIOR_MATRIX.md` and persist C06 evidence/report.
7. Advance to C07 only after C06 is verified.
