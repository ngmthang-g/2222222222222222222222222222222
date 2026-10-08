# N05 — Tối ưu: mode mapping, per-character configuration, selection versus native application

## Authority and current task
PLAN.md, STATE.md, PROJECT_STATUS.md and GitHub main were checked before work: HEAD a24d3be5bf9d488f4dee7dba47256d7f9a454e58; N01–N04 existed and N05 did not. Frozen ZIP SHA-256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd, 1050 files and valid CRC. Original inner EXE SHA-256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22, size 47450112. The original ToiuuTab compiled module was inspected read-only. Serialized constants are not Python source statements; no EXE was executed.

## Modes and precise distinction
| UI value | Internal mode key | TLMP mode mapping |
|---|---|---|
| Không | None / skip | no new command |
| Thấp vừa | medium | 1 |
| Cực thấp | low | 2 |
| Cực đại | max | 3 |

Compiled module contains MODE_ORDER, MODE_NAMES, NAME_TO_MODE, MODE_TO_TLMP, literal label lists and tagged integer objects 1/2/3. The earlier B11 static result corroborates the ordering. Original _mode_of_row documentation states cached _mode_key yields TLMP 0–3 and None for Không, keeping current config. Therefore Không must NOT be implemented as an immediate TLMP_RESTORE command: restore is a separate operation.

## UI controls and selection-only actions
Original exact code documentation:
- _set_all_combobox: Set combobox mọi dòng acc thành chế độ mode (không gửi perf); CHỈ gọi trên main thread.
- _cfg_assign_worker: CHI đổ chế độ vào combobox mọi acc (không kích hoạt perf); Nút Bắt đầu mới kích hoạt theo combobox từng acc.
- _cfg_assign_apply: bulk Tk UI updates; another exact doc says set hàng loạt 1 lần save.
- _set_single_worker: Chỉ gán combobox acc đó thành mode (không kích hoạt); Nút play đầu dòng mới bật/tắt chế độ + restore.
- _set_single_apply: Tk main-thread update, with original message (chua kich hoat).

Thus gray bulk Thấp vừa/Cực thấp/Cực đại buttons select values on all listed rows but do not send commands; corresponding per-row mode buttons change only that account's selection. Separate bottom Bắt đầu and row play/toggle own actual start/stop control flow. The read-only combobox has four current CONFIG_OPTIONS. The row selection uses StringVar trace_add(write), cached _mode_key and NAME_TO_MODE. Performing native TLMP when clicking the gray assignment buttons would be a functional regression.

## Account identity, settings and race boundary
The original _get_char_name uses RoleName; _sanitize_name removes HTML tags with <[^>]+>. Runtime rows use HWND with PID validation. A temporary Window ... pseudo-name is not a stable persistent identity.

Persistent per-character configuration has exact prefix toiuu_cfg_ and is keyed by real sanitized character name rather than HWND. The load_acc_config embedded documentation specifies valid-only restore by name because HWND changes on game restarts, and returns True when applying. _has_real_name and _cfg_touched appear around late-role-name restore: preserve user changes rather than overwriting them with late automatic loading, but exact mutation instruction order remains unknown.

_on_config_var_changed has original documentation: Trace combobox: cache mode + lưu setting (bỏ save khi đang set hàng loạt). The _save_config method and settings.ini reading/writing helpers also exist. Bulk changes are designed for a single save. The exact INI section, malformed-value fallback, default-priority behavior under toiuu_default_config and collision winner for duplicate sanitized character names are not sufficiently proven by the constant table and must remain UNKNOWN.

## Actual native application boundary — defer N06
The EXE contains _apply_single_acc, _send_perf_single, _send_perf_all, dll_injector, inject_into_pid, send_perf_command and TLMP_RESTORE. Its _send_perf_single document mentions an expected_pid ownership guard. The _send_perf_all document describes native TLMP rather than Lua/visible mouse-click commands, optionally injecting DLL when necessary.

N05 does not implement or guess native DLL payloads, handshake, success responses or safe stop/recovery transitions. These are N06. Permission guarding through has_permission_with_limit(toiuu_tab, toiuu) must remain in place.

## Cross-check after binary
The previously verified B11 screenshot shows three gray all-account mode buttons and separate green Bắt đầu. It has no account rows, so no per-row geometry or running visual state is inferred from the image. The exact static handler docs are stronger evidence for action meaning than the empty screenshot.

## Future acceptance checks (all NOT_RUN)
1. Exactly three ordered gray mode buttons.
2. Four readonly combobox choices including Không.
3. Correct medium/low/max and TLMP 1/2/3 mappings.
4. Không does not send restore or apply a new mode.
5. Bulk gray choice changes selection only.
6. Single-row gray choice changes only that row.
7. Bulk change persists one save round.
8. Separate bottom start performs application.
9. Row play controls execution/restore separately.
10. Permission guard rejects unauthorized execution.
11. Saved config restores by real sanitized RoleName.
12. Temporary Window ... is not used as persistent ID.
13. Invalid saved selection fails closed.
14. Late RoleName does not overwrite user-touched selection.
15. HWND reused by changed PID does not inherit old target.
16. Default/invalid/collision config matches original behavior.
17. Window/account refresh and Tk main-thread actions remain stable.
18. Native TLMP original-vs-new parity after N06/Windows runtime.

All 18 acceptance cases are PLANNED and NOT_EXECUTED; static proof is not executable feature parity.

## Gate and NEXT_ACTION
N05 status: STATIC_MODE_ACCOUNT_CONFIGURATION_AND_SELECTION_APPLY_BOUNDARY_AUDITED / LIVE_PARITY_DEFERRED.
No finished code, unrelated tab, PLAN, original EXE, Proxy runtime or B11 baseline was modified.

NEXT_ACTION: N06 — inspect original native TLMP mode commands and DLL send/restore, expected PID and single/all-account execution. Preserve N05 selection-only contract, security/permission guards and explicit UNKNOWNs. No invented native packet flow.
