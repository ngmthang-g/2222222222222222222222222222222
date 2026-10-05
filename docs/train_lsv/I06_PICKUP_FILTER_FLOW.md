# I06 — Train LSV pickup/filter flow

## UI policy

pickup_mode_var
→ shared KEEP mode alias

modes:
→ none = Không
→ weapons = Chỉ vũ khí
→ all = Tất cả

default:
→ all

mapping:
→ none → [discard_weapons, discard_nonweapon]
→ weapons → [discard_nonweapon]
→ all → []

all / []:
→ shared discard helper short-circuits
→ no scan
→ no packet.

## Per-account discard watcher

Farm session
→ owns discard_stop
→ starts account-targeted _discard_loop(hwnd,...)

every 10 seconds:
→ memory_items.get_bag(hwnd)
→ occupied Site-10 slots

read failure:
→ do not treat sample as full

valid slots:
→ compare with FULL_BAG_THRESHOLD

not-full side:
→ no discard

full side:
→ keys = get_pickup_preset_keys()
→ capture row previous state
→ temporary state Đang lọc đồ (#8e24aa)
→ bag_filter.discard_for_activity(
     hwnd,
     activity='train',
     keys=keys,
     stop_check=...
   )

shared defaults retained:
→ delay=1.0
→ dry_run=False

shared engine:
→ merge selected preset rules
→ dedupe by dbID
→ whole-stack action 4 / packet 100005 "4:dbID"
→ returns total/ok/fail/skipped/stopped/targets

TrainLSV:
→ log total/fail or exception
→ restore previous state.

Exact FULL_BAG_THRESHOLD numeric:
→ UNKNOWN.

## Steady state

serialized worker set:
→ {'Đang train LSV'}

Exact use as pre-gate vs restore guard:
→ native-placement UNKNOWN

observable state transition:
→ previous
→ Đang lọc đồ
→ previous.

## No hidden pickup enable

TrainLsvTab decoded constants contain no:
→ PICKITEM
→ IsOn
→ set_auto_fields
→ PickRanger
→ IsFilterItem

Therefore:
→ no direct TrainLSV PICKITEM.IsOn=true path recovered
→ Nhặt đồ radio is discard/keep policy, not pickup-enable switch.

## Runtime

packaged automove_log:
→ no correlated [Nhặt đồ]/Đang lọc đồ/PICKITEM records
→ action=4 primitive appears many times

classification:
→ low-level discard primitive runtime-evidenced
→ top-level TrainLSV trigger static only.

## Next

I07:
→ Train LSV treatment routing/execution.
