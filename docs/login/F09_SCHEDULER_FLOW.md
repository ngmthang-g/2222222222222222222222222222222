# F09 — Scheduler flow

Manual Login button and scheduler are independent.

Manual Bắt đầu:
→ open checked accounts immediately
→ second press stops current login batch
→ does not enable/disable schedule

Schedule checkbox ON:
→ clear schedule cancel state
→ mark schedule active
→ start background schedule worker
→ show countdown immediately
→ do not immediately open game

Schedule checkbox OFF:
→ request schedule worker stop
→ clear countdown
→ leave already-open game windows untouched

Schedule worker:
→ parse configured close/open HH:MM
→ next_close = today at HH:MM if future, else tomorrow
→ next_open = today at HH:MM if future, else tomorrow
→ evaluate due events on documented ~20s worker cadence

No catch-up rule:
if today's configured time already passed when scheduling is enabled
→ wait for tomorrow's occurrence
→ do not immediately run missed action

When close occurrence is due:
→ log scheduled close
→ Login close-all game behavior
→ advance next_close by +1 day
→ if shutdown_after_close:
   → show 60s shutdown confirmation popup

Shutdown popup:
→ topmost 340x150
→ WM_DELETE_WINDOW acts like cancel
→ Confirm:
   → _shutdown_pc
   → Windows command shutdown /s /t 0
→ Hủy/close:
   → cancel shutdown
→ no response for 60s:
   → _shutdown_pc automatically

When open occurrence is due:
→ if a Login batch is already running:
   → skip this open event
→ otherwise:
   → _open_game_batch
   → use currently checked Login rows
   → reuse normal F05/F06 launch/login pipeline
→ advance next_open by +1 day

After scheduled Login success/failure:
→ scheduler stays enabled
→ continues waiting for close/open events

Countdown UI:
→ main-thread update about every second
→ fixed close/open absolute timestamps
→ duration format examples 2h05p / 15p30s / 45s / 1d2h05p
→ visual composition contains:
   Tắt <HH:MM dd/mm> còn <remain> | Mở <HH:MM dd/mm> còn <remain>

Persistence:
settings/config lifecycle stores:
- schedule_on
- schedule_close
- schedule_open
- shutdown_after_close

Explicit unknowns:
- whether saved schedule_on automatically starts a worker on a completely fresh process launch
- exact internal order of cancelling an active login batch vs closing windows/tracking at scheduled close
