# I07 — Train LSV treatment flow

## Enable/config

trist_var
→ [TrainLSV] trist
→ clean default False

heal_map_var
→ [TrainLSV] heal_map
→ legacy compatibility variable
→ active _heal_at_death ignores it.

Active destination:
→ TRAIN_HEAL_COORDS
→ {'10000': (163,237)}.

## _heal_at_death(hwnd, stop_check)

read character info
→ HpPercent

if readable HP >= 50:
→ log skip
→ no treatment

if readable HP < 50:
→ treatment path

if HP unreadable:
→ treatment path anyway.

## Movement

fixed destination:
→ MapID 10000
→ tile (163,237)
→ shared-movement derived pixels (5216,7584)

call shared move_character
→ result ok

if movement fails:
→ log di chuyển đến map trị liệu thất bại
→ stop normal treatment path.

Cancellation:
→ helper accepts stop_check
→ exact internal check/pass-through points UNKNOWN.

## Active treatment stage

state:
→ Trị liệu
→ style #555555

click points:
→ (892,474)
→ (514,424)

frozen behavior:
→ 2 treatment points x4 repeat

local model has no explicit '_' loop variable
→ strongly suggests click-helper repeat/count mechanism

exact source call shape:
→ UNKNOWN

effective click delay:
→ UNKNOWN
→ shared click_at default is 0.5s, but TrainLSV override is not bound
→ do not import H06 0.2s.

## Completion

after move + treatment clicks:
→ log hoàn thành trị liệu tại map ...

no:
→ post-treatment HpPercent reread
→ HP target verification loop
→ _wait_active
→ common.active.

## Callers

Farm start contains:
→ % < 50% lúc bắt đầu → trị liệu trước
→ _heal_at_death

death/recovery caller:
→ deferred I09.

## Runtime evidence

packaged automove_log:
→ no correlated treatment markers/coordinates

classification:
→ STATIC_VERIFIED / RUNTIME_ENV_REQUIRED.

## Next

I08:
→ reconnect watchdog/recovery only.
