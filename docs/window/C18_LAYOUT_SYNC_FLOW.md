# C18 — Layout sync flow

Direct button:
`Đồng bộ các cửa sổ`
→ `_toggle_layout`
→ layout state changes (`layout_active` / `sync_layout_running`)
→ `_sync_windows_loop`
→ `_layout_worker`
→ `_refresh_cache`
→ current game HWND set
→ `_arrange_grid`
→ master index 0 / top-left
→ remaining HWNDs follow
→ repeat while layout sync remains active

Mode integration:
`Xếp lưới` / internal `sync`
→ automatically enables layout synchronization

`Auto/manual`
→ disables layout synchronization

Limit integration:
current game-process count
→ runtime max-window limit
→ over limit
→ `_auto_stop_sync`
→ both synchronization subsystems stopped

Master change:
layout auto-disable is NOT proven; subsequent grid passes are master-aware and use the current master.

Explicit unknowns:
- exact layout-worker cadence;
- exact initial layout-active assignment;
- exact stop/cancel ordering.
