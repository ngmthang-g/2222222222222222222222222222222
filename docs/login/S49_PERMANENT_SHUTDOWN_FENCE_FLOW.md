# S49 concurrent Tk shutdown during S48 stop cleanup

```text
S48 interleaving — BUG:
 stopper A: _end_stop_request(): closed == False
 stopper A: calls Event.clear [paused before actual clear]
 Tk Destroy: request_shutdown() sets closed=True, fence SET, cancel SET
 stopper A: Event.clear proceeds AFTER request_shutdown
 -> closed=True but stop-requested fence is FALSE (incorrect)

S49 interleaving — FIX:
 stopper A: Event.clear proceeds
 stopper A: rechecks closed after clear
              if closed=True: Event.set()
 -> closed=True and permanently set fence, cancel set

 If shutdown arrives after S49 final check, its Event.set is last
 and permanent fence is also preserved.
 S46 request_shutdown() remains lock-free and never joins from Tk.
 S47 mutex+join total timeout and S48 concurrent stopper count unchanged.
 No scheduled game action; no account/Proxy writes; NOT PRODUCT.
```
