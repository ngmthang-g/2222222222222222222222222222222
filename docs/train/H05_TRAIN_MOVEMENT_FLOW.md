# H05 — Train movement / Truyền routing flow

## Per-account Train target

row farm_var
→ selected saved-coordinate preset name
→ _preset_to_vars(name)
→ (map_var, x_var, y_var)
→ missing preset = (None,None,None)

row Tới bãi train
→ resolve preset
→ _move_acc

all-account Tới bãi train
→ checked rows
→ resolve each selected preset
→ parallel per-account movement

## Manual guard

_move_acc
→ account already in automatic Farm?
   → YES: log and skip manual movement
   → NO: continue

→ ensure movement/injection readiness
→ read selected map + tile X/Y

## Coordinate convention

saved X/Y
→ tile coordinates

movement primitive
→ pixel convention = tile × 32

live position for near check
→ PosX/PosY
→ convert with 32.0 pixels/tile

## Near-target skip

target map/tiles resolve?
current character info readable?
current map matches target?
→ if not, return False (fail-open, movement still runs)

otherwise:
→ compute tile-space dx/dy
→ FARM_NEAR_TILES = 8.0
→ if target considered near:
   → skip redundant movement
   → also suppress unnecessary Tới bãi train state/action

Exact dx/dy combination remains UNKNOWN.

## Forward normal/Truyền decision

target map has TRUYEN_DAI_LY_ROUTES entry?
→ NO:
   → ordinary move_character path

→ YES:
   → direct "to" steps or borrowed "to_from"
   → _move_truyen_to

_move_truyen_to
→ city -> farm shortcut steps
→ when route hits move_target:
   → substitute the user's selected target
      (farm_map_id, tile_x, tile_y)

## Route leg executor

move step
→ _truyen_move_retry
→ route-aware retry above move_character
→ wait_for_arrival
→ coordinate scale 32 pixels/tile

other handlers:
→ click
→ drag
→ pixel/wait-pixel
→ npc_hub
→ wait
→ sleep
→ move_target

wait:
→ default timeout 30s

sleep:
→ cancellation-aware remaining-time loop
→ cap/chunk 0.5s

npc_hub:
→ read current MapID
→ resolve_hub_npc
→ no TRUYEN_NPC_BY_TOWN entry?
   → abort
→ move_to_npc
   → may indirectly use live fast_hop_to_map

Exact route-leg retry count remains UNKNOWN.

## Return route resolution

return requested (sell or medicine)
→ _resolve_truyen_back

read current MapID
→ valid read:
   → prefer route for actual current map

memory read fails:
→ fallback to selected Farm preset route identity

normal map/no route:
→ route = None
→ ordinary movement

## Back shortcut execution

route exists
→ _run_farm_exit
→ execute "back" steps
→ refresh/invalidate map state
→ fast_travel.verify_exited_farm
→ fresh current MapID differs from farm map?
   → YES: exit verified
   → NO / unreadable: exited_ok=False

## Fallback to walking home

route None
→ ordinary walk to configured destination

route exists but exit verification fails
→ user/cycle canceled?
   → YES: abort
   → NO:
      → log teleport hụt
      → WALK to destination anyway

Sell:
→ log teleport hụt, vẫn ở farm → đi bộ về điểm bán

Medicine:
→ log teleport hụt, vẫn ở farm → đi bộ về điểm mua

Return target:
→ _get_sell_coords
   → built-in SELL_MAP_LIST + SELL_MAP_COORDS
   → or manual saved preset
   → or meds_map_var for medicine
→ (map_id, tile_x, tile_y)

Normal home movement:
→ home_priority = _get_nav_priority()
→ Phù 1 / Phù 2 / Phù 3 / Ngựa
→ pass to move_character
→ wait_for_arrival

## fast_travel module boundary

fast_travel.py:
→ run_steps/goto_map = DORMANT
→ fast_hop_to_map = LIVE via move_to_npc
→ verify_exited_farm = used by FarmTab return verification

Therefore:
FarmTab active movement owner
≠ generic fast_travel.goto_map.

Do not substitute dormant goto_map for FarmTab's current local movement helpers.

## Explicit unknowns

- exact near-target metric expression using dx/dy
- exact route-leg retry count
- active FarmTab forward-shortcut final failure: plain-walk fallback vs abort
- ordinary move_character arrival tolerance
- exact long walk fallback timeout
