# G07 — Party relationship to mouse synchronization

## Party direct action path

Party group/action worker
→ resolve intended target HWND
→ for create-team fallback:
   → resize leader window to 1366×768
   → check_pixel on target HWND
   → click_at fixed UI coordinate on that same target HWND
   → continue fixed action sequence

This is targeted automation.

## Start synchronized mouse path — separate subsystem

selected Start master HWND
→ mouse.Listener
→ _on_master_click / _on_master_scroll / _on_master_move
→ master client coordinates
→ size-aware master→slave scaling
→ serialized down/up worker
→ Start-managed slave HWNDs
→ scroll / throttled move replication

PartyTab has no call edge into this pipeline.

## Explicit non-edges

Party leader
-X→ Start master mouse source

Party group list
-X→ Start mouse slave list

Party start/stop
-X→ Start _toggle_input

Party click_at
-X→ mouse.Listener broadcast

Party fixed coordinates
-X→ C19 master/slave coordinate scaling

## Shared mouse symbol

Party `mouse`
→ bind_window_identity / unbind_window_identity
→ HWND/PID generation safety

It is not evidence of Party mouse-listener ownership.
