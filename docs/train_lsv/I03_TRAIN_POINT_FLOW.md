# I03 — Train LSV final train-point movement flow

## Manual row Tới chỗ train

row.farm_var
-> selected saved-coordinate preset name

_preset_to_vars(row.farm_var)
-> map_var, x_var, y_var

missing/invalid preset
-> log chưa chọn tọa độ Farm hợp lệ
-> do not start movement

valid preset
-> I02 _ensure_in_lsv(..., farm_map=...)
-> I03 _move_acc(hwnd, map_var, x_var, y_var, stop_check).

## _move_acc preconditions

log:
-> [Tới] Bắt đầu hwnd=

_ensure_injected(hwnd)

failed:
-> bỏ qua: chưa inject được DLL
-> stop this final move

success:
-> import/use shared move_character.

## Map resolution

selected map value
-> map_sel
-> resolve/validate numeric map_id

module lookup ownership:
-> _map_lookup
-> shared FARM_MAP_LIST
-> local _MAP_LIST

no map:
-> skip

invalid map_id:
-> skip

exact label/ID source expression:
-> UNKNOWN.

## Coordinates

saved X/Y
-> normalize textual value (strip surface)
-> validate numeric tile coordinates

invalid:
-> skip

valid:
-> tile_x / tile_y
-> x 32
-> pixel_x / pixel_y.

## Final shared movement

move_character(
-> hwnd
-> map_id
-> pixel_x
-> pixel_y
-> wait_for_arrival=True
-> stop_check=caller callback
)

manual button:
-> documented stop_check None semantics
-> run full movement

Farm cycle:
-> supplies stop callback
-> cancellation delegated into shared movement.

## No extra TrainLSV near skip

TrainLsvTab does NOT own:
-> _is_near helper
-> PosX/PosY sample
-> dx/dy distance
-> 8-tile threshold

So do not copy H05's explicit 8-tile FarmTab skip.

Shared move_character may still internally consider exact arrival; that is shared-helper behavior.

## No extra final active gate

after shared move_character:
-> no _wait_active call in _move_acc
-> no common.active
-> no second MapID read

I02 readiness waits belong to map/floor transitions only.

## Result

move_character success:
-> log [Tới] Hoàn thành hwnd=... (x, y)

move_character arrival timeout/failure:
-> log chưa đến nơi sau timeout (...) — tiếp tục tác vụ
-> do not reconstruct as unconditional fatal abort.

## Runtime evidence

packaged automove_log:
-> generic AutoMove/AutoPath primitive records exist
-> no correlated [Tới]/TrainLSV/Tới chỗ train top-level records

classification:
-> STATIC_VERIFIED.

## Next

I04:
-> Rời LSV only.
