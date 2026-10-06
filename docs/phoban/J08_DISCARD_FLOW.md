# J08 — Phó Bản discard flow

## Configuration mapping

```text
Vứt trang bị  → discard_equip_var → phoban_discard_equip
Vứt vật phẩm  → discard_items_var → phoban_discard_items
Vứt thuốc     → discard_meds_var  → phoban_discard_meds
```

Clean/default B07 state: all OFF.

## Runtime preset mapping

Exact serialized `DISCARD_TICK_KEYS`:

```text
(
  ("discard_equip_var", ("discard_equip",)),
  ("discard_items_var", ("discard_items",)),
  ("discard_meds_var",  ("discard_meds",)),
)
```

So `_discard_enabled_keys()` flattens current enabled presets in order:

```text
discard_equip
    ↓
discard_items
    ↓
discard_meds
```

## Toggle lifecycle

```text
checkbox changed
      ↓
_toggle_discard()
      ↓
enabled keys?
  ├─ no
  │    → _stop_discard()
  │    → save config
  │
  └─ yes
       ↓
     any group running?
       ├─ no
       │    → keep mode armed
       │    → "chờ lịch trình chạy"
       │    → save config
       │
       └─ yes
            → _start_discard()
            → existing-thread is_alive guard
            → stop/event + generation session
            → _discard_worker(gen)
```

## Periodic worker

```text
_discard_worker(gen)
    ↓
every PB_DISCARD_POLL seconds
    ↓
re-read enabled preset keys
    ↓
if no keys → exit
    ↓
collect accounts of currently-running groups
    ↓
for each account:
    if previous discard thread still inflight:
        skip this poll
    else:
        start one account thread
```

Accounts run in parallel.

## One account

```text
_discard_one_acc(hwnd, name, keys, stop)
    ↓
for key in keys:       # exact order from DISCARD_TICK_KEYS
    discard_for_activity(
        hwnd,
        "phoban",
        keys=[key],
        delay=1.0,
        stop_check=stop
    )
```

Within one account, presets are sequential.

## Shared bag_filter primitive

```text
discard_for_activity
    ↓
plan/filter bag
    ↓
discard_items
    ↓
memory_items Abandon
    ↓
CMD_ITEM_ACTION 100005
payload "4:<dbID>"
```

Action 4 = Abandon. No game-GUI click is required.

## Normal group final pass

Static normal-path ordering:

```text
last selected schedule row -> Xong
        ↓
_fkeys = current discard-enabled preset set
        ↓
_fkeys non-empty?
  ├─ no → skip final discard
  └─ yes
       → one dedicated final account-thread batch
       → _discard_one_acc for finishing group's targets
       → wait batch
       → "xong vứt lượt cuối"
        ↓
HOÀN THÀNH
        ↓
J07 _finish_group_run
```

If the user has unticked all discard controls, `_fkeys` is empty and the final pass is skipped.

No static evidence was recovered for a mandatory final flush after a hard abort/user stop.

## Multi-group behavior

```text
Group A normal completion
    → A final discard pass if ticks still ON
    → cleanup A

Group B still running
    → periodic discard worker continues for B

last group ends
    → worker detects no running groups
    → worker exits
```

## Explicit runtime unknowns

- numeric PB_DISCARD_POLL;
- exact worker-generation mutation/teardown order;
- exact per-account inflight key type;
- exact stop closure Boolean formula;
- a late cancel exactly around the final pass;
- periodic-vs-final-pass same-account interleaving.
