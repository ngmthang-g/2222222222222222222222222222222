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

## C03 — cơ chế preview HWND

```text
Xem trước cửa sổ game
↓
TLMStartTab.refresh_window_preview_list
↓
_is_hung(src_hwnd)
↓
_create_dwm_dst_hwnd + DwmRegisterThumbnail
↓
source HWND: game src_hwnd
destination HWND: ThlDwmThumbDst overlay
↓
destination positioned from Tk preview winfo_rootx/y/width/height
↓
DwmUpdateThumbnailProperties
↓
live DWM thumbnail over preview frame
```

Destination overlay:
- `WS_EX_LAYERED | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE`
- `WS_POPUP | WS_VISIBLE`
- owner derives from Tk toplevel `winfo_id()`
- click-target map associates destination HWND → source game HWND

DWM properties present:
- RECTDESTINATION
- OPACITY (255 static constant)
- VISIBLE
- SOURCECLIENTAREAONLY

Click/activation:
- destination WndProc recognizes WM_LBUTTONDOWN/UP/DBLCLK
- validates source HWND
- minimized source has SW_RESTORE path
- otherwise SW_SHOW path
- SetForegroundWindow(source)

Hung source:
- checked with nonblocking `IsHungAppWindow`
- preview error path shows `Cửa sổ không phản hồi`

Teardown:
- `DwmUnregisterThumbnail`
- remove destination click mapping
- `DestroyWindow(dst_hwnd)`
- destroy Tk frame

Screenshot reference:
- 3 visible preview items
- each outer border 205×137
- black visible preview surface 197×110

Explicit unknown:
- exact source-level boolean assignments to `fVisible` and `fSourceClientAreaOnly`.

---

## C04 — update preview và FPS

```text
Preview live image
↓
Windows DWM compositor
↓
source game HWND → registered DWM thumbnail → destination overlay HWND
↓
FPS/image composition is not driven by TLM's 800/2000ms timer
↓
kết quả: live thumbnail remains compositor-driven
```

```text
Preview maintenance
↓
TLMStartTab._update_window_previews_loop
↓
Tk after / _schedule_preview_loop
↓
HWND affected: current preview source/destination set
↓
timing:
  - threshold constant 6
  - low-count branch 800ms
  - high-count branch 2000ms
↓
mỗi cycle:
  - reposition destination overlays
  - compare alive_hwnds / valid_items
  - conditional list rebuild via need_refresh
  - refresh cached RoleName/HP
  - update slot combobox HWND mapping
  - reschedule while _refresh_active
```

Other clocks:
- Start UI list poll: 2000ms
- background EnumWindows + character info: ~3s
- heavy memory: ~8s
- resize reposition debounce: 60ms

Detached:
- `_detached_update_loop`
- independent of Start tab visibility
- rebuild when game-window list changes
- exact detached timer cadence remains UNKNOWN

Explicit unknown:
- boundary operator at threshold 6
- exact need_refresh source Boolean formula
- exact use/comparator of cache_ts float 3.0
- detached loop interval
- DWM compositor FPS

---

## C05 — cửa sổ chính / master HWND

```text
Danh sách game HWND
↓
TLMStartTab._update_master_combobox
↓
character-info cache → label Radiobutton
+ fallback "Cửa sổ ..."
↓
_hwnd_by_name[label] → HWND
↓
user chọn radio / automatic init path
↓
hwnd_master
↓
HWND affected: master = source/priority window; mọi HWND khác = follower/slave
↓
layout:
  - stack/offset: master index 0
  - grid: master top-left/index 0
  - auto tile: master first
↓
sync:
  - mouse/keyboard events originate from master
  - coordinates transformed toward slave client sizes
↓
kết quả: một HWND được dùng làm cửa sổ chính runtime
```

Manual master change:
- log `[MASTER] Đã chọn cửa sổ chính: ... (hwnd=...)`
- if input sync is active, original automatically stops it and unlocks all slaves
- user must enable input sync again after selecting a new master

Candidate UI:
- dynamic Radiobuttons
- rebuild only when HWND list changes
- `_master_hwnd_cache`, `_master_var`, `_hwnd_by_name`
- labels use character-info cache with a `Cửa sổ ...` fallback

Runtime/persistence:
- Start settings block persists grid/detached settings, not a master HWND key
- `_master_initial_selected` and `_auto_master_and_sync` prove automatic initialization exists
- exact automatic selection rule remains UNKNOWN
- exact stale-master replacement/clear rule remains UNKNOWN

Safety:
- watchdog unlocks slave input blocks after master close/change/exit.

---

## C06 — common multi-window layout engine

```text
worker-cached game HWNDs
↓
master-aware order
├─ master → index 0 / top-left
└─ remaining HWNDs → sequential after master
↓
_arrange_grid(windows, cols, rows)
├─ GetSystemMetrics
├─ exact literals 450 and 40
├─ min
├─ ww / wh
├─ exact arithmetic expression = UNKNOWN
└─ new_slots / _grid_slots
↓
SetWindowPos-family placement/resize
↓
continuous maintenance through _layout_worker while layout sync is active
```

Grid configuration:
- persisted keys: `grid_cols`, `grid_rows`
- recovered defaults: **3 columns × 4 rows**
- current Xếp-lưới screenshot independently shows `Cột:3`, `Hàng:4`

Move-only primitive:
- `_move_windows_offset(pos_fn)`
- exact doc says position comes from `pos_fn(index)`
- **keeps current size**
- master always index 0
- `SetWindowPos` / `SWP_NOSIZE` family recovered
- no `MoveWindow` literal/import recovered from the inner EXE

Resize primitive:
- `resize_window`
- `GetWindowPlacement` → `ShowWindow(SW_SHOWNORMAL)` when needed → `SetWindowPos`
- recovered flags include `SWP_NOMOVE | SWP_NOZORDER | SWP_NOACTIVATE`

Shared stack position rules recovered:
- tight: all → `(0,0)`
- diagonal: +50 x / +50 y per index
- horizontal: +50 x
- vertical: +50 y

Limit handling:
- runtime source: `new_version_info.max_windows`
- fallback literal: **999**
- process count comes from worker cache
- over limit cannot enable sync
- `_auto_stop_sync` disables both layout and input sync

Explicit unknowns preserved:
- exact grid x/y/w/h arithmetic involving screen metrics, 450, 40, cols/rows
- exact +/- row/column bounds
- exact max-window comparator operator
- exact layout-worker cadence

C07-only evidence (1366×768 Auto reset, RoleName auto-tile, 1-second loop) was observed but intentionally not promoted to C06/C07 completion.

---

## C07 — Auto

mode_var = auto
→ _on_mode_change
→ layout sync OFF + input sync OFF
→ get game HWNDs
→ reset each to (0,0) 1366×768
→ _auto_tile_loop
→ every 1 second while auto_tile_active=True:
   _auto_tile_windows → RoleName sort → master first → tile placement

Verified:
- Auto is the default visible Start mode.
- Auto transition reset is exactly (0,0) 1366×768.
- Auto tiling is recurrent; documented cadence is 1 second.
- sort key uses character-info RoleName.
- master is always first.
- Auto tile toggle references the max-window limit subsystem.
- Auto/manual turns off layout and input synchronization.
- switching to sync/Xếp-lưới stops active Train, Trừng ác and Tàng bảo đồ.

Explicit unknown: exact final tile arithmetic, exact auto_tile_active assignment timing, exact compiled call edge to the common arranger, exact max-window comparator.

---

## C08 — Xếp lưới

Xếp lưới / internal sync
→ _on_mode_change
→ stop conflicting Train / Trừng ác / Tàng bảo đồ
→ auto-enable layout sync + input sync

Layout:
_toggle_layout → _sync_windows_loop / _layout_worker → worker-cached HWNDs → master index 0 → _arrange_grid(current cols/rows)

Input:
_toggle_input → master input source → slave targets → _sync_keepalive every 1.5 seconds

Grid:
-/+ column and row handlers → _on_grid_change → update Cột/Hàng labels + persist settings.
Defaults: 3 columns × 4 rows.

Limit:
new_version_info.max_windows; over limit blocks sync and _auto_stop_sync disables both layout and input sync.

Explicit unknown: exact +/- bounds, exact layout-worker cadence, exact grid arithmetic, exact limit comparator.

---

## C09 — preview columns 1x–5x

Cột: 1x / 2x / 3x / 4x / 5x
→ preview_grid_var (default 2x)
→ _set_manual_preview_grid
→ _get_preview_columns
→ numeric preview_cols
→ refresh_window_preview_list
→ preview_rows + row/column placement
→ live DWM thumbnail frames

Current measured 2x state:
- 3 preview items
- 2 columns
- outer frame 205×137
- visible thumbnail surface 197×110.

Order control is separate: ◀/▶ updates _preview_order by HWND and refresh preserves that order.

Detached preview uses separate detached_grid state/Combobox and persists it; no main preview_grid config key was recovered.

Explicit unknown: exact preview_rows arithmetic and exact manual-flag assignment timing. Pixel geometry for 1x/3x/4x/5x remains runtime-unverified.

---

## C10 — Xếp gọn

Xếp gọn
→ _stack_tight_cmd
→ _move_windows_offset(pos_fn)
→ master index 0 + remaining game HWNDs
→ every pos_fn(index) = (0,0)
→ move only; preserve current size
→ _reset_hidden_state
→ [Xếp] Đã xếp N cửa sổ

Verified target: all windows stacked at top-left (0,0).
Explicit unknown: exact priority if the Auto 1-second tile loop is already running.

---

## C11 — Xếp chéo

Xếp chéo
→ _stack_diagonal_cmd
→ _move_windows_offset(pos_fn)
→ master index 0
→ index i position = (50*i, 50*i)
→ preserve current size
→ _reset_hidden_state
→ [Xếp] Đã xếp N cửa sổ

Exact original doc confirms origin (0,0) and +50/+50 per window.
Explicit unknown: later interaction if Auto tiling is already active.

---
