# S57 — C12 faithful hide primitive

Original binary C12:
\`\`\`text
Auto/Start Ẩn hết:
  _hide_windows_cmd
  _hide_all_game_windows
    → current cached game HWNDs (master index 0)
    → capture GetWindowRect (saved_window_rects)
    → move each window x=-2200 y=-2200
    → preserve w/h, avoid hiding visibility (Unity continues rendering)
    → label changes to Hiện hết; state windows_hidden
  _show_all_game_windows:
    → CONTRADICTORY STATIC DOC: previous rect vs (0,0), UNRESOLVED
\`\`\`

S57 code only implements confirmed hide half:
\`\`\`text
C12HideAll.hide(snapshot, max_windows, master, allowed)
  → prevalidate every candidate HWND/PID/game executable/class/title
  → deny if missing independently verified positive server window limit
  → store exact pre-move rectangles by HWND/PID
  → SetWindowPos(-2200,-2200, flags NOSIZE|NOZORDER|NOACTIVATE)
  → HIDDEN only when all items are moved / already at target
  → if interrupted, return partial result and freeze hidden tracker
  → if called twice, never overwrite original rectangles
\`\`\`

No guessed show, no UI button, no physical cursor, no login, no OS shutdown, no Proxy, no claim of actual game execution. Test-owned native Tk HWNDs prove only the Win32 mechanics.
