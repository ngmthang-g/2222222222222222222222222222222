# S55 C10/C11 shared original-backed movement primitive

Original recovered contract:
\`\`\`text
Start → Auto mode:
  Xếp gọn → _stack_tight_cmd
  Xếp chéo → _stack_diagonal_cmd
Both → _move_windows_offset(pos_fn)
  _get_preview_hwnds → promote master index=0 → all windows
  C10 pos_fn(i)=(0,0)
  C11 pos_fn(i)=(50*i, 50*i)
  position-only SetWindowPos, NO resize
  _reset_hidden_state (requires original C12 state subsystem)
  "[Xếp] Đã xếp N cửa sổ"
\`\`\`

S55 implementation \`src/window_stacking.py\` owns ONLY the original position-only geometric engine, the verified S09/Win32 HWND set and conservative permission/identity barriers. No new Tk Auto controls and no hidden-state implementation. Existing C18 grid formula (an expressly local unknown) is NOT reused.

Actual native CI moves only test-created Tk windows, never a real game. Test adapter simulates positive game identity; production NativeWin32Backend does not. The real native movement and measured dimensions are verified, while F05/F06 launch/login and original Auto UI are still not.
