# S46 — Cancel on Tk WITHOUT taking the worker lifecycle mutex

```text
S45 problematic chain:
  Tk <Destroy> → lifetime.close() → worker.shutdown(timeout=0)
                       │
                   worker.stop(timeout=0)
                       │
              ACQUIRE _lifecycle_lock  ← held by OTHER stopper in join
                       │
               GUI freezes despite timeout=0

S46 verified chain:
  Tk <Destroy> → lifetime.close()
                   │
            permanently set lifetime.closed
            preview.shutdown() / Tcl after_cancel
                   │ (always, even if Tk throws)
            worker.request_shutdown()
                worker._closed=True
                worker._cancel.set()
                   │ ZERO locks, ZERO join, ZERO Win32 calls
                   ├─ worker dead → CLOSED
                   └─ still alive → CLOSING_WORKER
                            │
       separate NON-Tk finish_close(timeout) joins/cleans
                            ↓
                           CLOSED

start(): verify permanent closed latch after every reentrant
clock/clear/worker.start boundary; never resurrect cancelled schedule.

NO game actions, no fake UI, no Proxy, no F02/F09 writes;
separate S41 preview and S43 20s worker remain read-only.
```
