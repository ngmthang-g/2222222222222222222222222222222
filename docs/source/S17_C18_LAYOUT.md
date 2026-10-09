# S17 C18 Native layout engine — bounded proof

Reference: original C18/C06/C08. Real layout engine uses Win32 SetWindowPos and master-first arrangement, with original worker-cached HWND list.

S17 layout is an **explicit local policy**, not recovered exact TLM geometry:
- 3x4 default grid; choose master as first surviving source unless supplied by master interface.
- Grid slots: (column * (master rectangle width + 8), row * (master rectangle height + 8)).
- Preserve native dimensions, position-only; refuse locations outside current screen.
- Before any move, verify every HWND is a live top-level S08 game candidate with matching PID, executable, class/title. Recheck immediately before each move.
- A positive max_windows must originate in independently verified PermissionSnapshot; absent/revoked denies.
- Run on worker, never direct native enumeration on Tk; consume S09 cache only.
- S13 existing Tk cache maintenance triggers worker retries. This does **not** establish the unknown C18 worker cadence.
- Event generation tokens stop stale worker after cancel/revoke.
- Never send keyboard/mouse events (C19), activate windows, run game memory readers or develop Proxy.

Success: [run 37887093950](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37887093950) shows 187/187 unit PASS and native SetWindowPos on 4 test-owned real HWNDs; 1 unrelated untouched, manual move corrected, permission revocation stops further movement. Same-code native regression runs S10–S17 + Stage S on dc4921fac73a7d232d817189ba5d509dd896170a all SUCCESS.

Unknown: exact original grid x/y/w/h equation, scheduling, initial state, limit comparator, original +/- bounds, C19 input mode and signed server. No actual game/EXE parity claim.
