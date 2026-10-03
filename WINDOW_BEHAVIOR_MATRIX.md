# WINDOW_BEHAVIOR_MATRIX — TLMTool 2.1.2

Authoritative Stage-C matrix. Add one verified task at a time; do not fill future rows from guesses.

## C01 — discovery / refresh source

```text
Tự động quét/cập nhật cửa sổ
↓
TLMStartTab._auto_refresh / refresh / _refresh_cache
↓
background _preview_worker_loop → EnumWindows
↓
IsWindowVisible
→ SendMessageTimeoutW(title, 150ms)
→ GetClassName
→ GetWindowThreadProcessId
→ psutil.Process
↓
HWND affected: qualifying visible top-level game HWNDs
↓
tọa độ/kích thước: N/A — discovery only
↓
kết quả: cache danh sách (hwnd, title) cho Start/master/preview
```

Cadence:
- UI list poll: 2 s while Start tab is active
- background EnumWindows + character info: ~3 s
- memory info: ~8 s
- preview-display loop: 800/2000 ms depending on account count

Verified candidate evidence:
- process literal: `thần long mobile.exe`
- class: `UnityWndClass`
- title predicate exists via `WINDOW_NAME` / `_title_matches_game`

Explicit unknown:
- exact final AND/OR grouping among process/class/title predicates.

### Strict requested-title resolver

```text
operation with explicit window_title
↓
coordinate_utils.find_target_window
↓
FindWindow(exact title)
↓
exact matching HWND only
↓
N/A
↓
no match => (0, ""); never take first/default HWND
```

---

## C02
TODO — mapping HWND ↔ nhân vật.
