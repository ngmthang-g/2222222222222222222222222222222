# H06 — Train treatment flow

## UI/config

Trị liệu sau khi chết
→ trist_var / config key trist
→ default off

Treatment combobox
→ heal_map_var / config key heal_map
→ default visible selection Trị liệu Tô Châu

Values:
→ separator Có sẵn
→ TRAIN_HEAL_COORDS built-ins
→ separator Thủ công
→ saved-coordinate names

_on_heal_sep_select
→ separator selected
→ jump to first real item below it

## Built-in destinations

Trị liệu Đại Lý
→ MapID 2
→ tile (43,178)

Trị liệu Lạc Dương
→ MapID 3
→ tile (255,126)

Trị liệu Tô Châu
→ MapID 4
→ tile (155,252)

Trị liệu Lâu Lan
→ MapID 5
→ tile (294,170)

## _heal_at_death resolution

heal_sel empty
→ log chưa chọn map trị liệu
→ failure/skip

heal_sel starts with "Trị liệu "
→ strip/resolve city name
→ resolve built-in MapID
→ lookup TRAIN_HEAL_COORDS

invalid MapID
→ explicit failure log

no built-in coordinate
→ explicit failure log

otherwise manual saved preset
→ resolve saved map/X/Y
→ unresolvable
   → explicit failure log

## Movement

resolved (map_id, tile_x, tile_y)
→ shared move_character
→ H05 convention: tile × 32 pixels
→ movement failure
   → log
   → treatment fails

No separate treatment-specific movement retry count is recovered.

## Treatment interaction

exact client points:
→ (892,474)
→ (514,424)

exact original doc:
→ click 2 points ×4 repetitions

same constant block:
→ exact 0.2 pacing value
→ ("common","active") readiness/completion pair

Safe boundary:
→ preserve 0.2
→ preserve common.active surface
→ exact binding of 0.2 and exact wait placement/timeout remain UNKNOWN

## Completion

interaction completes
→ log [Trị liệu] hwnd=... hoàn thành trị liệu tại <destination>
→ return success to Farm recovery caller

failure
→ return false/failure

Farm cycle
→ _heal_at_death(hwnd, hard_stop)
→ false
   → surface "trị liệu sau chết thất bại"

Exact death-FSM consequence after failure is H07.

## Cancellation

Farm hard_stop
→ treatment movement/interaction cancellation boundary
→ do not allow stale recovery worker to continue after Farm stop/generation change.
