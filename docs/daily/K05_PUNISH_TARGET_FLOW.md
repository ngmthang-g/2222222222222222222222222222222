# K05 — Trừng Ác target / summon flow

## Target acquisition

```text
_punish_goto_target(hwnd, stop...)
      ↓
get_bag()
      ↓
find itemID 40004000
  ├─ missing
  │    → "túi không có Trừng Ác Lệnh → dừng acc"
  │    → terminal current-account Trừng Ác session
  │
  └─ found dbID
       ↓
       use_item(dbID)
       packet 100005 "3:dbID"
       up to 2 send attempts
       ↓
       both fail?
         → skip current cycle
```

## Target extraction

```text
after item use
    ↓
get_dialog_target()
    ↓ target usable?
  ├─ yes
  │
  └─ no
       ↓
       get_use_item_target(40004000)
       ↓ target usable?
          ├─ yes
          └─ no
               → _punish_cancel_quest()
               → next outer cycle
```

GameDialog parser shape:

```text
- <TargetName> ở <MapName> (<PosX>, <PosY>)
```

UseItemData fallback reads live doing-task template data.

## Travel

```text
target:
  MapID
  PosX
  PosY
  TargetName (fallback "mục tiêu")
      ↓
fast_travel.goto_map(
  ...,
  wait_for_arrival=...,
  stop_check=...,
  tag="TrừngÁc"
)
      ↓
stop condition?
  → skip/return

ordinary fail?
  → stop_character
  → update target failure streak
  → skip cycle

success?
  → clear/rebase stale target-failure state
  → summon stage
```

The exact Daily tile→pixel source expression is not statically bound.

## Repeated target failure

```text
_punish_target_fail state
default prior state = (None, 0)

_tkey = current target identity   [exact shape UNKNOWN]
_last = prior target identity
_streak = consecutive fail count

same target fails repeatedly
   ↓
"kẹt <streak> vòng liên tiếp → hủy NV"
   ↓
_punish_cancel_quest()
   ↓
clear/reset tracking
   ↓
new outer cycle
```

Exact threshold numeric = **UNKNOWN**.

## Summon

```text
_punish_summon_target
      ↓
get_bag()
      ↓
find same itemID 40004000
  ├─ missing → skip cycle
  └─ found
       ↓
       use_item(dbID)
       ↓ fail/exception → skip cycle
       ↓
       read GameDialog
       expected doc title: "Trừng Ác Lệnh"
       buttons documented:
          [2] Triệu hồi
          [3] Để sau
       ↓
       find button text "Triệu hồi"
       ↓
       click_dialog_button("Triệu hồi")
       → GameDialog:FunctionButtonClicked
       → verify dialog closed
       ↓
       success → continue to K06 combat
```

Unlike target acquisition, no 2-attempt summon-use retry is recovered.
