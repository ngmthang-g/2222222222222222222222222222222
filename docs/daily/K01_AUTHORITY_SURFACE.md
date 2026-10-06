# K01 — Daily authority / visible surface

## Authority

The active Daily implementation in the frozen TLMTool 2.1.2 binary is:

```text
payload marker: .daily_tab @ 0x2903223
module file:    daily_tab.py @ 0x290aad1
module marker:  <module daily_tab> @ 0x290abe0
class:          DailyTab @ 0x290a22a
description:    Daily Tab - Quản lý tác vụ hàng ngày.
```

The next serialized module payload starts at:

```text
.debug_android_tab @ 0x290bb8c
```

So the frozen Daily serialized region between those payload markers is **35,177 bytes (0x8969)**.

Daily is **ACTIVE**, not dormant. The main application tab builder contains:
- visible tab name `Daily`;
- module key `daily_tab`;
- class reference `DailyTab`;
- `daily_tab_ref` integration used by start-tab coordination.

## Constructor/top-level state families

The frozen constructor owns distinct activity/runtime state:
- Trừng Ác: `_punish_running`, `_punish_cancel`, `_punish_btn`;
- Tàng Bảo Đồ: `_treasure_map_running`, `_treasure_map_cancel`, `_treasure_map_btn`;
- shared monitor: `_monitor_running`;
- account rows: `_acc_rows`;
- Trừng Ác discard worker: `_punish_discard_stop/_thread/_gen`;
- refresh/shutdown: `_refresh_id/_refreshing/_closing/_scroll_after`.

Daily binds `<Destroy>` to `_save_on_destroy`.

## Visible section split

### Trừng ác

Frozen UI surfaces:
- `Thời gian đánh ác tặc (giây):`, UI seed `15`;
- movement choice `Ngựa` / `Định vị phù`;
- teleport hotkey readonly combobox values `1/2/3`;
- `Trị liệu khi HP < 30%`;
- visible heal location `Tô Châu`;
- `Lọc trang bị (vứt vũ khí, trang bị trong quá trình làm nhiệm vụ)`;
- reconnect;
- respawn/Địa phủ;
- `Áp dụng Trừng ác cho tất cả acc`.

### Tàng bảo đồ

Frozen UI surfaces:
- `Thời gian đánh trong huyệt mộ (giây):`, UI seed `30`;
- `Trị liệu sau khi đào nếu HP < 30%`;
- heal-location combobox;
- reconnect;
- respawn;
- `Áp dụng Tàng bảo đồ cho tất cả acc`.

## Account list

Visible/static row architecture:
- headers `Nhân vật` / `Hoạt động`;
- row play button `▶`;
- activity values exactly `Trừng ác` / `Tàng bảo đồ`;
- state dot `⬤`;
- initial state `Đã dừng`;
- per-row `Tới bổ đầu`;
- per-row `Trị liệu`.

The B08 screenshots happen to show an empty account list. K01 does not invent populated-row geometry beyond the frozen static row controls.

## Global controls

Visible:
- `Điều khiển tất cả:`;
- `Tới bổ đầu`;
- `Trị liệu`;
- bottom `Bắt đầu`.

Runtime string surface also contains:
- `Dừng lại`;
- `Đang dừng...`.

Bottom start/stop handler is `_start_all_accs`; each row uses `_toggle_single_acc`.

## Top-level architecture split

The exact 70-member top-level callable inventory naturally separates into:

1. shared UI/account discovery/config;
2. injection/window/state helpers;
3. all-account and per-row orchestration;
4. Trừng Ác discard support;
5. Trừng Ác execution family;
6. Tàng Bảo Đồ execution family.

K01 does not deep-audit any execution sequence.

## Direct dependency boundary

Verified explicit internal module refs inside the exact Daily payload:
- `utils`;
- `permission_guard`;
- `dll_injector`;
- `bag_filter`;
- `memory_items`;
- `fast_travel`;
- `pixel`;
- `start_tab`.

Other exact module-level/external refs include:
- `tkinter`, `tkinter.font`, `configparser`, `os`, `threading`, `win32gui`, `keyboard`.

Important evidence rule:
existing D04 B-level edges from Daily to `emu_input/emu_reader/emu_remote/emu_setup` are only `STATIC_REFERENCE_NOT_IMPORT_PROOF`. K01 does **not** promote them to active Daily dependencies because those exact module names are not exposed as direct refs in the bounded Daily payload.

## Frozen B08 cross-check

Only after static extraction, K01 cross-checked the existing Gate-B Daily evidence:
- screenshot hashes:
  - `217178561894a4205c7b5835ed33c050b384c8f60359f6894165e3400d514834`
  - `3939691e166fa67d9c50069119e4e3904496cd6769b04cf0d3199c6b3e0f866b`
- both 452×1032;
- same Daily state;
- 265-pixel difference already isolated to cursor placement.

The EXE-derived visible labels and the frozen B08 surface agree. No hidden behavior was inferred from the screenshot.

## Phase-K split established by K01

To preserve PLAN's ~17-task decomposition:

- **K01** shared authority/surface inventory — complete.
- **K02** shared account discovery, row lifecycle, state/start-stop coordinator.
- **K03–K09** seven Trừng Ác research tasks.
- **K10–K15** six Tàng Bảo Đồ research tasks.
- **K16–K17** runtime/parity closure tasks.

Later task boundaries may be refined by exact evidence, but this preserves the PLAN count and keeps Trừng Ác separate from Tàng Bảo Đồ.

## K01 boundary

K01 verifies **what Daily is, what is visibly/configurably present, what top-level handlers exist, and what direct dependencies are present**.

K01 deliberately does not decide:
- Trừng Ác quest acquisition/navigation/combat details;
- Tàng Bảo Đồ item/use/tomb/combat details;
- exact Daily start/stop races;
- reconnect/respawn internals;
- runtime parity.

Those belong to K02+.
