# I10 — Train LSV coordinate persistence/edit flow

## Row creation

+ Thêm tọa độ
→ _add_coord_row(
     name=None,
     map_val=None,
     x_val=None,
     y_val=None
   )

row owns:
→ name_var
→ map_var
→ x_var
→ y_var
→ Train apply button
→ ✕ delete button

no Sell coordinate action in TrainLSV.

no hard max-row constant recovered.

generated-name path:
→ prefix "Tọa độ "
→ consults existing row-name surface
→ exact numbering/start algorithm UNKNOWN.

## Map identity

current TrainLSV local map list:
→ 10014..10017
→ 10004 / 10005 / 10007

save:
→ coord_id_for_name(display name)
→ numeric MapID

unknown display map:
→ exact [Farm] warning
→ skip row
→ do not invent ID.

load:
→ coord_name_for_id(saved MapID)
→ current display name

retired MapID:
→ skip

legacy display-map record no longer valid:
→ skip / recreate manually
→ no fuzzy remap.

No _on_map_select / "=====" separator path exists in TrainLsvTab.

## Record schema

shared parse_coord_value:

split on "|"

interpret:
→ parts[:-3] = preset-name portion
→ parts[-3] = map_id
→ parts[-2] = x
→ parts[-1] = y

return:
→ (preset, mid:int, x, y)

therefore current persisted value:
→ preset_name|map_id|x|y

preset name may itself contain "|" because parser owns all fields before last 3.

X/Y remain saved coordinate fields / tile-space text.
I03 performs runtime validation and ×32 pixel conversion.

## Save family

section:
→ TrainLSV

key family:
→ coord_<n>

save owns:
→ separate _n counter

exact first suffix:
→ UNKNOWN

invalid map row:
→ skipped
→ never serialized with guessed map id.

## Load

_load_coords
→ collect coord_* keys
→ sorted(..., key=<lambda>)
→ exact lambda expression UNKNOWN
→ preserve numeric row order
→ parse_coord_value
→ coord_name_for_id
→ _add_coord_row(name,map,x,y)

stale map:
→ skip.

## Rename / add / delete

name edit:
→ _on_name_changed
→ rename_map {old:new}
→ _refresh_acc_combo_values
→ every active account Train combobox options refresh
→ live old-name selections switch to new name
→ coordinate save path.

add/delete:
→ refresh account Train combobox options.

exact current selection behavior after deleting selected preset:
→ UNKNOWN.

duplicate manual names:
→ no explicit rejection recovered
→ exact resolver winner UNKNOWN.

## Apply to all

row Train button:
→ _apply_coord_to_all
→ use preset display name
→ assign to every account Train combobox.

No map/x/y snapshot is copied.

## Per-account persistence

selected farm_var
→ save key acc_<character>_train

load_acc_config:
→ apply only if saved preset name still exists

stale name:
→ ignore.

account farm_var has trace_add("write", ...)
→ interactive changes are save-wired.

## Edit-save lifecycle

coordinate row:
→ _auto_save
→ _on_name_changed
→ _schedule_save_all_coords

constructor guards:
→ _importing
→ _saving_enabled

exact scheduler delay/thread/debounce:
→ UNKNOWN

global safety autosave:
→ 30 seconds.

## Visibility

_toggle_coord_list:
→ hide/show coord header + body
→ toolbar stays visible

no persisted visibility key recovered.

## Runtime evidence

packaged automove_log:
→ no correlated coordinate config/edit trace

classification:
→ STATIC_VERIFIED / RUNTIME_ENV_REQUIRED.

## Next

I11:
→ Train LSV all-account commands + start/stop/FSM orchestration.
