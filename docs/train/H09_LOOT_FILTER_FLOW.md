# H09 — Train loot-filter / pickup interaction flow

## Keep-mode UI

Lọc đồ giữ lại:
→ pickup_mode

KEEP_MODES:
→ none
→ weapons
→ all

Labels:
→ none = Không
→ weapons = Chỉ vũ khí
→ all = Tất cả

Default:
→ all

## Exact preset mapping

keys_for_keep_mode("train", mode)

none
→ ["discard_weapons", "discard_nonweapon"]

weapons
→ ["discard_nonweapon"]

all
→ []

Interpretation:
→ keep-mode controls equipment discard presets
→ not “delete every non-kept bag item of every category”

Weapon path:
→ weapon_ids.is_weapon
→ weapons protected by default
→ only explicit discard_weapons / match_weapons=True may target them

Non-weapon equipment path:
→ metadata / NON_WEAPON_EQUIP_TYPES
→ metadata failure means non-weapon classification cannot be trusted

## Shared discard engine

FarmTab.get_pickup_preset_keys()
→ shared keys_for_keep_mode(activity="train", mode=current)

_filter_before_town
→ keys = current Train keep-mode presets
→ discard_for_activity(
     hwnd,
     activity="train",
     keys=keys,
     stop_check=Farm stop callback
   )

discard_for_activity defaults:
→ keys=None
→ extra_rules=None
→ delay=1.0s
→ stop_check=None
→ on_progress=None
→ dry_run=False

Farm supplies keys + stop_check
→ no Farm delay override recovered
→ shared 1.0s default pacing applies

empty keys/rules
→ no memory scan
→ no discard packet
→ zero discard result

selected presets
→ OR-combine rules
→ dedupe targets by dbID
→ one send pass

discard target
→ abandon packet 100005
→ payload "4:<dbID>"
→ whole stack represented by dbID

## Farm filter trigger

Normal FarmTab has no continuous _discard_loop.

Filtering is event-driven:
→ return-town / full-bag paths call _filter_before_town
→ H03 determines those trigger points

During filter:
→ state = Đang lọc đồ
→ style foreground #8e24aa
→ cancellation-aware discard pass

After filter:
→ if usable bag count exists: return slots_after integer
→ Tất cả/no-filter/error: return None
→ restore previous row state only if no other actor changed it

## Separate actual-pickup feature

checkbox:
→ Nhặt đồ không dùng hồ lô (càn khôn hồ)
→ pickup_no_cankhon
→ default False

Farm cycle path active?
→ invoke _pickup_no_cankhon

Exact helper behavior:
→ wait 5 seconds
→ memory_items.set_auto_fields
   → section PICKITEM
   → key IsOn
   → type bool
   → value True

No old physical/manual UI click sequence.

Important:
pickup_no_cankhon
≠ pickup_mode

pickup_no_cankhon
→ enables game pickup

pickup_mode
→ decides what Train filter discards later

## Explicit unknowns

- exact helper dispatch threading/inline micro-order relative to buff startup
- exact setter return/error handling in _pickup_no_cankhon
- any positive readback confirmation for PICKITEM.IsOn (not recovered)

Do not reinterpret 5 seconds as a recurring polling cadence.
