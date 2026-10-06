# J09 — “Nhặt không hồ lô” flow

## UI/config

```text
Nhặt không hồ lô
        ↓
pickup_var
        ↓
phoban_pickup
clean default = 0 / OFF
```

Internal docs call this mode `Tự nhặt đồ`.

## Lifecycle

```text
tick changed
    ↓
_toggle_pickup
    ↓
mode saved to config
    ↓
schedule currently running?
  ├─ yes + tick ON
  │    → _start_pickup
  │    → is_alive guard
  │    → _pick_stop.clear()
  │    → _pickup_worker
  │
  ├─ tick OFF
  │    → _stop_pickup
  │    → stop keepalive immediately
  │
  └─ idle
       → keep persisted mode only
       → no continuous pickup worker outside schedule
```

No `_pick_gen` field exists.

## Member collection

```text
_pickup_members
    ↓
get_groups_data()
    ↓
all selected members from ALL groups
    ↓
deduplicate with stable order
```

This is not restricted to only the currently-running group.

The worker lifetime itself is still schedule-scoped.

## One poll

```text
every PICK_POLL seconds
        ↓
names = _pickup_members()
        ↓
name_hw = _hwnd_by_name(...)
        ↓
for selected name with live hwnd:
        ↓
get_auto_settings(hwnd)
        ↓
PICKITEM.IsOn
        ↓
bool/readback says ON?
   ├─ yes
   │    → no write
   │
   └─ no / not effectively ON
        → set_auto_fields(
             hwnd,
             {
               "PICKITEM": {
                 "IsOn": True
               }
             }
           )
        → shared helper SaveSetting
        → log OK / FAIL
```

The worker repeats this readback/repair loop every poll.

## Operational meaning

```text
J09 does NOT:
  - scan bag items
  - run bag_filter presets
  - send ItemAction discard/use packets
  - click dropped objects on screen

J09 does:
  keep game auto setting PICKITEM.IsOn = True
  while the Phó Bản schedule background mode is active
```

## Stop behavior

Recovered pickup path contains:

```text
PICKITEM.IsOn = True
```

but no recovered pickup-local:

```text
PICKITEM.IsOn = False
_sweep_off()
```

Therefore:

```text
untick / stop
   → stop enforcing ON
   → do not invent forced OFF write
```

## Last-group teardown

```text
Group A finishes, Group B still runs
   → no global pickup teardown

last group finishes
   → _finish_group_run global teardown
   → reset/stop pickup worker lifecycle once
   → persisted checkbox is not proven cleared
   → PICKITEM.IsOn=False is not recovered
```

## Runtime unknowns

- numeric PICK_POLL;
- exact stop/thread join/reference-clear order;
- malformed/missing get_auto_settings branch;
- rapid stop→start race without generation protection;
- live Windows/game parity.
