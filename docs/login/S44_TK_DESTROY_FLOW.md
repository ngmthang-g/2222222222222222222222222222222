# S44 — Native Tk <Destroy> and reentrant cancellation

```text
F09 original EXE: Tk lbl_sched_countdown updates about every 1s
    S40 [Settings] real read-only HH:MM (unknown flags stay opaque)
                         ↓ explicit read-only preview ONLY
        S41 real Tk Label and after(1000)
                         ↓
          S44 Label.bind("<Destroy>", handler, add="+")
                         ↓
             Tk parent or label destroyed
                         ↓
             handler verifies event.widget is owned label
                         ↓
             preview.shutdown()
                _epoch++ ; _cancel.set()
                after_cancel(pending Tcl after id)
                status CLOSED; never restart

  When _now / Label.configure / Label.after invokes stop/shutdown:
      recheck epoch + active after every external call.
      A just-created after_id with stale epoch is canceled immediately.
      Old queued callback with stale epoch never arms again.

  S43 Event.wait(20) worker remains SEPARATE, blocked events only.
  No F05/F06 actions; no Info bypass; no game open/close/poweroff.
  No Proxy runtime, no F02/F09 account or boolean conversion/writes.
```
