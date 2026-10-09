# S32 — Hint freshness is NOT captured-ADB-list freshness

```text
P02/P05 audited original:
  ADB serial = current transport, mutable on reboot
  aid / hwid = sometimes cached, may collide across clones
  guest IPv4 = only diagnostic reverse mapping if unique
  guest game PID != Windows host emulator/game process PID

S31 captured AdbIdentityEvidence (text already collected)
   + per-serial HintTimes
       android_id_at, hwid_at, guest_ipv4_at, guest_game_pid_at
       absent timestamp => UNKNOWN (never silently use captured_at)
    -> S32 with_hint_times(): immutable snapshot; invalid timestamps rejected
    -> assess(serial, field, now):
        transport captured fresh?
        serial unique and ONLINE?
        field value present?
        exact field timestamp present & not older than LOCAL 30s?
        -> FRESH_HINT_DIAGNOSTIC_ONLY | reason for refusal
    -> unique_serial_for(field,value,now)
        ONLY when EVERY online peer's same field has fresh known value
        -> unique candidate serial as DIAGNOSTIC, not command target
    -> compare_adb_lifecycle(before,after,now)
        online/offline, appear/disappear
        aid moved serial (both snapshots fresh, unique) =>
          POSSIBLE_ONLY_NOT_VERIFIED, never auto rebind

E04 account total remains UNKNOWN:
  emulator_account_count=None
  combined_running_count=None
  is_authoritative_account_total=False
  S26 launch preflight => RUNNING_WINDOW_COUNT_UNKNOWN (denied)
```

The 30-second S32 hint TTL is a local **diagnostic** limit, **not** the original P02 Android ID cache (~5 minutes), not a cryptographic guarantee or proven original rule. S32 has **no live ADB/LDPlayer execution**.

[Windows success 475/475](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37910397034) · [native fixture evidence](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37910397034/artifacts/11606311244).
