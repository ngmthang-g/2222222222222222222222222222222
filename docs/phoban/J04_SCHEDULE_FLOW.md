# J04 — Phó Bản schedule-row flow

## 1. Data model

```text
PhoBanTab
  ├─ _groups[]                         # UI/group order
  │    ├─ num
  │    ├─ vars[6]                      # members
  │    ├─ rows[]                       # schedule row/UI order
  │    ├─ all_var                      # group header checkbox
  │    ├─ btn_run
  │    └─ _run_cancel / running state
  └─ _schedule_rows                    # retained compatibility/aggregate surface
```

A schedule row's persistent/business payload is:

```text
enabled
activity
name
times
```

A live row additionally carries widget/state references, including the frame and progress label.

## 2. Add-row flow

```text
+ Thêm Lịch trình
        ↓
_add_schedule_row(
  enabled=True,
  activity=None,
  name=None,
  times=1,
  rows=None
)
        ↓
rows=None → use final/current target group rows
        ↓
activity choices = Phó bản | Train
        ↓
_map_names_for_activity(activity)
        ├─ Phó bản → PHOBAN_MAP_LIST
        └─ Train   → TRAIN_MAP_LIST
                     "Về train theo thiết lập sẵn"
        ↓
create enabled/activity/name/times/status/delete widgets
        ↓
activity/name/times writes → _auto_save
```

Changing activity replaces the allowed name list. If the old name is invalid it is reset; `times` is preserved.

## 3. Progress flow

Canonical style table:

```text
chưa → Chưa  #808080
đang → Đang  #b8860b
xong → Xong  #1b5e20
```

Worker-safe update:

```text
background run thread
        ↓
_set_row_progress(row, status)
        ↓
schedule apply on Tk/main thread
        ↓
set_progress(row, status)
        ↓
PROGRESS_STYLES
        ↓
progress label text + foreground
```

Global reset:

```text
reset_all_progress()
  → all groups/all rows → Chưa
```

Per-group reset:

```text
_reset_group_progress(gd)
  → gd.rows only → Chưa
```

## 4. Persistence flow

### Modern

```text
get_groups_data()
        ↓
[
  {
    "num": n,
    "members": [...],
    "schedule": [
      {
        "enabled": ...,
        "activity": ...,
        "name": ...,
        "times": ...
      }
    ]
  }
]
        ↓
json.dumps(..., ensure_ascii=False)
        ↓
Settings/phoban_groups
```

### Legacy compatibility

```text
Settings/phoban_group1   # old single-group member surface
Settings/phoban_schedule # old flat schedule surface
        ↓
load/migrate into current group rows
        ↓
if activity == "Bán đồ":
    skip old row
missing enabled → True
missing times   → 1
```

The frozen save path still references modern and legacy keys, so reconstruction must preserve compatibility until later evidence explicitly removes it.

## 5. Schedule selection

```text
group rows (UI order)
        ↓
enabled/ticked filter
        ↓
get_selected_schedule()
        ↓
[
  {
    activity,
    name,
    times,
    row     # live row reference for status updates
  },
  ...
]
```

No sort by activity/name is recovered. Current UI row order is execution order.

## 6. Runnable group job

```text
_collect_group_job(gd)
        ↓
selected online targets
+
selected schedule rows
        ↓
(num, targets, sched)
```

Returns `None` if:
- no online selected account; or
- no enabled schedule row.

## 7. All-group concurrency

```text
bottom Bắt đầu
        ↓
collect runnable groups
        ↓
one _run_one_group thread per group
        ↓
Group 1 ───────────────┐
Group 2 ───────────────┼─ run independently / in parallel
Group N ───────────────┘
```

The button inside one group only starts/stops that group and leaves other groups untouched.

## 8. One-group row sequencing

```text
_run_one_group(job)
        ↓
optional J01 Tạo lại đội
        ↓
parallel _acc_setup for targets
        ↓
join all setup threads
        ↓
for item in sched:                # stable row order
    _set_row_progress(row, "đang")
        ↓
    Barrier for this schedule step
        ↓
    one _acc_step_worker per target
        ├─ Phó bản → _do_dungeon
        └─ Train   → _do_train
        ↓
    join all step workers
        ↓
    normal path:
    _set_row_progress(row, "xong")
        ↓
next row
        ↓
HOÀN THÀNH
        ↓
_finish_group_run(...)
```

The J04 concurrency contract is therefore:

```text
GROUPS: parallel
ROWS INSIDE A GROUP: sequential
ACCOUNTS INSIDE A ROW: parallel
```

## 9. Deferred boundaries

Not expanded here:
- J05: PHOBAN_MAP_LIST / dungeon-list and handler binding;
- J06: exact meaning and iteration of `times`;
- J07: cancel/abort/failure/status-machine branches and barrier-break behavior.

Those later tasks must consume this J04 row-order contract rather than recreating a different scheduler.
