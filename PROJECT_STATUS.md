# PROJECT_STATUS

Authoritative continuation state: [STATE.md](STATE.md)

## Gate A
A01–A08: **COMPLETE / VERIFIED**

## Gate B
B01–B14: **COMPLETE / VERIFIED**

## Gate C
- C01 — VERIFIED_WITH_EXPLICIT_UNKNOWN_BOOLEAN_FORMULA
- C02 — VERIFIED_WITH_EXPLICIT_UNKNOWN_FALLBACK_FORMAT
- C03 — VERIFIED_WITH_EXPLICIT_UNKNOWN_PROPERTY_BOOLEANS
- C04 — VERIFIED_WITH_EXPLICIT_UNKNOWN_BOUNDARY_AND_DETACHED_CADENCE
- C05 — VERIFIED_WITH_EXPLICIT_UNKNOWN_AUTO_SELECTION_RULE
- C06 — AUDITED_CLOSED_WITH_EXPLICIT_UNKNOWNS
- C07 — VERIFIED_WITH_EXPLICIT_UNKNOWNS
- C08 — VERIFIED_WITH_EXPLICIT_UNKNOWNS
- C09 — VERIFIED_WITH_EXPLICIT_UNKNOWNS
- C10 — VERIFIED_WITH_EXPLICIT_CONCURRENCY_UNKNOWN
- C11 — VERIFIED_WITH_EXPLICIT_CONCURRENCY_UNKNOWN
- C12 — VERIFIED_WITH_EXPLICIT_RESTORE_DOC_CONFLICT
- C13 — CURRENT
- C14 — TODO
- C15 — TODO
- C16 — TODO
- C17 — TODO
- C18 — TODO
- C19 — TODO
- C20 — TODO

Current task: **C13 — Đóng xem**

C06 was re-audited and closed. C07 Auto and C08 Xếp-lưới are now verified from the original EXE. Auto resets to (0,0) 1366×768 and re-tiles every 1 second; Xếp-lưới auto-enables layout+input sync, uses 3×4 defaults, and input keepalive re-blocks slaves every 1.5 seconds. Exact grid arithmetic/bounds/layout cadence remain explicit UNKNOWN.

Preserve Gate A/B baselines unchanged.

C09 verified the main preview 1x–5x column selector: runtime default 2x, manual callback, numeric column resolver, row/column rebuild and separate persisted detached-grid state.

C10 verified Xếp gọn as a real move-only multi-HWND action to (0,0), preserving each window's current size and clearing hidden-state bookkeeping.

C11 verified Xếp chéo as a move-only diagonal stack: master at (0,0), then +50 X/+50 Y per window index, preserving each current size.

C12 verified the off-screen hide design: move to (-2200,-2200), preserve size, avoid SW_HIDE to keep Unity rendering. Restore docs conflict between old-position wording and a specific (0,0) path, so that branch remains explicitly unresolved.
