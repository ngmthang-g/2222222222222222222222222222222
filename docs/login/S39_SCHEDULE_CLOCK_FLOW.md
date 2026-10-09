# S39 F09 clock-only flow — no fake game worker

```text
F09 authentic original evidence (frozen Nuitka specimen)
  next occurrence: today if future, otherwise tomorrow
  check cadence ~20s  |  countdown refresh on Tk thread ~1s
  open game pipeline: F05/F06 NOT YET IMPLEMENTED
  close all game: NOT YET IMPLEMENTED

new LoginScheduleClock:
  strict parse_HHMM("04:00" / "04:20")
  enable(now)
    -> calc absolute next_close and next_open
    -> does NOT open game
  poll(now) [called by test or future VERIFIED controller]
    -> emits typed ScheduleEvent("close" or "open", timestamp)
    -> move each due event to next future day
    -> DOES NOT execute system commands
  countdown(now)
    -> returns original-backed text string
    -> future owner must render on main Tk thread
  disable()
    -> clears pending schedule; no HWND mutation

NO product Tk checkbox, no fake trigger, no login, no shutdown.
F02 check token + legacy Có remain UNKNOWN; no account writes.

Next S40: verified callback integration only after authentic F05/F06
and close-all mechanisms become available.
```
