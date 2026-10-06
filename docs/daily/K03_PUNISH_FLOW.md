# K03 — Trừng Ác outer run flow

## Configuration

```text
duration: 15 seconds clean baseline
move mode:
  horse    → Ngựa
  teleport → Định vị phù

teleport hotkey:
  "" clean baseline
  choices 1 / 2 / 3
```

Config compatibility surface:

```text
daily_punish_duration
daily_tele_use
daily_move_mode
daily_tele_hotkey
old_tele_use local
```

Exact old/new move-mode precedence remains unresolved at source-expression level.

## Apply all

```text
Áp dụng Trừng ác cho tất cả acc
   ↓
_apply_punish_all()
   ↓
for every current account row:
    activity_var = "Trừng ác"
```

It selects activity; it does not start execution.

## Activity-wide entry

```text
_punish_start_worker
   ↓
inject first
   ↓
_punish_toggle
```

Toggle:

```text
idle
  → button Dừng lại / FireBrick
  → _punish_run_worker

running
  → signal activity-wide _punish_cancel
  → Đang dừng... / disabled
```

Reset:

```text
_punish_reset_ui
  → Trừng ác / RoyalBlue / normal
```

## Batch worker

```text
_punish_run_worker
   ↓
snapshot rows whose activity == "Trừng ác"
   ↓
snapshot process identities (selected_pids)
   ↓
no selected?
  → skip
   ↓
loop_idx = 1...
   ↓
filter live accounts
   ├─ none → stop
   ↓
filter still-active accounts
   ├─ all stopped → auto stop
   ↓
fan out one cycle to accounts in parallel
   ↓
next Lần
```

No user-configured repeat count exists.

## Single-row worker

```text
_toggle_single_acc / Daily bottom coordinator
   ↓
_punish_single_worker(hwnd, row)
   ↓
snapshot row._gen
   ↓
_GenStop(real row stop event + generation)
   ↓
loop_idx = 1...
   ↓
_punish_exec_sequence(...)
   ↓
repeat until stop/session/window/recovery condition
```

## Stop ownership

```text
activity batch stop:
  _punish_cancel
  reason = cancel(batch-trừng-ác)

row stop:
  row._stop_event
  reason = stop_event(dừng)

rapid row restart:
  row._gen changes
  reason = gen(phiên-mới)
```

These are separate stop identities.

## Entry-point distinction

```text
activity-wide Trừng Ác start:
  only Trừng Ác-selected rows
  one batch worker

Daily bottom Bắt đầu:
  mixed Trừng Ác / Tàng Bảo Đồ rows
  one single-account worker per row
```

Do not merge them.

## Deferred deep cycle

K03 deliberately stops before:
- NPC/quest acquisition;
- 30/30 detection and stuck quest cancellation;
- target extraction/navigation/summon;
- combat and movement-stop logic;
- heal/reconnect/respawn;
- discard worker details.
