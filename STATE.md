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
- C06 VERIFIED_WITH_EXPLICIT_UNKNOWNS

## C06 VERIFIED RESULTS
- Rechecked the exact user-provided `TLMTool_2.1.2(3).zip`: SHA-256 matches the Gate-A frozen archive, so no forensic baseline was redone.
- Inner `TLMTool.dist/TLMTool.exe` hash matches the binary used by C01–C05.
- Current Xếp-lưới screenshot is byte-identical to the prior Gate-B baseline; UI baseline therefore remains valid.
- Recovered grid config from original binary:
  - `grid_cols` default = 3
  - `grid_rows` default = 4
  - persisted under Start settings.
- `_arrange_grid` recovered with:
  - `GetSystemMetrics`
  - exact literals 450 and 40
  - `min`, `sorted`, `new_slots`, `ww`, `wh`
  - master index 0 / top-left
  - remaining HWNDs sequential after master.
- Exact grid arithmetic formula remains explicit UNKNOWN; no meaning is invented for literals 450/40.
- `_move_windows_offset` is the shared move-only primitive:
  - `pos_fn(index) -> (x,y)`
  - keeps current size
  - master index 0.
- `SetWindowPos` family is recovered; no `MoveWindow` literal/import was recovered from the inner EXE.
- `resize_window` block contains:
  - `GetWindowPlacement`
  - `ShowWindow(SW_SHOWNORMAL)`
  - `SetWindowPos`
  - `SWP_NOZORDER`, `SWP_NOACTIVATE`, `SWP_NOMOVE`.
- Shared stack primitives recovered:
  - tight → (0,0)
  - diagonal → +50 x/+50 y
  - horizontal → +50 x
  - vertical → +50 y.
- Layout sync architecture recovered:
  - `_toggle_layout`
  - `_sync_windows_loop`
  - `_layout_worker`
  - `_arrange_grid`
  - cached HWND list via worker.
- Limit model recovered:
  - server source `new_version_info.max_windows`
  - fallback literal 999
  - worker-cached process count
  - over limit prevents sync
  - `_auto_stop_sync` stops both layout sync and input sync.
- Explicit unknowns preserved:
  - exact grid arithmetic
  - exact grid +/- bounds
  - exact max-window comparator operator
  - exact layout-worker cadence.
- C07 evidence was observed (Auto 1366x768 reset, RoleName auto-tile, 1-second loop) but deliberately not marked complete.

## C06 FILES
- `docs/tasks/C06.md`
- `docs/window/C06_LAYOUT_STATIC_EVIDENCE.tsv`
- `docs/window/C06_LAYOUT_MODEL.md`
- `docs/window/C06_LAYOUT_MODEL.json`
- `WINDOW_BEHAVIOR_MATRIX.md`

## CURRENT_TASK
C07 — Auto.

## BLOCKERS
None known for C07.

## DO_NOT_TOUCH
- Preserve Gate A forensic baseline unchanged.
- Preserve Gate B visual contract unchanged.
- Preserve C01–C06 explicit unknowns.
- Do not invent the exact C06 grid formula from constants 450/40.
- Do not treat C07 cross-task evidence as full C07 verification until C07 is executed.
- Do not begin C08 before C07 is verified.

## NEXT_ACTION
On CONTINUE:
1. Read `PLAN.md`.
2. Read `STATE.md`.
3. Execute **C07 only**.
4. Recover exact Auto-mode switch behavior from the original binary.
5. Verify the 1366×768 reset path, `_auto_tile_windows`, RoleName ordering, master-first rule, 1-second `_auto_tile_loop`, start/stop conditions and limit integration.
6. Combine original EXE evidence with the existing Auto screenshot; do not infer behavior from the screenshot alone.
7. Update `WINDOW_BEHAVIOR_MATRIX.md` and persist C07 evidence/report.
8. Advance to C08 only after C07 is verified.
