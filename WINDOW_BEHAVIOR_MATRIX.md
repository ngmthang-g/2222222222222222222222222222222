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

## C02 — mapping HWND ↔ nhân vật

```text
HWND game
↓
_get_pid_from_hwnd(HWND)
↓
GetWindowThreadProcessId / PID snapshot
↓
bind_window_identity(HWND, PID)
↓
get_character_info(HWND)
↓
memory_reader.Reader keyed by PID
↓
RoleName + HP + Level + MapID + position
↓
row key: HWND; logical label/config key: sanitized RoleName
↓
kết quả: đúng nhân vật được gắn với đúng generation của HWND
```

Identity lifecycle:
- same HWND + same PID → update existing row/info
- same numeric HWND + different PID → HWND reused → remove old row and recreate
- closed HWND → remove stale row
- reconnect → invalidate Reader(PID) cache and resolve fresh memory pointers
- persistent settings use character name because HWND changes after reopening the game

Action guard:
- stored HWND→PID identity prevents a stale row from clicking a new process that inherited the old HWND value.

Start preview:
- src HWND + worker character-info cache → RoleName/HP/Level/Map labels.

Explicit unknown:
- exact formatting of temporary `Window ...` placeholder suffix.

---

## C03
TODO — cơ chế preview HWND.
