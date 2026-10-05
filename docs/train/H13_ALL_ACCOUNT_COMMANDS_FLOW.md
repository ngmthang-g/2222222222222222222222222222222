# H13 — Train all-account command flow

## Target set

`_checked_rows`
→ all current Train account rows
→ no per-row selection checkbox

Legacy text `acc được tick`
→ stale wording only
→ do not reconstruct checkbox selection.

## Visible all-account UI

`Điều khiển tất cả:`

`Tới bán đồ`
→ Tk callback
→ daemon outer Thread
→ `_goto_sell_all`

`Bán đồ`
→ Tk callback
→ daemon outer Thread
→ `_sell_all`

`Tới bãi train`
→ Tk callback
→ daemon outer Thread
→ `_move_all`

`Đánh`
→ Tk callback
→ daemon outer Thread
→ `_farm_all`

Tk does not synchronously wait for these multi-account workers.

## Tới bãi train

`_move_all`
→ all rows
→ parallel per-row work
→ recovered `rows/_threads/row` structure
→ per-account movement path

per-account guard:
active automatic Farm
→ log skip
→ do not force manual movement
→ user must stop Farm first.

## Đánh

`_farm_all`
→ all rows
→ parallel

for each eligible row:
selling / waiting sell-stop?
→ skip that row
→ guidance: stop sell first

otherwise:
→ manual Fight primitive
→ `start_auto_train`
→ StartAutoFight Train by memory/internal path
→ no game-UI click.

This is not the large `Bắt đầu` Farm FSM.

## Bán đồ

`_sell_all`
→ all rows
→ parallel
→ per-row sell lifecycle remains independent:
   `_sell_active`
   `_sell_stop_event`

Exact child entry:
`_sell_acc` vs `_toggle_sell`
→ UNKNOWN.

Do not merge sell state into `_farming_acc`.

## Tới bán đồ

`_goto_sell_all`
→ all rows
→ parallel
→ same navigation-to-sell-point route as real sell
→ includes Truyền return branch when applicable
→ stop at sell point
→ DO NOT open shop
→ DO NOT sell.

## Internal stop-all

`_stop_all`
→ all rows
→ parallel
→ recovered `rows/_threads/row`
→ `_stop_acc`
→ stop character + clear per-account Farm flag.

Full global stop/FSM/UI reset
→ H14, not H13.

## Internal buy-medicine all

`_buy_meds_all`
→ all rows
→ parallel
→ recovered `rows/_threads/row`
→ `_buy_meds_acc`.

No new visible button is added.

## Thread certainty boundary

Verified:
→ outer visible-button worker is daemon
→ commands execute off Tk
→ operations are parallel
→ move/stop/buy-all own explicit child thread collections

UNKNOWN:
→ daemon flag of every child thread
→ exact child join/wait policy
→ join timeouts
→ exact child-thread collection implementation for farm/sell/goto-all.

## Permission boundary

row UI permission:
→ has_permission + check_account_limit
→ disabled when denied

`_checked_rows`:
→ all rows

exact command-side permission recheck:
→ UNKNOWN.

## Handoff

Do not open H14 behavior early in H13.

Next:
→ `_toggle_farm`
→ global Bắt đầu/Dừng
→ `_farming/_farming_acc/_farm_threads/_stopping_play/_gen`
→ start/stop/wait/reset FSM.
