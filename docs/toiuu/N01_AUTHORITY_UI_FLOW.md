# N01 — Tối ưu: active authority and UI boundary (EXE-first)

## Continuity / authority
- Read unchanged `PLAN.md`, `STATE.md`, and `PROJECT_STATUS.md`, checked `main` HEAD `76fc32fb8cc6f3790e30cceaafece18ff1f4e82f` and confirmed no N01 artifacts existed. Reuse B11 visual baseline; do NOT redo B11 or Phase A–M research.
- ZIP **`c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`** (1,050 entries, CRC clean), inner TLM EXE **`15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`** (47,450,112 bytes); frozen TLM 2.1.2 is authoritative. No original Python source was recovered.
- Actual original serialized module **`.toiuu_tab`** at `0x2c01fb5`, length **22,485 bytes**, **940 constants**, class **`ToiuuTab`**, source filename marker `toiuu_tab.py`, module marker `0x2c06c69`. At least 76 direct `ToiuuTab.<method>`-style symbols present plus initializer; do **not** equate marker count with original source lines or all callable instructions.
- Other related compiled module **`.cpu_monitor`** at `0x28d82e9`, length **2,019**, 127 constants. Its `CPUMonitor` is the standalone *high-CPU warning* service using `psutil.cpu_percent`, not the Tối ưu tab's CPU/GPU two-panel chart. This boundary is important.

## 1. Active application surface
- This is the active `ToiuuTab` path, not an inferred abandoned page: constructor evidence ties `_build_ui`, `_load_config`, `_start_refresh`, `_start_watch`, `_start_graphs`, `_restore_monitor_view`, `_reconcile_stale_running`, `_save_on_destroy`. The shell's visible `Tối ưu` tab was previously confirmed in B11; exact entitlement at capture not recoverable.
- Permissions exist in two tiers: `_apply_row_permission` explicitly disables new account-row controls without `toiuu_tab` permission; worker path contains `has_permission_with_limit`. Do not bypass or guess license rules. More detailed gate sequencing belongs to N05/N06 or later.
- Current StartTab contains **Theo dõi** and **Tối ưu** quick controls. `_sync_start_tab_toiuu_btns` explicitly synchronizes their state with Tối ưu — not evidence of additional unspecified actions.

## 2. Current Tối ưu UI and actual bindings
Original compiled block directly gives:
- `Giám sát CPU/GPU` → `Theo dõi hiệu năng.` and `Tách theo dõi` bound to `_toggle_monitor_view`.
- `CPU: --%` plus blue `#1565c0` time-history Canvas; `GPU: --%` plus orange `#e65100` Canvas; histories `deque`, `GRAPH_HIST`.
- `Danh sách tài khoản` (scrollable Canvas) and headers `Nhân vật`/`Giảm cấu hình`.
- Config labels **Không**, **Thấp vừa**, **Cực thấp**, **Cực đại**. Actual mode keys are `medium`, `low`, `max`; UI row includes mode combobox, per-account mode buttons/play, name and state widgets; screenshot does not contain populated accounts.
- `Điều khiển tất cả:` followed by **Thấp vừa**, **Cực thấp**, **Cực đại**; bottom green **Bắt đầu** with a worker-thread target `_start_all_accs`.
- State strings **Đã dừng**, **Đang chạy**, **Treo tick** with original status palette from B11. Exact populated-row geometry, event ordering and active animation remain live-unverified.
- `_add_or_update_row` uses HWND/PID identity and `RoleName` with actual process-reuse invalidation; 5s tab-selected account refresh in B11; exact worker delays/refresh exclusion when tab hidden remain for later audit.

## 3. CPU/GPU graph ownership — N02/N03 future depth
- Exact compiled documentation: **Sample 1s/lần (thread phụ) + vẽ lại (main thread).**
- `_start_graphs`, `_sample_loop`, `_schedule_redraw`, `_fmt_pct`, `_draw_one`, `_redraw_graphs` are real Tối ưu handlers. Main-thread drawing is distinct from high-CPU `CPUMonitor` warnings.
- `_read_gpu` uses `nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits`; `GPU: N/A (không có nvidia-smi)` is an explicit failure/absence state. No claim about GPU availability on another machine.
- Graph width/height, exact history length and sampling races are **N02/N03**, not invented here.

## 4. Detached CPU/GPU monitor — N04 later
- `_toggle_monitor_view`, `_open_monitor_view`, `_close_monitor_view`, `_update_monitor_view` and `_restore_monitor_view` are real function surfaces.
- Embedded doc: **Mở/đóng view bar CPU/GPU tách rời (sát cạnh trái GUI chính, cao 768).**
- Detached title **CPU / GPU**, `-topmost`, **Đóng theo dõi**, state key **`toiuu_monitor_open`** in `settings.ini`; saved state can reopen after restart. Exact window geometry across varying displays remains NOT VERIFIED.

## 5. Native game optimization boundary — N05–N08 future
- `_cfg_assign_worker` documentation explicitly says the three all-account mode buttons **only populate the combobox; they do NOT invoke perf**. Another doc says **Nút Bắt đầu mới kích hoạt theo combobox từng acc**.
- `_set_single_worker` likewise sets only one account's combobox; `_apply_single_acc` applies chosen setting and **Không = bỏ qua**.
- The actual native apply paths `_send_perf_single`, `_send_perf_all` reference `dll_injector.inject_into_pid` and `send_perf_command` TLMP; documented as native rather than Lua/UI clicks. This is distinct from selecting a combobox value. Deep packet/ordinal/mode policy and exact callback micro-order belong to N05–N07; do NOT create simulated buttons that just log.
- Per-process PID validation exists in single-send doc; no game EXE/DLL was executed during this audit.
- Persistent keys include `toiuu_running`, `toiuu_was_running`, `toiuu_monitor_open`, plus per-character saved mode config. Reconcile old running state against process creation time; surviving game-vs-new game distinction and exact resume/revert ordering belong to N08.
- `_tick_watch_round` exact doc describes **TLMP-5 ping**, **2 missed responses** and **Treo tick**, with `_recover_row` referencing `login_tab` to relogin/reapply. This is a recovered *code-intent* surface, **not proof** that recovery works in live game.

## 6. Screenshot cross-check after EXE examination
Reused already-verified B11 visual baseline rather than redoing any pixel measurement:
- 452×1032 screenshot / 450×1000 client; selected `Tối ưu`.
- `CPU: 15%` in blue with a nonempty history plot; `GPU: N/A (không có nvidia-smi)` in orange with no GPU trace in this capture.
- Empty account list, three gray mode buttons and green `Bắt đầu`.
- Static original placeholders `CPU: --%` and `GPU: --%` need not equal a later sampled screenshot. They reflect initialization before live sampling.
- Row geometry and running-state coloring cannot be determined from the empty list. B11 prior screenshot is visual evidence, not a test of native TLMP command success.

## 7. Evidence tiers, non-goals and unknowns
**Exact original EXE symbols/strings**: module/class, visible UI, CPU/GPU samples/worker/redraw docs, `nvidia-smi` arguments, monitor state, combobox-versus-apply separation, native apply entry points, permission, watch/recovery intent.

**Previously verified visual**: B11 panel geometry/colors and captured empty state.

**Static semantic with limits**: original `ToiuuTab` current authority and related native optimizations. The serialized constants do *not* supply Python AST/source-line proof, precise callback order, all timeouts, mode packet semantics, or runtime outcomes.

**Unknown/live-required**: exact CPU utilization sampling expression and history limits, GPU subprocess error policies, detached geometry on multi-monitor PCs, populated row button states, all native TLMP handshake semantics, permission-limit evaluation sequence, restart/recovery races, true visual/functional parity.

**DO_NOT_TOUCH**: PLAN, original zip/EXE, B11 visual artifacts, completed A–M, Proxy exclusion, other feature modules; no Stage-S product source/build placeholder and no fake runtime PASS.

## 8. N01 gate and next step
N01 is **STATIC_AUTHORITY_AND_UI_SURFACE_AUDITED / LIVE_PARITY_DEFERRED**. It establishes scope for later Phase-N behavior tasks without implementing them.
**NEXT_ACTION: N02 — CPU monitoring sample/history/redraw audit**, separating tab graph from `CPUMonitor` warning service, inspecting EXE first. GPU deep logic deferred N03.
