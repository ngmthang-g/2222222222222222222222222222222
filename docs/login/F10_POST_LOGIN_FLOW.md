# F10 — Post-login routing flow

Login batch finishes account workers
→ Login monitor aggregates completion
→ use persisted `after_login`

`wait`
→ no routing action

`party`
→ resolve `party_tab_ref`
→ if missing: warn and stop routing
→ select Party tab on UI thread
→ hidden tab now gets a chance to scan game windows
→ wait for Party scan readiness
→ bounded by max 20s (original cross-reference to login_tab._wait_and_activate)
→ if Party already `_running`: skip
→ otherwise call real Party `_toggle_run`
→ log success/error

`train`
→ resolve `farm_tab_ref`
→ target label `Train`
→ select target tab
→ wait for target `_acc_rows` readiness, max 20s
→ if target `_farming` / `_farming_acc` indicates already running: skip
→ otherwise call real `_toggle_farm`
→ log success/error

`train_lsv`
→ resolve `train_lsv_tab_ref`
→ target label `Train LSV`
→ same readiness / already-running / `_toggle_farm` path

`don`
→ resolve `donvang_tab_ref`
→ compiled target label literal `Dồn vàng`
→ supplied screenshot visually reads `Đồn vàng`
→ same readiness / already-running / `_toggle_farm` path
→ final visible text decision deferred to F11 parity test

Readiness rule:
→ target tab must be selected first
→ hidden tabs may not scan while hidden
→ wait for scanned HWND-backed rows
→ maximum wait = 20s
→ final UI/start action returns to main Tk thread

Missing target:
→ warning only
→ do not invent fallback

Already running:
→ skip
→ never blindly call a toggle that could stop active automation

Routing error:
→ contained/logged as post-login error
→ does not retroactively change the completed credential-login result

Manual Login:
→ `_open_game_batch`
→ normal login workers
→ same completion/routing layer

Scheduled Login:
→ F09 schedule calls the same `_open_game_batch`
→ same normal login workers
→ same completion/routing layer
→ scheduler remains alive waiting for close event

Explicit unknowns:
- exact poll interval inside the 20s wait
- exact Login helper HWND match/count formula
- exact rule for invoking route after mixed success/failure or zero success
