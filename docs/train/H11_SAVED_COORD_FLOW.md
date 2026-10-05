# H11 — Train saved-coordinate persistence / edit flow

## Dynamic coordinate row

+ Thêm tọa độ
→ _add_coord_row(name=None, map_val=None, x_val=None, y_val=None)

No explicit name?
→ generate collision-aware "Tọa độ N"
→ numbering begins from 1
→ consult existing row names

row owns:
→ name_var
→ map_var
→ x_var
→ y_var
→ Bán button
→ Train button
→ ✕ delete

No fixed max-row constant is recovered.

## Edit hooks

name change
→ _on_name_changed
→ immediately refresh account combo options
→ rename_map {old_name:new_name}
→ any account currently selecting old_name moves to new_name
→ coordinate save path

other row edit
→ _auto_save
→ _schedule_save_all_coords

Exact coordinate-save scheduling/debounce delay:
→ UNKNOWN

Do not reuse FarmTab's unrelated exact 30ms scrollregion debounce.

Global H01 30-second config autosave remains a safety net.

## Map selection

coordinate map combobox
→ _on_map_select

selected entry is separator "====="?
→ jump to next real map item

save:
→ coord_id_for_name(display_map)
→ current MapID

map cannot resolve?
→ log unknown map
→ skip this row
→ never invent map id

## X/Y edit boundary

Coordinate row builder exposes x_var/y_var
but no dedicated _only_digits/vcmd validation surface.

Shared parse_coord_value:
→ split pipe record
→ returns (preset, mid:int, x, y)

Therefore:
→ H11 does not impose an invented numeric range/clamp
→ invalid/unusable coordinate text is left for later movement/runtime conversion.

## Config serialization

section:
→ Farm

for current dynamic rows in order:
→ _n = sequential index
→ key = coord_<n>
→ value = preset_name | map_id | x | y

Examples of key family:
→ coord_1
→ coord_2
→ ...

Map display name is normalized to map_id before serialization.

No persistent coordinate-row UUID is recovered.

## Config load

_load_coords
→ collect coord_* keys
→ ordered key/lambda path
→ parse_coord_value(value)
→ (name, map_id, x, y)
→ coord_name_for_id(map_id)
→ current map display name

map id/display no longer valid?
→ skip stale record
→ no fuzzy remap

valid?
→ _add_coord_row(name, map, x, y)
→ recreate dynamic row

Exact source expression of the key sort lambda remains UNKNOWN.
Preserve numerical coordinate-row order.

## Account Sell/Farm selections

save family:
→ acc_<character>_sell
→ acc_<character>_farm

load_acc_config:
→ load by character name
→ only apply saved preset if that preset name still exists

Preset renamed live:
→ rename_map immediately rewrites old selected value to new name

Preset added/deleted:
→ refresh all Sell/Farm combobox option lists

Exact immediate behavior when the currently selected preset is deleted:
→ UNKNOWN
→ do not auto-select an unrelated preset

## Apply-to-all

row Bán
→ _apply_coord_to_all(row, target="sell")
→ set this preset name in Sell comboboxes

row Train
→ _apply_coord_to_all(row, target="farm")
→ set this preset name in Train comboboxes

The selected identity is the preset name.
H05 later resolves name → live map/x/y vars.

## Coordinate list visibility

_toggle_coord_list
→ hide/show header + body
→ toolbar always remains visible

default B05 state:
→ header/body shown
→ button = Ẩn danh sách tọa độ

No Farm settings key persists this UI state.
Fresh tab construction starts shown.

## Load/save safety

FarmTab owns:
→ _importing
→ _saving_enabled

Constructor:
→ build UI
→ load config / recreate coordinate rows
→ normal interactive save enabled afterward

Exact guard flip statement ordering:
→ UNKNOWN

Semantic requirement:
→ loading rows must not rewrite/corrupt settings while the load itself is still in progress.
