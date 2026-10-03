# STATE — TLMTool 2.1.2

## STATUS
IN_PROGRESS

## GATE A
**COMPLETE / VERIFIED**

## GATE B
**COMPLETE / VERIFIED**

## GATE C
IN_PROGRESS

## COMPLETED
- A01 VERIFIED
- A02 VERIFIED
- A03 VERIFIED
- A04 VERIFIED_WITH_EXPLICIT_UNKNOWN
- A05 VERIFIED
- A06 VERIFIED
- A07 VERIFIED
- A08 VERIFIED
- B01 VERIFIED
- B02 VERIFIED
- B03 VERIFIED
- B04 VERIFIED
- B05 VERIFIED
- B06 VERIFIED
- B07 VERIFIED
- B08 VERIFIED
- B09 VERIFIED
- B10 VERIFIED
- B11 VERIFIED
- B12 VERIFIED
- B13 VERIFIED_WITH_EXPLICIT_UNKNOWN_FONT_POINT_SIZE
- B14 VERIFIED
- C01 VERIFIED_WITH_EXPLICIT_UNKNOWN_BOOLEAN_FORMULA
- C02 VERIFIED_WITH_EXPLICIT_UNKNOWN_FALLBACK_FORMAT

## C02 VERIFIED RESULTS
- Recovered the original three-layer identity model:
  - HWND = current runtime row/window anchor
  - PID snapshot = anti-HWND-reuse generation guard
  - sanitized RoleName = logical character identity/persistent config key
- `utils._get_pid_from_hwnd` resolves PID from HWND through the original ctypes/WinAPI path.
- `utils.get_character_info(hwnd)` reads character state through `memory_reader.Reader`.
- Shared Reader cache is keyed by PID:
  - each PID opens process/enumerates modules once
  - subsequent reads reuse handle/pointer chain
  - Reader cache TTL = 10 seconds
- `_format_char_info` computes HP% and strips HTML tags from RoleName.
- `invalidate_character_cache(pid)` is called after reconnect to force fresh pointer-chain resolution.
- Original row logic explicitly tracks rows by HWND.
- Each row keeps a PID snapshot and calls `bind_window_identity(hwnd,pid)`.
- Global identity guard rejects reused HWNDs when current PID differs from the stored snapshot.
- Multiple tabs contain the same stale-generation behavior:
  - Daily
  - Farm/Đồn
  - Party
  - Phó Bản
  - Rao
  - Tối ưu
  - Train LSV
- Same numeric HWND + different PID:
  - old row/member is removed
  - old identity binding is released safely
  - widgets/state are destroyed
  - fresh row is created from the new process
- Closed HWND rows are removed by incremental refresh.
- Before a real RoleName is readable, original tabs have a temporary `Window ...` placeholder; exact suffix formatting remains explicit UNKNOWN.
- When real character name becomes available, the existing HWND row label is updated.
- Persistent settings use character name rather than HWND:
  - original Tối ưu explicitly says HWND changes every game open, so key by name
  - Rao restores four slots by character name
  - farm-family tabs use the same pattern
- Start preview carries `src_hwnd`, has separate window/info caches, and refreshes RoleName from the background worker cache.
- Start auto-tile sorts game windows by character name with master first.
- Fake/debug accounts use fake HWNDs and are a separate compatibility namespace.

## C02 FILES
- `docs/tasks/C02.md`
- `docs/window/C02_HWND_CHARACTER_STATIC_EVIDENCE.tsv`
- `docs/window/C02_IDENTITY_FLOW.md`
- `WINDOW_BEHAVIOR_MATRIX.md`

## CURRENT_TASK
C03 — cơ chế preview HWND.

## BLOCKERS
None known for C03.

## DO_NOT_TOUCH
- Preserve Gate A forensic baseline unchanged.
- Preserve Gate B visual contract unchanged.
- Preserve C01's unknown exact discovery Boolean grouping.
- Preserve C02's unknown temporary Window-placeholder suffix.
- Do not begin C04 before C03 is verified.

## NEXT_ACTION
On CONTINUE:
1. Read `PLAN.md`.
2. Read `STATE.md`.
3. Execute **C03 only**.
4. Inspect original Start/DWM preview implementation.
5. Recover source HWND, destination HWND/frame, DwmRegisterThumbnail/Unregister/update properties, activation behavior and hung-window handling only where supported.
6. Update `WINDOW_BEHAVIOR_MATRIX.md` and persist C03 evidence/report.
7. Advance to C04 only after C03 is verified.
