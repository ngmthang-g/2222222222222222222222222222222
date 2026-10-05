# H12 — Train per-account row / identity / state flow

## Discovery / refresh

every 5000ms:
→ background worker
   → start_tab.get_windows()
   → for each window:
      → current HWND/title
      → character info
      → Site-10 occupied bag slots
   → build infos + active_hwnds
→ Tk main-thread apply
   → _add_or_update_row
   → _remove_stale_rows(active_hwnds)
   → reapply permission/account-limit state
   → refresh scroll region
→ schedule next refresh

Transient memory read failure
→ keep row
→ keep old bag value
→ do not flicker/rebuild the whole list.

## HWND / PID identity

new HWND
→ _pid_of(hwnd)
→ bind_window_identity(hwnd,pid)
→ create row with expected PID snapshot

existing HWND, same PID
→ update row in place

existing HWND, different PID
→ log process change
→ old row identity is stale
→ stop/teardown old activity as needed
→ unbind old identity
→ destroy/recreate fresh row

runtime ownership check:
→ IsWindow
→ IsWindowVisible
→ current PID == expected PID
→ PID mismatch means Windows reused the HWND.

## Visible row

row1:
→ ▶ play button
→ character name
→ Sell saved-preset combobox
→ Train saved-preset combobox

row2:
→ ⬤ state dot
→ state text (initial Đã dừng)
→ live MapID
→ per-row action buttons

row3:
→ one combined extra tracker label

No per-row selection checkbox exists.
_checked_rows means every account row.

## Role / map / bag refresh

RoleName
→ strip HTML tags <...>
→ lbl_name

MapID
→ live current character map
→ lbl_map_id
→ separate from selected destination preset

bag slots
→ occupied Site-10 slots
→ row._bag_slots
→ None read error keeps old value

## Extra tracker start

Farm session starts
→ _start_extra_track
→ establish start-time/session tracking state
→ do NOT synchronously read memory on Tk thread

first normal background refresh
→ baseline BoundMoney
→ baseline Exp

later refreshes:
→ current BoundMoney > previous?
   → add positive delta to _extra_earned
→ current decrease?
   → do not subtract earned total

→ current Exp > previous?
   → add positive delta to _extra_exp_gained
→ current decrease?
   → do not subtract session earned EXP

HP-zero death monitor
→ increments _extra_deaths once per latched death episode

## Extra line

initial:
→ 0h:00p
→ Túi: ?
→ Chết: 0
→ Vàng: 0,00
→ 0,00 vàng/h
→ 0 exp/h

running example:
→ 1h:30p | Túi: 98 | Chết: 3 | Vàng: 5.000,01 |
  3.333,33 vàng/h | 12.345.678 exp/h

rates:
→ elapsed_seconds / 3600
→ whole-session average, not rolling window

total EXP earned is tracked internally but hidden in the current line.

## Cadence correction

Frozen tracker prose says:
→ "Túi ... mỗi refresh 3s"

Active Farm refresh loop says:
→ exact 5000ms / 5s

No separate Farm extra/bag polling loop is recovered.

Therefore current effective extra-memory sample cadence:
→ 5s

Treat 3s phrase as stale embedded documentation.

## State model

row._state
→ canonical runtime state string
→ schedule state-label update
→ Tk after(0)
→ _apply_state_label

Never mutate Tk widgets directly from monitor/worker threads.

Exact styles:
→ Đã dừng        #555555
→ Về bán đồ      #1565c0
→ Bán đồ         #1565c0
→ Mua thuốc      #555555
→ Trị liệu       #555555
→ Tới bãi train  #1565c0
→ Đang train     #2e7d32
→ Về địa phủ     #c62828
→ Đang hồi sinh  #e65100
→ Đang lọc đồ    #8e24aa
→ Mất kết nối    #b71c1c
→ unknown state  #555555 default

## Farm lifecycle fields

_farming_acc
→ authoritative set of HWNDs with active Farm cycle

play button
→ mirrors _farming_acc

_stopping_play
→ orange "…" stop-in-progress state
→ do not flip back/start another cycle until old cycle exits

_gen
→ per-row Farm generation guard
→ old buff/reconnect workers exit when generation changes
→ exact increment statements UNKNOWN

_sell_active / _sell_stop_event
→ separate sell lifecycle
→ not equivalent to Farm membership

## Permission state

new row:
→ has_permission + account-limit guard
→ no farm_tab permission = row disabled

heartbeat:
→ reapply permission to every row

enabled combobox:
→ readonly

disabled row:
→ controls disabled
→ dropdown binding does not run.

## Stale-row cleanup

active HWND disappears
→ _remove_stale_rows

same HWND but PID changes
→ identity stale
→ old row replaced

teardown:
→ unbind identity
→ stop/wait if Farm work still active
→ remove widget row

Exact thread join/finally ordering:
→ UNKNOWN.
