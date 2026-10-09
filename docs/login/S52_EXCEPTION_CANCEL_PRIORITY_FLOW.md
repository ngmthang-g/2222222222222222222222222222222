# S52 — Exceptions must not overwrite external cancellation intent

\`\`\`text
Thread A (worker start / poll):
  _start_locked(): _now() or clock.enable()
  poll_once(): _now() or clock.poll()
  _run(): _cancel.wait(20) or internal worker callback
  callback BLOCKS, then raises ValueError/RuntimeError

Thread B (GUI / caller):
  Tk <Destroy> -> F09ReadOnlyTabLifetime.close()
    worker.request_shutdown() [LOCK-FREE]
      closed=True; stop_requested.set(); cancel.set()
  OR timed-out stop() -> stop_requested stays set, cancel.set()

Old S51 exception branch:
  status=BLOCKED_CLOCK / BLOCKED_WORKER even after cancellation [WRONG]

S52 exception branch:
  status =
    CLOSED   if permanent worker._closed
    STOPPING if worker._stop_requested already set
    BLOCKED_CLOCK/BLOCKED_WORKER otherwise (unchanged healthy diagnostics)

After cleanup, stop() sets STOPPED or CLOSED as before.
Tk close remains nonblocking; no UI/game/OS action dispatch added.
\`\`\`

These branches do not create new activation paths or decode opaque schedule
flags and do not claim a global atomic state transition.
