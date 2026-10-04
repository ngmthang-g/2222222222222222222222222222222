# C16 — Đóng hết flow

`Đóng hết`
→ `_close_all_preview_windows`
→ `_close_all`
→ shared `utils.close_all_game_windows`

Game close:
`get_game_windows()`
→ current HWND list
→ `IsWindow`
→ `PostMessage(WM_CLOSE)`

Then:
→ cleanup lingering Unity crash-handler processes

Post-close UI/cache:
HWND disappears
→ discovery cache updates
→ preview maintenance detects changed alive set
→ stale preview/master rows are removed/rebuilt

Distinct actions:
- `Đóng xem` = detached preview teardown only
- `Làm mới` = preview rebuild only
- `Đóng hết` = actual game-window close requests

Unknown: exact immediate refresh timing and any unrecovered wrapper confirmation.
