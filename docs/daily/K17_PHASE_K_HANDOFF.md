# K17 — Daily integrated runtime/parity closure and Phase-K handoff

## 1. Scope

K17 does not reopen Trừng Ác, Tàng Bảo Đồ or shared Daily internals. It treats:
- K09 as the frozen Trừng Ác static handoff;
- K15 as the frozen Tàng Bảo Đồ static handoff;
- K16 as the frozen shared Daily integration handoff.

K17's job is to convert the remaining environment-only unknowns into an explicit runtime/parity matrix and decide whether Phase K can be closed without pretending that live parity was executed.

## 2. Exact specimen and packaged runtime evidence

The exact original was revalidated again before closure:
- `TLMTool_2.1.2(7).zip` SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`;
- archive size `93,715,901` bytes;
- ZIP CRC clean;
- inner `TLMTool.exe` SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`;
- inner EXE size `47,450,112` bytes.

The exact packaged runtime log remains:
- SHA-256 `17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`;
- `15,741,058` bytes;
- `387,238` lines.

## 3. Packaged log cannot prove Daily parity

Rechecked correlated counts are all zero for:
- `[Daily]`;
- `[Bắt đầu]`;
- `[Inject]`;
- `DailyTab`;
- `Tới bổ đầu`;
- `[Trị liệu]`;
- `Trừng ác`;
- `Tàng bảo đồ`;
- `Mất kết nối`;
- `Địa phủ`;
- `Tất cả acc đã dừng`.

This is useful negative evidence only.

It means the bundled log cannot validate the Daily runtime contracts. It must not be converted into a fake runtime PASS.

## 4. Static closure status

Static Daily research is internally complete:
- every Trừng Ác top-level callable is covered by K03-K09;
- every Treasure top-level callable is covered by K10-K15;
- every shared/cross-activity top-level callable is covered by K01/K02/K16;
- no blocking contradiction remains across K09/K15/K16.

Therefore there is no remaining known static Daily handler gap that requires another reverse-engineering task before leaving Phase K.

## 5. Runtime matrix

The runtime handoff is stored in:
`docs/daily/K17_RUNTIME_PARITY_MATRIX.tsv`.

It deliberately distinguishes:
- `VERIFIED_STATIC`;
- `VERIFIED_NEGATIVE_EVIDENCE`;
- `NOT_EXECUTABLE_HERE`.

No live test is marked PASS without a real Windows + live Thần Long environment.

## 6. Highest-priority live boundaries

The remaining runtime-only boundaries are:

1. Populated roster refresh and HWND/PID reuse while rows actually exist.
2. Rapid per-row Stop -> Start to confirm generation protection under real thread timing.
3. Activity-wide versus per-row ownership of the same HWND.
4. Manual `Tới bổ đầu` / `Trị liệu` overlap while a Daily worker owns that HWND.
5. Mixed all-account Trừng Ác + Treasure start/stop and final global reset.
6. Singleton `_daily_all_monitor` and StartTab synchronization under concurrent unwind.
7. Trừng Ác reconnect/death runtime recovery.
8. Treasure reconnect/death runtime recovery, including measuring the currently-unknown Treasure reconnect timeout.
9. Config save/reload/destroy behavior, especially `daily_move_mode` compatibility.
10. Tk `after(0)` state marshalling under real concurrency.

## 7. Same-HWND ownership remains runtime-only

K16 proved separate state domains:
- activity-wide Trừng Ác;
- activity-wide Treasure;
- per-row/bottom sessions.

No unified mutex was recovered.

Static evidence also cannot prove that the original permits overlap.

K17 therefore leaves the original conflict policy to live observation and forbids reconstruction from inventing either:
- a new cross-domain mutex; or
- an assumption that overlap is safe.

## 8. Manual action overlap remains runtime-only

`Tới bổ đầu` and `Trị liệu` are shared HWND actions, not activity dispatchers.

The exact original rule when those buttons are used while an activity worker is already controlling the same account remains unresolved statically.

The runtime matrix records this explicitly instead of silently choosing a policy.

## 9. Recovery live boundaries

Trừng Ác static recovery is closed in K07/K09.

Treasure static recovery is closed in K13/K15, but the Treasure reconnect timeout numeric remains unknown.

Live runtime validation must confirm:
- success handoff after reconnect;
- timeout behavior;
- death/Map87 recovery;
- event ordering when recovery conditions overlap.

## 10. Persistence and destroy live boundaries

K16 freezes what is and is not persisted.

Still live-only:
- exact `daily_move_mode` migration/write behavior;
- exact `_save_on_destroy` cleanup order;
- whether any live timing creates duplicate save/cleanup or orphan thread behavior.

These belong in runtime parity, not further static speculation.

## 11. Phase-K closure decision

Phase K can be closed as:
`STATIC RESEARCH COMPLETE / LIVE RUNTIME PARITY HANDOFF PENDING`.

This is not equivalent to:
`LIVE PARITY PASS`.

The distinction is intentional.

Static research is complete enough for later reconstruction because:
- handler coverage is complete;
- ownership boundaries are documented;
- failure classes are documented;
- unresolved items are isolated to runtime timing/race/environment behavior;
- every unresolved live-only boundary has an explicit test entry.

## 12. Reconstruction rule

Later implementation must:
- preserve K01-K16 contracts;
- keep K17 live-unknowns observable/testable;
- avoid converting UNKNOWN runtime behavior into hardcoded guesses;
- use the K17 matrix as the required parity checklist when a Windows/game environment becomes available.

## 13. Phase transition

Phase K — Daily is statically complete.

Next phase:
`L — Dồn`.

Next task:
`L01 — Dồn authority / visible surface / handler inventory / dependency boundary audit`.