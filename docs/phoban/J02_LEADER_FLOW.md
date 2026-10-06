# J02 — Phó Bản leader semantics flow

## UI leader

group slot 1
→ visible leader label

slot 1 blank
→ "(chưa chọn)"

slot 1 stale/offline
→ combo refresh invalidates stale value
→ leader label follows current slot state.

No live game TeamLeader read drives this label.

## Current execution roster

_group_targets(gd)
→ iterate current group comboboxes
→ resolve online HWND
→ skip blank/offline
→ preserve current slot order
→ unique [(name, hwnd)] roster.

## Run-local leader metadata

_run_one_group
→ receives current online targets
→ owns run-local _leader_hw
→ owns per-target _idx
→ starts per-account _acc_step_worker.

Strong static model:
→ one current target is captured as run leader
→ each target gets member index
→ worker gets:
   is_leader
   member_index
   total_members.

Exact native assignment:
→ UNKNOWN at source-expression level.

## Recreation relationship

Tạo lại đội OFF
→ skip J01 B0/B1/B2/B3
→ schedule workers still receive leader metadata.

Tạo lại đội ON
→ J01 recreate-team first:
   nominal first-slot leader
   offline fallback -> first online target
→ then normal schedule worker creation.

Do not require read_team_leader before creating is_leader metadata.

## Per-account step

_acc_step_worker(
  ...,
  is_leader,
  member_index,
  total_members
)

Phó bản activity
→ _do_dungeon(
     ...,
     acc_name=...,
     is_leader=...,
     member_index=...,
     total_members=...
   )

Train activity
→ leader metadata is not needed by _do_train.

## DungeonCtx

DungeonCtx:
→ tab
→ hwnd
→ acc_name
→ dungeon
→ is_leader
→ member_index
→ total_members
→ mid
→ post
→ stop_check
→ cancel
→ barrier
→ run_idx
→ times

defaults:
→ is_leader=False
→ member_index=0
→ total_members=1.

## Hook layer

_do_dungeon
→ build DungeonCtx
→ get_dungeon_handler
→ call common/dungeon hooks with ctx.

BaseDungeon:
→ pass-through
→ no leader-specific action.

SatTinhDungeon:
→ current docs explicitly "mọi acc giống nhau"
→ no leader-specific branch
→ is_leader/member_index reserved for future specialization.

## Common dungeon config

all participating accounts:
→ SelectedFuBen = dungeon code
→ AutoRepeat=False
→ FollowLeader=True
→ AutoRevive=True

This FUBEN.FollowLeader flag is separate from PhoBanTab is_leader.

## Team-leader memory

PhoBanTab:
→ read_team_id present
→ read_team_leader absent
→ TeamLeader / LeaderID / is_team_leader absent.

phoban_dungeons:
→ same absence.

Shared memory_items read_team_leader exists elsewhere in EXE
→ not part of current Phó Bản leader pipeline.

## Follower source boundary

J03 follow worker:
→ leader position source = first combobox of running group.

Follower polling/movement behavior:
→ deferred to J03.

## Runtime evidence

packaged automove_log:
→ no is_leader
→ no member_index
→ no leader/Đội trưởng
→ no PhoBanTab/[Phó bản]/Sát Tinh top-level trace.

classification:
→ STATIC_VERIFIED / RUNTIME_ENV_REQUIRED
   for exact _leader_hw expression and offline race timing.

## Next

J03
→ follower / Theo sau đội trưởng worker semantics.
