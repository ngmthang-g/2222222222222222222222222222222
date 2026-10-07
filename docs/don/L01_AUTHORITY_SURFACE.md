# L01 — Dồn authority / visible surface / handler inventory / dependency boundary

## Authority

The active implementation is the Nuitka module `donvang_tab`, source label `donvang_tab.py`, class `DonVangTab`.

Frozen EXE evidence:
- marker `.donvang_tab` at `0x2920bc1`;
- header size field = **65,260 bytes**;
- header count field = **1,813 constants**;
- source filename string at `0x292e0da`;
- module qualname `<module donvang_tab>` at `0x292e366`;
- class `DonVangTab` at `0x292d1c6`;
- next module marker `.emu_chat` at `0x2930abd`.

The dense direct class-qualname block contains **127 top-level DonVangTab methods**, excluding nested `<locals>` functions.

## Main-app and StartTab wiring

`TLMMainApp.create_tabs` owns a `donvang_tab` slot and the exact visible tab label is **Dồn**. The main app directly references/constructs `DonVangTab`.

The app also owns `_set_donvang_tab_visible`. Frozen comment text describes permission/dev-like visibility control. This is treated as a visibility policy boundary, not as evidence that the module is dormant.

`TLMStartTab` separately exposes the Dồn row:
- **Dồn vàng**;
- **Tới nơi nhận**;
- **Tới chỗ bán**;
- **Tới nơi train**;
- **Cấu hình**.

Direct StartTab callables include `_goto_donvang_tab`, `_donvang_action`, and `_toggle_donvang_cmd`.

## Visible Dồn-tab surface

Static UI strings and the captured Dồn screenshot agree on these major sections.

### Cấu hình Về thành

- Điều kiện về thành:
  - Khi đầy túi
  - Theo chu kỳ (phút)
- Phương thức về thành:
  - Phù 1
  - Phù 2
  - Phù 3
  - Ngựa

Captured state shows cycle mode selected with value **30**.

### Cấu hình Train

Visible controls include:
- Quay lại train khi chết
- Dừng khi mất kết nối mạng
- Tự gỡ kẹt
- Nhặt đồ không dùng hồ lô (càn khôn hồ)
- Lọc đồ
- Trị liệu sau khi chết
- Tọa độ trị liệu

Captured state shows Tự gỡ kẹt checked, filter **Tất cả**, and heal map **Trị liệu Tô Châu**.

### Cấu hình tọa độ lưu sẵn

The UI has name/map/X/Y plus Apply/Delete behavior, add-coordinate control, and hide/show list control.

Captured state contains one visible row: **Tọa độ 1 / Đại Lý / 0 / 0**.

### Danh sách tài khoản / receiver setup

The Dồn UI owns:
- one shared **Tọa độ dồn** selector;
- dynamically addable **Acc nhận** rows;
- **+ Thêm acc nhận**.

The captured screenshot shows two receiver rows and no live game-account rows.

### Per-account row surface

When game rows exist, the class contains exact row controls for:
- train coordinate selector;
- bag count;
- state indicator;
- **Đến tọa độ**;
- **Dồn đồ**;
- **Tới nơi dồn**;
- **Bán đồ**;
- elapsed time / donated gold / gold-per-hour tracking.

### All-account surface

Exact all-account controls:
- **Tới nơi nhận**
- **Tới chỗ bán**
- **Tới nơi train**
- bottom **Bắt đầu** toggle.

## Persistence surface

The module owns the `[DonVang]` settings section and a documented **30-second autosave loop**.

L01 records only the persistence authority/surface. Exact key semantics are deferred to later Phase-L tasks.

## Dependency boundary

High-confidence module-level/current runtime dependencies include:
- tkinter/ttk/font;
- os/configparser + shared settings helpers;
- farm_data;
- start_tab;
- permission_guard;
- utils;
- dll_injector;
- don_logic;
- fast_travel;
- memory_items;
- bag_filter;
- pixel;
- the constructor-supplied info_tab object.

`farm_tab` appears in port/reference documentation and is not promoted by L01 to a current runtime import.

Existing graph-only `donvang_tab -> emu_input/emu_reader` edges remain **STATIC_REFERENCE_NOT_IMPORT_PROOF** because no direct literal/call surface was recovered inside the frozen DonVang blob.

## Active versus dormant

Dồn is **active/wired**, not dormant:
- the main app constructs `DonVangTab`;
- the main app owns a Dồn tab slot;
- StartTab exposes direct Dồn actions;
- the user-supplied captured UI shows both the Dồn tab and the StartTab Dồn row.

The exact permission state that makes the dedicated Dồn tab visible is not inferred from the screenshot. Static comment text and captured visibility are preserved as separate evidence layers.

## Screenshot cross-check

Cross-check was performed only after EXE-first extraction.

Dồn-tab capture:
- SHA-256 `dffb4da895d21dea87dd72a6601c29104f519dca89c2f716f5a7445bcbe4421a`
- 452×1032

StartTab capture:
- SHA-256 `4f1b126ea4ba0034889545653046f552a226d5f0033d2329a8693342184c28cd`
- 452×1032

## L01 boundary

L01 does not decide return priority, receiver selection, inventory/full-bag behavior, selling, train lifecycle, heal/reconnect, or Dồn execution semantics. Those are later Phase-L tasks.

Next: **L02 — Dồn return mechanism audit**.
