# S43 F09 race guard

```text
S42 (before)
  stop() captures old Thread
        releases _lock; waits join
                                  start() sees old thread terminated
                                  reassigns clock + thread
  stop() acquires _lock, disables NEW clock  <-- INVALID

S43 (after)
  start() obtains lifecycle lock or REFUSES
  stop() holds lifecycle lock through:
      Event.set() immediately, with no _lock needed
      old thread join(timeout)
      timed out? -> STOPPING, restart blocked while thread still alive
      finished?  -> under _lock, clear only current clock/state
  start() attempted during cleanup: refused, never resurrected accidentally

S42 (before)
  worker poll_once() holds _lock
  now() stalls under _lock
  stop() waits for _lock BEFORE setting cancel, timeout ineffective
  now() returns late -> due events recorded AFTER stop request

S43 (after)
  stop() Event.set() without acquiring poll _lock
  join(timeout) bounded, possibly STOPPING
  now() returns:
      check Event.is_set() -> DISCARD, no new due-event audit
  next stop() after release joins and frees old clock
  readonly thread status/active getter does not wait on blocked clock _lock

ALWAYS:
  source-backed F09 cadence exactly 20s (unchanged)
  only BLOCKED_ACTION_UNAVAILABLE events; no real game actions
  S41 Tk countdown is independent
  no F02 account writer, no Proxy, no poweroff, no fake UI
```
