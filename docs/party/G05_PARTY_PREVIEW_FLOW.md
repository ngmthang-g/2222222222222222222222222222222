# G05 — Party relationship to preview

## Verified Party path

Start background window cache
→ start_tab.get_windows()
→ Party background member refresh
→ Party HWND/PID member identity
→ Party RoleName / group UI / action state

This is **window discovery sharing**, not preview sharing.

## Start preview path — separate ownership

game HWND
→ TLMStartTab preview item
→ src_hwnd
→ DWM destination HWND
→ DwmRegisterThumbnail
→ live embedded preview
→ click preview
→ Start activation helper
→ source game HWND foreground

Main preview grid/columns
→ Start-owned

Detached preview
→ Start-owned

## No Party edge recovered

PartyTab
-X→ DwmRegisterThumbnail
-X→ refresh_window_preview_list
-X→ _activate_game_window
-X→ preview order
-X→ detached preview

Party direct game actions
→ click_at / resize_window / later team-action helpers
→ target game HWND directly
→ not through preview widgets.

## Important separation

Same physical game HWND
├─ may have a Start preview item
└─ may have a Party member row

But:
Start preview state/order/layout
≠ Party group state/order/layout.
