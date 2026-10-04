# C17 — Preview order flow

Embedded preview item header
→ ◀ or ▶
→ `_move_preview_item(src_hwnd, delta)`
→ `_preview_order` keyed by source HWND

Delta semantics:
- ◀ → delta -1 → one logical position earlier
- ▶ → delta +1 → one logical position later

Then:
`refresh_window_preview_list` / rebuild
→ surviving HWNDs are laid out using retained manual order
→ current preview-column count converts the ordered list into row/column positions
→ DWM preview item is recreated/repositioned for the same source HWND

Separate concerns:
- 1x–5x controls columns, not ordering
- detached preview has separate control bar/grid state

Explicit unknowns:
- exact edge behavior at first/last item;
- exact insertion point for a newly discovered HWND;
- whether detached preview indirectly reuses the same order;
- persistence across app restart.
