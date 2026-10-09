# S47 total stop deadline (worker lifecycle + Tk teardown)

```text
BEFORE:
  GUI <Destroy> -> immediate request_shutdown()  [S46 safe]
  Non-Tk finish_close(timeout=0.03)
       -> worker.stop(0.03)
       -> acquire _lifecycle_lock WITHOUT timeout
             [external stopper owns mutex after worker join]
       -> may hang arbitrarily; timeout only applied to Thread.join

S47:
  stop(timeout):
      deadline = monotonic() + timeout
      _stop_requested.set(); _cancel.set()   [no locks]
      _lifecycle_lock.acquire(timeout=remaining)
           if timeout: STOPPING, return False (pending stop fence intact)
      if acquired: join(worker, timeout=remaining)
           if still alive: STOPPING, return False
           else: disable clock; clear stop fence; STOPPED or CLOSED
      always release lock

  concurrent slow start():
      check permanent CLOSED + pending stop flag on entry,
      AFTER injected now(), AFTER clear(cancel), AFTER thread.start.
      stop signal always wins if observed before finishing start.

  real Tk Label Destroy:
      cancels preview and sets worker closed/cancel immediately;
      finish_close outside Tk inherits total-budget contract.

  NO game dispatch, no Info bypass, no account write, no PC shutdown.
```
