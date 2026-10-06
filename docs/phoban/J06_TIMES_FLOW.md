# J06 — Phó Bản run-count flow

## UI/config

```text
Lần column
   ↓
current widget = tk.Entry
   ↓
times_var
   ↓
new row default = 1
legacy missing times = 1
seed conversion failure -> "1"
```

The current UI is not a 1–5 readonly combobox.

A frozen auxiliary table still exists:

```text
TIMES_CLICK_POS
"1" -> (337,241)
"2" -> (336,266)
"3" -> (341,291)
"4" -> (337,317)
"5" -> (337,340)
```

but current dungeon execution does not use game `RepeatCount`; do not use this table to cap schedule `times`.

## Schedule dispatch

```text
J04 selected row
  {activity, name, times, row}
             │
             ▼
      _acc_step_worker
        │           │
        │           └─ Train
        │                ↓
        │             _do_train(
        │               ...,
        │               stop_check=...
        │             )
        │                ↓
        │             activate once
        │             times ignored
        │
        └─ Phó bản
             ↓
          _do_dungeon(..., times, ...)
```

## Why this is manual repetition

```text
_config_dungeon_memory
  SelectedFuBen = code
  AutoRepeat = False
  FollowLeader = True
  AutoRevive = True
  RepeatCount = UNTOUCHED
```

So `times` belongs to TLMTool's own control loop.

## One Phó Bản repetition

```text
current run
   ↓
DungeonCtx(run_idx=current, times=total)
   ↓
pre_config hook
   ↓
_config_dungeon_memory
   └─ its own 5-attempt / 2s write retry
   ↓
post_config
   ↓
pre_move
   ↓
move to meeting/NPC point
   └─ total movement attempts shown as /3
   ↓
post_move
   ↓
ROW-SHARED Barrier wait
   ↓
pre_start_fuben
   ↓
_start_fuben_retry
   ├─ current frozen doc: 5 × 0.3s
   ├─ from retry #2 onward, MapID already target -> pass
   └─ None while loading does not prove entry
   ↓
post_start_fuben
   ↓
_wait_dungeon_cycles
   ↓
one completed cycle requires:
   target MapID entered
       ↓
   later non-None MapID != target
       ↓
   count +1
   ↓
post-cycle stage
   ↓
ROW-SHARED Barrier wait again
   ↓
next requested repetition
```

The same Barrier created by J04 for the row is reused; it is not recreated for each run.

## Total count

```text
requested normalized times = N

normal contract:
  complete N dungeon enter→exit cycles
       ↓
  _do_dungeon returns success
       ↓
  account worker returns
       ↓
  all workers for row joined
       ↓
  row -> Xong
```

## `run_idx`

```text
_do_dungeon local: run
        ↓
nested context builder: run_idx
        ↓
DungeonCtx.run_idx
DungeonCtx.times = total requested count
```

Per-run context is proven. Exact first value (0 vs 1) is not statically instruction-bound in the current evidence.

## Helper watchdog conflict

The helper doc contains “vô thời hạn”, but its compiled constant/local block also contains:

```text
deadline
480
"theo dõi map timeout (...s) — hoàn thành ..."
```

So current reconstruction must preserve a 480-second watchdog branch and must not implement a truly infinite wait solely from the stale prose line. Deep timeout outcome belongs to J07.
