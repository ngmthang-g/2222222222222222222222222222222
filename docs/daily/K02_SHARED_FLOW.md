# K02 — Daily shared account / row / coordinator flow

## Account refresh

```text
tab selected
   ↓
_start_refresh()
   ↓
_refresh_acc_lists()
   ↓ background worker
info_tab/get_windows
   ↓
current HWND/account info
   ↓
Tk after(...)
   ↓
_add_or_update_row(...)
_remove_stale_accs(...)
_request_scroll_update()
   ↓
_schedule_refresh()
   ↓
5 seconds
```

`_stop_refresh()` cancels the scheduled refresh when the tab is switched away.

## HWND identity

```text
row
  ├─ hwnd
  └─ bound PID snapshot

_is_window_alive(hwnd, expected_pid)
  ├─ hwnd closed → false
  ├─ current PID differs → false
  └─ PID matches / no snapshot compatibility path → alive
```

If the same HWND number is reused by another process, Daily destroys/recreates the logical row instead of trusting the handle.

## Row lifecycle

```text
new HWND
   → create row
      ▶ | name | activity | status | map | Tới bổ đầu | Trị liệu

known same HWND+PID
   → update name / level / map in-place

closed/reused HWND
   → unbind identity
   → destroy stale row
```

## UI-thread safety

```text
worker/monitor
   ↓
_set_state(...)
   ↓
_schedule_state_label(...)
   ↓
Tk after(0)
   ↓
_apply_state_label(...)
```

Background workers must not mutate row widgets directly.

## Per-row session guard

```text
row
  ├─ _stop_event      # real threading.Event
  └─ _gen             # session generation

worker snapshots gen_snap
   ↓
_GenStop(row, gen_snap)
   ↓
is_set() == true when:
  - real _stop_event is set
  OR
  - row _gen != gen_snap
```

This prevents an old worker from surviving a rapid Stop→Start after the shared Event is cleared for the new session.

## Per-row play

```text
▶ / || row button
    ↓
_toggle_single_acc(row)
    ↓
current activity_var
   ├─ Trừng ác      → _punish_single_worker
   └─ Tàng bảo đồ  → _treasure_single_worker
```

Only the selected row is controlled.

## Bottom all-account toggle

Idle:

```text
Bắt đầu
   ↓
_start_all_accs()
   ↓
shared inject/preparation
   ↓
for each non-running eligible row:
    choose activity
    start one per-account thread
   ↓
no rows started?
  ├─ yes → "Không acc nào cần chạy"
  └─ no  → bottom "Dừng lại" / red
           _ensure_daily_monitor()
```

Running:

```text
Dừng lại
   ↓
_start_all_accs()
   ↓
for every running row:
  _farming_acc = False
  _stop_event.set()
   ↓
row play UI → ▶
bottom UI   → Bắt đầu / green
_sync_start_tab_btns()
```

The worker threads unwind cooperatively.

## All-account monitor

```text
_ensure_daily_monitor()
   ↓
only one monitor instance
   ↓
_daily_all_monitor()
   ↓
wait until every row is no longer running
   ↓
Tk/UI reset
   ↓
_punish_reset_ui()
_treasure_map_reset_ui()
   ↓
"[Bắt đầu] Tất cả acc đã dừng — tự động reset UI"
```

## Shared resize monitor

```text
_resize_monitor(hwnd, is_running_fn)
   ↓ every 1 second
bound HWND still valid and visible?
   ↓
GetWindowRect
   ↓
size != 1366×768?
   → start_tab.resize_window(...)
```

## Persistence boundary

Persisted:
- Daily mode/config options.

Not recovered as persisted:
- row activity selection;
- PID binding;
- _farming_acc;
- _stop_event;
- _gen;
- current row state.

Those are runtime row/session state.
