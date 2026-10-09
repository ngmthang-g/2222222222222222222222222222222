# S41 F09 — Real Tk-only read-only countdown

```text
                F09 original frozen EXE evidence
               lbl_sched_countdown main thread ~1s
                           |
S40 read_settings(settings.ini) [READ ONLY]
   opaque persisted schedule_on and shutdown flags NOT DECODED
   schedule_close HH:MM + schedule_open HH:MM validated
                           |
             explicit TEST-owned preview_start()
                           |
                  S39 pure LoginScheduleClock
                  enable(now) future deadlines
                           |
             Tk.Label.configure(text=countdown)
                           |
             Tk.Label.after(1000, _refresh)
                           |
          Tk main thread _refresh():
             clock.poll(now) [discard all due events]
             clock.countdown(now)
             label.configure(text=...)
             label.after(1000, _refresh)
                           |
          stop() / tab destroy():
             Event.set / epoch invalidation
             after_cancel(pending)
             label.configure(text="")
                           |
       NO game open, NO HWND close, NO PC shutdown
       NO F02 account/INI writes, NO Proxy runtime

Production S35 Login tab is NOT changed or shown a fake schedule
button, because real F05/F06 authenticated dispatcher is missing.
```
