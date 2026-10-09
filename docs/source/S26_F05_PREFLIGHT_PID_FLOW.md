# S26 — Genuine read-only F05 preflight and PID-bound HWND

```text
VerifiedClaims from future signed Info service -> PermissionSnapshot
    [unverified or blocked?] -> deny
    [has login_tab right?] -> deny if absent
    [real external current running windows known?] -> deny if unknown
    [running_windows + 1 <= snapshot.max_windows?] -> deny if false
    [F04 saved canonical game_dir/Thần Long  Mobile.exe still file?] -> deny if false
    -> LaunchPreflight(allowed=True, reason="PREFLIGHT_ONLY_NOT_LAUNCHED")
       NEVER translates directly into real game opened.

future proven launcher returns real PID
  -> find_main_window_by_pid(pid, existing S08 NativeWin32Backend)
      -> EnumWindows
      -> IsWindow / IsWindowVisible / GetWindowThreadProcessId == pid
      -> GetClassNameW
      -> SendMessageTimeoutW title (<=150ms)
      -> recheck HWND+PID and visibility
      -> sort: UnityWndClass > title contains Thần Long > other PID-owned visible
      -> recheck selected HWND again before return
      -> hwnd or None; NO process creation, no unsafe input
```

F05 original finder preference is proven; exact ordering **UnityWndClass over title** in this implementation is local and not source-parity proven. The original 25-second wait, serialized one-window launch, stabilization and suspend/inject DLL are deferred. No default running=0; extra=1 is enforced and path must exist. Caller-provided snapshots do not prove a real signed service exists.

[Windows S26 SUCCESS, 348 tests, genuine test-owned Tk HWND](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37901273260) • [Native evidence 11602416816](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37901273260/artifacts/11602416816).
