# C06_AUDIT — Re-audit before C07

## RESULT
**C06 CLOSED — NO REWORK REQUIRED**

The previous C06 commit was audited against the same original TLMTool 2.1.2 specimen before continuing.

## Integrity re-check
- user archive SHA-256: `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`
- inner EXE SHA-256: `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`
- Xếp-lưới screenshot SHA-256: `f1573668b94667e85b380326dcb5a4fc1a8cbc723d9cee80e6335c13961c339a`

All match the existing locked evidence.

## Recovered evidence reconfirmed
- `grid_cols` default 3
- `grid_rows` default 4
- `_arrange_grid`
- `GetSystemMetrics`
- constants 450 and 40
- `min`, `sorted`, `new_slots`, `cols`, `ww`, `wh`
- master index 0 / top-left
- followers sequential after master
- `_move_windows_offset(pos_fn)` keeps size
- `SetWindowPos` family
- `resize_window` with normal-state handling
- tight / diagonal / horizontal / vertical position primitives
- worker-backed layout synchronization
- server-backed `max_windows` with fallback literal 999
- over-limit path stops layout + input sync

## Newly clarified during audit
The original EXE explicitly documents:
`Re-block slaves mỗi 1.5s — cửa sổ mới được block, phòng bị unblock.`

This belongs to `_sync_keepalive` (input sync), not `_layout_worker`. It must not be used to fill the C06 layout-worker cadence field.

## Explicit unknowns that remain valid
1. Exact arithmetic combining screen metrics, 450, 40, cols and rows.
2. Exact min/max bounds used by the grid +/- controls.
3. Exact source comparator around `max_windows`.
4. Exact `_layout_worker` cadence.

These are evidence limits, not unfinished work hidden in the repo.

## DECISION
C06 is closed as `AUDITED_CLOSED_WITH_EXPLICIT_UNKNOWNS`.

Next task remains **C07 — Auto**.
