# S58 — Original-proven C12 hidden reset follows original C10/C11 visible re-layout

\`\`\`text
S57 C12 hide(target=(-2200,-2200), no resize)
   → record original hwnd+pid+GetWindowRect
   → HIDDEN or PARTIAL

C10 Xếp gọn or C11 Xếp chéo (existing S55 engine)
   → native live Win32 SetWindowPos
   → all game HWNDs at exact targets
        C10: all (0,0)
        C11: (50*index,50*index), master=0

S58 C12HideAll.reset_after_verified_layout(..)
   → validate original saved HWND/PID records still live
   → verify every game HWND class/title/process/PID
   → verify every actual window RECT equals C10/C11 target
   → check permission cancellation fence
   → clear C12 hidden state and saved rects, NO extra SetWindowPos
   → RESULT VISIBLE_LAYOUT_VERIFIED_STATE_RESET
\`\`\`

If any live geometry, HWND/PID or authorization fails, retain hidden bookkeeping; do NOT guess restoration. Exact original \`_reset_hidden_state\` internals may be less conservative than the S58 read-only verification fence. Original show vs saved previous positions remains unresolved, so no full "Hiện hết" action or pixel Auto UI is claimed. Native smoke proves actual Windows geometry only on test-owned Tk windows.
