# H08 — Train reconnect flow

## Feature gate

auto_reconnect
→ default False
→ when disabled: no automatic reconnect behavior should be performed

Exact source-level placement of the gate
→ UNKNOWN (caller launch vs monitor early-return vs loop check)

## Parallel watchdog

Farm session
→ _disconnect_monitor(row, stop_event, reconnect_ok, halt, hwnd, ...)
→ runs beside Farm loop
→ tick every 2s

## Detection

read connection memory:
→ True
   → reset dc_strikes
   → never halt from pixel coincidence
→ None
   → memory unavailable
   → pixel decides
→ False
   → still require persistent dialog evidence before halt

check both:
→ login.ngatKetNoi1
   point (640,244)
   RGB (160,145,52)
→ login.ngatKetNoi2
   point (702,453)
   RGB (212,28,34)

both present?
→ NO: consecutive strike chain cannot complete
→ YES:
   → dc_strikes += 1
   → require 3 consecutive ticks
   → 2s cadence ≈ 6s confirmation

strike 3/3
→ log MAT KET NOI
→ signal halt
→ Farm loop/sub-actions interrupted
→ stop_character movement surface
→ Farm state Chờ kết nối lại

## Reconnect attempt batch

repeat visible attempts 1..5:

re-check BOTH disconnect pixels
→ dialog missing:
   → skip click
   → still observe active-state recovery

dialog still present:
→ click_at client (616,455)

then:
→ wait common.active
→ timeout 30s for this attempt

common.active frozen probe:
→ point (1330,33)
→ RGB (34,8,11)
→ tolerance 5

active found?
→ YES:
   → reconnect success
   → invalidate Reader cache for current PID
   → set reconnect_ok
   → cycle reset
   → watchdog session remains available

→ NO:
   → next attempt in batch

all 5 fail
→ log retry after 30s
→ wait 30s
→ start a new 5-attempt batch
→ repeat indefinitely

Never disable the account merely because reconnect remains unsuccessful.

## Exit conditions

Watchdog only exits when session validity ends:
→ user stop / stop_event
→ account no longer farming
→ generation changed
→ real game window death

## Farm-cycle recovery after reconnect_ok

halt branch
→ Chờ kết nối lại
→ event-driven reconnect_ok wait
→ exact event-wait poll quantum UNKNOWN

success:
→ shared memory recovery gate
→ wait_memory_ready(timeout=45.0, need=3)

Each memory-ready sample:
→ invalidate Reader cache
→ require clear RoleName
→ require MapID != None
→ need 3 consecutive valid reads

ready before 45s:
→ resume/reset Farm cycle

45s expires:
→ helper returns False
→ log
→ FAIL-OPEN
→ caller may continue rather than wedging Farm forever

## Cache / DLL boundary

Reconnect success:
→ invalidate_character_cache(current PID) is explicitly documented

Farm has _ensure_injected:
→ inject resources.dat only if not already loaded
→ double-inject guarded

But:
→ readable reconnect constants do NOT directly prove an unconditional
   post-reconnect _ensure_injected call

Therefore:
→ do not add forced reinjection solely because TCP reconnect happened
→ preserve helper/guard if stronger evidence later proves the edge

## stop_character vs game-auto

_disconnect_monitor uses stop_character
→ stop movement surface

It does not directly expose stop_game_auto
→ do not reinterpret stop_character as disabling all game auto modes

halt is what interrupts the Farm execution path.

## Death overlap

H07/H06 actions use hard_stop.

disconnect confirmed
→ halt asserted
→ current death-treatment/movement work that honors hard_stop is interruptible
→ reconnect state takes over

reconnect success
→ cycle reset
→ current game/death state is read again

Exact ordering if death signal and third disconnect strike occur in the same
scheduling window before halt is set:
→ UNKNOWN / runtime parity.
