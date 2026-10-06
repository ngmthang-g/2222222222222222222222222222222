# J07 — Phó Bản run-state / abort flow

## State ownership

```text
PhoBanTab
  ├─ _running
  ├─ _cancel              # tab/global Event
  ├─ _run_lock
  ├─ _active_runs
  ├─ _run_jobs
  └─ groups[]
       └─ _run_cancel     # per-group Event
```

Exact running test:

```text
_group_is_running(gd)
  = gd has _run_cancel
    AND that Event is not set
```

## Button state machine

```text
GROUP
idle
  Bắt đầu lịch trình
        │ start
        ▼
running
  Dừng lịch trình
  #f44336
        │ stop
        ▼
stopping / winding-down
  Đang dừng lịch trình...
  #ef6c00
  disabled
        │ _finish_group_run
        ▼
idle
```

```text
BOTTOM TAB
no group running
  Bắt đầu
        │
        ▼
at least one group running
  Dừng lại
  #f44336
        │ stop all
        ▼
Đang dừng...
#ef6c00
disabled
        │ final group teardown
        ▼
Bắt đầu
```

## Cooperative stop

```text
stop one group
  → set that group's cancel
  → synchronization/failure shell releases that group's workers
  → other groups keep running

stop all / stop()
  → global cancel
  + each group cancel
  → all active group workers unwind
  → final finishing group owns global teardown
```

No forced Python thread-kill mechanism was recovered.

## Hard failure shell

```text
one account hard-fails
        ↓
_abort_cycle(barrier, group_cancel)
        ├─ abort/break Barrier
        └─ set group cancel
        ↓
peers blocked at barrier are released
        ↓
_barrier_wait(...) returns False
        ↓
workers do not advance to next schedule step
        ↓
_finish_group_run(...)
```

`_abort_cycle` is explicitly idempotent.

## Hook behavior — J13 correction

```text
_call_hook(...)
  ├─ explicit False → _abort_cycle → current-group abort
  ├─ missing hook   → common/pass model
  └─ hook raises    → STATIC CONFLICT
       docstring says pass
       adjacent branch text says "→ abort"
```

Hook exception behavior must remain unresolved until J14/stronger native evidence.

## Failure escalation by dungeon stage

```text
config write
  5 × 2s retry
  exhausted → group hard-fail

move to meeting point
  up to 3 total attempts
  exhausted → group hard-fail

row barrier
  no normal timeout
  aborted by failure/stop → False

start FuBen
  5 × 0.3s
  still outside target map → group hard-fail

cycle wait
  False → "chờ cycle map FAIL" → group hard-fail

unexpected generic _acc_step_worker exception
  → log worker lỗi
  → no independent worker-local abort wiring recovered

unexpected _do_dungeon exception
  → log lỗi chu trình
  → exact abort micro-order remains unresolved
```

## 480-second branch

```text
_wait_dungeon_cycles
  locals:
    deadline
    done
  compiled constant:
    480
  log:
    "theo dõi map timeout (...) — hoàn thành ..."
```

The static artifact proves the branch exists but not its exact native return expression. That return remains explicit UNKNOWN.

## Row progress

Only three states exist:

```text
Chưa → Đang → Xong
```

No Error/Cancelled row style exists.

```text
start/restart group
  → _reset_group_progress
  → Chưa

normal row
  → Đang before worker batch
  → workers join
  → normal continuation
  → Xong
```

Exact abort-race placement relative to the final `Xong` write is not instruction-bound; do not invent a new failure label.

## Identity-safe teardown

```text
old session:
  gd + job_old + cancel_old
           │
           └── winding down

user starts same group again:
  gd + job_new + cancel_new

_finish_group_run(old)
  checks identity
  ├─ old cancel/job is no longer current
  │    → MUST NOT clear new session
  └─ only current-owned state is removed
```

This prevents a late old worker from:
- deleting the new run;
- making the group falsely idle;
- tearing down the tab while another session/group is active.

## Multi-group finalization

```text
Group A finishes
  ├─ Group B/C still running
  │    → clean A only
  │    → log remaining group count
  │    → NO global teardown
  │
  └─ no group remains
       → "[Phó bản] Hết nhóm chạy — teardown toàn cục"
       → reset global flags/buttons/pickup lifecycle
```

## Recovery model

```text
hard failure
  → local stage retries exhausted
  → abort only current group
  → safe teardown
  → idle/startable again

manual/new start
  → progress reset
  → fresh cancel/job identity
  → old finishing worker cannot remove new run
```

No automatic whole-group restart after a hard abort was recovered.
