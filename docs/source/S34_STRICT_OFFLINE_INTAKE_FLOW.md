# S34 — One ordered offline identity intake

```text
CapturedAdbFrame (text, monotonic timestamp, optional externally supplied
  android_id/hwid/guest_ipv4/guest_pid, independent hint times, reboot markers)
    |
    v
OfflineAdbIntake.ingest
    S31: inspect_captured_adb_devices
      -> must be PARSED: header, states, duplicate serial, provenance
    S32: with_hint_times
      -> per-field source timestamps present, valid, not future/orphan
    S33: advance_serial_epochs
      -> epoch boundary after first observed ONLINE
      -> observed offline/disappeared/reboot invalidates previous hints
      -> changing/replayed/nonmonotonic timestamps rejected
    |
    +-- any error/lost capture -> REJECTED, CLEAR prior epoch
    |
    v
IntakeReceipt (immutable status/events only; no low-level wrappers)
    |
OfflineAdbIntake.lookup
    -> STRICT S33 unique_serial_for with fresh S31+S32+S33 evidence only
    -> UNIQUE_DIAGNOSTIC_ONLY (may_control_device=False) | refusal
    -> emulator_account_count=None
    -> combined_running_count=None
    -> is_authoritative_account_total=False
```

No ADB/Frida process created; even fresh caller-provided observations are not authenticated. The façade promotes correct diagnostic usage, not code isolation or product-runtime parity. Original P02/P05 serial/aid collision facts are preserved. No Proxy.

[Windows S34 523/523 PASS](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37913166723) · [native evidence artifact 11607239078](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37913166723/artifacts/11607239078).
