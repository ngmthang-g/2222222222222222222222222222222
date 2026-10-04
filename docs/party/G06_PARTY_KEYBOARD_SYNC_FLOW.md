# G06 — Party relationship to keyboard synchronization

## Party path

Party group/member state
→ HWND + PID generation
→ RoleName / RoleID / TeamID
→ Party action worker
→ direct Party game/UI actions such as click_at/check_pixel/resize_window

No recovered Party keyboard broadcast stage.

## Start keyboard-sync path — separate ownership

selected Start master HWND
→ keyboard.Listener
→ _on_master_key_press / _on_master_key_release
→ foreground/master validation
→ virtual key (vk)
→ WM_MY_SYNC_KEY protocol
→ Start-managed slave HWNDs

PartyTab does not call into this lifecycle.

## Explicit non-edges

Party leader
-X→ Start master assignment

Party group member list
-X→ Start keyboard slave list

Party start/stop
-X→ Start _toggle_input

Party action worker
-X→ keyboard.Listener

Party action worker
-X→ WM_MY_SYNC_KEY

## Meaning

Party may target the same physical HWNDs for its own actions, but keyboard synchronization remains an independent Start/window feature controlled by Start mode/master/input-sync state.
