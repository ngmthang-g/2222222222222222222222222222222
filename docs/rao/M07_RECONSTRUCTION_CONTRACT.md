# M07 — Rao reconstruction/parity handoff (evidence-tiered)

## Authority, scope and completion meaning
This file consolidates M01–M06; it does **not** implement Rao or certify functional parity. Repository main was inspected: Phase M01–M06 artifacts exist; M07 was absent; no reconstructed product application, build workflow or tests exist. Previous work remains authoritative unless stronger contrary evidence appears.

Frozen original TLMTool 2.1.2:
- ZIP SHA-256: `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd` (1,050 entries).
- Inner `TLMTool_2.1.2/TLMTool.dist/TLMTool.exe` SHA-256: `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Compiled module `rao_tab.py`, class `RaoTab`; original EXE serialized module marker `.rao_tab` at `0x2bd7850`, length 11,774, 582 constants. Source-level control-flow is **not** available.
- Original user screenshot shows the Rao tab with `Rao 1`, channel `Thế giới`, interval `30`, empty account list, bottom `Bắt đầu`; *do not* use the empty screenshot to assert account-worker UI or behavior.
- This report distinguishes **EXACT_STATIC** (literal/embedded doc), **STRONG_STATIC** (well-supported semantic interpretation), **VISUAL** (actual captured screen), **RUNTIME_REQUIRED** (needs Windows/game), and **EXPLICIT_UNKNOWN** (not recoverable safely).

## 1. UI and permission contract — M01
- The present shell constructs Rao via `TLMMainApp` and controls tab visibility with `_set_rao_tab_visible`. Rao is current but permission controlled. Do not expose a forbidden tab to bypass entitlement.
- Dedicated Rao group `Cấu hình rao tự động`: exact headers **Tên | Nội dung rao | Kênh | Lặp (s) | Xóa**, editable name and message, readonly channel picker, interval entry, red row delete, `+ Thêm rao`.
- Account group `Danh sách tài khoản`: **Nhân vật | Nội dung rao**. The original compiled row builder has **four** Rao selectors, initial `▶` and `Đã dừng` state. These account widgets are **static-only** until a nonempty account screenshot and Windows test.
- Bottom `Bắt đầu` belongs to the dedicated tab, not a confirmed Rao quick action on StartTab. The exact current StartTab serialized block has no Rao-specific label.
- Account list refresh is designed for about **5 seconds while the tab is selected**. Permission checks exist both on row creation and action start.
- Reconstruction must match original Tk/ttk visual baseline, not just a mock layout.

## 2. Rao message definition and config — M02
- Each row has `name_var`, `msg_var`, `chan_var`, `sec_var`. New auto-name uses the **lowest unused positive Rao N**. No verified manual duplicate-name rejection.
- Definition identity is the trimmed *display name*, **not** a hidden UUID. Editing a row triggers save + account-options refresh; delete removes it.
- `[Rao]` owns two **independent** key families: `rao_<trimmed name>` for definitions and `acc_<real character name>` for assignments.
- Definition values are JSON object fields `content`, `channel`, `sec`; `ensure_ascii=False` supports Unicode. Loader sorts `rao_` keys, loads JSON, reconstructs rows. Preserve unrelated settings and `acc_` keys on saves.
- `_resolve_rao(name)` returns `(content, seconds, numeric_channel_id, display_channel)` or `(None, reason)`. Invalid/blank name, content, channel or interval fails closed.
- Definition rename/delete does *not* migrate old name references to the new name via UUID/alias. Stale selections cease to be resolvable.

## 3. Channel mapping and send boundary — M03
| Current Rao channel | Packet ID |
|---|---:|
| Thế giới | 8 |
| Bang hội | 2 |
| Môn phái | 6 |
| Tổ đội | 4 |
| Liên minh | 3 |
| Quân đoàn | 11 |
| Lân cận | 5 |

- **Only these seven** are displayed. Do not add Đặc biệt, Nói thầm or Liên máy chủ from the wider chat system.
- New row default **Thế giới / 8**. Config stores channel *name*, not numeric ID. Resolution maps current valid names to IDs; no arbitrary stale string is sent as a numeric ID.
- Call exactly `memory_items.send_chat(hwnd, channel_id, content)`, using the shared encoded `CMD_CLIENT_CHAT` path. The underlying Lua packet uses Base64 content. A True/queued return **does not prove server receipt or echo**.
- Nonempty stale saved channel value's exact load-time UI presentation is UNKNOWN. Never silently invent a new numeric channel or unproven migration rule.

## 4. Timing contract — M04
- Interval label `Lặp (s)`; `sec_var` is a digit-only entry with transient blank allowed.
- Current missing/invalid load fallback is textual **30** seconds. Strong static evidence supports **0..60** normalization of stored values; normal usable repeat intervals are **1..60**; zero/blank is not an uncontrolled send loop.
- Each account has **up to four independent slot workers**. A valid slot **resolves and sends first**, then waits its own interval via interruptible `_stop_event.wait(...)`, then repeats.
- Live valid message/interval/assignment edits affect the **next iteration**; they do not retroactively re-time the wait already underway. No separate rapid retry/backoff loop is recovered.
- Exact clamp expression syntax and Windows timer jitter were not reconstructed: retain their evidence tier.

## 5. Account identity, assignments and refresh — M05
- Live row identity = HWND plus validated expected PID; persistent assignment identity = sanitized real `RoleName`. Sanitizer strips HTML tags with `<[^>]+>`; no verified casefold rule.
- A temporary `Window ...` fallback is not a normal persistent restore identity. A reused HWND with another PID invalidates/remakes the live row. A vanished and returned character can recover by the real name key.
- A single `[Rao] acc_<real sanitized name>` stores one **ordered JSON list of four Rao display-name strings**, including empty slots. No HWND/PID suffix; no per-slot key family.
- Only currently existing Rao names restore. Rename/delete rebuilds option lists and clears stale live selections; it does not redirect references. The exact same-callback save timing of the clear is UNKNOWN.
- User changes mark `_rao_touched` and save; delayed real-name restore must not overwrite manual choices. Duplicate real character names collide in persistence: do not invent disambiguation or a conflict winner.
- An edit to a running slot's assignment is observed by next-loop resolution, not by a forced restart.

## 6. Worker, state and failure boundaries — M06
- Dedicated bottom `Bắt đầu` spawns asynchronous `_start_all_accs`; row `▶` delegates asynchronously to `_toggle_single_acc`.
- `_start_all_accs` starts only accounts with assigned Rao content; no selected content → skipped. Do **not** infer a global Stop All action or the behavior of a second bulk-start click.
- `_start_slot` validates and starts one slot, returning a boolean. `_slot_loop(self, hwnd, slot, gen)` is the independent loop, `_stop_slot` halts one invalid/deleted slot, `_stop_acc` halts all slots of one account. `_any_slot_running` is true as long as **one or more** slots remain active.
- Per-account runtime fields include `_stop_event`, `_gen`, `_slot_running`, and four `rao_vars`. Existence of a generation guard is proven; exact increments/check ordering **not**.
- Worker calls `MI.send_chat`; optional echo check and result/exception states are present (`không echo`, `lỗi gửi`). Echo is a diagnostic, not proof of successful delivery.
- UI status is routed via `_ui` to the Tk main thread; strings include `Đã dừng`, `Đang rao ... /4 nhóm...`, `Dừng lại`. Multi-slot partial-stop paint sequence/visual colors need live confirmation.
- Both row/bulk actions check `permission_guard.has_permission_with_limit` for `rao_tab` / `rao`. Unauthorized row state `Không có quyền rao`; bulk-warning surface exists. **Never bypass license/limit enforcement.**
- HWND/PID liveness loss fails closed (`Cửa sổ đã đóng`); precise ordering when removal races an in-flight send/echo/Tk callback remains UNKNOWN.

## 7. Evidence conflicts, explicit unknowns and non-goals
No direct M01–M06 contradictions were identified in this consolidation. However the following must *not* be promoted to source-proven behavior:
1. Exact Python source statements/operator order, `_gen` compare/increment, worker join timing.
2. Repeat bottom-start click/stop/restart and `_start_all_busy` serialization.
3. In-flight `send_chat`/echo interruption, multi-slot partial-stop repaint, stale UI callbacks after PID change.
4. Malformed or non-list account JSON; definition duplicate-name and character-name collision winner; transient blank name persistence; immediate stale selection save timing.
5. Nonempty invalid channel load-time display normalization; precise application layer for missing-value defaults.
6. Exact per-widget color/font/geometry in account-populated state; live send/echo timing and result.
7. Any claim of current source/build/Windows functional parity.

**Scope locks:** no unrelated refactor, no changed UI tab order, no Proxy runtime development (PLAN stage Q explicitly excluded), no extra StartTab Rao button, no simulated worker that only changes text.

## 8. Stage-S implementation handoff graph (future; NOT built now)
```text
TLMMainApp permission/tab lifecycle
  └─ RaoTab UI + account refresh [5s]
      ├─ definition rows [name_var/msg_var/chan_var/sec_var]
      │    ├─ [Rao] rao_<trimmed name> JSON
      │    └─ _resolve_rao -> (content, sec, numeric channel, label)
      └─ acc_rows keyed by HWND with PID verification
           ├─ [Rao] acc_<real RoleName> -> 4 ordered names
           ├─ per-account ▶ / _toggle_single_acc
           ├─ bottom Bắt đầu / _start_all_accs [eligible accounts]
           └─ up to 4 _slot_loop workers
                ├─ validate permission, assignment, generation, HWND/PID
                ├─ memory_items.send_chat(hwnd, channel_id, content)
                ├─ optional verify_chat_echo + UI status on Tk thread
                └─ interruptible Event.wait(interval) -> next resolution
```
This is an **interface contract**, not recovered source code. Future implementer must use the original behavior as authority when tests reveal differences. Do not infer unproven call sequence from the arrows.

## 9. Acceptance gates and ownership
- **Gate M STATIC RESEARCH**: M01–M07 documents exist, model parses, evidence matrix names source, counts consistent, known unknowns preserved. Mark **STATIC_RESEARCH_CLOSED / LIVE_RUNTIME_PARITY_DEFERRED** only.
- **Stage S**: actual executable product source, deterministic state/config tests and integrated callbacks. Merely drawing the UI or logging actions is NOT DONE.
- **Stage T**: reproduce Windows Nuitka standalone build, launcher/dependencies and artifact; provide actual CI/build logs.
- **Stages U/V/W/X**: static and visual comparison, original-vs-new live account/packet/GUI parity, multi-HWND stress and race analysis.
- The matrix `M07_RAO_PARITY_MATRIX.tsv` has **70 acceptance cases**. All are intentionally `NOT_EXECUTED_STAGE_S_NOT_STARTED`, even when the corresponding *requirement* is backed by exact static evidence.
- For all live tests, use a controlled account/test environment and do not present server echo or any game action as verified absent a real trace.
- No Rao source or build output is created in M07.

## 10. Next planned task
**N01 — Tối ưu module/active UI authority audit**: inspect the original `toiuu_tab` module, CPU/GPU graph and screenshot *after* static extraction; identify visible vs dormant controls, direct handlers and permission dependency only. Do not redo M01–M07. Stage S/T remain future gates.
