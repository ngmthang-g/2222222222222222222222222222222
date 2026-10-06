# K04 — Trừng Ác quest/NPC flow

## Return to NPC

```text
cycle
  ↓
teleport mode?
  ├─ yes
  │    configured DLL key
  │    fixed click (490,429)
  │    ↓
  └──────────────┐
                 ↓
_punish_goto_bodau
  ↓
attempt re-inject
  ├─ fail → log, still continue move
  ↓
move_character
  target = map 4 / (224,285)
  tolerance = 96
  wait_for_arrival
  stop_check
  ↓
stopped/fail/wrong map?
  ├─ yes → skip this cycle
  └─ no  → quest interaction
```

## Normal quest interaction

Strong static source-order coordinate grouping:

```text
"trả nhiệm vụ"
  (890,471)
  (884,423)
  (481,423)

"nhận nhiệm vụ"
  (891,467)
  (484,424)

  ↓
_punish_check_full
```

The shared row state `Làm nhiệm vụ` belongs to this quest phase.

## 30/30

```text
get_dialog_raw()
  ↓
Title / CleanMsg / Buttons
  ↓
Ngô Giới?
message has "tối đa 30"?
button "Ta biết rồi"?
  ↓ no
False = not full
  ↓ yes
click_dialog_button("Ta biết rồi")
  ↓
dialog verified closed?
  ├─ no  → False = not full
  └─ yes → True
             ↓
       terminal-stop this account's Trừng Ác
```

This replaces the older unreliable pixel full detector.

## No-target/stuck cancellation

```text
target coordinates cannot be parsed
   ↓
_punish_cancel_quest
   ↓
click (1072,130) close current panel
   ↓
move_to_npc(map=4, npc=698)
   ↓
dialog open?
  ├─ no → log failure
  └─ yes
       click (479,480)
       click (476,422)
       "đã gửi hủy nhiệm vụ → sang vòng mới"
   ↓
current cycle skipped
next outer cycle restarts from quest phase
```

The same cancellation concept is reused after repeated target travel failures; streak accounting is K05.

## Outcome split

```text
NPC movement/cancel-recovery failure
   → fail-soft / later cycle retry

verified 30/30
   → terminal for this account's Trừng Ác session
```
