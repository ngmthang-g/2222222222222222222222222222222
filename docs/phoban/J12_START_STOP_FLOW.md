# J12 — Integrated start/stop lifecycle

## Entry points

```text
bottom button
  "Bắt đầu" / "Dừng lại"
        ↓
_toggle_run(gd=None)
  ├─ any group running → _stop_all_runs()
  └─ none running      → start all runnable groups
```

```text
group button
  "Bắt đầu lịch trình" / "Dừng lịch trình"
        ↓
_toggle_run(gd)
  ├─ this group running → stop this group only
  └─ idle               → start this group only
```

## Fresh start preflight

```text
stop branch? no
      ↓
has_permission_with_limit("phoban_tab", "phoban")
      ↓ denied
"[PhoBan] Khóa bản quyền - khong cho phep"
      ↓
NO new job/cancel/thread

allowed
      ↓
required memory plumbing
      ↓
_collect_group_job(gd)
      ↓
online targets + checked schedule?
  ├─ no → log / remain idle
  └─ yes → launch path
```

## One-group launch

```text
valid group job
      ↓
_reset_group_progress(gd)
      ↓
fresh group _run_cancel identity
      ↓
register current job/run
      ↓
active group becomes visible to run-scoped modes
      ↓
enabled shared modes may be ensured
      ↓
_run_one_group thread
      ↓
_sync_run_buttons()
```

Exact ordering of the shared-mode start calls versus the native Thread.start is not statically instruction-bound.

## Start-all launch

```text
for each group in UI order:
    job = _collect_group_job(gd)
    invalid → skip
    valid   → batch

batch empty
  → "[Phó bản] Không có nhóm nào để chạy"

batch non-empty
  → reset_all_progress()
  → fresh cancel/job identity per runnable group
  → one _run_one_group thread per runnable group
  → ensure enabled shared modes
  → "[Phó bản] Bắt đầu song song N nhóm — M acc"
  → _sync_run_buttons()
```

## Shared modes

All are tab-level, not one worker per group:

```text
Follow:
  ON+idle waits
  run start re-arms
  scope = running groups separately

Discard:
  tick+idle waits
  run start re-arms
  scope = running groups

Pickup:
  mode+idle waits
  run start re-arms
  scope = all selected members across all groups

Nga My buff:
  ON+idle waits
  run start re-arms
  scope = running groups
```

Existing-worker guards prevent duplicate workers when another group starts.

## Stop one group

```text
set this group's cancel
      ↓
group is immediately logically non-running
      ↓
button:
  Đang dừng lịch trình...
  #ef6c00
  disabled
      ↓
worker unwinds
      ↓
_finish_group_run(identity-safe)
      ↓
other groups continue
```

## Stop all

```text
bottom "Dừng lại"
      ↓
_stop_all_runs
      ↓
all run buttons:
  Đang dừng...
  #ef6c00
  disabled
      ↓
global cancel + every group cancel
      ↓
group workers unwind
      ↓
last group owns one global teardown
```

Public `stop()` has the same all-group cancellation semantics.

## Persisted modes survive run stop

```text
stop / normal end
  ≠ clear phoban_pickup
  ≠ clear phoban_follow
  ≠ clear discard ticks
  ≠ clear phoban_nga_my_buff
  ≠ clear phoban_recreate_team
```

Worker lifecycle ends, but the user's persisted selections remain for a later run.

## Final teardown

```text
_finish_group_run(current identity)
      ↓
still another active group?
  ├─ yes → clean this run only
  └─ no
       → "[Phó bản] Hết nhóm chạy — teardown toàn cục"
       → reset global flags/buttons/pickup lifecycle once
       → other run-scoped workers self-exit on no-running-group rules
```

## Destroy boundary

```text
<Destroy> → _on_destroy
```

Dedicated cleanup callback is verified. Exact internal source-line cleanup sequence is not recovered from printable constants and remains a runtime/native-decompilation item.
