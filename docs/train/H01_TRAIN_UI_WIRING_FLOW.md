# H01 — Train/FarmTab wiring flow

## Construction

FarmTab(parent, info_tab, notebook)
→ initialize row/farm/refresh/autosave/map state
→ _build_ui
→ _load_config
→ bind Destroy → _save_on_destroy
→ _start_refresh
→ _autosave_loop

## UI ownership

FarmTab
├─ Cấu hình Về thành
│  ├─ _toggle_town_config
│  ├─ town_condition_var
│  ├─ _on_town_condition_changed
│  ├─ loop_var
│  └─ hidden _town_body
│     ├─ nav priority comboboxes
│     └─ sell/buy/medicine config vars
├─ Cấu hình Train
│  ├─ respawn/reconnect/pickup/heal/keep-mode vars
│  └─ manual buff rows
├─ saved coordinates
│  ├─ _add_coord_row
│  ├─ _toggle_coord_list
│  └─ row save/apply/remove callbacks
├─ account list
│  ├─ Canvas + Scrollbar
│  ├─ _add_or_update_row
│  └─ per-row action entry points
├─ all-account bar
│  ├─ _goto_sell_all
│  ├─ _sell_all
│  ├─ _move_all
│  └─ _farm_all
└─ bottom Bắt đầu
   └─ _toggle_farm

## Account refresh

_start_refresh
→ _refresh_acc_list
→ background worker
   → shared start_tab.get_windows()
   → character info / bag reads
→ main-thread apply
   → add/update rows
   → remove stale rows
   → reapply permission state
   → scroll update
→ _schedule_refresh
→ every 5000ms

Identity surfaces:
_pid_of + bind/unbind window identity.

## Config

shared settings backend
→ section Farm
→ active town/train/buff/coord/per-account key families

interaction saves
+ periodic _autosave_loop every 30000ms
+ Destroy save.

## Boundary

H01 locks UI/config/lifecycle wiring only.
Deeper Train behavior is deferred to H02+.
