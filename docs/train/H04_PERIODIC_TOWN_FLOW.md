# H04 — Periodic-town / common farm-wait flow

## Cycle timing

outer Farm cycle
→ cycle_start captured
→ front-half work:
   sell / buy medicine / move / start farm
→ read/parse loop_minutes
→ elapsed = time already spent in this cycle
→ target period = loop_minutes × 60 seconds
→ derive remaining sleep_time

Exact clamp/floor expression is not statically safe to reproduce.

## Mode overlay

cycle
→ wait remaining periodic duration
→ normal expiry
→ next outer cycle
→ return-town work is authorized by cycle mode

full_bag_timer / legacy full_bag
→ same remaining timed wait
→ overlay stop_bag_check
→ if bag becomes full before timeout:
   → early break
   → town path
→ otherwise normal timer expiry
   → next outer cycle/town path

never
→ outer loop still lives
→ timer boundary does not authorize automatic town
→ H03 full-bag path may filter
→ still-full result stays in place

lock_town
→ H02 forces never
→ same no-town authorization boundary.

## Interrupts

user/per-account stop
→ stop_check / hard_stop
→ current long-running cycle work can exit before timer expiry

death/respawn monitor
→ cadence 4s
→ respawn_event
→ cycle diverts/resets into recovery
→ detailed recovery is later H scope

disconnect monitor
→ cadence 2s
→ require 3 consecutive disconnect ticks (~6s)
→ set halt
→ stop farm loop immediately
→ reconnect attempts
→ common.active wait 30s/attempt
→ success sets reconnect_ok
→ cycle reset
→ wait_memory_ready(timeout=45.0, need=3)
→ resume trusted cycle work

## Normal completion

No special terminal state/log is recovered for timer expiry.

Timer expiry means:
→ periodic boundary reached
→ outer Farm worker remains alive
→ begin the next cycle according to current condition.

## Explicit unknowns

- exact sleep/check quantum inside the periodic wait
- exact time API used for cycle_start/elapsed
- exact clamp/floor around remaining sleep_time
- invalid/min/max loop_minutes parsing range

Do not bind literal 5 to the scheduler: the same Farm module independently uses an exact documented 5-second pickup delay and constants are deduplicated.
