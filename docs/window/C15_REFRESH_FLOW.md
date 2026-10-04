# C15 — Refresh flow

Main embedded preview:
`Làm mới` / btn_refresh_preview
→ full preview-list refresh behavior
→ _clear_window_preview_list
→ for each old item:
   DwmUnregisterThumbnail
   destroy destination overlay HWND
   destroy preview frame
→ read current game-window/cache set
→ apply retained _preview_order by HWND
→ current 1x–5x column choice
→ recreate preview frames
→ DwmRegisterThumbnail
→ apply DWM properties
→ live preview list restored

Automatic maintenance:
_update_window_previews_loop
→ alive_hwnds + valid_items + need_refresh
→ conditionally rebuild preview list
→ refresh labels/HP
→ update slot combobox mapping

Detached preview:
↺
→ _refresh_detached_preview
→ close detached preview
→ reopen detached preview
→ load current game-window list

Explicit unknowns:
- exact main Tk command expression;
- exact need_refresh Boolean expression;
- whether manual refresh forces a new worker-memory read.
