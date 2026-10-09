# S53 — Total stop deadline includes final clock cleanup lock

\`\`\`text
Precondition:
  F09 Event.wait(20) background worker RUNNING
  Another TEST-OWNED caller manually invokes poll_once()
    poll_once owns _lock
    injected _now() is blocked

  User/Tk lifetime issues close(): worker.request_shutdown() (LOCK-FREE)
  Background worker exits promptly from cancelled Event.wait

S52 stop(timeout=0.035):
  _lifecycle_lock.acquire(timeout=remaining) -> OK
  thread.join(timeout=remaining)            -> OK
  with _lock                                -> UNBOUNDED HANG [BUG]

S53 stop(timeout=0.035):
  _lifecycle_lock.acquire(timeout=remaining) -> OK
  thread.join(timeout=remaining)            -> OK
  _lock.acquire(timeout=remaining)          -> False on deadline
    _status=STOPPING; cleaned=False; return False
    _end_stop_request(False) retains cancellation fence
    _lifecycle_lock released

  Tk Destroy remains nonblocking
  original poll unblocks -> sees cancel -> no blocked due events
  separate finish_close(2) succeeds; final status CLOSED
  restart denied permanently after lifetime closed
\`\`\`

No product actions and no global rework: only the final previously-unbounded
cleanup lock is subject to the existing total stop deadline.
