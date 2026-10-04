# H02 — Return-town condition / town-panel gating flow

## Base UI

town_condition_var
├─ never            → Không về
├─ full_bag_timer   → Khi đầy túi
└─ cycle            → Theo chu kỳ (phút)

Default:
→ cycle
→ loop_var = 30

_on_town_condition_changed
→ save config
→ does not own town-body visibility
→ no recovered condition-specific loop-Spinbox state toggle.

## Town-panel visibility

Hiện cấu hình
→ _toggle_town_config
→ show everything below the condition row
→ button becomes Ẩn cấu hình

Ẩn cấu hình
→ _toggle_town_config
→ hide town body
→ condition row remains visible
→ button becomes Hiện cấu hình

Default:
→ body hidden.

## Current vs legacy condition value

Current config:
→ town_condition

Current UI full-bag value:
→ full_bag_timer

Legacy accepted value:
→ full_bag

Runtime bag-enabled family:
→ full_bag_timer OR full_bag

Reconstruction semantic normalization:
→ legacy full_bag means current full_bag_timer
→ never create a fourth visible radio.

Exact source statement used during load remains UNKNOWN.

## lock_town gate

Account rows
→ selected farm_var preset
→ _preset_to_vars
→ selected route/map
→ TRUYEN_DAI_LY_ROUTES
→ route lock_town?

if ANY selected route is locked:
→ has_dungeon = true
→ town_condition_var = never
→ return-town condition radios = disabled

if NO selected route is locked:
→ condition radios = normal

No previous-condition restore state is recovered:
→ unlock re-enables controls
→ do not invent automatic return to the pre-lock cycle/full-bag mode.

Per-account safety predicate:
→ _is_dungeon_farm
→ old dungeon OR route lock_town.

## Mode semantics boundary

never
→ no automatic town return
→ bag-full path may filter
→ if still full, direct original log says stay because Không về.

full_bag_timer
→ bag-enabled timed condition
→ bag-full watcher can end the common wait early
→ town return path is allowed.

cycle
→ periodic loop_minutes condition
→ no full-bag early-stop branch used by full_bag_timer.

H03 owns the actual bag threshold/filter algorithm.
H04 owns exact periodic timer execution.

## Navigation priority UI

Four readonly comboboxes.

Available route methods:
→ blank
→ Phù 1
→ Phù 2
→ Phù 3
→ Ngựa

Defaults:
→ Phù 1
→ Phù 2
→ Phù 3
→ Ngựa

_on_nav_priority_changed
→ for each combobox:
   → collect route methods used by other priority slots
   → preserve current choice
   → rebuild available values excluding already-used methods

lock_town gate
-X→ nav combobox disable

Shared permission system may still disable the Farm UI globally.

## loop_minutes

loop_var remains persisted independently.
Condition switching does not clear it.
Town-body hide/show does not hide the Spinbox because Spinbox is in the condition row.
