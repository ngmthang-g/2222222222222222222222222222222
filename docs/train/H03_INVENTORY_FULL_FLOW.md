# H03 — Inventory-full / filter interaction flow

## Bag source

FarmTab._get_bag_slots(hwnd)
→ memory_items.get_bag(hwnd)
→ bag dict or None
→ bag["slots"]
→ occupied Site-10 slot count

Read error:
→ None
→ caller/UI keeps previous displayed bag value
→ never synthesize zero.

## Fullness predicate

Farm cycle
→ internal threshold
→ MI.is_full_bag(...)
→ full / not-full decision

The local threshold surface is verified.
Its exact numeric binding is not.

## Filter stage

_filter_before_town
→ get_pickup_preset_keys()
→ if no discard preset / keep-all:
   → no filtering
   → return None
→ else:
   → row state = Đang lọc đồ
   → bag_filter.discard_for_activity(
        activity="train",
        keys=pickup preset keys,
        stop_check=Farm cancel predicate
      )
   → read occupied slots after discard
   → return slots_after integer when readable
→ on error/unreadable:
   → return None
→ restore prior row state only if nobody changed it meanwhile

## never / Không về

fullness detected
→ log: túi đầy (N ô, Không về) → lọc
→ _filter_before_town

post-filter integer available?
→ re-evaluate fullness

still full
→ log: lọc xong vẫn đầy (N ô) → ở lại (Không về)
→ no automatic town return

no longer full
→ continue normal farm loop
→ no town forced

filter returns None
→ unknown/no-filter result
→ never mode still does not authorize automatic town return

## full_bag_timer / legacy full_bag

condition belongs to bag-enabled family
→ common wait installs stop_bag_check
→ stop_bag_check uses MI.is_full_bag
→ fullness becomes true
→ wait ends early
→ log N ô → về thành
→ shared pre-town filter remains available
→ enter town-return path

Exact periodic wait/poll mechanics are H04.

## cycle

cycle mode
→ bag fullness is not the early-stop condition used by full_bag_timer
→ periodic loop_minutes owns the return trigger
→ H04.

## Separation

Pickup discard filter
≠ sell-equipment/shop workflow.

Bag occupied-slot count
≠ total item quantity
≠ free-slot count.
