# S56 — Start callbacks for original C10 / C11

\`\`\`text
Original TLM Start Auto:
  Xếp gọn        → _stack_tight_cmd()
  Xếp chéo       → _stack_diagonal_cmd()

S56 source callback (not exposed in unverified original UI yet)
  TLMStartTab._dispatch_auto_stack("tight"|"diagonal")
    ├ check: current Start selected + visible + non-closed
    ├ check: max_windows from separately verified Info, positive
    ├ check: cached S09 window snapshot valid and size <= limit
    ├ check: separate C18 Xếp-lưới layout not active
    ├ check: previous stack worker not still moving
    ├ clear old operation/event epoch
    └ launch background thread (NEVER Win32 call on Tk thread)
       └ S55 C10C11WindowStacker.apply(...)
          ├ original C10 (0,0) or C11 (50*i,50*i)
          ├ master first, preserve current HWND size
          ├ last-moment live HWND/PID + executable/class/title validation
          ├ cancellation fence before each SetWindowPos
          └ pure StackResult publication IF still authorized, selected

On master change / permission revoke / tab hide / destroy:
  clear event and invalidate generation, NO blocking join on Tk
  any inflight native call may still finish, but no further moves if cancelled
  discard late callback status

UNKNOWN / NOT CLAIMED:
  source exact Auto-frame pixel control coordinates
  complete C07 original Auto 1s tiling coexistence
  C12 _reset_hidden_state after re-layout
  real signed Info token, F05/F06 game actions, game-runtime parity
\`\`\`
