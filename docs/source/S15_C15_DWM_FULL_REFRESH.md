# S15 — C15 real native full preview refresh lifecycle

From original `docs/tasks/C15.md`: main `Làm mới` must destroy/rebuild the DWM preview list, not repaint text. Current adaptation preserves C09 user column choice and C17 manual HWND ordering.

```text
User clicks "Làm mới" in selected, authorized Start
   -> validate selected Start active + widget visible
   -> read ONE already-existing immutable S09 WindowSnapshot
   -> cancel old 60ms geometry callback
   -> DwmUnregisterThumbnail for all old DWM thumbnail resources
   -> DestroyWindow for old ThlDwmThumbDst overlay HWNDs
   -> destroy all old Tk tile frames
   -> if invalid/empty: error / original no-game text, no stale preview
   -> if valid: restore surviving per-HWND manual preview order
               preserve "Cột:" selected 1x...5x
               create tile widgets at chosen grid positions
               register new DWM thumbnail overlays at 60ms debounce
               verify real HWND/PID before registration, re-check on maintenance

S09 producer ~3s, S09 Tk list poll 2s, S13 maintenance 800/2000ms:
   UNCHANGED; manual refresh never calls EnumWindows or memory scan.
```

The Windows-native test actually invokes the Tk button with 4 test-owned HWNDs; three complete refreshes each free 4 native resources before registering 4 new thumbnails. Native DWM API lifetime tracing confirms unregister-before-re-register, resource balance and no stale overlay. Test-owned Windows are NOT actual game accounts. Win32 may reuse numerical destination HWND values after closing, so handle *lifetimes* and `IsWindow` state are the ground truth, not numerical inequality.

CI **SUCCESS** [run 37883868392](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37883868392): **142/142 S01–S15 unit tests PASS** + `PASS_NATIVE_S15_MANUAL_FULL_DWM_REFRESH_AND_REVOCATION`. Initial CI failure [37883811777](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37883811777) was limited to Windows cp1252 console output of Vietnamese, fixed in test telemetry while UTF-8 JSON preserved.

**Explicit unknowns**: original Tk callback binding expression, whether clicking manual refresh triggers fresh worker/game-memory scan, detached preview, original 3.0s cache freshness predicate, game pixel parity, token server and production EXE. No further modules rewritten.
