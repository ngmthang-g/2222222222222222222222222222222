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

## B05 — Train — VERIFIED

Binary-first evidence:
- compiled `farm_tab.py` / `<module farm_tab>`
- inner binary SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`

Primary screenshot:
- `TLMTool_b2OvbUQCNB(2).png`
- SHA-256 `17d98f6b6a263daa5857224d100355379672eae7bd7c72794323f31417d8bc53`
- `452 × 1032`; copy (1) is byte-identical

### Train selected
At `y=56`, selected bridge = `x=102..137`.

### Cấu hình Về thành
- group: `x=11..438, y=69..133`
- `Hiện cấu hình`: `x=312..431, y=83..104`
- `Theo chu kỳ (phút)` selected; value **30**
- `Không về`, `Khi đầy túi` unselected

Original FarmTab explicitly marks the lower town block as **mặc định ẩn**. Hidden static controls include navigation priority `Phù 1/2/3/Ngựa`, `Bán trang bị`, HP/MP item+quantity controls and `Tọa độ Dược:`. No hidden pixels are invented.

### Cấu hình Train
- group: `x=11..438, y=147..329`
- Quay lại train khi chết: unchecked
- Tự kết nối lại khi mất mạng: unchecked
- Nhặt đồ không dùng hồ lô (càn khôn hồ): unchecked
- Trị liệu sau khi chết: unchecked
- treatment combobox: `x=235..389, y=230..250` → `Trị liệu Tô Châu`
- keep mode: **Tất cả**
- no buff row visible
- `+ Thêm`: `x=18..151, y=304..325`

Static buff row supports **F1–F10 + 1,2,3** with `Phím:`, `Thời gian:`, `ph`, `giây`.

### Cấu hình tọa độ lưu sẵn
- group: `x=11..438, y=343..406`
- headers: `Tên | Map | X | Y | Áp dụng hết | Xóa`
- no saved row visible
- `+ Thêm tọa độ`: `x=18..151, y=381..402`
- `Ẩn danh sách tọa độ`: `x=298..431, y=381..402`

Static row structure includes `Bán`, `Train`, delete `✕`.

### Danh sách tài khoản
- group: `x=11..438, y=420..983`
- headers: `Nhân vật | Tọa độ bán | Tọa độ Train`
- capture is empty-list state
- scroll track/chevrons visible, no thumb visible

Static populated-row structure includes `▶`, `⬤`, `Đã dừng`, sell/train comboboxes and goto/sell/move/farm controls. Their pixels are not inferred.

### Điều khiển tất cả
- Tới bán đồ: `x=133..207, y=959..979`
- Bán đồ: `x=212..267, y=959..979`
- Tới bãi train: `x=272..352, y=959..979`
- Đánh: `x=357..403, y=959..979`

### Bottom
- `Bắt đầu`: `x=16..433, y=988..1017`

Behavior remains deferred.


## B06 — Train LSV — VERIFIED

Binary-first evidence:
- compiled `train_lsv_tab.py` / `<module train_lsv_tab>`
- inner binary SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`

Train-LSV screenshot set:
- four available files are byte-identical
- SHA-256 `9e3b57671a2ff165ea31264a1c2fb19493f861a7bdadc4dc993a55bd130f5d29`
- `452 × 1032`, client `450 × 1000`

### Selected tab
At `y=56`, Train LSV selected bridge = `x=136..193`.

### Cấu hình Train LSV
- group: `x=11..438, y=69..253`
- Quay lại train khi chết: unchecked
- Tự kết nối lại khi mất mạng: unchecked
- Trị liệu sau khi chết tại Lạc Dương LSV: unchecked
- Nhặt đồ: **Tất cả** selected; Không / Chỉ vũ khí unselected

### Dạ Minh Châu fixed row
- checked square: `x=20..32, y=203..215`
- visible label: `Dạ Minh Châu`
- key combobox: `x=174..220, y=199..219` → `1`
- minutes: `x=289..310, y=200..218` → `0`
- seconds: `x=336..357, y=200..218` → `5`
- `+ Thêm`: `x=18..151, y=228..249`

Original binary documents Dạ Minh Châu as the fixed buff row, with no delete button and always-active state; normal buff rows support F1–F10 + 1/2/3.

### Static LSV map names
- Tần Hoàng Địa Cung Tầng 1
- Tần Hoàng Địa Cung Tầng 2
- Tần Hoàng Địa Cung Tầng 3
- Tần Hoàng Địa Cung Tầng 4
- Phàm Liên Trại
- Thanh Liên Trại
- Khô Vinh Đạo

### Cấu hình tọa độ lưu sẵn
- group: `x=11..438, y=267..330`
- headers: `Tên | Map | X | Y | Áp dụng | Xóa`
- no saved-coordinate row visible
- `+ Thêm tọa độ`: `x=18..151, y=305..326`
- `Ẩn danh sách tọa độ`: `x=298..431, y=305..326`

Original binary also contains `Hiện danh sách tọa độ` and explicitly documents that header+body toggle while toolbar stays visible.

### Danh sách tài khoản
- group: `x=11..438, y=344..983`
- headers: `Nhân vật | Tọa độ Train`
- empty-list screenshot state
- scrollbar arrows/track visible, no thumb

Static populated-row structure contains play glyph `▶`, state dot `⬤`, initial `Đã dừng`, Train-coordinate combobox, LSV/move/leave/farm row actions, and extra track text such as `0h:00p`, `Túi:`, `Chết: 0`, `exp: 0`, `0 exp/h`. No row pixels are invented.

### Điều khiển tất cả
- Tới LSV: `x=133..189, y=959..979`
- Tới chỗ train: `x=194..277, y=959..979`
- Đánh: `x=282..328, y=959..979`
- Rời LSV: `x=333..390, y=959..979`
- purple fill: `#8E24AA`

### Bottom
- `Bắt đầu`: `x=16..433, y=988..1017`
- green fill: `#388E3C`

Behavior remains deferred.


## B07 — Phó Bản — VERIFIED

Binary-first evidence:
- compiled `phoban_tab.py` and related `phoban_dungeons.py`
- inner EXE SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`

Primary capture:
- `TLMTool_Ij9dp7pweA(2).png`
- SHA-256 `8b62070b04231f762dc080f4432cbc178f020ae0614540dc0e9c293d16987fb8`
- `452 × 1032`; copy (1) is byte-identical

### Selected tab
At `y=56`, Phó Bản white bridge = `x=192..245`.

### Cấu hình tổ đội
- border: `x=13..436, y=69..110`
- `Danh sách acc sẵn sàng:`
- no ready-account entry visible

### Cấu hình phó bản
- border: `x=13..436, y=124..206`
- all visible options unchecked:
  - Tạo lại đội
  - Theo sau đội trưởng
  - Nhặt không hồ lô
  - Vứt trang bị
  - Vứt vật phẩm
  - Vứt thuốc
  - Nga My buff (Sát Tinh)

The follow-leader checkbox is partly obscured by the mouse cursor; its text/state are visible, but B07 records the exact border as partially occluded.

### Static hidden sale-coordinate block
Original `phoban_tab.py` creates `Cấu hình tọa độ bán đồ` with `Tên | Map | X | Y | Xóa` and `+ Thêm tọa độ`, then executes `pack_forget` before the schedule UI. It is therefore excluded from the visible pixel baseline.

### Cấu hình lịch trình
- outer border: `x=13..436, y=220..979`
- visible scrollbar arrows/track; no thumb
- Nhóm 1 frame: `x=18..423, y=240..372`
- leader: `(chưa chọn)`
- six blank account comboboxes = **2 rows × 3**
- `✕ Xóa nhóm`: `x=329..418, y=252..271`
- schedule header checkbox unchecked
- headers: `Hoạt động | Tên Map | Lần | Status | Xóa`
- no schedule row visible

Toolbar:
- `+ Thêm Lịch trình`: `x=24..137, y=348..370`
- `Tắt auto PB`: `x=141..219, y=348..370`
- `Bắt đầu lịch trình`: `x=223..418, y=348..370`

Static original schedule activities: `Phó bản`, `Train`.
Train map value: `Về train theo thiết lập sẵn`.

Static dungeon names:
- Tô Châu  - Thủy Lao
- Tô Châu 1 - Tống Liêu
- Tô Châu 2 - Trúc Lâm
- Tô Châu 3 - Dã Ngoại
- Lâu Lan 1 - Hoàng Kim
- Lâu Lan 2 - Huyền Phật Châu
- Lâu Lan 3 - Dung Nham
- Sát Tinh - Thử nghiệm

Static progress vocabulary: `Chưa / Đang / Xong`.
Runner-state strings include `Dừng lịch trình`, `Đang dừng lịch trình...`, and global `Dừng lại`.

### Add group
- `+ Thêm nhóm`: `x=20..154, y=954..976`

### Bottom
- `Bắt đầu`: approx outer `x=16..433, y=988..1017`
- exact green fill `x=19..430, y=989..1016`

Behavior remains deferred.


## B08 — Daily — VERIFIED

Binary-first evidence:
- compiled `daily_tab.py`
- inner EXE SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`

Two Daily captures show the same UI state; their only raster difference is mouse-cursor placement.

### Selected tab
At `y=56`, Daily selected bridge = `x=244..279`.

### Trừng ác
- group: `x=13..436, y=69..279`
- duration: **15**
- move mode: **Ngựa** selected
- Định vị phù unselected
- Phím tắt phù combobox blank; original values = `1 / 2 / 3`
- Trị liệu khi HP < 30%: checked
- visible location text: `Tô Châu`
- Lọc trang bị: unchecked
- Tự kết nối lại khi mất mạng: checked
- Hồi sinh khi chết/Địa phủ: checked
- apply-all fill: `#795548`, `x=23..426, y=253..274`

### Tàng bảo đồ
- group: `x=13..436, y=295..408`
- tomb duration: **30**
- Trị liệu sau khi đào nếu HP < 30%: unchecked
- Vị trí trị liệu: `Tô Châu`
- reconnect: checked
- respawn: checked
- apply-all fill: `#795548`, `x=23..426, y=382..403`

### Danh sách tài khoản
- group: `x=13..436, y=424..983`
- headers: `Nhân vật | Hoạt động`
- screenshot state: empty list
- scrollbar arrows/track visible, no thumb

Static populated-row structure:
- `▶`
- activity combobox `Trừng ác / Tàng bảo đồ`
- status dot `⬤`
- initial state `Đã dừng`
- per-row `Tới bổ đầu`
- per-row `Trị liệu`

### Điều khiển tất cả
- Tới bổ đầu fill: `x=136..208, y=958..976`
- Trị liệu fill: `x=215..266, y=958..976`
- both use `#795548`

Static later-behavior targets are preserved:
- bổ đầu: Tô Châu map 4, 224,285
- trị liệu: Tô Châu map 4, 155,252

### Bottom
- `Bắt đầu`
- green fill: `x=19..430, y=989..1016`
- `#388E3C`

Behavior remains deferred.


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
