# G12 — Party reconstruction handoff

This file is the compact contract for later Stage-S reconstruction. It does not authorize starting Stage S now.

## UI
Reuse B04/G01 exactly.

Do not remeasure or redesign Party.

Visible controls and sections:
- Sau khi party
- Cấu hình tổ đội
- Cấu hình nhóm
- dynamic 6-slot 2×3 clusters
- Rời nhóm
- Xóa nhóm
- ▶ Tạo nhóm N
- + Thêm nhóm
- bottom Bắt đầu.

After-party values:
- Chờ/wait
- Train/train
- Train LSV/train_lsv
- Dồn vàng/don
- Phó bản/phoban.

Do not add Party follow/pick controls.

## Window/member refresh
- source: start_tab.get_windows()
- Party owns no EnumWindows
- own recurring refresh: 3000ms
- background reads, Tk main-thread applies
- identity generation = HWND + PID
- same HWND/new PID means replace old member generation
- RoleName is display/config identity.

## Action identity
- RoleID is resolved live from read_own_ids + hwnd_of_pid
- TeamID is read live from read_team_id
- 0 / 0xFFFFFFFF = outside team
- None = read failure
- real non-sentinel equal TeamID = same team.

Never persist runtime HWND/PID/RoleID/TeamID.

## Start/window ownership boundaries
Party does not own:
- physical window grid/tiling
- preview/DWM
- keyboard sync
- mouse sync.

Party leader is not Start master.

Party's own game interaction is targeted automation, not sync broadcast.

## Config
Shared settings.ini / Settings:
- party_after
- party_groups
- party_group1 legacy mirror.

Current group schema:
`[{num:n, members:[name,...]}, ...]`

JSON uses ensure_ascii=False.

Do not restore dormant:
- party_corps_groups
- party_corps_group1
- party_follow
- party_pick.

## Global action lifecycle
Idle:
- Bắt đầu / green.

Run:
- one thread per cluster
- each cluster gets own cancel
- _run_one_group shared engine
- bottom becomes Dừng lại / red.

Stop request:
- Đang dừng... / orange / disabled
- cancellation-aware workers settle
- reset through _reset_run_button.

Aggregate:
- wait all group threads
- post-party action once
- reset once.

## Single-cluster lifecycle
▶ Tạo nhóm N:
- permission/limit guard
- minimum 2 members
- join_running duplicate guard
- own cancel + own thread
- ⏳ Đang vào... / disabled
- reuse _run_one_group
- reset through _reset_single_button.

Different single clusters may run concurrently.

Same-cluster collision with the global worker remains runtime-only UNKNOWN.

## B0→B3
B0:
- set UTILITIES.AutoAcceptInviteTeam=True
- read back
- False/None warn.

B1:
- skip known no-team
- leave via 200057 / action4 / 4:<ownRid>
- verify outside TeamID
- timeout logs and continues.

B2:
- leader packet create first:
  200057 / action0 / "0"
- verify real leader TeamID
- fallback only if needed:
  leader 1366×768
  conditional (391,683)
  conditional (34,462)
  (27,467)
  (154,214)
  (127,336)
  1 second between clicks
- retry count remains symbolic CREATE_RETRY until resolved.

B3:
- invite team via 200051 / 5:<RoleID>
- burst all members
- one shared TeamID wait
- resend missing once
- final wait
- remaining missing -> warning/manual-autoaccept diagnostic.

## Direct Rời nhóm
- resolve live targets
- skip offline/outside
- leave_team
- delay/log
- no added aggregate TeamID wait.

## Post-party
Global aggregate only.

wait:
- no action.

phoban:
- select Phó Bản tab on main thread
- skip if already running
- start Phó Bản's own process.

train/train_lsv/don:
- use just-partied name+HWND target set
- select destination tab first
- background readiness:
  want.issubset(have)
  1.0s polling
  max 20s
- main thread:
  exact HWND
  then name/lower
  then fresh resolve
  use current destination-row HWND
  skip missing
  skip already-running _farming_acc
  call destination _toggle_single_farm.

## Do not guess
Keep these unresolved until the correct evidence class resolves them:
- first refresh tick immediate/delayed — runtime
- same-cluster global+single collision — runtime
- global cancel -> post-action or suppress — runtime
- exact one-live-account branch — runtime
- numeric invalid RoleID sentinel — stronger decompile
- _run_lock exact critical section — stronger decompile
- _last_targets exact reset/merge sequence — stronger decompile
- exact CREATE_RETRY numeric — stronger decompile
- exact symbolic Party timing constant bindings — stronger decompile
- syntax-only cleanup/load/fresh-map microdetails — implementation-safe unknowns.

## Mandatory runtime parity
Before Party runtime parity is marked complete, exercise the 33 cases in docs/tasks/G12.md, with special focus on:
- same HWND reused by new PID
- same cluster global + single action
- explicit cancellation
- packet-first create vs click fallback
- auto-accept not confirmed
- B3 missing member after resend
- hidden destination readiness
- stale HWND name/fresh fallback
- ordinary cluster failure followed by post-party.

## Gate result
G01–G12 close Party research/static handoff.

Do not reopen an earlier Party task unless new evidence directly contradicts it.
