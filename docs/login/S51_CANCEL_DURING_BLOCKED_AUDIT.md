# S51 — Cancel between F09 due check and audit construction

\`\`\`text
F09 poll_once() holds _lock:
  now = _now()
  events = _clock.poll(now)
  if cancel/closed: return ()      [existing S42 check]
  construct BlockedScheduleOccurrence records:
    [test-controlled pause here]

Tk <Destroy> on creator thread, concurrently:
  F09ReadOnlyTabLifetime.close()
    preview.shutdown()
    worker.request_shutdown()     [S46 lock-free]
      closed=True
      _stop_requested.set()
      _cancel.set()
    returns without worker _lock or Thread.join

Old S50:
  resumes materialization; extends _audit, returns events
  => stale post-cancel blocked-only audit

S51:
  resumes materialization
  if cancel/closed: return ()      [NEW]
  only then may extend _audit; normal blocked-only events unchanged

  Native Tk close latency and worker Event.wait(20) unchanged.
  Still test-only, no real game/Proxy/account/OS actions.
\`\`\`

Note: the final check narrows the publication window at the reproduced boundary;
the lock-free signal and audit publication are not claimed to be one globally
atomic critical section. Any stronger guarantee needs a separate proven design.
