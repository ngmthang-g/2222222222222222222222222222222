# S16 — Verified C16 WM_CLOSE with safe identity and selected-tab gates

```text
Original C16 Start: [Đóng hết] native ttk.Button
 -> E03 authorization: only selected visible Start may act
 -> read ONE existing S09 immutable cache (no unscheduled EnumWindows from UI)
 -> fail closed on invalid, empty, duplicated or non-game cache rows
 -> live native EnumWindows membership (top-level HWND only)
 -> validate IsWindow / visible / PID snapshot
 -> validate current EXE basename = "thần long mobile.exe"
    AND class = UnityWndClass OR exact "Thần Long  Mobile" title
 -> recheck IsWindow + PID immediately before message post
 -> PostMessageW(hwnd, WM_CLOSE=0x0010, 0, 0)
 -> report "đã gửi" (message posted); NOT proof client already exited
 -> S09 cache / S13 maintenance eventually removes closed previews
```

**No** `TerminateProcess`, taskkill, Win32 injection, game memory, fake auth grant or Proxy. Original includes UnityCrashHandler64 cleanup separately but S16 purposely DOES NOT implement it. Original confirmation and immediate refresh after close are not visible in binary source-level evidence and remain UNKNOWN. Process/class/title predicate is the previously documented conservative S08 reconstruction, not exact recovered original source.

The Native Windows smoke sends real `PostMessageW` to **three test-created HWNDs only** using a test-only identity shim and an allowlist-asserting native poster. Win32 actually destroys those three Tk native source windows and leaves the unrelated HWND intact. Same numerical HWND reuse + PID checks and revoke/Info fallback are covered. [SUCCESS Windows GitHub Actions run 37884623539](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37884623539): 163/163 Stage S unit tests and genuine native test-owned Windows WM_CLOSE PASS. Production was NOT tested against real Thần Long game windows or entitlement server.
