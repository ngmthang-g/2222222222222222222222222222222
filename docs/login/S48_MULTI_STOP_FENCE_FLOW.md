# S48: two-stopper pending cancellation fencing (read-only F09)

Original S47:
  stop A sets _stop_requested -> acquires _lifecycle_lock
  stop B sets SAME _stop_requested -> waits on _lifecycle_lock
  stop A joins/cleans -> CLEARS _stop_requested [BUG: B is pending]
  competing start may rearm -> B eventually stops

S48:
  stop A:
    _stop_request_lock: pending += 1; _stop_requested.set(); _cancel.set()
    acquire lifecycle mutex (remaining S47 deadline) and join
  stop B:
    _stop_request_lock: pending += 1; _stop_requested.set(); _cancel.set()
    wait lifecycle mutex within its OWN S47 deadline
  stop A cleanup:
    pending -= 1
    pending != 0 -> _stop_requested REMAINS SET
  stop B cleanup:
    pending -= 1
    successful AND pending == 0 AND NOT permanently closed -> clear fence
    otherwise keep fence set for next explicit successful cleanup

No slow time source, actual Tk methods or Thread.join runs inside _stop_request_lock.
Permanent request_shutdown() remains immediately lock-free and one-way.
No credential/account writer, Proxy, scheduled game action or OS shutdown.
