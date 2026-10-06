# J11 — Multiple-group coordination flow

## Group container

```text
PhoBanTab
  ├─ _groups[]
  ├─ _group_counter
  ├─ _run_lock
  ├─ _active_runs
  └─ _run_jobs
```

UI:

```text
+ Thêm nhóm
    ↓
_add_group_cluster()
    ↓
group dict
  ├─ six member vars
  ├─ leader label
  ├─ schedule rows
  ├─ group header all_var
  ├─ Tắt auto PB
  ├─ Bắt đầu lịch trình
  └─ _run_cancel when running
```

## Count semantics

```text
reference B07 baseline: 1 group

✕ Xóa nhóm:
  exact doc says "cho phép xóa hết"
  → runtime minimum = 0 groups

MAX_GROUP_MEMBERS exists = 6
MAX_GROUPS does not exist in recovered Phó Bản contract
  → do not invent a group-count cap
```

## Cross-group member uniqueness

```text
ready accounts
      ↓
Group 1 selection
      ↓
selected name removed from later-group dropdowns
      ↓
Group 2 / Group 3 ...
```

Current valid selection stays; stale/dead selection resets.

## Delete / renumber

```text
✕ Xóa nhóm
    ↓
_remove_group(gd)
    ├─ run-cancel-aware path
    ├─ remove gd from _groups
    └─ _renumber_groups()
         ↓
      compact visible group numbering / persisted num model
```

Compatibility-only helpers remain:
- `_remove_last_group`
- `_update_del_group_state`.

## Persistence

```text
get_groups_data()
    ↓
[
  {
    "num": n,
    "members": [...],
    "schedule": [...]
  },
  ...
]
    ↓
phoban_groups
```

Group order is UI order.

## Start all

```text
bottom Bắt đầu
    ↓
for gd in groups:
    job = _collect_group_job(gd)
      ├─ no online targets → skip
      ├─ no checked schedule → skip
      └─ (num, targets, sched)
    ↓
one cancel/job identity per runnable group
    ↓
_run_jobs / _active_runs under _run_lock
    ↓
one _run_one_group thread per runnable group
```

Log contract:

```text
[Phó bản] Bắt đầu song song N nhóm — M acc
```

## Independent group execution

```text
Group 1 thread ─── rows sequential; acc per row parallel
Group 2 thread ─── rows sequential; acc per row parallel
Group 3 thread ─── rows sequential; acc per row parallel
```

Stopping/failing one group sets that group's cancel and leaves other groups running.

## Finish ownership

```text
_finish_group_run(Group A)
   ↓
other groups still active?
  ├─ yes
  │    → clean only A's matching run identity
  │    → "... còn N nhóm chạy tiếp"
  │    → NO global teardown
  │
  └─ no
       → "Hết nhóm chạy — teardown toàn cục"
```

## Shared background-worker scopes

```text
Follow:
  running groups only
  leader/followers resolved inside each group

Discard:
  accounts of running groups only

Pickup:
  all selected members across ALL groups
  unique/order-preserving
  while pickup worker is schedule-scoped

Nga My buff:
  accounts of running groups only
```

These scopes are intentionally not identical.
