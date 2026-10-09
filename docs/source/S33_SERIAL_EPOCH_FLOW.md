# S33 — Offline per-serial connection-epoch provenance guard

```text
existing offline S31 captured 'adb devices' rows
  + S32 per-serial HintTimes (aid/hwid/IP/guest game PID field age)
  + OPTIONAL caller-observed reboot serials (unverified by S33)
     |
     -> advance_serial_epochs(previous_epoch, current_S32, observed_reboots)
        -> validate capture, S32 hint timestamps, chronology, marker targets
        -> maintain immutable per-serial state + generation + online boundary
        -> first observed online: boundary = captured_at
        -> online -> offline / unauthorized / ABSENT: remove live epoch
        -> offline / absent -> online: generation++ and NEW boundary
        -> explicit observed reboot while online: generation++ / boundary
        -> missing/corrupt/too-long history: fail closed / re-baseline
     |
     -> snapshot.assess(serial, field, now)
        S32 already fresh? AND hint observed_at STRICTLY AFTER epoch boundary?
        -> FRESH_HINT_DIAGNOSTIC_ONLY or rejection cause
     -> snapshot.unique_serial_for(field, value, now)
        ALL online peers individually fresh and post-epoch?
        unique value? -> diagnostic serial (never a command target)
     |
     -> emulator_account_count = None
     -> combined_running_count = None
     -> authoritative_account_total = False
     -> S26 check_open_game_preflight(..., None) -> DENIED
```

Original P02/P05 support mutable ADB serials, Android ID/HWID clone collisions and the need for correct active serial; original exact epoch invalidation algorithm is UNKNOWN. S33 uses local fail-closed safety boundaries. No real ADB daemon started and no actual LDPlayer game tested.

[Windows S33 497/497 PASS](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37911372037) · [Native evidence artifact](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37911372037/artifacts/11606572419).
