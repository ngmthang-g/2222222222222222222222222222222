# S10 — Original-backed Start HWND/PID/title diagnostic view

## Source contract
Original C01/C02: Start UI must consume a background cache of top-level **game** windows and guard HWND/PID reuse. C03 describes DWM live preview; C05 master radios; C06/C08 grid/controls; E03 only authorized tabs are visible and only the selected tab refreshes. This task intentionally implements **only** the first, real, passive Start list required before those later controls.

## Thread and permission boundaries
```text
Windows EnumWindows worker (S08, S09 ~3s)
  → immutable WindowSnapshot(revision, HWND, PID, title, valid, error)
  → TkStartCachePoller (S09, root.after 2000ms)
  → TLMStartTab._on_cache_event (Tk thread only)
  → ttk.Treeview rows: title / PID / HWND
```

TabLifecycle is the source of authorization-gated construction and refresh; S10 never enables Start by itself. A test-only PermissionGuard verifier is used to exercise the gate on actual Windows; it is not a server implementation and is not wired into `src/TLMTool.py`.

## Lifecycle
- Initially: Info-only, no Start construction/worker.
- Verified tab key (test harness): Start becomes visible; switching to it creates one view, enables worker, shows pending.
- First valid scan (including 0 games): pending becomes LIVE/EMPTY, rows exactly the cache.
- Failed enumeration: ERROR and no old rows.
- Losing Start selection or permission: stop poller, clear HWND/PID UI, revoke cache; late Tk/worker results are fenced by S09 generations.
- Destroy: release/stop the same services idempotently.

## Visual and behavioral limits
The pane uses a truthful view rather than constructing fake original buttons or static black preview cells. It does **not** yet recreate the measured original 205x137 preview tiles or 197x110 DWM regions, 3×4 grid, master radios, HP/RoleName, click activation, Ẩn hết/Đóng xem, or any game command. Screenshot parity remains NOT_RUN. Native test-owned Tk window is **not** accepted as a game. Production EXE is still NOT_BUILT.

## Evidence
Windows 3.10 GitHub Actions [37874342004](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37874342004): compileall PASS, 77 unit PASS, native `PASS_NATIVE_READONLY_START_AUTH_AND_POLLING`; cached scan yielded EMPTY because game absent, background worker true, start permission revoke returned to Info and cleared visible handles.
