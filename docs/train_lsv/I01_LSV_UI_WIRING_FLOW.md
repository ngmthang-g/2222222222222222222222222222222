# I01 — Train LSV wiring flow

## Module lifecycle

`TrainLsvTab`
→ dedicated `train_lsv_tab.py`
→ module description: farm liên server (LSV) with account list

constructor surface
→ initialize module state
→ `_build_ui`
→ `_load_config`
→ bind `<Destroy>` → `_save_on_destroy`
→ `_start_refresh`
→ `_autosave_loop`.

## Persistent state

shared settings backend
→ TLMTool/settings.ini
→ section `TrainLSV`

direct key families:
→ respawn
→ auto_reconnect
→ trist
→ heal_map
→ pickup_mode
→ buff_*
→ acc_*_train
→ coord_*.

Autosave:
→ every 30 seconds
→ plus interaction saves / Destroy save.

## Train LSV UI

Cấu hình Train LSV
→ respawn_var
→ auto_reconnect_var
→ trist_var
→ heal_map_var
→ pickup_mode_var

pickup UI
→ shared PICKUP mode labels/default constants
→ deep discard semantics deferred I06.

## Manual schedule / Dạ Minh Châu

_buff_body
→ _buff_rows
→ fixed _da_minh_chau_row
→ dynamic _add_buff_row

fixed row:
→ name Dạ Minh Châu
→ always active
→ no delete
→ key list F1-F10 + 1,2,3
→ minute + second fields

persist:
→ buff_*.

Execution:
→ deferred I05.

## Saved coordinates

_coord_rows
→ + Thêm tọa độ / _add_coord_row
→ hide/show / _toggle_coord_list
→ name/map/X/Y
→ apply/delete
→ account Train combobox values

helpers:
→ _coord_name_list
→ _preset_to_vars
→ _apply_coord_to_all
→ _refresh_acc_combo_values
→ _remove_coord_row
→ _schedule_save_all_coords
→ _load_coords

persist:
→ coord_*
→ acc_<character>_train

deep schema/MapID behavior:
→ deferred I10.

## Account discovery / refresh

shared:
→ start_tab.get_windows()

every 5 seconds:
→ background worker
   → windows
   → character info
   → bag slots
→ Tk main-thread apply
   → _add_or_update_row
   → _remove_stale_rows(active_hwnds)
   → _reapply_permission_state
   → _request_scroll_update

refresh methods:
→ _start_refresh
→ _stop_refresh
→ _schedule_refresh
→ _refresh_acc_list.

## Row actions

row:
→ ▶ / _toggle_single_farm
→ Train coordinate combobox
→ move action
→ Fight action
→ state/map/extra surfaces

nested action references:
→ _ensure_in_lsv
→ _move_acc
→ _move_lsv
→ _farm_acc
→ _leave_lsv

permission:
→ permission_guard
→ has_permission
→ check_account_limit
→ trainlsv_tab.

Deep behavior deferred.

## All-account bar

`Tới LSV`
→ daemon Thread
→ _move_lsv_all

`Tới chỗ train`
→ daemon Thread
→ _move_all

`Đánh`
→ daemon Thread
→ _farm_all

`Rời LSV`
→ daemon Thread
→ _leave_lsv_all

Bottom:
→ green Bắt đầu
→ _toggle_farm.

Target/conflict/FSM semantics:
→ deferred I11.

## StartTab integration

TrainLsvTab
→ start_tab_ref
→ _sync_start_tab_btn

StartTab quick group
→ Train LSV toggle
→ Tới LSV
→ Tới chỗ train
→ Rời LSV
→ config navigation

StartTab docs:
→ bulk LSV action runs in worker thread
→ LSV toggle updates StartTab + TrainLsvTab

Therefore StartTab is a forwarding/mirror surface, not a second LSV engine.

## Visual cross-check

static extraction first
→ B06 screenshot second
→ SHA-256 matches exactly
→ no geometry remeasurement
→ no behavior inferred only from screenshot.
