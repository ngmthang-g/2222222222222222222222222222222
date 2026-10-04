# G04 — Party relationship to physical window layout

## Independent systems

Party UI/member grouping
→ ready list
→ Tk grid / grid_remove
→ 3 ready accounts per UI row
→ group cluster
→ 6 Combobox slots = 2×3 UI layout
→ leader + follower logical ordering

This does NOT flow into:
→ Start grid_cols/grid_rows
→ Start _arrange_grid
→ Start _move_windows_offset
→ Start _auto_tile_windows
→ Start master HWND ordering
→ Start layout worker

## Shared HWND consumption

Start/window subsystem
→ owns EnumWindows/cache
→ Party calls start_tab.get_windows()
→ Party refreshes ready/member state

No recovered Party edge:
start_tab.get_windows()
→ arrange/tile

The returned HWNDs are used for identity/member refresh, not Party-owned desktop layout.

## One geometry exception

PartyTab._click_create_team(lhwnd, ...)
→ shared resize_window
→ width 1366
→ height 768
→ shared C06 resize semantics:
   - normalize window state
   - resize via SetWindowPos
   - keep x/y because SWP_NOMOVE
   - no activation via resize helper
   - no z-order change

Then later:
→ fixed-coordinate Party create-team UI interactions

Meaning:
1366×768 is a coordinate precondition for the leader create-team window, not a Party grid layout.

## Leader vs Start master

Party group leader
≠ automatically Start master HWND

No static call/assignment connects these concepts.

Party selection/order changes
→ must not silently reorder physical desktop game windows.
