# I02 — Train LSV entry / premove flow

## Tới LSV: _move_lsv

read current MapID

if current map in:
`{10000,10014,10015,10016,10017}`
→ shared `move_character`
→ target MapID 10000
→ tile (236,190)
→ pixel (7552,6080)
→ skip normal-world gate clicks

else:
→ shared `move_character`
→ normal Lạc Dương MapID 3
→ tile (232,190)
→ pixel (7424,6080)
→ movement failed? return failure
→ click (891,473)
→ 1-second pacing constant exists in this click block
→ click (480,605)
→ log entry completion

Important:
→ no `_wait_active` local/call surface inside _move_lsv
→ no second post-click character-info variable
→ do not fabricate MapID-10000 verification inside this helper.

## Shared movement/mount

_move_lsv
and
_ensure_in_lsv
→ direct shared `move_character`

Therefore:
→ shared memory/packet mount path is reused
→ shared remount/requeue can apply
→ no I02-specific horse click/hotkey recovered.

## Authoritative Train LSV map IDs

hub:
→ 10000

flat maps:
→ 10004 Phàm Liên Trại
→ 10005 Thanh Liên Trại
→ 10007 Khô Vinh Đạo

Địa Cung:
→ 10014 Tầng 1
→ 10015 Tầng 2
→ 10016 Tầng 3
→ 10017 Tầng 4

full ensure-zone set:
→ {10000,10004,10005,10007,10014,10015,10016,10017}.

## _ensure_in_lsv

input:
→ hwnd
→ stop_check
→ farm_map

farm_map None compatibility:
→ target 10014

outside full LSV set:
→ invoke Tới LSV with stop_check
→ post-entry block owns an exact one-arg integer 3 constant
→ exact sleep/call binding not instruction-bound

unknown map after normalization:
→ reason as if 10000.

## Flat target

TRAIN_FLAT_WAYPOINTS:
→ 10004: (37,264)
→ 10005: (487,257)
→ 10007: (256,36)

already on selected flat map:
→ no premove

otherwise:
→ move from hub side toward flat target
→ monitor resulting MapID
→ common.canhBaoPK visible?
   → click (617,454)
→ final MapID must equal requested flat map
→ mismatch = failure
→ success → _wait_active
→ premove complete

branch owns 0.3 and 0.5 timing constants
→ exact argument placement UNKNOWN.

## Floor target

TRAIN_FLOOR_ORDER:
→ 10000
→ 10014
→ 10015
→ 10016
→ 10017

invalid/not-found floor target:
→ default 10014

already at or above target index:
→ no lower-floor replay
→ final coordinate movement left to caller/I03

need climb:
→ sequential TRAIN_FLOOR_WAYPOINTS

10000 → 10014:
→ waypoint (258,470)
→ need_click=True
→ click (609,450) exactly 3 times
→ 0.5s apart
→ verify map becomes 10014
→ _wait_active

10014 → 10015:
→ waypoint (26,215)
→ need_click=False
→ movement/map-change verification
→ _wait_active

10015 → 10016:
→ waypoint (95,90)
→ need_click=False
→ movement/map-change verification
→ _wait_active

10016 → 10017:
→ waypoint (132,224)
→ need_click=False
→ movement/map-change verification
→ _wait_active

after premove:
→ caller/I03 performs final saved-coordinate move.

## _wait_active

exact defaults:
→ timeout=30
→ click_if_stuck=False

shared probe:
→ common.active
→ point (1330,33)
→ RGB (34,8,11)
→ tolerance 5

wait_pixel kwargs surface:
→ window_hwnd
→ timeout
→ interval
→ debug

exact interval/debug:
→ UNKNOWN.

if click_if_stuck=True and initial active check not found:
→ click (609,450) 2 times
→ 1s apart
→ continue waiting common.active.

Cancellation:
→ _wait_active signature has no stop_check
→ bounded wait is not directly Farm-stop-aware.

## Runtime evidence

packaged automove_log:
→ generic movement primitives exist
→ no correlated [Tới LSV] / gate-click / active / floor-entry trace found

classification:
→ STATIC_VERIFIED
→ runtime parity deferred to I12.
