# N07 — Tối ưu per-account/all-account start/stop lifecycle and concurrency audit

## Authority and continuity
- GitHub main was checked before work: HEAD 5ac47f041091fff57d0b33826427126738033172. PLAN.md, STATE.md, PROJECT_STATUS.md and N06 were reviewed. N01–N06 are complete static research; N07 had no artifacts. Preserve them unchanged.
- Original frozen ZIP TLMTool_2.1.2(9).zip SHA-256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd, 1050 ZIP entries and CRC clean. Inner TLMTool.dist/TLMTool.exe SHA-256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22, 47,450,112 bytes.
- Analysis used original binary compiled constants/symbols, embedded Vietnamese docs and previous N05/N06; no EXE, game, DLL or Windows worker was executed. Constants are NOT recovered Python AST.
- N07 addresses orchestration/visible state; N08 will address TLMP ping/watch/recovery; N09 will address stale-session startup resume, and N10 contract/parity.

## 1. Account row identity and individual toggle
Active ToiuuTab rows are keyed by HWND and guard expected PID. Row construction includes:
- _toggle_this callback -> _toggle_single_acc on a daemon Thread;
- per-row ▶ play button, _state initially Đã dừng (gray #555555);
- _stop_event and _gen; state dot lbl_dot and status lbl_state;
- row cached _mode_key and CONFIG_OPTIONS (N05), permission-disabled buttons when toiuu_tab is not authorized.
- Removing a closed/reused HWND unbinds prior identity and destroys that row. A new PID must not inherit its worker state.

The _toggle_single_acc original constant region references _set_state, clear, red Dừng lại and logs [Toiuu] acc hwnd=... bắt đầu — TODO logic.

**Important and deliberately precise conclusion:** The TODO string is a real compiled current string. It is an unambiguous warning sign that the per-account start route has an unfinished/logging branch. BUT the class also has separate _apply_single_acc, _send_perf_single and _stop_restore_single paths. A string alone cannot prove the TODO branch executes under every click, or that the entire account button never functions. N07 cannot certify complete single-account start. A Windows trace or stronger recovered control flow must determine exactly whether selection -> TLMP send happens for this button.

Likewise, _gen and Event existence does not prove precise generation increments, stop cancellation during DLL send, or stale UI callback ordering. The account lifecycle contract is a testing target, not an implementation pass.

## 2. Bulk Bắt đầu/stop/scan worker
Bottom green Bắt đầu dispatches _start_all_accs on a daemon thread. The ToiuuTab constructor holds _start_all_busy and _scan_seq. The exact original _start_all_accs symbol block establishes:
- busy/reentry message Đang xử lý lệnh trước — bỏ qua;
- Đang quét... plus disabled/button-orange scan state;
- Không acc nào cần chạy short-circuit;
- Gửi lệnh dừng tất cả acc... and Đã dừng tất cả acc;
- per-target nested _start_one and Đã chạy ... acc completion message;
- _schedule_state_label_reset and _all_monitor for post-start/stop updates.

The presence of both bulk start and bulk stop strings means there is explicit all-account start/stop functionality in the compiled module. It does NOT prove that repeated bottom button clicks always toggle directly without intermediate busy/scan/restore states. Nor do the strings guarantee every live game account was successfully changed.

N05 guards still apply: the gray Thấp vừa/Cực thấp/Cực đại buttons only update combobox values; the green bottom Bắt đầu is the command/apply boundary. Accounts with Không/None are not arbitrary TLMP_RESTORE recipients on start.

## 3. Background tab lazy refresh and selection of eligible accounts
Original _ensure_rows_loaded exact embedded documentation:
- tab hidden/unselected may have refresh paused; rows can be empty or stale;
- perform one full scan when needed;
- then targeted cheap refresh of rows with unresolved real character names (no system-wide EnumWindows for every poll);
- if the first completed full scan has zero rows, return False early, rather than waiting until timeout;
- this blocking/sleep orchestration must run on a worker, never the Tk thread.

The _refresh_unresolved_names and _apply_name_infos documents independently confirm targeted name retrieval in worker and applying updates on the Tk main thread. _scan_seq, _start_seq and _last_targeted occur in this control area and show sequencing state, though exact comparisons/retry count are UNKNOWN.

Separate _restore_targets embedded doc states target filtering on restore:
- alive process AND (has a real selected mode OR the game predates the current tool boot);
- a fresh game opened after tool boot with mode None needs no cleanup by default.
This is an intentional distinction between start eligibility, stop restoration, and old-session reconciliation; the exact all-stop filter and order cannot be inferred solely from the docs.

Runtime row state is HWND plus PID, while persistent per-character config uses real sanitized RoleName. Do not let stable saved name bypass live PID-owner validation.

## 4. Bulk lifecycle and automatic UI reset
Method _all_monitor is distinct from _tick_watch_loop:
- _all_monitor block contains exact status string Tất cả acc đã dừng — tự động reset UI;
- _tick_watch_loop is the independent TLMP-5 ping/recovery system and belongs to N08.

Other state/paint evidence:
- STATE_STYLE and STATE_DEFAULT_STYLE, _schedule_state_label, _apply_state_label, _ui main-thread marshal.
- Đã dừng gray, Đang chạy running, Dừng lại red #f44336 and temporary Đang quét... orange #ef6c00 / disabled control.
- _monitor_running in constructor and _all_monitor method indicate a monitor lifecycle distinct from sampling graphs and watch/recovery.

The correct architectural reconstruction should not leave the green Start button stuck in a running/red/stopping state after all account workers stop. However exact timing, UI color transitions in every partial failure, and whether _all_monitor runs in a single thread for simultaneous bulk operations are unverified.

## 5. Native send/stop relation with N06
- _send_perf_single provides native TLMP with expected_pid guard; _send_perf_all handles account counts.
- _stop_restore_single documents a stage-down of Cực đại to Cực thấp before TLMP_RESTORE; numeric STAGE_DOWN_DELAY and full error behavior remain UNKNOWN.
- Permission-guarded account and bulk action checks exist; do not disable them.
- A TLMP send helper boolean means transport-level result, NOT observed game-state change.
- Do not change N06 mode IDs: mode 0 normal; 1 Thấp vừa; 2 Cực thấp; 3 Cực đại; 4 restore; 5 ping. Selecting Không in N05 is skip, not 0/4.

## 6. Explicit unverified edges
1. Exact Python if/else path inside _toggle_single_acc containing TODO logic; how _apply_single_acc is reached and when.
2. _gen compare/increment, _stop_event signaling and thread join/wait policy.
3. _start_all_busy set/clear timing and action button repeated clicks.
4. Which account states and counts drive the main Bắt đầu/Dừng lại button, and how partial failure is painted.
5. Precise ordering of changed PID validation and in-flight native sends/restores.
6. Eligibility of mode-None accounts under every type of all-stop, especially old-session survivors.
7. Actual worker state save/restore races; detailed previous-session handling reserved N09.
8. Runtime ping/watch and account relogin reserved N08.

A current screenshot of the main Tối ưu tab is available from the already verified B11 baseline. That image has 0 account rows and shows only static bottom bulk actions, so it cannot validate any per-row start/stop or green-to-red transitions. It was consulted after binary analysis only.

## 7. Future test matrix — all NOT_RUN
| ID | Required behavior | Gate |
|---|---|---|
| N07-01 | Account ▶ spawns proper worker and correctly executes selected TLMP mode | Windows live |
| N07-02 | Identify whether TODO logic path is reached and whether it skips native apply | Windows trace |
| N07-03 | Individual Dừng lại stops that account and restores safely without other rows | Windows |
| N07-04 | _gen and stop Event prevent stale generation UI/worker resurrection | Race instrumentation |
| N07-05 | Invalid or closed HWND and PID mismatch fail closed | HWND/PID reuse test |
| N07-06 | Row creation/refresh preserves valid account config on real RoleName | Windows/config |
| N07-07 | Global Start skips none/invalid modes and permission-denied accounts | Windows |
| N07-08 | Global scan refreshes stale or empty rows from background tab | Windows |
| N07-09 | Empty full scan exits promptly without artificial timeout delay | Windows |
| N07-10 | Deferred real-name resolution does not block Tk | Windows thread |
| N07-11 | Second Start/Stop action during busy period follows original reentry policy | Windows |
| N07-12 | Bulk nested worker/counts match real successful TLMP sends, not merely eligible rows | Windows |
| N07-13 | Bulk stop differentiates mode-None fresh versus old-session survivor | Windows old/new game |
| N07-14 | Cực đại stage-down and restore remain correct during global stop | Windows visual |
| N07-15 | Monitor resets to Bắt đầu only when no active account remains | Windows state |
| N07-16 | Mixed account success/failure paints exact statuses/button styles | Windows visual |
| N07-17 | Native send in progress during stop/window loss cannot target reused PID | Windows stress |
| N07-18 | Main thread only mutates Tk, despite worker and targeted refresh | Windows thread |
| N07-19 | Permission limit enforced per action and per eligible account | Windows |
| N07-20 | StartTab shortcut state matches current Tối ưu tab state | Windows integration |
| N07-21 | Real tool/app restart and recovered running-session state are not conflated | N09/Windows |
| N07-22 | Full original-vs-new functional and screenshot parity | Stages S/T/U/V/W/X |

All 22 are acceptance requirements, NOT PASSED tests.

## 8. Gate and next action
N07 = STATIC_START_STOP_WORKER_STATE_AND_PID_BOUNDARY_AUDITED_WITH_TODO_UNCERTAINTY / LIVE_PARITY_DEFERRED.

No application source/build workflow was created. N01–N06, original EXE, PLAN, Proxy exclusion and prior B11 baseline were unchanged.

NEXT_ACTION: N08 — Tối ưu TLMP-5 ping/watch, Treo tick, recovery through Login tab, worker/snapshot evidence and false-positive behavior audit. Inspect exact original _tick_watch_loop, _tick_watch_round, _ping_one, _recover_row, WATCH_INTERVAL / WATCH_MAX_MISS and log parsing; do not claim live recovery until original Windows test.
