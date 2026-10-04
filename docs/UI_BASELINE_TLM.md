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

Direct selected captures now exist for **all 11 tabs**. Party was added during B04 and `i` during B12.

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
- Party / Train / Train LSV / Dồn vàng unselected

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

### G01 correction
The later G01 EXE audit determined that the Party module prose mentioning `Theo sau đội trưởng` / `Tự nhặt đồ` is not part of the active PartyTab UI contract in this frozen build. These controls belong to the Phó Bản implementation. Do not add them to Party reconstruction. Party B04 pixel geometry is unchanged.

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


## B09 — Đồn — VERIFIED

Binary-first evidence:
- compiled `donvang_tab.py` and related `don_logic.py`
- inner EXE SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`

Primary capture:
- `TLMTool_m7F9EFdzp5(2).png`
- SHA-256 `dffb4da895d21dea87dd72a6601c29104f519dca89c2f716f5a7445bcbe4421a`
- `452 × 1032`; copy (1) is byte-identical

### Selected tab
At `y=56`, Đồn selected bridge = `x=278..309`.

### Cấu hình Về thành
- group: `x=11..438, y=69..178`
- `Theo chu kỳ (phút)` selected; value **30**
- `Khi đầy túi` unselected
- priority values: `Phù 1 | Phù 2 | Phù 3 | Ngựa`

### Cấu hình Train
- group: `x=11..438, y=192..326`
- Quay lại train khi chết: unchecked
- Dừng khi mất kết nối mạng: unchecked
- Tự gỡ kẹt: checked
- Nhặt đồ không dùng hồ lô: unchecked
- Lọc đồ: **Tất cả** selected, `Chỉ vũ khí` unselected
- Trị liệu sau khi chết: unchecked
- treatment coordinate: `Trị liệu Tô Châu`

The screenshot clips the dynamic unstuck label at the right edge; no hidden suffix is invented.

### Cấu hình tọa độ lưu sẵn
- group: `x=11..438, y=340..427`
- visible row: `Tọa độ 1 | Đại Lý | 0 | 0 | Train | Xóa`
- Train button fill `#B48608`
- delete fill `#C62828`
- `+ Thêm tọa độ`: `#2E8B57`
- `Ẩn danh sách tọa độ`: `#808080`

### Danh sách tài khoản / receiver setup
- group: `x=11..438, y=441..983`
- `Tọa độ dồn:` combobox visible blank
- `Acc nhận 1`: blank
- `Acc nhận 2`: blank
- `+ Thêm acc nhận` visible
- scrollbar arrows/track visible, no thumb

Static shared dồn-coordinate choices:
- Dồn Lạc Dương
- Dồn Đại Lý
- Dồn Tô Châu
- Dồn Lâu Lan

Original module explicitly documents that the dồn coordinate is shared across receiver rows. Receiver rows are dynamic; loader creates one row if config has none and removal keeps at least one.

### Điều khiển tất cả
- Tới nơi nhận
- Tới chỗ bán
- Tới nơi train
- gold fill `#B48608`

### Bottom
- `Bắt đầu`
- fill `#388E3C`

### Static populated-row evidence
Original `donvang_tab.py` contains row controls/state vocabulary for:
- `▶`
- `Tọa độ bán:`
- `Tọa độ train:`
- `Túi:`
- `⬤`
- `Đã dừng`
- `Đến tọa độ`
- `Dồn đồ`
- `Tới nơi dồn`
- `Bán đồ`
- receiver tracking: elapsed time / vàng đã dồn / tốc độ vàng/h

No populated-row pixels are inferred from the empty screenshot.

Behavior remains deferred.


## B10 — Rao — VERIFIED

Binary-first evidence:
- compiled `rao_tab.py`
- inner EXE SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`

Rao screenshots:
- `TLMTool_kOf9oeNPWm(1).png` and `(2).png` are byte-identical
- SHA-256 `341f2b4653f31f5a0ee4a3f29d3cf9245edbf43c0ca140ac09a859925d8a2319`

### Selected tab
At `y=56`, Rao selected bridge = `x=308..337`.

### Cấu hình rao tự động
- group: `x=13..436, y=69..154`
- one visible Rao row:
  - name `Rao 1`
  - content blank
  - channel `Thế giới`
  - repeat `30`
  - red delete `✕`
- `+ Thêm rao`: green `#2E8B57`

Static channel list:
`Thế giới | Bang hội | Môn phái | Tổ đội | Liên minh | Quân đoàn | Lân cận`

Default channel: `Thế giới`.

Original module automatically names rows `Rao 1, Rao 2, ...` using the smallest unused number and applies digits-only validation to the repeat field.

### Danh sách tài khoản
- group: `x=13..436, y=170..983`
- headers: `Nhân vật | Nội dung rao`
- empty-list screenshot state
- scrollbar arrows/track visible, no thumb

Static populated-row structure:
- `▶`
- character name
- initial state `Đã dừng`
- four Rao-content combobox slots per account
- saved slot choices restored by character name

Original module states maximum **4 independent Rao slots per account**, and account list refreshes every **5 seconds**.

### Bottom
- `Bắt đầu`
- green fill `x=19..430, y=989..1016`
- `#388E3C`

Static running vocabulary includes `Đang rao X/4 nhóm...` and `Dừng lại`.

Behavior remains deferred.


## B11 — Tối ưu — VERIFIED

Binary-first evidence:
- compiled `toiuu_tab.py`; related `cpu_monitor.py`
- inner EXE SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`

Tối ưu screenshots:
- `TLMTool_tormBQu5Vy(1).png` and `(2).png` are byte-identical
- SHA-256 `653110b20120e26d115f11e64cb61b23af686b77432cf211b28be51a40364933`

### Selected tab
At `y=56`, selected bridge = `x=336..378`.

### Giám sát CPU/GPU
- group: `x=13..436, y=69..285`
- `Tách theo dõi` dark fill: `x=337..428, y=82..100`, `#616161`
- visible CPU: `CPU: 15%`
- CPU canvas: `x=18..431, y=125..190`
- CPU line: `#1565C0`
- visible GPU: `GPU: N/A (không có nvidia-smi)`
- GPU canvas: `x=18..431, y=216..281`
- GPU label: `#E65100`
- graph border `#BBBBBB`; grid `#E0E0E0`

Original module samples every 1 second and queries GPU through `nvidia-smi`. Detached monitor title: `CPU / GPU`; open state is persisted.

### Danh sách tài khoản
- group: `x=13..436, y=301..983`
- headers: `Nhân vật | Giảm cấu hình`
- screenshot state: empty list
- scrollbar arrows/track visible, no thumb

Static mode mapping:
- `medium` → `Thấp vừa`
- `low` → `Cực thấp`
- `max` → `Cực đại`
- config labels also contain `Không`

Static states:
- `Đã dừng`
- `Đang chạy`
- `Treo tick`

### Điều khiển tất cả
- Thấp vừa fill: `x=136..200, y=958..976`
- Cực thấp fill: `x=207..269, y=958..976`
- Cực đại fill: `x=276..330, y=958..976`
- all use `#616161`

### Bottom
- `Bắt đầu`
- fill `x=19..430, y=989..1016`
- `#388E3C`

Behavior remains deferred.


## B12 — i / Thông tin — VERIFIED

Binary-first evidence:
- compiled `info_tab.py` / `TLMInfoTab`
- inner EXE SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`

Direct screenshot:
- `TLMTool_f8iidp8FS8.png`
- SHA-256 `e536e081c653c72991344bfe505dd79cbcbf5fa52c9befa63214eb9d1516e4bc`
- `452 × 1032`

### Selected tab
At `y=56`, i selected bridge = `x=377..402`.

### Header + version status
- `TLMTool - Thông tin`
- separator y=96
- status panel `x=17..432, y=110..153`
- current state: `Bạn đang dùng bản phát triển: v2.1.2`
- background `#E2E3FF`, text/icon `#4A00E0`

Original module contains conditional status variants for too-old, update-available, development, latest and checking states, with their original colors.

### Info rows
- Phiên bản: `2.1.2`
- Mã ứng dụng: `d9ab65e4e118663e` + `Copy`
- Key: blank + `Nhập`
- Loại bản quyền: `FREE`
- Cửa sổ: `1/1`
- Hiệu lực: `Vĩnh viễn`

Application ID is classified runtime/device-derived; original module contains device-hash/MAC/MachineGuid/window-type methods.

### Changelog
Scrollable region approx `x=17..432, y=354..462`.

Current screenshot content:
- Bản 2.0 (30-09-2026)
- Trừng ác nhanh, sử dụng truyền lượt đi lẫn về
- Đổi cơ chế đồn vàng, có thể đồn ngay tại chân NPC bán
- Thêm chế độ rao spam tất cả kênh, chạy song song
- Cải thiện chế độ tối ưu giảm cấu hình thấp hơn
- Tất cả map di chuyển tại Train đều ưu tiên dùng truyền nếu có thể

These exact lines are server-fed/current content, not hardcoded package strings.

### Price block
Current visible server-fed text:
- Báo giá key bản quyền theo máy/tháng
- 200k/1 cửa sổ
- 400k/3 cửa sổ
- 500k/6 cửa sổ
- 600k/12 cửa sổ
- 700k/Không giới hạn

### Support
- `● Facebook`
- `● Zalo`
- `Gửi log hỗ trợ`
- Facebook URL is hardcoded in original module.
- log button has real trim/sanitize/upload/save workflow in static code.

### Auto trong hệ thống
Current visible dynamic two-column catalog:
- Lineage W
- Lineage L2M
- Legend of YMIR
- Thiên Mệnh Lạc Hồng
- Diệt quỷ Online
- Thần long Mobile

Original module builds this area dynamically from server `price_tools` items.

### Conditional hidden structures
Original module also contains:
- Cập nhật thủ công
- Cập nhật tự động
- Tính năng mới:
- hidden license-entry section
- log-upload dialog

No pixels are invented for conditional UI not present in this screenshot.

Behavior remains deferred.


## B13 — Màu/font/button metrics — AUDITED_WITH_ROOT_FONT_SIZE_VERIFIED

### Exact base raster
- client/inactive tab: `#F0F0F0`
- selected tab / input field: `#FFFFFF`
- notebook separator: `#D9D9D9`
- LabelFrame border: `#DCDCDC`
- entry/combobox border: `#7A7A7A`
- checkbox/radio stroke: `#333333`
- Info separators: `#A0A0A0`
- scrollbar thumb: `#CDCDCD`

### Main semantic fills
- Start green `#388E3C`
- add `#2E8B57`
- running green `#2E7D32`
- RoyalBlue `#4169E1`
- action blue `#1565C0`
- Phó Bản blue `#0277BD`
- red `#C62828`
- LSV purple `#8E24AA`
- Daily brown `#795548`
- Đồn gold `#B48608`
- gray `#808080`
- dark gray `#616161`
- orange `#E65100`
- Start sync red `#F44336`

### Classic raised-button raster
Representative custom buttons have one-pixel lighter top/left edge and one-pixel dark/black right/bottom edge.

Examples:
- #388E3C → #9CC79E highlight
- #4169E1 → #A0B4FF
- #2E8B57 → #97C5AB
- #808080 → #C0C0C0

### Common dimensions
- checkbox/radio: 13 × 13
- ttk combobox: ~21 px outer height
- entry/spin: ~19–21 px
- vertical scrollbar: 15 px
- small custom button: ~21–23 px outer
- bottom Start: 30 px outer / 28 px fill

### Font lock
Original binary verifies the root/global default tuple **(`Segoe UI`, 9)** and applies it through `option_add("*Font", default_font)`. It also repeatedly configures `Bold.TLabelframe.Label` and bold custom-button fonts.

Raster envelopes:
- normal labels 9–11 px glyph height
- bold section labels ~12 px
- small button text ~9 px
- bottom Start ~11 px
- Info title ~16 px

**Root/global default is now VERIFIED as Segoe UI 9.** Exact point sizes for explicit per-widget overrides remain UNKNOWN where not separately evidenced, and screenshot DPI/scaling is not established. Reconstruction should use Segoe UI 9 as the root/default and calibrate only widget-specific overrides against these raster envelopes.

### Theme/rendering rule
ClearType fringe pixels and some ttk details are environment-sensitive. Large fills, structural lines, control bounds and text envelopes are strict; anti-alias/native-theme fringe pixels are comparison-tolerant.


## B14 — Pixel comparison checklist — VERIFIED

Gate-B comparison contract:

### Comparison classes
- **S0 STRICT_RASTER** — locked structural coordinates and flat fills: 0 px drift, exact RGB.
- **S1 STRICT_GEOMETRY_NATIVE_RENDER** — native ttk/classic controls: exact outer geometry, native glyph AA may vary within ±1 px envelope.
- **T1 TEXT_ENVELOPE** — Segoe UI family/weight and text bbox placement; ±1 px envelope, ignore ClearType fringe RGB.
- **D1 DYNAMIC_CONTENT_MASK** — machine/server/runtime pixels masked, container geometry/style remains strict.
- **C1 CURSOR_MASK** — capture cursor pixels excluded.
- **N0 NONCLIENT_EXCLUDED** — titlebar/window-frame pixels excluded from Gate-B pass.

### Reference scope
Direct screenshot references cover:
- ▶ Start / Auto-Điều khiển nhanh
- ▶ Start / Xếp lưới
- Login
- Party
- Train
- Train LSV
- Phó Bản
- Daily
- Đồn
- Rao
- Tối ưu
- i / Thông tin

### Party exception
Party's 451 × 1035 raw capture has different right/bottom framing. Use B04 raw measured UI regions; do not compare that outer framing against the common 452 × 1032 reference.

### Dynamic masks
Explicit masks exist for live HWND previews, account/character state, CPU/GPU data, device ID, server changelog/price/catalog, persisted config differences and cursor artifacts.

### Pass order
1. client normalization
2. notebook geometry
3. selected tab
4. frame/group bounds
5. control bounds
6. semantic flat fills
7. static text envelopes
8. cursor masks
9. dynamic masks
10. regional mismatch report

A page does not pass merely from a low whole-window mismatch percentage if a locked structural coordinate or semantic color is wrong.

### Gate decision
B01–B13 provide the required geometry, selected-state evidence, tab/page baselines, palette and common metrics. B14 provides the strict/tolerant comparison contract.

Remaining **per-widget override** point-size, ClearType and non-client uncertainties are explicitly environment-sensitive and are not visual blockers. Root/global default font is statically verified as Segoe UI 9.

**GATE B — COMPLETE / VERIFIED.**

## F01 Login EXE supplement
Original-EXE-first F01 analysis resolves several screenshot-only B03 unknowns while preserving the measured raster: the Login groups are Tk `LabelFrame`s using `Bold.TLabelframe`; the header selector is a custom toggle-all Button; logical account capacity is exactly 100 rows with plan-controlled hiding/restoration; captcha modes are `Không / Tool / Proxy`; `Không` produces a blank gray disabled proxy-action cell; and the exact right-edge after-login label is `Dồn vàng`. Hidden/conditional Login widgets such as `lbl_dll_status`, `lbl_sched_countdown`, `lbl_proxifier_status`, and `_profile_btns` are not assigned invented pixel coordinates.
