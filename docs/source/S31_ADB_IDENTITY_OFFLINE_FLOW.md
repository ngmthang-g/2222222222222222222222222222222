# S31 — ADB device identity evidence is NOT a Windows emulator count

```text
independently CAPTURED 'adb devices' output (future provider, not present)
 + OPTIONAL independently observed per-serial aid / hwid / guest IPv4 / guest game PID
   |
   -> offline inspect_captured_adb_devices(...)
      -> require List of devices attached header
      -> preserve each current ADB transport state (device/offline/unauthorized...)
      -> detect duplicate transport serials
      -> detect shared aid/hwid/guest IP among connected rows
      -> unique_serial_for('guest_ipv4'/'android_id'/'hwid')
         only with a fresh local capture + single match;
         collisions/old/offline/ambiguous => None
      -> possible serial rebind from same unique aid across two captures:
         POSSIBLE_ONLY_NOT_VERIFIED (clone/reboot ambiguity)
      -> emulator_account_count=None
         combined_running_count=None
         is_authoritative_account_total=False
           |
           -> S26 check_open_game_preflight ... running_windows=None
              = RUNNING_WINDOW_COUNT_UNKNOWN (denied)
```

P02 original: ADB serial mutable; Android ID cache ~5min, clone duplicate aid/hwid; guest IPv4 useful when unique. P05 original UI rows by aid, commands/coords by serial. Original E04 combined game+emulator licensing arithmetic NOT recovered. S31 30-second transport-capture TTL is a **local diagnostic convention**, NOT original verified cadence or signed freshness.

Native Windows evidence only means Python used genuine Toolhelp PID; **captured ADB text was a test-owned fixture**, with no real LDPlayer/ADB/Frida execution.

[GitHub Windows 450/450 tests PASS](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37909199630) · [Windows evidence 11606181801](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37909199630/artifacts/11606181801).
