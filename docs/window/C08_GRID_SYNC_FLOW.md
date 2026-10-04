# C08 — Xếp lưới flow

Radiobutton Xếp lưới (internal value sync)
→ _on_mode_change
→ stop conflicting Train / Trừng ác / Tàng bảo đồ if active
→ show sync_frame
→ auto-enable layout synchronization
→ auto-enable mouse/keyboard synchronization

Layout side:
_toggle_layout → _sync_windows_loop / _layout_worker → worker-cached HWNDs → master first → _arrange_grid(grid_cols, grid_rows)

Input side:
_toggle_input → master as source → slaves as targets → _sync_keepalive re-block every 1.5 seconds

Grid controls:
- / + columns and rows → _on_grid_change → update labels + persist Start settings.

Limit:
new_version_info.max_windows → over-limit warning → _auto_stop_sync turns both systems off.

Unknowns preserved: exact +/- bounds, exact layout-worker cadence, exact grid arithmetic, exact limit comparator.
