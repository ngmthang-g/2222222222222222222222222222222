# C09 — Preview columns flow

UI Cột: 1x / 2x / 3x / 4x / 5x
→ preview_grid_var (default 2x)
→ _set_manual_preview_grid
→ preview_grid_manual state
→ _get_preview_columns
→ parse selected x-form to numeric preview_cols
→ refresh_window_preview_list
→ preview_rows + row/column grid positions
→ preview frames
→ DWM destination HWNDs positioned over frames

Preview order is separate:
◀/▶ → _move_preview_item → _preview_order keyed by HWND → rebuild preserves order.

Detached preview is separate:
detached Cột Combobox → detached_grid → persisted settings.

Main preview_grid persistence key is not recovered.

Explicit unknowns: exact preview_rows expression and exact manual-flag assignment sequence.
