# C12 — Hide/show flow

Ẩn hết
→ _hide_windows_cmd
→ current game HWNDs
→ save window rect bookkeeping
→ move to (-2200,-2200)
→ SWP_NOSIZE / preserve size
→ do NOT SW_HIDE
→ PrintWindow/PostMessage background operation remains possible
→ button becomes Hiện hết

Hiện hết
→ _show_all_game_windows
→ specific log/doc says move to (0,0), preserve size

Conflict retained:
generic toggle doc says return to old position while specific restore doc/log says (0,0); exact saved-rect restore branch remains UNKNOWN.

Any later visible re-layout
→ _reset_hidden_state
→ hidden bookkeeping cleared.
