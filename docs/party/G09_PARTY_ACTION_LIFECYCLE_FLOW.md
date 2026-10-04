# G09 — Party action lifecycle

## Global Party button

Bắt đầu / green
→ _toggle_run
→ collect get_groups_data jobs
→ no selected group?
   → log and stay idle
→ otherwise
   → clear global _cancel
   → global run state active
   → button = Dừng lại / red
   → launch _run_worker

_run_worker
→ create one cancel Event per cluster
→ one thread per cluster
→ each thread runs _run_one_group
→ keep own_cancels + threads
→ wait/join aggregate workers
→ when all settle:
   → _after_party_action once
   → _reset_run_button once
   → normal Bắt đầu / green state

## Global stop

while global run active
→ _toggle_run / external stop()
→ button = Đang dừng... / orange / disabled
→ signal cancellation lifecycle
   → global _cancel
   → per-cluster cancel Events tracked by _run_cancels
→ workers exit through cancellation-aware waits
→ aggregate completion/reset
→ Bắt đầu / green

Exact Event-set iteration/lock statement order: UNKNOWN.

## Single-cluster button

▶ Tạo nhóm N
→ _run_single_cluster
→ permission/limit check
→ if join_running:
   → log đang chạy rồi
→ collect _group_members
→ if fewer than 2:
   → log cần ít nhất 2 acc
→ create/use separate join_cancel
→ mark join_running
→ button = ⏳ Đang vào... / disabled
→ background _run_single_worker
→ same _run_one_group engine
→ cleanup/discard cancel tracking
→ completion lambda
→ _reset_single_button
→ ▶ Tạo nhóm N normal/green

Multiple distinct single-cluster actions may run in parallel.

Exact collision rule if the global worker is simultaneously running the same cluster: UNKNOWN.

## Rời nhóm

Rời nhóm
→ _leave_group
→ daemon _leave_group_worker
→ current cluster members
→ skip offline/already-outside members
→ later leave protocol (G10)

## Structural controls

+ Thêm nhóm
→ _add_group_cluster

✕ Xóa N
→ _remove_group
→ keep at least one cluster
→ renumber

These are configuration/UI structure actions, not run workers.
