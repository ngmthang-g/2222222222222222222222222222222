# N06 — Native TLMP/performance command, bundled DLL and HWND/PID guards

## 1. Authority and stop conditions
N06 continues PLAN.md / STATE.md NEXT_ACTION exactly. GitHub main parent HEAD: d0d6bfd1148b267386575b9f35d55139bcefaeb0. N01–N05 already completed; N06 artifacts absent. No prior feature was rewritten.
Frozen authority: TLMTool_2.1.2(9).zip, 1050 entries, clean CRC, SHA256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd; inner original TLMTool.dist/TLMTool.exe size 47450112, SHA256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22. Static original EXE + packaged payload and packaged log were read, not executed. Original Python AST and DLL source are not available.

N06 studies native TLMP transport, mode/restore semantics, per-account PID guard, bulk helper result and DLL existence. Precise global start/stop scheduling and UI race/state machine are N07; watch/hung recovery later N08; stale-session replay later N09. No permission bypass or unrestricted injection is an N06 task.

## 2. Native transport from original compiled dll_injector
The EXE includes a current compiled .dll_injector module at 0x2918f40, with the exact send_perf_command function and matching local signature pid, mode -> bool in the module-local metadata (0x291ab3b). The relevant symbols and original embedded doc define:
- PerfCmd structure, WM_PERF_TOKEN and WM_COPYDATA;
- native performance message carrying token TLMP; not a Lua UI click;
- main game thread OnTick handling described by the wrapper;
- SendMessageTimeoutW used in the module to avoid indefinite blocking for hung windows.
The exact PerfCmd struct layout, COPYDATA dwData constant, WinAPI success/ack semantics and full handler execution order are NOT safely reconstructed from these constants alone. The original documentation provides a behavioral target, not verified source for the injected listener.

### TLMP mode enum: original EXE embedded documentation
| Numeric mode | Documented function |
|---|---|
| 0 | Normal/medium settings, 40 fps and partial restore |
| 1 | Thấp vừa: 30 fps and eco GameSetting |
| 2 | Cực thấp: builds on mode 1; AA/LOD/far/URP shadow changes |
| 3 | Cực đại: builds on mode 2; dark/black background |
| 4 | Restore original snapshotted config (Stop) |
| 5 | Diagnostic ping; writes a state log |

Modes 0 and 4 are different. Crucially, N05 established the combobox Không means SKIP/keep existing config and does NOT immediately invoke mode 0 or mode 4.

## 3. Real bundled payload: data/resources.dat
The original dll_injector.get_default_dll_path embedded documentation returns ./data/resources.dat. The archive contains TLMTool.dist/data/resources.dat, 39424 bytes, SHA256 1375240c85abb9c211c66d3e8157a6dbfbc5551aabec465375b68e5301e645d4. Unlike the extension, its binary header is MZ/PE32+, x64 machine 0x8664, DLL characteristic; a static PE reader describes UPX2-packed sections and export symbols including MinHook-related names.

Therefore a real PE64 DLL is bundled as data, not merely a fake DLL filename. Yet this finding DOES NOT prove every TLMP command will be accepted in a currently running game or prove the packed native listener's exact implementation. The EXE itself logs DLL không nhận (DLL cũ chưa có TLMP? build lại + restart game), showing explicit compatibility/failure handling.

The general injector module also contains is_dll_loaded, get_default_dll_path and inject_into_pid and their original documentation. The DLL loaded check compares normalized module paths and avoids repeated injection of the same path. The native APIs exposed for a running game cover the process/remote-load boundary. Current task does NOT create an injector, modify native binaries or bypass game/license restrictions. The DLL source and exact hook logic remain UNKNOWN.

## 4. Per-account and all-account sending interfaces
Original ToiuuTab function names, method-local metadata and embedded docs:
- _send_perf_single: native TLMP send to one account, returns True/False; expected_pid checks HWND ownership, rejecting reused-window cross-process requests;
- _send_perf_all: native TLMP send to all eligible live accounts; inject DLL if not loaded; returns (ok_count,total);
- _apply_single_acc: applies selected mode; None / Không means do not change current config (N05);
- _start_all_accs: separate orchestration entry point using a nested _start_one and log counters, analyzed more deeply in N07;
- _stop_restore_single: per-account stop with distinct TLMP_RESTORE stage and per-mode shutdown, details below.

The original static logs include missing PID, changed PID, absent DLL, injector failure and DLL not accepting TLMP. A helper returning True/False or total/ok is **transport-level status**, not independently verified game-state parity.

Permissions: has_permission_with_limit with toiuu_tab/toiuu is part of the action path and must not be disabled. Runtime row validity = HWND + current PID; character-name persistence belongs to N05 and cannot replace PID validation.

## 5. Stop/restore: stage down before full restore
The original compiled _stop_restore_single contains symbols _perf_mode, low, STAGE_DOWN_DELAY, TLMP_RESTORE and the exact embedded text describing a sequence:
- if the account was at Cực đại, lower to Cực thấp first;
- wait a few game frames for model rebuilding;
- invoke restore of the original snapshotted configuration.
The reason stated by the original is to avoid the game/model becoming visually stuck. This is a real stop-specific design boundary, NOT equivalent to clicking Không or sending mode 0. The exact numeric STAGE_DOWN_DELAY, timing, per-step failure handling and which modes need the staged path remain UNKNOWN. N07 must preserve the stage-down contract while testing stop behavior.

## 6. Bulk control boundaries and a TODO string
The original _start_all_accs region contains:
- Đang xử lý lệnh trước — bỏ qua (busy/reentry guard surface);
- Đang quét..., Không acc nào cần chạy;
- Gửi lệnh dừng tất cả acc..., Đã dừng tất cả acc;
- _start_one nested helper and Đã chạy ... acc.
Related _ensure_rows_loaded documentation distinguishes lazy background-tab scanning and targeted name refresh before bulk operations.

The _toggle_single_acc region also contains a literal acc bắt đầu — TODO logic. This exact string is an **incompleteness flag** worth investigating before claiming complete single-row behavior. It is NOT sufficient on its own to declare all single-account runtime code nonfunctional. The full active branch, actual worker calls and reentrancy require N07 and live Windows tests.

## 7. Historical native Perf log (important evidence-tier refinement)
Original archive contains data/automove_log.txt, SHA256 17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500, 15741058 bytes. Offline inspection counts:
- 71247 log lines with Perf: across 122 distinct PID tags;
- 4134 Perf: ping lines;
- 737 Perf: snapshot restored;
- 1282 Perf: unity-low applied;
- 532 Perf: cam black ON.
Other visible templates include snapshot taken, unity restored, monster hide/show, black background OFF and normal applied. No [Toiuu marker was found in this packaged log.

This is **packaged historical runtime evidence of native Perf activity**, materially stronger than only source strings. But it is not a current Windows-game test of this session, does not prove which UI button caused any given event, and does not certify that the recovered DLL binary accepts every command in the reconstructed tool. Do not conflate native Perf logs with current functional parity.

## 8. Known unknowns and safety boundaries
Exact source-code statements, low-level PerfCmd packed structure, WM_COPYDATA data pointer/length/return-value interpretation, DLL activation checks and hook runtime remain unverified. A boolean helper return is not a proof that frame rate, shadows, camera or GameSetting actually changed. No automatic payload replay was attempted.

N06 does not change any exe or DLL, produce new native executables or bypass permission. It does not add Proxy runtime or alter established selection-only UI behavior. The original standalone EXE and embedded payload are reference artifacts, never executed or modified.

## 9. Minimum acceptance matrix (planned, all NOT_RUN)
| ID | Condition | Verification gate |
|---|---|---|
| N06-01 | Exact mode 0..5 semantics differentiated | Original binary/static |
| N06-02 | Không/None skips without TLMP mode 0/4 | N05 + Windows |
| N06-03 | Native PerfCmd and WM_COPYDATA token behavior matches original | Windows with instrumented test target |
| N06-04 | Correct bundled resources.dat path, x64 binary and hash | Static packaging |
| N06-05 | Not loaded -> controlled DLL load, loaded -> no duplicate | Windows testing |
| N06-06 | Missing file, load failure and outdated DLL produce clear failure | Windows fault injection |
| N06-07 | Per-account hwnd owner PID mismatch fails closed | Multi-process HWND test |
| N06-08 | Bulk helper only counts intended live accounts | N07/Windows |
| N06-09 | Native wrapper False is not mislabelled real applied success | Windows log/state |
| N06-10 | Lower Cực đại to Cực thấp before restore where original does | Windows visual/state |
| N06-11 | Mode 4 restores snapshot and mode 5 pings without changing mode | Windows/original |
| N06-12 | Save/restoration respects prior snapshot/no snapshot | Windows/original |
| N06-13 | Busy/reentry and lazy background-tab refresh avoid duplicate sends | N07/Windows |
| N06-14 | Verify TODO logic account branch is actually connected | N07/Windows |
| N06-15 | Permission guard/limit remains effective on all actions | Windows entitlement |
| N06-16 | Native packaged historical Perf evidence distinguished from new live test | Evidence review |
| N06-17 | Game-window/sending race and stop-during-send cannot corrupt state | Windows stress |
| N06-18 | Reconstructed Windows product builds and matches functional behavior | Stages S/T/U/V/W/X |

No test is marked PASS merely because original constants, an external DLL or a historical log exist.

## 10. Gate and NEXT_ACTION
N06 = STATIC_NATIVE_TLMP_AND_DLL_BOUNDARY_AUDITED_WITH_HISTORICAL_PERF_LOG / LIVE_PARITY_DEFERRED.
Current rebuilt app/source: NOT_STARTED. Current Windows live game: NOT_RUN. Current product build: NOT_APPLICABLE.

NEXT_ACTION: N07 — Tối ưu per-account/all-account start/stop lifecycle, worker concurrency, UI state and PID permission orchestration audit. Use the exact original ToiuuTab block first, focus on _start_all_accs, _toggle_single_acc, _all_monitor, _restore_targets and _ensure_rows_loaded. Preserve N05 selection-only and N06 DLL/restore mode semantics. Never infer successful game behavior solely from TODO texts or historical logs.
