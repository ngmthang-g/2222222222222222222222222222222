# H07 — Train death-recovery flow

## Session startup

Farm account session
→ create per-session recovery/cancel state
   → monitor_stop
   → respawn_event
   → gen_snap
   → hard_stop
→ start extra tracker
→ start _diaphu_monitor immediately with session
→ start disconnect monitor separately

## _diaphu_monitor

every 4 seconds:

read character info

### HP branch
real numeric HpPercent == 0?
→ hp_latched already set?
   → YES: no repeated respawn click
   → NO:
      → click_at(hwnd, 792, 441)
      → one respawn click
      → increment latched death counter surface
      → hp_latched = true

HpPercent becomes non-zero
→ hp_latched re-armed/reset

Unreadable HP
→ never reinterpret as zero death.

### Map branch
MapID == 87?
→ detected already?
   → YES: no duplicate recovery event
   → NO:
      → enter/label Địa phủ state
      → respawn_event set once
      → detected armed

MapID leaves 87
→ clear/re-arm recovery event/latch
→ future death-map entry may signal again

This prevents a recovery loop while moving out of Địa phủ.

## Farm-cycle recovery consumer

respawn_event observed
→ row state: Đang hồi sinh
→ death recovery branch

optional treatment enabled?
→ H06 _heal_at_death(hwnd, hard_stop)
→ success:
   → continue recovery
→ failure:
   → surface "trị liệu sau chết thất bại"
   → exact next FSM statement remains UNKNOWN

return-to-train enabled (respawn)?
→ recovery intent is to return to selected Train target
→ must reuse H05 current farm_var / saved-coordinate movement contract

return-to-train disabled?
→ do not fabricate automatic return-to-train
→ exact worker continuation (stop vs remain alive/skip relocation) remains UNKNOWN

## Readiness boundary

HP click success alone
≠ recovery ready

MapID 87
→ observable state used to raise recovery event

FarmTab does not expose the separate Train-LSV
"common.active after respawn" wait.

Farm wait_memory_ready(45, need=3)
→ belongs reconnect branch
→ must not be reused as death-respawn wait.

Any extra post-respawn delay before treatment/movement:
→ NOT RECOVERED.

## Counter / labels

row initial:
→ Chết: 0

HP-zero latched episode:
→ _extra_deaths branch
→ tracker displays Chết: N

state phases recovered:
→ Về địa phủ
→ Đang hồi sinh
→ Trị liệu (when enabled)
→ later normal Farm state

Exact reset of death counter on stop/start of same row:
→ UNKNOWN.

## Safety

_diaphu_monitor
→ canceled by per-session stop_event

Farm cycle
→ gen_snap
→ hard_stop
→ _hwnd_alive

_hwnd_alive:
→ window must exist
→ visible
→ still bound to expected process/PID
→ reused numeric HWND with different PID is invalid

Old session recovery monitor must never keep clicking a reused HWND.

Exact monitor-stop/finally ordering remains UNKNOWN.

## Reconnect overlap

Death recovery and reconnect watchdog are separate event paths.

respawn_event
≠ halt/reconnect_ok

Exact simultaneous death+disconnect arbitration:
→ H08 / runtime parity.
