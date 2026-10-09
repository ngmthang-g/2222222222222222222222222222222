# S45 read-only F09 tab lifetime — real Tk + real worker

```text
Original F09 evidence:
  Tk main-thread lbl_sched_countdown refresh ~1 second
  independent background worker Event.wait(20)
  schedule disable stops worker without closing running games
                          │
TEST-OWNED explicit F09ReadOnlyTabLifetime.start_preview_and_evaluation()
  ├─ S44 TkScheduleCountdownPreview.start()
  │    └─ Tk Label configure/after(1000), owned Destroy observer
  └─ S43 F09ScheduleEvaluationWorker.start()
       └─ Thread / Event.wait(20), due-event BLOCKED audit only

REAL Tk Label <Destroy>
  ├─ S44 handler: preview.shutdown(), cancel Tcl timer
  └─ S45 handler: lifecycle.close()
       closed latch → worker.shutdown(timeout=0) [Event.set IMMEDIATELY]
       ├─ worker exited     → CLOSED
       └─ worker now() hung → CLOSING_WORKER
                               │ (NO Tk main-thread join)
                               ↓ after clock source released
                         finish_close(timeout)
                         join worker WITHOUT touching Tk → CLOSED

NO production Login tab binding, fake buttons, game actions, PC poweroff,
account migrations, F09 boolean guesses, Proxy or Info bypass.
```
