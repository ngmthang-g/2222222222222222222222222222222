# H14 — Train global Farm start/stop FSM flow

## State ownership

`_farming`
→ global Farm mode / large-button state

`_farming_acc`
→ authoritative per-account Farm membership

`_farm_threads`
→ worker lifecycle collection

`_stopping_play`
→ rows requested to stop whose old Farm cycle has not actually exited yet

`row['_gen']`
→ session generation barrier for stale monitor/buff/reconnect workers

Do not collapse these states.

## FarmTab initial / stopped UI

bottom button:
→ `Bắt đầu`
→ bg `#388e3c`
→ enabled/normal

StartTab quick Farm control:
→ stopped baseline label `Train`

## Global Bắt đầu

`_toggle_farm`

if global stopped:
→ all current Train rows
→ skip rows already in `_farming_acc`
→ start eligible not-yet-Farm rows
→ full per-account Farm session, not manual Fight
→ running projection

global active projection:
→ FarmTab `Dừng lại`
→ `#f44336`
→ StartTab state synchronized

per active row:
→ `II`
→ `#f44336`.

Exact global in-function permission recheck:
→ UNKNOWN.

## Single ▶ start

`_toggle_single_farm(hwnd)`

row already in `_stopping_play`:
→ must not start a replacement session before old cycle exits

permission:
→ `has_permission_with_limit`
→ scope `farm_tab`
→ action `farm`

start full session:
→ `_farm_cycle`
→ `_resize_monitor`
→ refresh row play projection
→ global FSM becomes/remains running

exact Thread daemon flags:
→ UNKNOWN

exact membership/gen mutation order:
→ UNKNOWN.

## Running Farm cycle

`_farm_cycle(row)`

owns one account loop:
→ bán đồ
→ mua thuốc
→ tới
→ farm
→ chờ chu kỳ

session locals:
→ monitor_stop
→ reconnect_ok
→ halt
→ respawn_event
→ gen_snap
→ hard_stop
→ buff_stop
→ cycle_start
→ buff_thread

H07/H08 subworkers belong to this session generation.

## Stop request

No force-kill.

cooperative guards:
→ `_check_stop`
→ `_is_acc_farming`
→ generation checks
→ HWND/PID validity
→ hard_stop/halt for relevant subflows

row stopping UI:
→ `_stopping_play`
→ `…`
→ orange `#ef6c00`
→ disabled
→ normal play refresh skips this row.

This prevents a new overlapping cycle.

## Worker drain

`_wait_farm_stop(threads, has_remaining)`
→ calls `join`
→ wait for requested Farm worker(s) to actually exit

join timeout:
→ UNKNOWN

if `has_remaining=True`:
→ remove/cleanup only stopped worker(s)
→ keep global Farm running
→ keep global Dừng state

if `has_remaining=False`:
→ all Farm sessions stopped
→ reset FarmTab:
   `Bắt đầu`
   `#388e3c`
   `normal`
→ synchronize StartTab stopped state.

## Per-row end

while old cycle is alive:
→ keep orange `…`

actual cycle exits:
→ allow play refresh
→ inactive row:
   `▶`
   `#388e3c`

Exact row `Đã dừng` state-label statement timing:
→ UNKNOWN.

## Single stop with other accounts remaining

row A stop request
→ A enters stopping sentinel
→ A worker exits/join cleanup
→ B/C remain in `_farming_acc`
→ global Farm remains running
→ large button remains active Dừng state.

## Single stop of last account

last active row stop
→ exact single-toggle doc says switch to global-stop workflow
→ wait worker drain
→ no remaining
→ global reset to green `Bắt đầu`.

## Global Dừng lại

`_toggle_farm` while running:
→ target only accounts currently Farm
→ non-Farm rows already in correct state are skipped
→ cooperative stop all targets
→ drain workers
→ final reset only after no remaining.

The module has an explicit:
→ `Đang dừng...`
→ orange `#ef6c00`
→ disabled
stop/drain UI surface used by cleanup.

Whether every ordinary global stop click displays that exact intermediate caption:
→ UNKNOWN.

## Generation

old session monitor/buff/reconnect work:
→ row no longer Farm OR generation changed
→ exit

frozen doc explicitly attributes gen change to:
→ user stop/start

exact `_gen += ...` statement placement/order:
→ UNKNOWN.

## StartTab sync

`_sync_start_tab_btn(text,bg,state,...)`
→ nested `_upd`
→ keeps StartTab Farm control synchronized with FarmTab FSM

StartTab wrapper:
→ `_toggle_farm_cmd`
→ calls Farm toggle path
→ syncs both controls

stopped captions intentionally differ:
→ FarmTab: Bắt đầu
→ StartTab: Train

running state:
→ red Dừng lại.

## H15 handoff

H15 must runtime-verify:
→ button transitions
→ partial start/stop
→ last-account stop
→ stopping sentinel duration
→ actual thread exit/wait behavior
→ generation cancellation
→ StartTab/FarmTab synchronization
→ unknown daemon/join timeout/intermediate ordering where observable.
