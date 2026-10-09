# S13 — Tk adaptive preview maintenance is not DWM FPS

Original evidence: `docs/tasks/C04.md`, C03 and E03.

```text
S09 native Win32 producer ~3 seconds (background)
       ↓ immutable WindowSnapshot(HWND, PID, title, valid)
       ├── S09 selected Start list poll: 2 seconds (Tk root.after)
       └── S13 selected Start preview housekeeping (Tk root.after)
            ├─ 0–5 current cached windows: 800ms
            ├─ 6+ current cached windows: 2000ms
            │  NOTE exact original six-window boundary unknown
            ├─ only update Tk list when cached state changed
            ├─ compare HWND+PID and test current native HWND validity
            ├─ reposition/revalidate actual DWM overlays
            └─ cancel when Start hidden/revoked/shutdown
Tk <Configure>   └─ C04 originally recovered 60ms debounce
Windows DWM      └─ live compositor, unrelated to "800ms FPS"
```

No process memory reads, BitBlt screenshot loop, fake characters/HP, API mouse clicking or Proxy. Runtime authorization comes from E03 existing shell gate. If invalid cache is returned, source items and DWM handles are cleared. Revalidation of source HWNDs does not fabricate a game account.

Evidence: Windows Python 3.10 run [37880150984](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37880150984) proves 112/112 tests PASS, native test-owned actual Win32 HWNDs 1→800ms, 6→2000ms, cache invalidation/recovery, HWND close, and revoked timer cancellation. Other Windows S10/S11/S12 workflows also pass on the implementation commit.

Unknown original details: exact comparator at 6; original 3-second cache-age Boolean; original role/HP metadata and its refresh; detached preview cadence. This is a bounded functional adaptation, not complete source parity.
