# M01 — Rao authority / UI surface audit

## Authority

M01 starts Phase M from the exact frozen original again before using the supplied screenshot.

Revalidated specimen:

- archive: `TLMTool_2.1.2(8).zip`
- SHA-256: `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`
- size: **93,715,901 bytes**
- ZIP entries: **1,050**
- CRC: clean
- inner authority: `TLMTool_2.1.2/TLMTool.dist/TLMTool.exe`
- inner SHA-256: `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`
- inner size: **47,450,112 bytes**.

The active Rao serialized module header is:

- marker: `.rao_tab` at `0x2bd7850`
- size field: `0x2dfe` = **11,774 bytes**
- constant-count field: `0x0246` = **582**
- source filename: `rao_tab.py`
- exact module marker: `<module rao_tab>` at `0x2bd9f72`
- active class: `RaoTab`
- direct top-level class-method inventory: **40 methods**, including `__init__`.

The full method list is frozen separately in `M01_HANDLER_INVENTORY.tsv`.

## Main application integration

`TLMMainApp.create_tabs` contains the current visible tab pair:

`Rao -> rao_tab`.

The tab is created on the shell's hidden/permission-controlled surface, and the main application contains:

- `RaoTab` class reference;
- `_set_rao_tab_visible`;
- exact documentation:
  **Show/hide Rao tab — chỉ hiện khi có quyền (như donvang_tab).**

The same main-shell block says feature tabs are built once when they do not yet have content.

Therefore Rao is a current integrated feature, not a dormant/dead module.

The supplied screenshot visibly has **Rao** present and active, so the capture was in an allowed/visible state. The exact server/license-plan permission value that enabled it is not recovered and is not guessed.

## No current Rao quick control on StartTab

This requires a distinction.

The Rao module carries a `start_tab` dependency because it reuses shared helpers such as:

- `get_windows`
- `get_character_info`
- settings lock/read/write helpers.

That does **not** prove a Rao button exists on StartTab.

The exact serialized `.start_tab` block is:

- offset `0x2bf8bf7`
- size **37,643 bytes**
- count **1,536**.

A case-insensitive scan of that exact serialized block finds **0 `Rao/rao` strings**.

No current Rao-specific StartTab button/action binding was recovered. The user's StartTab screenshot also contains no Rao quick action.

This negative finding is current-surface evidence only; it does not assert that no hidden/plugin path could ever call Rao.

## Dedicated Rao tab — exact visible configuration surface

Static EXE labels:

### Cấu hình rao tự động

Columns:

- **Tên**
- **Nội dung rao**
- **Kênh**
- **Lặp (s)**
- **Xóa**

Action:

- **+ Thêm rao**

A Rao definition row contains:

- editable name;
- editable message content;
- readonly channel combobox;
- numeric interval entry;
- red delete control.

The module carries:

- `RAO_CHANNELS`
- `RAO_DEFAULT_CHANNEL`.

Visible channel labels serialized in the current build:

1. **Thế giới**
2. **Bang hội**
3. **Môn phái**
4. **Tổ đội**
5. **Liên minh**
6. **Quân đoàn**
7. **Lân cận**

`RAO_DEFAULT_CHANNEL` is statically serialized as **Thế giới**.

Exact channel IDs/packet semantics are deliberately deferred to M03.

The interval field owns a digits-only validation helper. Exact interval normalization, minimum/default and worker timing are deferred to M04.

## Rao definition row naming

The current module has:

- `_rao_names`
- `_next_rao_name`
- `_add_rao_row`
- `_remove_rao_row`.

Exact embedded documentation says automatic names are:

`Rao 1, Rao 2, ...`

using the **smallest unused positive number**.

Message persistence/schema details belong to M02.

## Account-list visible surface

Second group:

### Danh sách tài khoản

Headers:

- **Nhân vật**
- **Nội dung rao**

The static row builder additionally exposes, when accounts exist:

- character-name label;
- **4 Rao-selection combobox slots** per account;
- per-account **▶** play control;
- state label with stopped surface **Đã dừng**.

The user's Rao screenshot contains no account rows, so these widgets are established from EXE static evidence rather than inferred from the empty capture.

Account assignment semantics belong to M05.
Start/stop worker semantics belong to M06.

## Main bottom action

The dedicated Rao tab has one large bottom button:

**Bắt đầu**

The EXE binds that visible surface to `_start_all_accs` through a background-thread dispatch surface.

M01 only inventories this boundary. Exact start-all inclusion rules, slot startup, stop behavior and lifecycle belong to M06.

## Permission boundary

Rao has permission controls at both shell and row/action level.

Main shell:

- `_set_rao_tab_visible`
- Rao hidden when not permitted.

Inside RaoTab:

- `permission_guard.has_permission` with `rao_tab` is present in row-permission handling;
- exact documentation:
  **Disable row mới tạo khi không có quyền rao_tab.**
- `_check_perm` contains `has_permission_with_limit` with adjacent arguments `rao_tab` and `rao`.

M01 does not deep-audit the account-limit algorithm; it only freezes the permission boundary.

## Account refresh / current-window boundary

Rao has its own incremental account refresh surface.

Exact documentation:

**Tự động refresh danh sách acc mỗi 5 giây.**

Methods include:

- `_refresh_acc_lists`
- `_start_refresh`
- `_stop_refresh`
- `_schedule_refresh`
- `_add_or_update_row`
- `_remove_stale_accs`.

The tab starts refresh when selected and stops its refresh loop when left.

Window identity is guarded with:

- HWND/PID checks;
- `bind_window_identity`;
- `unbind_window_identity`;
- stale/reused HWND row removal.

Deep account assignment behavior remains M05.

## Persistence boundary

Current persistence section is:

`[Rao]`.

Recovered key-family boundaries:

- `rao_` — Rao definition rows;
- `acc_` — per-character selection data.

Shared settings surface:

- `_settings_lock`
- `read_settings`
- `write_settings`.

Current persistence handlers:

- `_save_config`
- `_load_config`
- `load_acc_config`
- `_save_on_destroy`
- `_on_rao_var_changed`.

M01 does not freeze the exact JSON/message/account schema. Those are M02 and M05.

## Worker/send boundary

The Rao module's own embedded documentation says:

> Rao tự động — gửi qua memory_items.send_chat / Network.SendPacket CMD_CLIENT_CHAT, ngầm, không cần mở bảng chat.

This proves the current PC Rao feature is not a visible mouse-click chat implementation.

The worker boundary is inventoried through:

- `_slot_loop`
- `_start_slot`
- `_stop_slot`
- `_stop_acc`
- `_toggle_single_acc`
- `_start_all_accs`.

M01 does not yet audit packet/channel mapping, interval loop or worker cancellation.

## Dependency boundary

### Direct/current module surface

- tkinter / ttk / messagebox / tkinter.font
- os
- start_tab shared helpers

### Direct runtime symbol evidence

- threading
- time
- json
- memory_items
- utils
- win32gui
- permission_guard
- bind/unbind window-identity symbols.

### Constructor/context

- `info_tab`
- notebook/parent surface.

### Weak/static-only evidence

Existing architecture evidence also carries:

- D04 Tier-B `rao_tab -> info_tab`;
- D04 incoming Tier-B `party_tab -> rao_tab`;
- D03 conservative `requests` reference for `rao_tab`.

These weak references are **not promoted to active imports** unless direct Rao-block evidence supports them.

## Screenshot cross-check

Only after the EXE-first extraction, the supplied Rao screenshot was compared.

It matches the static layout:

- **Cấu hình rao tự động**
- one visible row:
  - `Rao 1`
  - empty content
  - `Thế giới`
  - `30`
  - red delete button
- **+ Thêm rao**
- **Danh sách tài khoản**
- no account rows in the captured moment
- bottom **Bắt đầu**.

The screenshot's `30` is recorded as captured state here. Exact interval-default semantics remain M04.

## M01 boundary

Verified now:

- active Rao authority/module/class;
- serialized module identity/size/count;
- 40 direct methods;
- TLMMainApp construction;
- permission-controlled visibility;
- absence of current Rao-specific StartTab quick control;
- dedicated-tab visible UI;
- channel-label surface/default-channel symbol;
- account-row visible structure;
- persistence section/key-family boundary;
- refresh boundary;
- direct dependency boundary;
- send/worker handler boundary.

Deferred exactly as PLAN requires:

- M02 — message storage/schema
- M03 — channel selection/mapping
- M04 — interval normalization/timing
- M05 — account assignment/persistence
- M06 — start/stop worker
- M07 — parity/reconstruction contract.
