# N08 — Tối ưu TLMP-5 ping watchdog, Treo tick and Login recovery audit

## 1. Provenance, scope and continuity
Read PLAN.md, STATE.md, PROJECT_STATUS.md and main GitHub tree before editing; parent main was 87cf332be49e963239611bd2c9be0910316e3ea0. N01–N07 were already completed and N08 did not exist. Frozen original TLMTool_2.1.2(9).zip SHA256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd, 1050 entries with valid CRC. The original inner TLMTool.dist/TLMTool.exe SHA256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22 and 47450112 bytes was inspected read-only.
No original EXE, DLL or game was launched. Compiled Nuitka constants/docstrings are not original Python AST. The packaged automove_log.txt is a historical artifact, not a fresh N08 Windows execution. N08 owns watchdog ping/diagnosis and recovery integration, not N09 boot-session reconstruction or N05 mode selection.

## 2. Startup and separate watchdog identity
Active ToiuuTab constructor references _start_watch alongside _start_refresh and _start_graphs. Its fields include _watch_running, _auto_revive, login_tab_ref, _closing, _acc_rows. Watch methods have exact class markers _tick_watch_loop (0x2c06ab0), _watch_log_path (0x2c06acb), _tick_watch_round (0x2c06ae5), _recover_row (0x2c06b01).
The watch-loop constant region contains WATCH_INTERVAL, _tick_watch_round and a caught-error message [Toiuu watch] lỗi:. The actual interval seconds, thread/cancellation and initial _auto_revive value are NOT source-bound. The watchdog is distinct from _all_monitor (bulk running-state reset, N07), _sample_loop (CPU/GPU graph, N02–N03), and CPUMonitor (CPU-high warning, N01).

## 3. Ping proof is a log line, not a native sender boolean
The exact original embedded _tick_watch_round documentation says:
> Ping TLMP-5 mọi acc đang chạy; 2 miss liên tiếp → đỏ + tự hồi sinh.
The original compiled method has a nested _ping_one worker, WATCH_PING_WAIT, _watch_log_path, getsize/fstat/st_size/seek, regex finditer and a pongs collection. Its regex literal is the byte/text expression \[pid=(\d+)\] Perf: ping. The method maps decimal PID captures to pong membership, retains _ping_miss state and contains messages tick sống lại and miss ... lần — Treo tick.
Together these establish a two-part design: issue native TLMP mode 5 as a diagnostic ping, then look for a matching PID log acknowledgment, rather than interpreting the send command's return alone as evidence of game-tick progress. Native mode 5 is explicitly a ping rather than configuration application (N06).
READ BOUNDARY: the packaged constant/local metadata suggests recording a file-size baseline, waiting for new output, then reading a later file region, but it does not prove precise getsize/seek instruction order, regex compilation flags, all exception branches or response window. A historical line or a returned send=True is not automatically a new live pong. Do not invent robust log rotation handling.

## 4. Miss threshold, state color and false-positive risks
Exact EXE fields/constants: _ping_miss, WATCH_MAX_MISS, Treo tick, tick sống lại, _recover_row, and the embedded two-consecutive-misses doc. State palette from original ToiuuTab: Treo tick #c62828; healthy Đang chạy #2e7d32; Đã dừng #555555. The exact UI callback/transition order is not recoverable from serialized data.
Two misses in a row are explicitly documented as the trigger. However, WATCH_MAX_MISS numeric binding and WATCH_PING_WAIT/WATCH_INTERVAL values remain unverified; do not hardcode guessed seconds from adjacent binary bytes. Recovery after a new pong is indicated by tick sống lại, but whether it resets every timer/worker bit immediately is unknown.
Potential false-positive or missed-ping cases to test, not assert as confirmed bugs: logging disabled or unwritable, log path wrong, log truncated or rotated between baseline and seek, log buffering, slow game OnTick, delays longer than WATCH_PING_WAIT, PID reuse, stale log lines, process exit during send or read, and multiple watched accounts writing concurrently.

## 5. Recovery interface and fail-manual branches
Original _recover_row function has _recovering guard and diagnostic fields hwnd/acc/mode. It explicitly names LoginTab integration via _tracked_windows, pid/idx, _close_single_account, _login_single_account, and mode_key. Original LoginTab module independently contains class markers LoginTab._close_single_account (0x2b679c9), LoginTab._login_single_account (0x2b6798a), and LoginTab._single_login_worker (0x2b679aa). These provide real cross-module interfaces.
Exact recovery doc: Kill acc treo → relogin qua login_tab → ép lại eco + start. It additionally contains WATCH_RECOVER_TIMEOUT, a loop-local alive/deadline/new-HWND context, and status strings đã login lại (hwnd=...) — start lại and quá ... s chưa login lại — kiểm tra tay.
Crucially, original EXE contains explicit fail-manual states: chưa nối login_tab — bỏ qua, relogin tay; and không map được dòng login cho pid=... — relogin tay. This means the reconstruction must NOT kill an unrelated process or report successful restart without an unambiguous Login row mapping. The existence of close/login helper symbols alone does not prove the original code always performs the full sequence, that permissions are satisfied, or that a native TLMP mode was reapplied successfully after the new PID.
An _auto_revive constructor field is present, but its enabled default and policy for unattended destructive close/kill are not proven from the constant table. Treat auto-close/relogin as conditional/permissioned in future acceptance, never infer a safe unconditional call.

## 6. Historical bundled log correlation (NOT a new run)
The original ZIP includes TLMTool.dist/data/automove_log.txt (15741058 bytes, SHA256 17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500). Offline read of its 387238 newline records found exactly 4134 lines containing Perf: ping, all 4134 matching the compiled watcher regex, covering 88 distinct PID labels.
Representative valid lines have variable trailing status fields:
- [pid=33544] Perf: ping busy=1 pending=0 addhook=0 camblack=0 snap=0
- [pid=19804] Perf: ping addhook=1 camblack=0 snap=1 active=2
The watcher's regex deliberately matches the PID/ping prefix and does not need the entire trailing state format. This is stronger evidence of compatibility between compiled reader and bundled native log format than string presence alone. It still does not establish receipt within a fresh ping window, login recovery success, actual process health or a reproduced scenario. There are zero [Toiuu-prefixed lines in this packaged log, so it cannot directly trace watcher UI transitions.

## 7. Ownership graph and future reconstruction contract
START: ToiuuTab._start_watch -> _tick_watch_loop -> _tick_watch_round on active running accounts.
READ: _ping_one sends TLMP-5; baseline/count/seek and regex parse new automove_log entries; pongs keyed by PID.
HEALTH: matching pong resets/reports responsiveness; misses track _ping_miss; documented two consecutive misses mark Treo tick/red.
RECOVER (conditional): _recover_row / _recovering -> check login_tab_ref -> match LoginTab tracked HWND/PID to exact row index -> request close and individual login -> wait for new window within WATCH_RECOVER_TIMEOUT -> reapply remembered mode/start if verified live.
FALLBACK: no connected LoginTab, no safe PID->row mapping, timeout or other uncertain result -> manual recovery/status, not ungrounded success.
The arrows summarize related compiled symbols and the original embedded doc. They are not a byte-for-byte recovered Python control-flow graph. Exact close/login invocation order and native acknowledgement must be validated later.

## 8. Acceptance matrix — ALL NOT_RUN
| ID | Test or expected parity property | Required gate |
|---|---|---|
| N08-01 | Watcher starts for correct active account set, no duplicate watch threads | Windows/instrumented |
| N08-02 | TLMP 5 sends diagnostic without mode alteration | Windows/native |
| N08-03 | Watch reads correct runtime automove_log path | Windows/filesystem |
| N08-04 | Fresh response regex matches exact PID and variable suffix fields | Unit + Windows |
| N08-05 | Old pong lines before baseline do not mask new missed pings | Log isolation |
| N08-06 | Valid new pong resets _ping_miss and prevents false Treo tick | Windows |
| N08-07 | Two *consecutive* misses produce Treo tick and red state | Windows/timing |
| N08-08 | Exact interval, ping wait, threshold, recover timeout values match original | Original runtime trace |
| N08-09 | Slow/absent log, truncation, rotation and unreadable file are safe | Fault injection |
| N08-10 | Concurrent accounts/pings do not misattribute PID acknowledgements | Stress |
| N08-11 | Exited/reused PID cannot trigger wrong-account recovery | HWND/PID race |
| N08-12 | _recovering prevents overlapping recovery attempts | Windows stress |
| N08-13 | No LoginTab connection falls back to manual action safely | Windows |
| N08-14 | No unique login-row PID mapping does not close another account | Windows |
| N08-15 | Correct LoginTab close_single/login_single integration | Windows/integration |
| N08-16 | Timeout waiting for new HWND produces manual-attention state | Windows/timing |
| N08-17 | After genuine relogin, remembered mode and native TLMP apply actually succeed | Windows/game |
| N08-18 | _auto_revive default/permission/disable flow mirrors original | Windows/config |
| N08-19 | Tk error/status repaint and account worker cancellation are main-thread safe | Stress |
| N08-20 | N07 stop/all-stop does not cause false hang/relogin cycle | Windows |
| N08-21 | Watcher vs N09 previous-session restoration has correct ownership | Stage N09/Windows |
| N08-22 | Rebuilt EXE original-vs-new functional parity and error messages | Stages S/T/U/V/W/X |

These are planned acceptance tests, not executed passes. Existing historical Perf ping records are explicitly not a replacement for live tests.

## 9. Status, preserved scope and NEXT_ACTION
N08 status = STATIC_WATCH_PING_AND_LOGIN_RECOVERY_INTERFACE_AUDITED_WITH_HISTORICAL_PING_LOG / LIVE_PARITY_DEFERRED.
No original executable, DLL, app source, unrelated module or Proxy feature was changed. N01–N07 remain authoritative, and N09 owns stale-session persistence. Build remains NOT_APPLICABLE until Stage-S product source and Stage-T workflow exist.

NEXT_ACTION: N09 — Tối ưu persisted running set, tool-crash/restart reconciliation, pre-tool-boot game detection and safe restore/resume audit. Inspect _save_running_set, _load_running_set, _reconcile_stale_running, _reconcile_stale_worker, _resume_running_rows and _game_predates_boot from original frozen EXE before screenshot. Keep watchdog N08 and native N06 unchanged.
