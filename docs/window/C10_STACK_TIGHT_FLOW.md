# C10 — Xếp gọn flow

Auto frame button Xếp gọn
→ _stack_tight_cmd
→ _move_windows_offset(pos_fn)
→ _get_preview_hwnds
→ master promoted to index 0
→ pos_fn(index) = (0,0) for every window
→ position-only SetWindowPos-family movement
→ preserve current size
→ _reset_hidden_state
→ [Xếp] Đã xếp N cửa sổ

Explicit unknown: later interaction if the 1-second Auto tiling loop is already active.
