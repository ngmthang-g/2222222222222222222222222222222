# L05 — Dồn coordinates flow

## Authority
Exact `TLMTool_2.1.2(8).zip` was revalidated first: SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, 93,715,901 bytes, 1,050 entries, CRC clean. Inner `TLMTool.dist/TLMTool.exe`: SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, 47,450,112 bytes. Active Dồn authority remains `donvang_tab.py / DonVangTab`, exact module size 65,260 bytes / 1,813 constants.

## Saved-coordinate editor
`_add_coord_row(name=None,map_val=None,x_val=None,y_val=None)`
→ dynamic row with name/map/X/Y
→ **Train** apply button
→ delete button.

Generated names use `Tọa độ N`, starting from 1 and checking existing names. Dồn's current saved-coordinate builder has no Bán apply button.

`_coord_name_list`
→ current saved preset names.

`_preset_to_vars(name)`
→ `(map_var,x_var,y_var)`
→ missing → `(None,None,None)`.

Rename immediately refreshes account selectors and rewrites an active old-name selection to the new preset name.

## Coordinate resolution
`_name_to_coords(name)`
→ built-in sell name OR built-in Dồn/receive name OR saved manual preset
→ `(map_id,x,y)`
→ unresolved → `None`.

The current built-in Dồn targets are:

| Name | MapID | X | Y |
|---|---:|---:|---:|
| Dồn Lạc Dương | 3 | 247 | 93 |
| Dồn Đại Lý | 2 | 258 | 124 |
| Dồn Tô Châu | 4 | 416 | 239 |
| Dồn Lâu Lan | 5 | 249 | 275 |

Shared sell targets are:

| Name | MapID | X | Y |
|---|---:|---:|---:|
| Đại Lý | 2 | 103 | 188 |
| Lạc Dương | 3 | 231 | 219 |
| Tô Châu | 4 | 191 | 257 |
| Lâu Lan | 5 | 37 | 126 |

Old config names like `Bán Đại Lý` are normalized to `Đại Lý` when the suffix is a valid current `SELL_MAP_LIST` entry.

## One shared Dồn coordinate
Current UI owns exactly one shared `Tọa độ dồn` combobox: `self._recv_coord_var`.

Receiver rows only contain receiver-account selection + delete. Each row's compatibility `rd["recv_coord_var"]` points to the same shared variable. Deleting a receiver row does not delete the shared Dồn coordinate.

`_don_point_coords`
→ resolves the shared Dồn coordinate
→ invalid/unselected → `None`
→ donor stays at train and waits later cycle.

The shared Dồn point is not pinned to receiver row 1.

## Role-dependent account coordinate selector
Current account-row metadata exposes one coordinate variable/widget pair: `farm_var / cb_farm`.

Role update:
- receiver account → show sell destinations: built-in `SELL_MAP_LIST` + manual saved presets;
- donor account → show train destinations: manual saved presets.

Visible label follows role:
- `Tọa độ bán:`
- `Tọa độ train:`.

This is the current effective surface even though some legacy helper wording still refers to indexed Bán/Train combos.

## Apply-all
Saved-row **Train** button:
`_apply_coord_to_all`
→ applies the saved preset **name** to train selectors for all accounts.

Coordinates are resolved later from the current row, so apply-all does not freeze a separate map/X/Y snapshot.

## Separators and dropdowns
Saved map selector:
- choosing `=====` jumps to the next real map.

Bán/Nhận coordinate selectors:
- `======Có sẵn======` jumps to the first real `SELL_MAP_LIST` or `RECV_COORD_LIST` entry;
- `=====Thủ công=====` jumps to the first saved preset.

Readonly combos still open their dropdown on click. Permission-disabled combos do not.

## Persistence
Section: `[DonVang]`.

Saved coordinate rows:
`coord_<n> = preset_name|map_id|x|y`.

Save:
→ map display name resolved by `coord_id_for_name`
→ unknown map → skip, do not save.

Load:
→ collect `coord_*`
→ `parse_coord_value`
→ `coord_name_for_id`
→ stale map id/name → skip
→ valid → recreate dynamic row.

Shared parser contract:
`preset_name|map_id|x|y`
→ `(preset,mid:int,x,y)` or `None`.

No persistent row UUID is recovered.

Per-account coordinate selection:
`acc_<character>_farm`.

The old `_farm` suffix remains even when receiver-role UI presents the same selector as a sell destination. Load restores only when the value still exists in current saved preset names or `SELL_MAP_LIST`.

Receiver config key surface:
- `recv_count`
- `recv_<n>_acc`
- `recv_<n>_coord`
- `receiver`
- `recv_coord`.

Current effective runtime Dồn coordinate is still the one shared `_recv_coord_var`. Exact precedence if old/per-row receiver coordinate values conflict is deferred to L06.

## Validation
No dedicated numeric-only validator is recovered for coordinate X/Y. L05 therefore adds no invented clamp or range.

Invalid/unresolvable values fail closed:
- movement skip/log;
- sell coordinate resolver returns `None`;
- shared Dồn point returns `None`;
- unknown save map skipped;
- stale load map skipped.

## List visibility
`_toggle_coord_list` hides/shows coordinate header + body; toolbar remains visible. No `[DonVang]` persistence key for this visibility state is recovered.

## Screenshot
Cross-check only after EXE-first analysis. Screenshot SHA-256 `dffb4da895d21dea87dd72a6601c29104f519dca89c2f716f5a7445bcbe4421a`, 452×1032.

It matches:
- saved row `Tọa độ 1 / Đại Lý / 0 / 0`;
- saved-row action **Train**;
- one shared **Tọa độ dồn** selector;
- receiver rows with account combo + delete only.

Those visible values are captured config/runtime state and are not promoted to universal fresh-install defaults.

## Runtime
Frozen `automove_log.txt`: SHA-256 `17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`, 387,238 lines.

No correlated Dồn-coordinate trace is present. Classification: **STATIC_VERIFIED / LIVE_RUNTIME_PARITY_REQUIRED**.

## Deferred
- legacy/per-row receiver-coordinate conflict precedence;
- exact fresh-row map/X/Y defaults independent of captured config;
- L06 receiver readiness/selection/locking/transaction internals;
- live runtime parity.
