# N09 — Tối ưu persisted running set / startup stale-session reconciliation

## Authority and scope
- Checked GitHub main first: parent HEAD `d3ee4531e324a619444e913dd5ba7987c196085c`, N01–N08 completed, N09 absent. Read PLAN.md and STATE.md; `NEXT_ACTION` specifically requested N09.
- Original frozen uploaded `TLMTool_2.1.2(9).zip`: SHA256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, 1,050 entries, ZIP CRC test clean. Inner `TLMTool.dist/TLMTool.exe`: 47,450,112 bytes, SHA256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- EXE inspected **read-only, without executing it**. Exact Nuitka constant locations and embedded docstrings establish author intent/entry-point surfaces, not byte-for-byte Python source control flow. No prior N01–N08 source or artifacts were changed.

## 1. Distinct identities and what actually persists
Active original `ToiuuTab` constructor has `_boot_ts`, `_acc_rows`, `_reconcile_tries` and schedules `_reconcile_stale_running`. Per-account live windows are keyed by HWND/PID while **persistent running session** is keyed by the real character name, not the HWND.
Exact original embedded `_save_running_set` doc:
> Lưu tập acc đang chạy {tên: mode_key} — sống sót khi app bị kill giữa chừng để lần mở sau resume đúng phiên (nút đỏ) thay vì quên.
The serialization cluster contains `json.dumps`, `ensure_ascii`, and key `toiuu_running`; `_load_running_set` has `json.loads` and doc saying `{}` means no interrupted session. A separate `toiuu_was_running` appears near `pop`, but exact migration/cleanup purpose is **unknown**; do not invent simultaneous keys or modify persisted schema based on string presence alone.
Separate N05 `toiuu_cfg_<sanitized RoleName>` means a **chosen preference**, not proof the previous program was actively optimizing. N09 `toiuu_running` means **prior active session intent**; neither can replace a currently live HWND/PID/process-creation test. N04 `toiuu_monitor_open` only represents the auxiliary monitor window and must not cause resuming a game.

## 2. Distinguish surviving game from newly launched game
Exact original `_game_predates_boot` vicinity contains `_get_pid_from_hwnd`, `_psutil.Process`, `create_time` and this embedded doc:
> True nếu process game chạy từ TRƯỚC khi tool mở (= sống sót qua lần kill app trước) — chỉ những process này mới có thể kẹt cấu hình giảm. Game mở sau tool boot chắc chắn tươi.
Consequently **game still running when the tool was restarted** is eligible for old-session reconciliation; **new game launched after this tool instance** is not, even if the same character has the same saved name or HWND number. A saved account name alone is never sufficient.
Strong inferred test: compare process create_time and `_boot_ts`; exact `<`, tolerance, clock source, missing-psutil handling and PID reuse checks require deeper source/Windows evidence. N07 already proved reusing HWND with a new PID recreates a row; the process-creation guard further prevents stale optimized-state adoption.

## 3. Reconcile decision flow
`_reconcile_stale_running` is present in constructor after `_start_refresh`, `_start_watch`, `_start_graphs` and scheduling `_restore_monitor_view`; the exact `after` timing is not verified. The reconcile region contains an interrupted-session detection log, `_reconcile_stale_worker`, `_ensure_rows_loaded`, `_check_perm`, `_resume_running_rows`, `_save_running_set` and `_restore_targets`.
Original log/text evidence supports these **decision branches** (semantic contract, not source AST):
1. **No persisted session:** `_load_running_set` yields `{}`; no old-active row should be fabricated.
2. **A current new optimization session already started:** original literal `Đang chạy phiên mới — bỏ qua khôi phục phiên cũ`. Do not let a delayed recovery worker overwrite a new session.
3. **Background tab account scan not yet completed:** original literal `Quét chưa xong vòng nào — giữ phiên cũ, thử lại sau 30s`. Do not eagerly erase previously saved session merely because an early scan has no rows.
4. **Prior game no longer alive / new instance replaced it:** original literal `Phiên cũ không còn (game đã tắt/mở lại) — bắt đầu mới khi cần`. Old red/running UI should not be inherited by the fresh process.
5. **Prior surviving game and permission:** `_resume_running_rows` marks only rows whose real character names occur in saved and whose game `predates boot`. Resumed row is `Đang chạy`, red stop button `Dừng lại` (`#f44336`) and `_ensure_monitor` maintains running-state updates. Doc states it returns resumed account count.
6. **Permission not yet determined:** original log says `Chưa có quyền (lần ... /5) — thử khôi phục phiên cũ lại sau 60s`. This explicitly indicates a bounded-count retries path, not immediate irreversible permission failure on the first check.
7. **Permission finally missing:** exact doc `Resume phiên cũ (nút đỏ) nếu còn quyền; mất quyền hẳn thì trả game về thường cho sạch (nút xanh).` Recovery/cleanup paths contain `_restore_targets`, `_stop_restore_single`, `Đang khôi phục...` orange `#ef6c00`, native stop/restore worker joins, StartTab shortcut sync and `Đã dọn phiên cũ — nút về Bắt đầu`.
This last branch is **restoration to normal**, not bypassing entitlement to start optimizing. Its restore-target docs from N07 specify alive process with a selected mode OR process surviving the old tool boot. Restoration and resumption therefore use **different** eligibility predicates.

## 4. Avoid false positive state and destructive cleanup
- Resuming stale red state must require a matched real saved character **and** process proven older than the tool instance. A newly created game with same RoleName must not be set to red solely from saved JSON.
- Unknown/unresolved character identity, partial scan and time-of-check/time-of-use PID mutation need conservative state; specific original fallback ordering remains unknown.
- Permission in the original is guarded by `_check_perm` / `toiuu`; do not bypass or immediately clear state on a transient auth startup issue. The `/5` retry text is exact; exact retry counter increments and timer registration need further validation.
- Stopping a prior surviving game should use N06 native staged-down restoration where applicable, not a fresh config assignment; `_stop_restore_single` is the cleanup entry point. Bool returned from transport is not guaranteed game-state success.
- Do not confuse N08 `_recover_row` (game hung -> close/relogin/new HWND) with N09 `_reconcile_stale_worker` (tool restarted while a game survives). These two paths have opposite process-creation expectations and should never silently claim one another's success.
- `toiuu_was_running` is recovered exactly but its original mutation semantics and version migration behavior are unverified.

## 5. Persistence and callback boundaries
- The original module has `settings.ini` and shared settings read/write/lock utilities. `toiuu_running` uses JSON by name/mode; exact INI section and malformed-JSON branch are not proven from constant locality alone.
- `ToiuuTab` has `<Destroy>/_save_on_destroy`, but whether an abrupt forced-kill invokes this event is explicitly **not** guaranteed. Therefore the persistent running set must reflect live-running intent before an unexpected termination, not rely only on graceful destructor execution.
- A delayed reconcile worker must not paint stale Tk widgets or overwrite a currently running fresh session. The original has `_ui` main-thread marshaling and `_reconcile_tries` but full cross-thread checks remain unverified.
- Exact 30s/60s numbers are literal status texts; they are *not measured runtime schedules* in this work. Original `WATCH_*` numeric constants (N08) are separate and must not be substituted for these retry periods.

## 6. Screenshot cross-check AFTER binary inspection
Prior B11 original screenshot shows Tối ưu panel with no account rows, GPU N/A and bottom green `Bắt đầu`. It cannot demonstrate interrupted-session red `Dừng lại` state, permission retry state or Native TLMP restoration; no populated rows or restarted-game screenshot should be fabricated.

## 7. Future acceptance tests — all NOT_RUN
| ID | Requirement | Gate |
|---|---|---|
| N09-01 | Serialize active real names/mode keys, not current HWND identifiers | Config/static |
| N09-02 | No active rows yields `{}` without phantom old session | Config |
| N09-03 | Handle valid JSON and malformed/unexpected saved types safely | Fault injection |
| N09-04 | Preserve old session if the first full account scan is incomplete | Windows/scan |
| N09-05 | Resume only saved real names with game create_time before tool boot | Windows/PID |
| N09-06 | Fresh game after boot never inherits old red stop button | Windows/PID |
| N09-07 | Reused HWND/PID and same name cannot accept stale restore commands | Windows/stress |
| N09-08 | A newly started optimizer session prevents overwriting by old reconcile | Windows/race |
| N09-09 | Authorized survivor gets running/red `Dừng lại` and correct saved mode | Windows/UI |
| N09-10 | Missing old process cleans stale intended-running record correctly | Windows |
| N09-11 | Permission initially unavailable retries without premature destructive cleanup | Windows/auth |
| N09-12 | `/5` retries and 60s messages match actual original timing/counter policy | Original runtime |
| N09-13 | Incomplete scan retries after original declared 30s without erasing data | Original runtime |
| N09-14 | Permission permanently absent invokes restore for eligible survivors only | Windows/permission |
| N09-15 | Max-mode restoration retains N06 low-stage-down then TLMP_RESTORE semantics | Windows/native |
| N09-16 | Cleanup reaches green `Bắt đầu`, correct StartTab shortcut sync | Windows/UI |
| N09-17 | Start/stop saved-set roundtrip survives forced tool termination | Windows/crash |
| N09-18 | Multiple names, duplicate names, stale config and partial survivors are handled | Windows/config |
| N09-19 | No psutil/process create_time does not falsely classify game as old | Windows/fault |
| N09-20 | N08 hung-relogin new game is not incorrectly resurrected as old | Integration |
| N09-21 | No stale worker updates destroyed Tk UI; no overlapping restoration | Windows/stress |
| N09-22 | Original-versus-new EXE live parity including statuses/cleanup | Stages S/T/U/V/W/X |

All 22 checks remain **NOT_RUN**; static proof is not a functioning Windows application.

## 8. Gate / next action
**N09 = STATIC_STALE_RUNNING_PERSISTENCE_BOOT_GUARD_AND_PERMISSION_RECONCILE_AUDITED / LIVE_PARITY_DEFERRED**.
N01–N08, PLAN, old reports and bundled EXE/DLL were not changed. No source/build files were added; Stage-S and Stage-T not started.
**NEXT_ACTION: N10 — Tối ưu reconstruction contract and parity matrix handoff**, reconciling N01–N09 UI, CPU/GPU, detached monitor, mode selection, TLMP native, per-account/global actions, watchdog, and stale-session state into one evidence-tiered checklist. Mark all runtime checks NOT_RUN, then move to Phase O only after N10 completion.
