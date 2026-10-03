# C01 — Window discovery flow

```text
TLMStartTab becomes active
↓
_auto_refresh UI poll every 2 s
↓
_refresh_cache reads background worker cache
↓
_preview_worker_loop
↓
EnumWindows (~3 s discovery/cache cadence)
↓
top-level HWND callback
↓
IsWindowVisible
↓
_get_window_title_safe
  └─ SendMessageTimeoutW, 150 ms timeout
↓
_get_window_info
  ├─ GetClassName
  ├─ GetWindowThreadProcessId
  └─ psutil.Process → process name
↓
evaluate:
  - normalized game-process predicate
  - UnityWndClass predicate
  - title/WINDOW_NAME predicate
↓
append qualifying (hwnd, title)
↓
cache
↓
Start UI / master-selection / preview consumers
```

## Important distinctions

- UI polling is exactly **2 s**.
- Background EnumWindows + character-info worker is approximately **3 s**.
- Heavier memory reads are approximately **8 s**.
- Preview display delay is **800 ms / 2000 ms** depending on account count.
- Exact class/title Boolean grouping is intentionally left UNKNOWN until stronger evidence exists.

## Specific title resolver

For an already-known requested title, `find_target_window` is fail-stop:
- exact `FindWindow` title only;
- no exact match → `(0, "")`;
- no “first HWND” fallback;
- no default-title scan.
