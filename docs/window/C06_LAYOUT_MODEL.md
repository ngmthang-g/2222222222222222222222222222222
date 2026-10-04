# C06 — Common layout model

## Integrity gate

```text
user archive TLMTool_2.1.2(3).zip
SHA256 c1d51f...
        =
Gate-A frozen archive
↓
inner TLMTool.dist/TLMTool.exe
SHA256 15c8044f...
        =
binary used by C01–C05
```

C06 therefore continues the same original specimen; it does not redo forensic/UI baselines.

## Grid path

```text
worker-cached game HWND list
↓
master-aware ordering
├─ master → index 0
└─ all other HWNDs → sequentially after it
↓
_arrange_grid(windows, cols, rows)
├─ GetSystemMetrics
├─ exact constants: 450, 40
├─ min
├─ ww / wh
├─ exact arithmetic formula = UNKNOWN
└─ new_slots / _grid_slots
↓
slot 0 = top-left = master
remaining slots = remaining HWND order
↓
SetWindowPos-family placement/resize paths
```

Persisted Start defaults:
- cols = 3
- rows = 4
- screenshot corroborates Cột:3 / Hàng:4.

## Move-only path

```text
_get_preview_hwnds
↓
master promoted first
↓
_move_windows_offset(pos_fn)
↓
for each index:
  (x,y) = pos_fn(index)
  keep current width/height
↓
SetWindowPos semantics / SWP_NOSIZE
↓
_reset_hidden_state
```

The inner binary contains SetWindowPos and does not expose a MoveWindow literal/import.

## Resize path

```text
resize_window
↓
GetWindowPlacement
↓
ShowWindow(SW_SHOWNORMAL) when needed
↓
SetWindowPos
  + SWP_NOMOVE
  + SWP_NOZORDER
  + SWP_NOACTIVATE
↓
size changes while position/z-order/activation are preserved by the recovered flag set
```

## Stack primitives built on the same engine

```text
tight      pos_fn(i) = (0,0)
diagonal   origin (0,0), +50 x / +50 y per index
horizontal origin (0,0), +50 x per index
vertical   origin (0,0), +50 y per index
```

C10/C11 remain separate tasks; C06 only establishes their common primitive.

## Continuous layout sync

```text
Đồng bộ các cửa sổ
↓
_toggle_layout
↓
_sync_windows_loop / _layout_worker
↓
_refresh_cache (worker-cached HWND list)
↓
_arrange_grid
↓
maintain layout while layout sync is active
```

Exact worker cadence remains UNKNOWN.

## Limit gate

```text
new_version_info.max_windows
↓
_get_max_windows
├─ server-provided runtime limit
└─ fallback/default literal 999
↓
_count_game_processes
(worker cache; no tasklist spawn on main UI thread)
↓
if over allowed limit
├─ cannot enable sync
└─ _auto_stop_sync
    ├─ layout sync OFF
    └─ input sync OFF
```

Exact source comparison operator remains UNKNOWN.

## C07 evidence held back

The same binary scan sees:
- Auto reset message to `(0,0) 1366x768`;
- auto tile sorted by RoleName with master first;
- 1-second auto-tile loop.

These facts are **not** used to mark C07 complete. They are the starting evidence for the next task.
