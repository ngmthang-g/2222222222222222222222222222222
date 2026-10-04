# C07 — Auto flow

mode_var default = auto
→ _on_mode_change
→ layout sync OFF + input sync OFF
→ get game HWNDs
→ reset to origin (0,0), size 1366×768
→ _auto_tile_loop
→ every 1 second while auto_tile_active=True: _auto_tile_windows

Ordering:
HWND set → character-info cache → RoleName sort → master first → tile placement.

Limit:
_toggle_auto_tile → _get_max_windows + _count_game_processes → same server-backed limit subsystem as C06.

Boundary:
select sync/Xếp lưới → stop Train/Trừng ác/Tàng bảo đồ if active → auto-enable layout+input sync.

Explicit unknowns: exact auto_tile_active assignment timing, exact compiled edge to common arranger, exact final tile geometry, exact limit comparator.
