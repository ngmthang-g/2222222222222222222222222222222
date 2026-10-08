# M06 — Rao start/stop worker audit

## Authority and continuity
- Checked GitHub `main` before work: HEAD `eedf0a1f31fc27ae4b63b582b1967785a70d8037`. The existing Rao artifacts are M01–M05; no M06 artifacts existed.
- Original uploaded archive `TLMTool_2.1.2(9).zip`, SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`.
- Active inner `TLMTool.dist/TLMTool.exe`, SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Exact serialized authority `.rao_tab` starts at `0x2bd7850` (11,774 bytes; 582 constants), active `RaoTab`.
- All conclusions below derive first from the original binary's exact strings/constants, symbol-local surfaces and prior M01–M05 contracts. Screenshot cross-check occurred **after** static review. Serialized constants are NOT decompiled Python code; uncertain control-flow micro-order stays unknown.

## 1. Entry points and execution ownership
- Bottom dedicated-tab button is `Bắt đầu` (`0x2bd7f20`). Its build-UI path uses `threading.Thread`, target `_start_all_accs`, `daemon`, `start` (`0x2bd802a..0x2bd8060`). Hence bulk start is dispatched off the Tk event callback rather than doing the entire start-all traversal synchronously in it.
- The per-account green play button starts as `▶` (`0x2bd8b89`). Its nested `_toggle_this` handler and `_toggle_single_acc` plus `target/args/daemon` are present (`0x2bd8b4a..0x2bd8b58`, `0x2bd8dd7..0x2bd8dfb`). The row toggle is also dispatched to a worker; precise Tk callback instruction order is not reconstructed.
- `_acc_rows` are HWND rows, with expected PID/window validity separately guarded (M05). Each row owns four `rao_vars`, a stop `Event` and a `_gen` field (`0x2bd8d18..0x2bd8d74`).
- Constructor also has `_bulk_set` and `_start_all_busy` (`0x2bd790d..0x2bd7918`): bulk-operation state exists, but exact re-entry predicate and simultaneous-click arbitration are unknown.

## 2. Four independent slots
- The exact `_slot_loop` doc says one independent loop per slot and a maximum of **four simultaneous slots per account**.
- Each `_slot_loop(self, hwnd, slot, gen)`-associated locals include `row`, `_running`, `want`, `resolved`, `reason`, `content`, `interval`, `chan_id`, `chan_name`, `ok`, `stamp`, `hit` (`0x2bda43d..0x2bda4b3`).
- The loop directly touches `row._gen`, `row._slot_running`, `_is_window_alive(hwnd)`, and the row PID before continuing, and has `_stop_slot` and the literal failure reason `Cửa sổ đã đóng` (`0x2bd8556..0x2bd85bf`).
- `_stop_slot` is distinct from `_stop_acc`. Its exact doc is **Dừng 1 slot (rao bị xóa/lỗi giữa chừng).** (`0x2bd8797..0x2bd87d6`).
- A single invalid/deleted Rao selection can fail closed for its affected slot; there is **no static evidence that this must stop healthy sibling slots**.
- Generation state exists at account creation, loop entry and stop/UI paths. It is a stale-generation safeguard boundary; exact equality comparison, increment locations and all race outcomes are not recoverable from constants alone.

## 3. Resolve, send, result state and timer
- M02–M04 remain the norm: on each active iteration the slot resolves the currently selected Rao definition; blank/missing content/channel/interval or missing Rao name cannot be sent.
- The loop calls `memory_items.send_chat` through `MI.send_chat` (`0x2bd8548`, `0x2bd85ff..0x2bd860e`); it is not a UI chat-panel click.
- The loop includes `verify_chat_echo` and catches/logs both `send_chat EXC` and `echo check EXC`; UI state strings include `Rao [<time>] ...`, `không echo` and `lỗi gửi` (`0x2bd860e..0x2bd86b9`). Echo checking is a visible result diagnostic **not proof of server acceptance**.
- The exact loop doc states **send, then wait the configured interval, then repeat**, not wait-before-first-send.
- Wait is through `row._stop_event.wait(max(... interval ...))` token surface (`0x2bd86bf..0x2bd86d7`), interruptible on stop. M04 fixed default 30s, normal valid 1..60s and independently resolved intervals. Live definition/account changes are observed on a subsequent iteration, not by rewinding the wait already in progress.
- On loop shutdown the `_ui_after_stop` path exists. Exact time to return from an in-flight `send_chat`/echo verification, interruption semantics of those calls, and server response timing remain unknown.

## 4. Per-account stop and visible status
- `_any_slot_running` exact doc: **True nếu acc còn ít nhất 1 nhóm đang chạy.** (`0x2bd9250`). Account-level running status is therefore an aggregation of four slot flags, **not all-four-must-run**.
- `_set_state` drives the row `lbl_state` using a nested UI update lambda; the shared `_ui` helper's exact doc requires Tk widget mutations to occur on the main thread (`0x2bd9215..0x2bd9250`, `0x2bd893e..0x2bd8963`).
- `_ui_after_stop` and `_paint_stopped` are separate methods, with a generator check and UI dispatch `_ui` (`0x2bd9286..0x2bd9318`). A stopped row can return to original **Đã dừng** status and play control; exact status-paint races when another slot continues remain unspecified.
- `_stop_acc` exact doc: **Dừng tất cả nhóm đang chạy của 1 acc.** (`0x2bd9318..0x2bd936f`). It is distinct from one-slot stop and not a global stop across all accounts.
- The per-account toggle references `_stop_acc`, stop-event `clear`, `_start_slot`, `started`, and both status/action strings **Đang rao ... /4 nhóm...** and **Dừng lại** (`0x2bd93cc..0x2bd94ab`).
- With no usable Rao selected it has failure text **Chưa chọn nội dung rao** (`0x2bd944d`). No dummy worker should be launched solely to paint a running state.

## 5. Start-slot guard and permission
- `_start_slot` exact doc: **Bật 1 nhóm (slot) nếu nội dung hợp lệ. Trả True nếu đã bật.** (`0x2bd9370..0x2bd93cb`). This freezes validated per-slot start and a boolean started result, without fabricating how each internal condition is ordered.
- `_check_perm` calls `permission_guard.has_permission_with_limit` on `rao_tab` / `rao` (`0x2bd919f..0x2bd9215`), with a no-permission diagnostic.
- Per-account toggle exposes **Không có quyền rao** (`0x2bd940d`). Bulk start has a warning `messagebox.showwarning("Rao", "Không có quyền rao (rao_tab) hoặc vượt giới hạn acc.")` (`0x2bd94ab..0x2bd950e`).
- No license bypass or newly invented limit is allowed in reconstruction. Exact ordering of limit evaluation relative to each eligible account remains unknown.

## 6. Bulk start policy
- Exact `_start_all_accs` doc: **Bắt đầu rao mọi acc đã chọn nội dung (bỏ qua acc chưa chọn).** (`0x2bd9547`).
- It uses account rows, slot iteration/generator checks (local `n_slot`, `items`, `genexpr`) and the dedicated per-slot start routine from the same class. The overall behavior is selective start, **not an unconditional spawn on every game HWND**.
- The bottom control's captured label is `Bắt đầu`. Static evidence establishes a `_start_all_busy` state but does not prove whether bottom button becomes `Dừng lại`, whether repeated presses are ignored, whether running accounts are restarted, or exactly how bulk concurrency is serialized. Keep those as explicit UNKNOWN; do not invent a global stop-all action here.
- No Rao-specific StartTab quick button was recovered in M01. Bulk Rao belongs to the dedicated tab.

## 7. HWND/PID disappearance
- Per-loop validity checks are explicitly present. A gone window gives **Cửa sổ đã đóng** and follows the per-slot stop boundary; no stale HWND may be treated as a currently valid process solely because its number was reused.
- The incremental 5s refresh independently removes HWND rows that close or change PID (M05), and the row is unbound from its previous window identity.
- Worker stop during disappearance is intended to fail closed. Exact sequencing of row removal, Event signal, generation invalidation, UI repaint and threaded send already in flight is **RUNTIME_REQUIRED/UNKNOWN**, not source-proven.

## 8. UI screenshot cross-check after EXE extraction
- Supplied Rao screenshot matches the dedicated tab with one message definition (Rao 1 / Thế giới / 30), an empty account listing, and `Bắt đầu` at bottom.
- An empty account list cannot visually verify per-row play/pause transitions, active slot counts, echo messages, or state colors. Those require actual Windows + live game runtime.
- EXE itself carries row play `▶`, stopped text `Đã dừng`, active **Đang rao ... /4 nhóm...** and **Dừng lại** surfaces. Do not show these as screen-captured evidence when they were recovered only statically.

## 9. Current acceptance boundary
**STATIC_WORKER_CONTRACT_AUDITED — LIVE_PARITY_DEFERRED**, not functional reconstruction DONE.

Required future Stage-S / live tests:
1. Four valid slots per account can run independently; one invalid slot does not incorrectly mark healthy siblings stopped.
2. First valid message attempts immediately; next attempts honor each slot's own interval.
3. Per-account button starts/stops precisely its own four slots. Stop interrupts an interval wait.
4. Bottom `Bắt đầu` ignores rows with no assignments; permission/limits block disallowed starts.
5. Same HWND reused by a new PID never inherits previous worker generation.
6. Late/invalid live edits take effect on the next cycle without a fabricated timer reset.
7. Message/send failures, echo absent, window closure, and tab refresh do not leave a stale running UI.
8. Compare EXE-static widget states and actual source reconstruction against the original via Windows live trace.

### Explicit uncertainties
- exact check order in `_start_slot` and `_toggle_single_acc`;
- exact `_gen` increment/compare and stale-callback suppression;
- exact UI state transitions when only one of four slots stops;
- whether repeated bottom `Bắt đầu` is ignored, restarts already-running rows, or has any stop role;
- exact bulk busy/re-entry/permission-check ordering;
- exact stop during in-flight send/echo verification and timing of row cleanup on HWND/PID loss;
- exact per-slot thread object ownership / join policy;
- any measured Windows scheduling jitter or actual server-echo behavior.

**NEXT:** M07 — Rao parity/reconstruction handoff, without creating Stage-S application/source/build placeholders.
