# I04 — Rời LSV flow

## _leave_lsv(hwnd)

read character info
→ current_map

if current_map != 10000:
→ log map hiện tại ... không phải 10000 → bỏ qua
→ stop helper

if current_map == 10000:
→ shared move_character
→ target MapID 10000
→ tile (236,190)
→ pixel (7552,6080)
→ explicit keyword wait_for_arrival=<VALUE UNKNOWN>

movement result false:
→ log di chuyển tới cổng thất bại
→ do not run normal exit-click sequence

movement result success:
→ click (887,475)
→ pacing via local time exists; exact sleep interval/order UNKNOWN
→ click (478,427)
→ log [Rời LSV] Hoàn thành hwnd=

## What is NOT in _leave_lsv

no _ensure_in_lsv
no TRAIN_FLOOR_ORDER
no TRAIN_FLAT_WAYPOINTS
no floor/flat normalization
no stop_check argument
no explicit _ensure_injected
no post-click get_character_info
no second MapID read
no _wait_active
no common.active wait.

Therefore:
floor/flat map → direct manual leave helper skips;
hub 10000 → move to gate + two clicks;
completion is not post-exit MapID verified by TrainLsvTab.

## Runtime evidence

packaged automove_log:
→ no correlated Rời LSV log/click trace
→ generic movement primitives only

classification:
→ STATIC_VERIFIED.

## Next

I05 → Dạ Minh Châu / manual timed-key schedule execution.