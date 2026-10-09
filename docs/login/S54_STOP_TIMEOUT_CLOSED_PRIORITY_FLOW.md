# S54 — Permanent close is a one-way latch even when stop times out

\`\`\`text
Native/test-only F09 worker normal and permanent paths:

stop(timeout):
    _register_stop_request()  # cancel.set + stop_requested.set

    _lifecycle_lock.acquire(timeout=remaining)
      if unavailable:
        S53: status=STOPPING (even after permanent shutdown)  [BUG]
        S54: status=CLOSED if closed else STOPPING

    thread.join(timeout=remaining)
      if still alive:
        S53: status=STOPPING (even after permanent shutdown)  [BUG]
        S54: status=CLOSED if closed else STOPPING

    _lock.acquire(timeout=remaining)  # S53 total deadline
      if unavailable:
        S53: status=STOPPING (even after permanent shutdown)  [BUG]
        S54: status=CLOSED if closed else STOPPING

    On successful cleanup: status=CLOSED if closed else STOPPED

The independent Tk Label.destroy callback remains lock-free:
  F09ReadOnlyTabLifetime.close() -> worker.request_shutdown()
  _closed=True, cancel.set(), stop_requested.set(), no join or _lock

Normal nonclosed timeout remains STOPPING; a timed-out CLOSED worker
may still require finish_close() off the Tk thread. CLOSED here describes
the permanent scheduling prohibition, not evidence of completed joining.

No new product actions, no 20-second cadence change, no Proxy runtime.
\`\`\`
