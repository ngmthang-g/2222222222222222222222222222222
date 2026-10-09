# S19 C19 — native client geometry and safe ordered input MODEL

## Evidence from recovered original
C19: selected C05 HWND master is source. `WindowFromPoint`, `GetAncestor`, `ScreenToClient`, and `GetClientRect` support screen-to-master CLIENT coordinates and proportional slave size mapping. Input worker serializes queue `_do_down` / `_do_up` so press and release order is preserved. Re-block keepalive 1.5 seconds applies to C19 input sync only, not C18 layout. Watchdog unlocks stale slave lock after ~10 seconds; master change stops input synchronization and unlocks all slaves.

## Implemented narrow S19 model

```text
C05 master identity (HWND,PID) + immutable S09 cached source set
      + independently verified positive account limit (caller responsibility)
      ↓ validate source rows, identity, master membership (no native sends)
real read-only GetClientRect for current test-owned source HWNDs
      ↓ check HWND/PID before and after
ClientSize(master), ClientSize(slaves)
      ↓ master-client point, original scaling proven
S19 LOCAL floor/clamp proportional scaling (original rounding UNKNOWN)
      ↓ enqueue ordered MouseEvents (button left/right/middle; down/up)
FIFO sequence down-slave-A → down-slave-B → up-slave-A → up-slave-B
      ↓ explicit test-owned sink + live identity + permission callback
only test-owned Tk event_generate (no native Win32 input message)
      ↓ revoke/PID reuse/master switch → cancel queue and logical press flags
watchdog at 10s: model press flags/queue cleared (NOT DLL unlock)
```

`InputSyncModel` has no default sender, hook/listener or native lock. It never generates any Win32 input messages, uses no fabricated keyboard WM_MY_SYNC_KEY or undefined payloads. S19 **does not add a fake button** to Start. Actual native Windows test reads client dimensions from three real test-created Tk HWNDs (280×190, 410×260, 360×310) and verifies real Tk callbacks on the 2 test slave windows at scaled coords, FIFO order and revocation/PID guards.

S19 [GitHub Actions run 37889666893](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37889666893): 239/239 unit PASS and native `PASS_NATIVE_S19_WIN32_CLIENTRECT_TEST_OWNED_FIFO_REVOKE`. [Stage S run 37889666867](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37889666867) SUCCESS.

## Limits
Exact original rounding, actual mouse listener, key payload bit-packing, DLL hook and forced slave-lock release, UI toggle/mode auto-activation, real game/account session and final exe remain NOT_RUN, UNKNOWN or UNIMPLEMENTED. No Proxy.
