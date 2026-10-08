# N10 — Tối ưu reconstruction contract and parity handoff

## Authority and meaning
- GitHub main parent `7b1a728c7dae4c91b461b217a1cb975ce6eee6c0` was checked; N01–N09 reports are completed, N10 did not exist.
- Original frozen ZIP SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd` (1050 entries) and inner EXE SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22` (47,450,112 bytes). Exact active compiled module `toiuu_tab.ToiuuTab` uses header 0x2c01fb5, 22,485 serialized bytes and 940 constants.
- This is an evidence-tiered **research-to-implementation handoff**, NOT reconstructed Python source, working UI, runnable EXE, new Windows test or certified functional parity.
- B11 original screenshot: 452×1032 capture/450×1000 client, selected Tối ưu, CPU 15% blue trace and GPU N/A empty graph; no account rows and no detached Toplevel visible. It cannot prove unshown worker controls.

## Consolidated component contract
| Phase | System | Frozen reconstruction interface |
|---|---|---|
| N01 | UI/authority | Active ToiuuTab, monitor and account areas; separate CPU-high warning; permissions, B11 empty-list baseline |
| N02 | CPU | Guarded psutil CPU read; bounded deque history; worker sampling and Tk Canvas main-thread redraw |
| N03 | GPU | nvidia-smi utilization.gpu CSV query; unavailable None/N/A; orange bounded GPU series |
| N04 | Detached | Toplevel CPU / GPU; CPU/GPU bars, close control, left-side 768-height intent, toiuu_monitor_open |
| N05 | Selection | Medium/low/max = 1/2/3; three gray bulk/per-account mode controls only select; Không=skip; toiuu_cfg_<name> |
| N06 | Native | WM_COPYDATA TLMP 0 normal,1 medium,2 low,3 max,4 restore,5 ping; PE64 resources.dat; PID guard; max->low->restore |
| N07 | Workers | Row ▶ and global Bắt đầu thread/busy/lazy scan/stop/reset; TODO logic must be traced |
| N08 | Watchdog | TLMP-5 and new Perf: ping log lines; two-miss Treo tick, safe Login mapping/manual fallback |
| N09 | Prior session | toiuu_running JSON {name:mode}, live PID/create_time earlier than tool boot and permission-gated resume/restore |

## Critical invariants — do not replace with fake controls
1. **Mode selection is not execution.** Three gray buttons for all accounts or one row update the combobox only. Native optimization is initiated through a separate start/play path, subject to entitlement and current HWND/PID.
2. **Không does not restore.** It means skip/keep game settings. TLMP mode 0 is normal configuration and mode 4 is restore original snapshot; modes 1/2/3 are Thấp vừa/Cực thấp/Cực đại and 5 is ping.
3. **No false success.** dll_injector/WM_COPYDATA send result is not proof of in-game graphics changes. Original bundled `data/resources.dat` is PE64 DLL SHA-256 `1375240c85abb9c211c66d3e8157a6dbfbc5551aabec465375b68e5301e645d4`; original listener source is not recovered.
4. **Main-thread Tk safety.** CPU and GPU sampling/worker/send are separate from Tk/Canvas redraw. Do not mutate widget state in background threads.
5. **Safe account identity.** Actual game commands target live HWND and matching expected PID, while saved per-character preferences use sanitized real RoleName (`toiuu_cfg_`). Persistent running intent is `toiuu_running` JSON; monitor-open preference is `toiuu_monitor_open`.
6. **Safe stop/restore.** For Cực đại, the original describes downgrade to Cực thấp, wait, and TLMP_RESTORE. Exact waiting time unverified and must not be guessed.
7. **Watchdog is not a sender ACK.** TLMP-5 diagnostic ping must be matched against a fresh `[pid=N] Perf: ping` log line; the packaged historical log includes 4134 such pings but is NOT this run's evidence.
8. **No wrong-login recovery.** `_recover_row` requires unambiguous LoginTab PID/row correspondence; otherwise explicit manual fallback, never kill another account by guesswork.
9. **Fresh game is not stale game.** Tool restart red Dừng lại state requires saved real name AND an alive game process that predates current tool `_boot_ts`; new PID/game cannot inherit old state by matching name.
10. **Permission and scope stay enforced.** Do not remove authorization/limit checks, create Proxy implementation, or modify completed N01–N09/other tabs.

## Original UI/visual checklist
- `Giám sát CPU/GPU` graph with CPU blue `#1565c0`, GPU orange `#e65100`; grid `#e0e0e0`, historical percentages and fallback `GPU: N/A (không có nvidia-smi)` when utility unavailable.
- Detached `CPU / GPU` is a real Tk Toplevel bar panel with `Đóng theo dõi`, `WM_DELETE_WINDOW`, saved open/close state. Original document describes left-of-main and nominal height 768; exact width/position and DPI unsupported by screenshots.
- Scrollable `Danh sách tài khoản` with `Nhân vật` and `Giảm cấu hình`; readonly combobox `Không, Thấp vừa, Cực thấp, Cực đại`; separate global mode buttons and bottom green `Bắt đầu`. Hidden/per-row controls are STATIC-only evidence when B11 shows no accounts.
- Running statuses `Đã dừng`, `Đang chạy`, `Treo tick`, temporary `Đang quét...`, red `Dừng lại` and StartTab Theo dõi/Tối ưu shortcut sync require game/account runtime to verify.

## Dependency and failure-state graph
UI selection -> cached mode -> permission check -> actual live HWND/PID owner -> native TLMP send (may fail) -> running row/bulk monitor -> TLMP-5 fresh-log health -> optional LoginTab recovery. On tool restart: saved `toiuu_running` -> scan rows -> verify same name and process created before boot -> permission -> resume red or safe restore normal/green.
This describes the component contract deduced from original symbols/docs, NOT recovered instruction-level Python control flow. The N07 TODO literal prevents claiming account start is complete. N08 hung-game relogin creates a new process; N09 resume works only with an old survivor. N05 saved preference is different from N09 running intent.

## Explicit unverified blockers (DO NOT fabricate)
1. N02: CPU 1-second embedded documentation versus unbound 750/GRAPH_TICK_MS; exact GRAPH_HIST not recovered
2. N03: nvidia-smi timeout, exception handling, first/multiple-GPU aggregation and None/0% history behavior
3. N04: detached Tk Toplevel exact width/geometry, close/destroy timing, multi-display and no popped screenshot
4. N05: config INI section/default priority, sanitized RoleName collisions, late real-name user-edit order
5. N06: TLMP PerfCmd packed structure/ACK and actual game-side effect, numeric STAGE_DOWN_DELAY; DLL listener source absent
6. N07: _toggle_single_acc contains a literal TODO logic branch; actual reachability/native execution and worker race unverified
7. N08: original ping timing, log rotation/freshness, auto_revive default, PID-to-LoginTab row mapping and relogin outcomes
8. N09: toiuu_was_running legacy semantics, exact boot-time comparison and /5 30s/60s retry implementation

## Evidence categories and test gates
- `EXACT_STATIC`: original EXE symbols, docstrings and file hashes. It proves design/strings but not runtime behavior.
- `STRONG_STATIC`: supported relationships (sampler, parser, saved settings), without original Python AST.
- `VISUAL_B11`: one original empty-account capture, not a screenshot of detached panel/populated rows.
- `PACKAGED_HISTORICAL_LOG`: 71,247 Perf lines, of which 4,134 are ping records. Historical, NOT a new test.
- `RESEARCH` gate: unresolved original timer/branch/packet mappings require stronger trace/evidence.
- `WINDOWS` gate: behavior with game/process/permissions/DLL/races requires instrumented Windows execution.
- `VISUAL` gate: compare new running Tk application screenshot against ground truth. `STATIC` gate: compare reconstructed source/config/assets to verified original constants.
- Parity matrix: **152** unique case IDs, with breakdown N01=14, N02=12, N03=8, N04=16, N05=18, N06=18, N07=22, N08=22, N09=22; gates STATIC=13, VISUAL=9, WINDOWS=122, RESEARCH=8. **ALL results are `NOT_EXECUTED_STAGE_S_NOT_STARTED`**, including STATIC and VISUAL tests, because the reconstructed app does not yet exist.

## Implementation/verification sequencing after research
1. Stage S: actual product source and coherent Tk shell with original permission/identity/config boundaries; no mock-only button handlers.
2. Introduce bounded CPU/GPU chart and detached view, then mode selection and character-name persistence, with isolated tests and source-level unknowns tracked.
3. Integrate verified native send/restore path without guessing TLMP protocol internals or bypassing entitlement; handle failure as failure.
4. Build robust single/global worker state, watchdog relogin and old-session reconcile. Require owner PID and safe fallback.
5. Stage T: real Windows build workflow and packaged assets, followed by case-by-case STATIC/VISUAL/WINDOWS/RESEARCH acceptance; original-vs-new parity requires runtime evidence.

## Phase N result and next action
**PHASE_N_STATIC_RESEARCH_HANDOFF_COMPLETE / LIVE_PARITY_DEFERRED.** This closes N01–N10 *research* only. Product source absent; no rebuilt EXE, no test runs, no function marked working.
**NEXT_ACTION: O01 — memory/item subsystem authority audit**, inspect original frozen compiled `memory_reader`, `memory_items`, `bag_filter`, `item_meta_data`, `weapon_ids` and active references; read PLAN.md and STATE.md plus GitHub main first. Do not copy unrelated game-tool logic or rework completed N tasks.
