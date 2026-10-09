# S30 — Non-authoritative E04 game process / HWND provenance

```text
Original E04 entitlement count:
  running Windows game EXE processes
  + Windows/Android emulator-account count (exact mapping UNKNOWN)
  -> authoritative combined count requires separate ORIGINAL contract
     NOT AVAILABLE, NEVER GUESSED.

S30 diagnostic-only independent observation:
  monotonic start
  -> S29 Toolhelp32 snapshot #1 exact "Thần Long  Mobile.exe" PID set
  -> S08 Win32 EnumWindows game process/HWND/title guard
  -> S29 Toolhelp32 snapshot #2 same image PID set
  -> monotonic complete
  -> if count/PID churn, HWND PID not in process list or scan exception:
       INCOMPLETE_OR_CHANGING / UNKNOWN process count
     else:
       OBSERVATION_CONSISTENT (diagnostic ONLY)
       diagnostic_freshness(now, max_age=2.0s, max_span=2.0s)
         -> FRESH_DIAGNOSTIC_ONLY / STALE_DIAGNOSTIC / SPAN_TOO_WIDE
            NEVER turns into permission or combined count.

RunningSnapshotProvenance:
  game_process_count = int | None   # diagnostic only
  visible_game_hwnd_count = int | None
  emulator_count = None             # exact Windows LD identity unproven
  combined_running_count = None    # cannot calculate safely
  is_authoritative_account_total = False
```

Audited P01/P02/P05/P06: original Android ADB serial, android_id and game guest PID are not a verified Windows emulator HOST executable/account-count rule. Do not equate Android guest PID with Windows host PID, or multiply windows per emulator as accounts. The 2-second S30 freshness thresholds are a **local safety choice**, not original E04 proven source.

Evidence: [S30 Windows 428/428 tests PASS](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37907996507) · [native diagnostic artifact](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37907996507/artifacts/11605510692).
