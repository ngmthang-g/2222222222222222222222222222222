# C14 — Detached preview flow

Main preview button Tách rời
→ _toggle_detached_preview
→ detached_active
→ _open_detached_preview
→ create DWM thumbnail overlays in region:
   x=0
   y=768
   width=screen_width-450
   height=remaining area to screen bottom
→ topmost detached overlays
→ build detached control bar
→ _detached_update_loop
   rebuild when game HWND list changes
   independent of Start tab visibility

Persisted detached settings:
- detached_auto_open (fallback True)
- detached_grid (default-like 3)

Refresh → close + reopen.
Đóng xem → close detached view.
Hủy tách → separate action; exact embedded-preview restoration sequence remains UNKNOWN.
