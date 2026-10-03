# UI_BASELINE_TLM — TLMTool 2.1.2

This document is the authoritative screenshot-derived UI baseline. It is built incrementally through Gate B.

Do not treat screenshot parity as functional parity. Behavior remains a separate verification track.

---

## B01 — Main window dimensions — VERIFIED

### Locked reconstruction target
- **Client/content area:** `450 × 1000 px`
- **Observed full window raster:** `452 × 1032 px`

### Observed non-client boundary in supplied screenshots
- left frame: 1 px
- right frame: 1 px
- top/titlebar through row 30
- client starts at row 31
- bottom frame: final row 1031

All **12/12** supplied screenshots agree on these dimensions.

### Confidence
**HIGH / VERIFIED from raster evidence.**

### Explicit UNKNOWN
- DPI/scaling percentage
- exact geometry-setting API/source code
- resizable/min/max policy
- initial screen coordinates
- decoration metrics under other OS themes/DPI settings

### Implementation parity rule
Target the **450 × 1000 client area**. Use the observed **452 × 1032 outer raster** only as the screenshot-environment parity reference; do not hard-code Windows decoration assumptions unless later evidence requires it.

---

## B02 — Tab bar + style chung — VERIFIED

### Tab order
`▶ | Login | Party | Train | Train LSV | Phó Bản | Daily | Đồn | Rao | Tối ưu | i`

**11 tabs total.**

### Shared notebook geometry
- frame left/right: `x=6..443`
- tab strip top: `y=36`
- inactive-tab bottom separator: `y=56`
- notebook bottom: `y=1024`
- visible frame width: **438 px**
- client margins: left **5 px**, right **7 px**, top-to-tab **5 px**, bottom **6 px**

### Nominal inactive tab separator X coordinates
`6, 29, 67, 102, 136, 192, 244, 278, 308, 336, 377, 401`

Nominal separator spans:
- ▶ 23
- Login 38
- Party 35
- Train 34
- Train LSV 56
- Phó Bản 52
- Daily 34
- Đồn 30
- Rao 28
- Tối ưu 41
- i 24

These are raster separator spans, not source widget width units.

### Shared raster style
- client/inactive tab: `#F0F0F0`
- active tab: `#FFFFFF`
- tab/frame separator: `#D9D9D9`
- tab text/glyph: black
- title: `TLMTool`

### Selected tab evidence — corrected during B04
Direct selected captures exist for:
`▶, Login, Train, Train LSV, Phó Bản, Daily, Đồn, Rao, Tối ưu`.

Direct selected Party and i captures remain **UNVERIFIED**.

The selected tab expands/merges through the lower separator into the page.

**Focus correction:** a dotted focus rectangle is not a required selected-state feature. The `TLMTool_fTpCsm0auQ` Start/Xếp-lưới capture has `▶` selected but focus is on the `Xếp lưới` radio, so the selected tab does not carry the dotted focus rectangle. Treat the dotted rectangle as widget-focus state, not tab-selection state.

### Deferred to B13
Exact font family/point size, font weight, button palette/borders and deeper anti-aliasing/color metrics.

---

## B03 — Login — VERIFIED

Primary capture: `TLMTool_4dw2sgi7mQ(2).png`, SHA-256 `a555bce4054a0d32d19c2377a726c7fa2e6b78c03ce80e8291affb6185f04461`.

### Group boxes
- Cấu hình game: `x=11..438, y=69..133`
- Cấu hình lịch trình: `x=11..438, y=147..283`
- Cấu hình tài khoản: `x=11..438, y=297..1013`

### Cấu hình game
- Chọn thư mục game button: `x=16..150, y=83..106`
- Mở game button: `x=157..232, y=83..106`
- checked success indicator visible
- selected path text is clipped; hidden suffix remains UNKNOWN

### Cấu hình lịch trình
Visible defaults:
- Chạy theo lịch: unchecked
- tắt game: **04:00**
- Tắt máy sau khi tắt game: unchecked
- mở game: **04:20**
- Sau khi login: **Chờ** selected
- Party / Train / Train LSV / Đồn văn unselected

### Cấu hình tài khoản
- Hiện mật khẩu: unchecked
- header columns: selector | Tài khoản | Mật khẩu | Ẩn captcha | Login | Proxy
- header selector appears checked
- first row selector appears unchecked
- first account: `ngmthang1`
- password: masked; underlying value UNKNOWN
- first captcha: `Tool`
- following visible captcha rows: `Không`
- first proxy cell: blue arrow button
- following proxy cells: gray/disabled-looking
- row pitch: **35 px**
- **17 full rows + partial 18th row** visible in the scroll viewport
- scrollbar thumb observed at `x=418..432, y=349..472`
- bottom `Bắt đầu`: `x=20..429, y=978..1007` → **410 × 30**

Behavior/config semantics are not inferred from this baseline.

---

## B04 — Party — VERIFIED

Primary Party-selected capture:
- `image(5).png`
- SHA-256 `b04e9a73887bb8093bba8bfcd8a77a4dc57c5838ca11370c85def0f8adeb9590`
- raw bitmap `451 × 1035`

This capture has different right/bottom edge-shadow framing from the original 452 × 1032 set, so B04 coordinates are raw Party-capture coordinates. B01's 450 × 1000 client reconstruction target remains unchanged.

### Party selected tab
At `y=56`, white selected bridge = `x=65..101`.

Party is selected without a dotted focus rectangle in this capture, confirming that the dotted rectangle is focus state rather than required selection state.

### Sau khi party
- group: `x=11..434, y=69..130`
- `Chờ` selected
- `Train`, `Train LSV`, `Dồn vàng`, `Phó bản` unselected

### Cấu hình tổ đội
- group: `x=11..434, y=144..181`
- label: `Danh sách acc sẵn sàng:`
- no ready-account entry visible in this captured state

### Cấu hình nhóm
- outer: `x=11..434, y=195..611`
- Nhóm 1: `x=16..429, y=215..326`
- Nhóm 2: `x=16..429, y=340..451`
- Nhóm 3: `x=16..429, y=465..576`
- each group visibly has **6 account slots = 2 rows × 3 comboboxes**

#### Nhóm 1
- leader: `ThápCa`
- row 1: `ThápCa | 75C.S6 | TổngTài.S6`
- row 2: blank
- `Rời nhóm`: `x=261..330, y=227..245`
- `✖ Xóa nhóm`: `x=335..423, y=227..245`
- status/action bar: `x=22..423, y=297..322` — hourglass + `Đang vào...`

#### Nhóm 2
- leader: `(chưa chọn)`
- six blank slots
- action bar: `x=22..423, y=422..447` — `Tạo nhóm 2`

#### Nhóm 3
- leader: `(chưa chọn)`
- six blank slots
- action bar: `x=22..423, y=547..572` — `Tạo nhóm 3`

### Other controls
- `+ Thêm nhóm`: `x=18..151, y=586..607`
- bottom `Bắt đầu`: `x=16..429, y=988..1017`

### Static-only facts not visible in this capture
The compiled Party module also contains documentation/labels for `Theo sau đội trưởng` and `Tự nhặt đồ`. They are not visibly present here, so no pixel placement is invented.

Behavior remains deferred.


---

## B05 — Train
TODO

## B06 — Train LSV
TODO

## B07 — Phó Bản
TODO

## B08 — Daily
TODO

## B09 — Đồn
TODO

## B10 — Rao
TODO

## B11 — Tối ưu
TODO

## B12 — i
TODO

## B13 — Màu/font/button metrics
TODO

## B14 — Pixel comparison checklist
TODO
