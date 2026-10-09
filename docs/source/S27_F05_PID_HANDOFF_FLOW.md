# S27 — F05 25s cancellable PID-owned HWND readiness handoff

```text
External real PID from future verified actual F05 spawn operation
   -> SerializedPidWindowHandoff.wait(pid, cancel, timeout<=25s)
      -> lock-acquire with bounded time/cancel (S27 local)
      -> wait_for_pid_window(...)
         -> S26 find_main_window_by_pid(pid)
            -> S08 NativeWin32Backend / EnumWindows
            -> PID/visible/class/title matching and reuse rechecks
         -> check cancellation and 25s monotonic deadline
         -> revalidate HWND visibility + PID at final handoff
         -> FOUND(hwnd) | TIMEOUT | CANCELLED | INVALID_PID | failure
      -> always release serialization lock

no hwnd -> next poll on bounded wait, NOT Tk thread
post-HWND stabilization seconds -> UNKNOWN, NOT IMPLEMENTED
actual spawn suspended + resource injection + resume -> NOT IMPLEMENTED
```

### Proven original vs local behavior
- **Original F05 evidence:** 25s no-HWND limit, PID-bound main-window discovery, serialized launch path, preference for UnityWndClass/title containing Thần Long, post-HWND stability phase of unknown length.
- **S27 implementation choices:** 100ms polling, 50ms cancellable lock-acquire retry, typed result codes and monitor clock, error reporting, exact lock scope. No claim that these are identical to original hidden Python.
- **Real Windows test:** delayed Tk title-matching HWND created on Tk main thread after 250ms; read-only Win32 worker sees no HWND then finds correct PID; missing, wrong-PID, cancel paths rejected. F05 real game **NOT RUN**.

[Successful S27 Windows CI: 368 tests + all native regressions](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37901945848) · [Test evidence archive](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37901945848/artifacts/11602743621).
