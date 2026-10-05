# I11 — Train LSV all-account / FSM flow

## Visible bulk actions

UI bulk bar
→ Tới LSV
→ Tới chỗ train
→ Đánh
→ Rời LSV

Each button:
→ outer threading.Thread(..., daemon=True).start()
→ calls its *_all worker off the Tk thread.

_checked_rows:
→ ALL current TrainLSV account rows
→ no row checkbox filtering.

## Bulk child operations

_move_lsv_all
→ rows = _checked_rows()
→ parallel per-account work
→ I02 _move_lsv.

_move_all
→ rows = _checked_rows()
→ resolve each row's selected train preset
→ per-row mv/xv/yv
→ I02 ensure/premove
→ I03 _move_acc final coordinate
→ parallel.

_leave_lsv_all
→ rows = _checked_rows()
→ parallel per-account I04 _leave_lsv.

_farm_all
→ rows = _checked_rows()
→ parallel per-account _farm_acc
→ manual StartAutoFight only
→ NOT full _farm_cycle.

_stop_all
→ internal helper
→ rows = _checked_rows()
→ parallel per-account _stop_acc
→ not a fifth visible B06 button.

Exact inner child daemon/join behavior:
→ UNKNOWN.

## Manual Fight

_farm_acc(hwnd, stop_check)
→ if _is_acc_farming(hwnd):
   → log skip
   → do not overlap full auto Farm
→ otherwise shared start_auto_train
→ memory StartAutoFight Train
→ no click.

## Single account full Farm toggle

inactive row:
→ start permission/account-limit guard
→ denied: log and do not start
→ allowed:
   → change session generation
   → add hwnd to _farming_acc
   → start _farm_cycle
   → start _resize_monitor
   → track worker in _farm_threads
   → row/global running UI.

active row stop:
→ set _stopping_play
→ row text …
→ orange
→ _stop_acc
→ invalidate/leave current Farm generation/membership
→ worker cooperatively exits.

last active account stopping:
→ same final global-stop workflow.

## Row play UI

stable inactive:
→ ▶
→ green #388e3c

stable active:
→ ASCII II
→ red #f44336

draining:
→ …
→ orange #ef6c00
→ _refresh_play_buttons skips row until worker end.

## Cooperative cancellation

_farm_cycle captures gen_snap.

stop closure:
→ _check_stop(self,row,halt,gen_snap,hwnd)

worker/subhelpers exit if session is invalid:
→ account no longer active
→ generation changed
→ halt/stop state
→ other owned stop event as applicable.

No asynchronous Python thread kill.

## Large Bắt đầu / Dừng toggle

stopped/global start:
→ target ALL rows not already in _farming_acc
→ no rows: log no account list
→ all already active: no-op log
→ otherwise start inactive rows only.

running/global stop:
→ target rows currently in _farming_acc only
→ none active: no-op log
→ mark/stop targets
→ log wait for current sub-cycle completion.

Stable stopped:
→ Bắt đầu / green

Stable running:
→ Dừng lại / red.

## Wait/drain

_wait_farm_stop(threads, has_remaining)
→ join/drain selected Farm workers.

has_remaining=True:
→ remove stopped workers
→ remaining accounts continue
→ global state stays running.

has_remaining=False:
→ all stopped
→ Bắt đầu / green / normal
→ sync StartTab.

Exact join timeout:
→ UNKNOWN.

## Automatic stale-window cleanup

all game windows gone while Farm active:
→ automatic global stop
→ large button Đang dừng...
→ orange
→ disabled
→ sync StartTab
→ wait/drain workers.

This orange global transition is proven for stale/no-window cleanup only.

## StartTab mirror

TrainLsvTab _sync_start_tab_btn
→ stopped local text Bắt đầu maps to StartTab text Train LSV
→ running/stopping text/bg/state mirrored.

StartTab _toggle_train_lsv_cmd
→ invokes same TrainLsvTab Farm toggle
→ not a separate engine.

## Full Farm cycle

per-account:
→ I02/I03 move to selected train point
→ I05/I06 support workers
→ Đang train LSV
→ fight
→ I07/I08/I09 recovery paths as needed
→ repeat.

Exact frozen scope:
→ no ordinary Train sell
→ no medicine-buy cycle
→ no return-town scheduler.

## Runtime evidence

packaged automove_log:
→ no correlated top-level TrainLSV/FSM logs

generic primitives:
→ AutoFight_Main 8511
→ AutoMove queued 16040
→ StartAutoPath called 15993
→ StopAutoPath called 2027

classification:
→ top-level I11 STATIC_VERIFIED / RUNTIME_ENV_REQUIRED.

## Next

I12:
→ Train LSV parity/runtime matrix and Gate I closure.
