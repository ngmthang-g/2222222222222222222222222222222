Được. Dưới đây là **PLAN tổng hợp chính thức** dựa trên toàn bộ yêu cầu trong đoạn trao đổi này. Tôi coi đây là tài liệu khóa phạm vi để các phiên sau không tự phát triển lệch hướng.

# PLAN TÁI TẠO TLMTool 2.1.2 — SOURCE + EXE + GIAO DIỆN + HÀNH VI

## 1. Mục tiêu cuối cùng

Nguồn chuẩn là:

- `TLMTool_2.1.2.zip` mà bạn đã cung cấp.
- Toàn bộ ảnh chụp giao diện TLMTool.
- Ảnh bố cục nhiều cửa sổ game hoạt động đồng thời.
- Repo đích: `ngmthang-g/2222222222222222222222222222222`.

Sản phẩm cuối phải gồm:

1. Một project source mới có cấu trúc rõ ràng để tiếp tục phát triển về sau.
2. Build được EXE chạy độc lập.
3. Giao diện phải tái tạo TLM hiện tại sát nhất có thể.
4. Các nút không được làm giả; phải thực sự hoạt động giống TLM.
5. Các tab, logic, thao tác cửa sổ, preview, cấu hình, luồng chạy phải được kiểm chứng.
6. Source + công cụ build + tài liệu + artifact EXE được đưa lên repo đích.
7. Không tự thêm chức năng ngoài TLM.
8. Không refactor chỉ vì thấy cách khác “đẹp hơn”.
9. Không tự thay đổi thời gian, thứ tự thao tác, màu, tên nút, điều kiện logic nếu chưa xác minh.
10. Mỗi task phải nhỏ khoảng **18 phút** để phù hợp giới hạn mỗi phiên làm việc khoảng 20 phút.

---

# 2. Định nghĩa “giống 100%”

Phải phân biệt hai mức.

### A. Bộ TLM gốc

Toàn bộ package gốc có thể được bảo tồn **100% byte-for-byte**.

Sẽ dùng:

- đường dẫn file,
- kích thước,
- SHA-256,
- số lượng file,
- cấu trúc thư mục

để chứng minh không thiếu hoặc thay đổi file nào.

### B. Source code

TLM hiện tại là Python 3.10 đã được compile bằng Nuitka standalone và ZIP không chứa `.py` gốc.

Do đó, nếu không có source Python ban đầu thì không thể chứng minh source dựng lại giống từng ký tự/từng comment của source tác giả.

Mục tiêu khả thi phải là:

> **Functional parity + UI parity + runtime parity 100% theo những gì có thể kiểm chứng từ TLM.**

Nếu sau này có source TLM gốc thì chuyển sang kiểm tra source line-by-line.

---

# 3. Ba tiêu chí bắt buộc cho mọi chức năng

Không được đánh dấu một tính năng là hoàn thành chỉ vì có giao diện.

Mỗi phần phải qua cả ba kiểm tra:

### Visual parity

Giao diện:

- vị trí,
- kích thước,
- text,
- màu,
- checkbox,
- combobox,
- radio,
- bảng,
- thanh cuộn,
- tab,
- group box

phải giống TLM.

### Behavior parity

Ví dụ nút:

`Tới bản đồ`

thì phải thực sự đưa cửa sổ/nhân vật tới trạng thái giống TLM.

Không chấp nhận:

- nút hiện ra nhưng chưa có code,
- nút chỉ log,
- mock action,
- placeholder.

### Runtime parity

Phải kiểm tra trong tình huống thật:

- nhiều tài khoản,
- nhiều HWND,
- cửa sổ đang ẩn,
- cửa sổ resize,
- preview,
- game mất kết nối,
- thao tác tab khác nhau,
- start/stop.

---

# 4. Baseline giao diện phải giữ

Thứ tự tab chính:

`▶ | Login | Party | Train | Train LSV | Phó Bản | Daily | Đồn | Rao | Tối ưu | i`

Không tự ý:

- đổi tên,
- đổi thứ tự,
- gộp tab,
- tách tab,
- thêm tab.

---

# 5. Baseline tab điều khiển nhanh / cửa sổ game

Ảnh nhiều cửa sổ game là baseline bắt buộc.

Phải tái tạo đúng nhóm:

### Chế độ

- Auto
- Xếp lưới

### Điều khiển nhanh

Các hàng chức năng đang thấy gồm:

- Ẩn hết
- Đóng xem
- Xếp gọn
- Xếp chéo
- Login
- Reload
- Cấu hình
- Trừng ác
- Tăng bảo đồ
- Tới bổ đầu
- Trị liệu
- Train
- Tới chỗ train
- Đánh
- Bán đồ
- Train LSV
- Tới LSV
- Tới chỗ train
- Rời LSV
- Dồn vàng
- Tới nơi nhận
- Tới chỗ bán
- Tới nơi train
- Theo dõi
- Tối ưu

Phải giữ đúng quan hệ giữa các hàng/nút theo TLM.

---

# 6. Hệ thống preview nhiều cửa sổ

Phải nghiên cứu và tái tạo chính xác:

- TLM tìm game HWND như thế nào.
- Cách xác định tên nhân vật.
- Cách lấy HP hiển thị bên trên preview.
- Cách capture cửa sổ.
- Cách refresh preview.
- Cách preview nhiều game đồng thời.
- Cách cửa sổ chính lớn và các cửa sổ phụ được bố trí.
- Cách chuyển cửa sổ đang xem.
- Hai nút mũi tên trên từng preview.
- Cách bố trí khi có 1, 2, 3, 4… tài khoản.

Không được thay bằng ảnh tĩnh.

---

# 7. Các chức năng bố trí cửa sổ phải hoạt động thật

Phải phân tích chính xác:

- `Ẩn hết`
- `Đóng xem`
- `Xếp gọn`
- `Xếp chéo`
- `Tách rời`
- `Làm mới`
- `Đóng hết`

và:

`Cột: 1x / 2x / 3x / 4x / 5x`

Mỗi chức năng phải xác định:

`UI → handler → HWND → WinAPI → kết quả cửa sổ`.

---

# 8. Tab Login

Phải tái tạo các phần nhìn thấy:

### Cấu hình game

- Chọn thư mục game
- Mở game
- thông báo đường dẫn

### Cấu hình lịch trình

- Chạy theo lịch
- Hẹn giờ tắt game
- Hẹn giờ mở game
- Tắt máy sau khi tắt game
- Sau khi login:
  - Chờ
  - Party
  - Train
  - Train LSV
  - Dồn vàng

### Cấu hình tài khoản

Bảng:

- chọn
- Tài khoản
- Mật khẩu
- Ẩn captcha
- Login
- Proxy

Nút Login phải hoạt động thật.

Scrollbar và số hàng phải theo TLM.

---

# 9. Tab Party

Phải giữ:

- Auto
- Xếp lưới
- điều khiển hàng/cột
- lựa chọn cửa sổ chính
- `Đồng bộ các cửa sổ`
- `Đồng bộ phím chuột`
- preview
- lựa chọn 1x–5x
- Hủy tách
- Làm mới
- Đóng hết
- thông tin bản quyền.

Đặc biệt cần phân tích cơ chế:

### Đồng bộ phím chuột

Không được tự đoán đây là kiểu:

- SendInput,
- PostMessage,
- SendMessage,
- hook,
- RawInput,
- mirror coordinates

cho đến khi xác minh TLM.

---

# 10. Tab Train

Baseline hiện thấy gồm:

### Cấu hình về thành

Điều kiện:

- Không về
- Khi đầy túi
- Theo chu kỳ
- thời gian chu kỳ
- Hiện cấu hình

### Trong khi train

- Quay lại train khi chết
- Tự kết nối lại khi mất mạng
- Nhặt đồ không dùng hồ lô
- Trị liệu sau khi chết
- tọa độ trị liệu

### Lọc đồ giữ lại

- Không
- Chỉ vũ khí
- Tất cả

### Dùng thú cưỡi

- Thêm

### Tọa độ lưu sẵn

Các cột:

- Tên
- Map
- X
- Y
- Áp dụng hết
- Xóa

### Danh sách tài khoản

- Nhân vật
- Tọa độ bán
- Tọa độ Train

### Điều khiển tất cả

- Tới bản đồ
- Bán đồ
- Tới bãi train
- Đánh

và nút:

`Bắt đầu`

---

# 11. Tab Train LSV

Phải có:

- Quay lại train khi chết
- Tự kết nối lại khi mất mạng
- Trị liệu sau khi chết tại Lạc Dương LSV
- Nhặt đồ:
  - Không
  - Chỉ vũ khí
  - Tất cả

### Thú cưỡi

Ví dụ baseline hiện thấy:

- Đá Minh Châu
- Phím
- thời gian phút/giây
- nút thêm

### Tọa độ

- Tên
- Map
- X
- Y
- Áp dụng
- Xóa

### Điều khiển tất cả

- Tới LSV
- Tới chỗ train
- Đánh
- Rời LSV

Mọi nút phải chạy đúng.

---

# 12. Tab Phó Bản

Phải có:

### Cấu hình tổ đội

Danh sách acc sẵn sàng.

### Cấu hình phó bản

Các lựa chọn hiện thấy:

- Tạo lại đội
- Theo sau đội trưởng
- Nhặt không hồ lô
- Vứt trang bị
- Vứt vật phẩm
- Vứt thuốc
- Nga My buff

### Cấu hình lịch trình

- nhiều nhóm
- đội trưởng
- member
- hoạt động
- tên map
- lần
- status
- xóa
- thêm lịch trình
- tất auto PB
- bắt đầu lịch trình
- xóa nhóm
- thêm nhóm

Phải nghiên cứu luồng thật trong EXE chứ không viết phó bản mới theo suy nghĩ.

---

# 13. Tab Daily

Hai khối lớn:

### Trừng ác

- thời gian đánh ác tặc
- cách về NPC nhận nhiệm vụ
- Ngựa
- Định vị phù
- phím tắt phù
- trị liệu khi HP < 30%
- vị trí trị liệu
- lọc trang bị
- tự kết nối
- hồi sinh khi chết/Địa phủ
- áp dụng cho tất cả acc

### Tàng bảo đồ

- thời gian đánh trong huyệt mộ
- trị liệu HP
- vị trí trị liệu
- reconnect
- hồi sinh

### Điều khiển tất cả

- Tới bổ đầu
- Trị liệu

---

# 14. Tab Đồn

Phải tái tạo:

### Về thành

- Khi đầy túi
- Theo chu kỳ
- số phút

### Phương thức về thành

Ưu tiên:

- Phù 1
- Phù 2
- Phù 3
- Ngựa

### Trong khi train

- quay lại train khi chết
- dừng khi mất kết nối mạng
- tự gỡ kẹt...
- nhặt đồ
- trị liệu

### Tọa độ

- tên
- map
- X/Y
- Train
- xóa

### Danh sách tài khoản

- tọa độ đồn
- acc nhận 1
- acc nhận 2
- thêm acc nhận

### Điều khiển

- Tới nơi nhận
- Tới chỗ bán
- Tới nơi train.

---

# 15. Tab Rao

Phải có:

### Cấu hình rao tự động

Các trường:

- tên
- nội dung rao
- kênh
- lặp (s)
- xóa

Ví dụ:

`Rao 1 | nội dung | Thế giới | 30`

- thêm rao

### Danh sách tài khoản

- Nhân vật
- Nội dung rao

và:

`Bắt đầu`.

---

# 16. Tab Tối ưu

Phải giữ:

### Giám sát CPU/GPU

- biểu đồ CPU
- GPU
- nút `Tách theo dõi`

### Danh sách tài khoản

- Nhân vật
- Giảm cấu hình

### Điều khiển tất cả

- Thấp vừa
- Cực thấp
- Cực đại

Không thay biểu đồ bằng UI giả.

---

# 17. Tab i / thông tin

Phải xác minh nội dung và behavior thật từ TLM.

Không tự suy ra chỉ dựa vào chữ `i`.

---

# 18. Kiến trúc module đã xác định được từ binary

Các tên module đã quan sát được phải được dùng làm bản đồ reverse engineering, gồm ít nhất:

```text id="ktiob5"
TLMTool.py
bag_filter.py
coordinate_utils.py
cpu_monitor.py
daily_tab.py
debug_android_tab.py
dll_injector.py
don_logic.py
donvang_tab.py
emu_chat.py
emu_farm_tab.py
emu_input.py
emu_reader.py
emu_remote.py
emu_setup.py
farm_data.py
farm_tab.py
fast_travel.py
forwarder.py
info_tab.py
item_meta_data.py
login_tab.py
memory_items.py
memory_reader.py
party_tab.py
permission_guard.py
phoban_dungeons.py
phoban_tab.py
proxy_refresh.py
proxy_tab.py
rao_tab.py
splash.py
start_tab.py
toiuu_tab.py
train_lsv_tab.py
utils.py
weapon_ids.py
```

Không được coi danh sách này là đầy đủ cho đến khi scan toàn binary hoàn tất.

---

# 19. Nguyên tắc reverse engineering

Thứ tự ưu tiên:

1. Phân tích static.
2. Strings/imports/symbols.
3. Phân tích module relationship.
4. Resource/data.
5. Runtime observation.
6. API trace.
7. HWND behavior.
8. Config read/write.
9. File I/O.
10. Network nếu có.
11. Memory behavior nếu có.
12. Sau khi đủ bằng chứng mới dựng source.

Không bắt đầu bằng việc đoán code.

---

# 20. Không tự phát triển ngoài luồng

Danh sách cấm:

- không thêm tab mới;
- không thêm chức năng mới;
- không thay thuật toán vì nghĩ tốt hơn;
- không tối ưu code khi chưa parity;
- không đổi framework UI tùy tiện nếu làm giao diện sai;
- không thay PostMessage bằng SendInput hoặc ngược lại khi chưa xác minh;
- không thay timer;
- không đổi thread model;
- không đổi tên config key;
- không đổi format file;
- không tự đổi vị trí lưu dữ liệu;
- không đổi hotkey;
- không tự “fix bug của TLM”.

Nếu TLM có bug mà mục tiêu là clone, trước hết phải clone đúng behavior.

Fix chỉ được làm sau khi có yêu cầu riêng.

---

# 21. Quy tắc task 18 phút

Mỗi task phải:

- có đầu vào cụ thể;
- chỉ nghiên cứu một phạm vi nhỏ;
- không lan sang module khác;
- lưu kết quả;
- tạo checkpoint;
- ghi vấn đề chưa xác minh;
- kết thúc trước khi chat hết thời gian.

Mỗi task dùng trạng thái:

`TODO → ANALYZING → IMPLEMENTED → VERIFIED → DONE`

Không dùng DONE khi chỉ dựng UI.

---

# 22. Kế hoạch thực thi chi tiết

## GIAI ĐOẠN A — Khóa bản gốc

| Task | ~18 phút | Công việc |
|---|---:|---|
| A01 | 18m | Giải nén sạch TLM, lập toàn bộ tree |
| A02 | 18m | SHA-256 toàn bộ file |
| A03 | 18m | Phân loại EXE/DLL/PYD/data/resource |
| A04 | 18m | Xác định Python/Nuitka/compiler/runtime |
| A05 | 18m | Xác minh launcher ngoài và EXE trong `.dist` |
| A06 | 18m | Phân tích bootstrap/update |
| A07 | 18m | Lập `ORIGINAL_MANIFEST` |
| A08 | 18m | Tạo bản copy forensic chỉ đọc |

**Gate A:** chưa qua A thì không viết source.

---

# 23. GIAI ĐOẠN B — Khóa giao diện

| Task | ~18 phút | Công việc |
|---|---:|---|
| B01 | 18m | Chốt kích thước cửa sổ chính |
| B02 | 18m | Tab bar + style chung |
| B03 | 18m | Baseline Login |
| B04 | 18m | Baseline Party |
| B05 | 18m | Baseline Train |
| B06 | 18m | Baseline Train LSV |
| B07 | 18m | Baseline Phó Bản |
| B08 | 18m | Baseline Daily |
| B09 | 18m | Baseline Đồn |
| B10 | 18m | Baseline Rao |
| B11 | 18m | Baseline Tối ưu |
| B12 | 18m | Baseline `i` |
| B13 | 18m | Màu/font/button metrics |
| B14 | 18m | Pixel comparison checklist |

Output:

`docs/UI_BASELINE_TLM.md`

---

# 24. GIAI ĐOẠN C — Multi-window / HWND

Đây là phần ảnh mới bổ sung.

| Task | ~18 phút | Công việc |
|---|---:|---|
| C01 | 18m | TLM tìm cửa sổ game thế nào |
| C02 | 18m | mapping HWND ↔ nhân vật |
| C03 | 18m | cơ chế preview HWND |
| C04 | 18m | update preview và FPS |
| C05 | 18m | cửa sổ chính |
| C06 | 18m | bố trí nhiều cửa sổ |
| C07 | 18m | `Auto` |
| C08 | 18m | `Xếp lưới` |
| C09 | 18m | 1x–5x |
| C10 | 18m | `Xếp gọn` |
| C11 | 18m | `Xếp chéo` |
| C12 | 18m | `Ẩn hết` |
| C13 | 18m | `Đóng xem` |
| C14 | 18m | `Tách rời` |
| C15 | 18m | `Làm mới` |
| C16 | 18m | `Đóng hết` |
| C17 | 18m | chuyển preview trái/phải |
| C18 | 18m | đồng bộ các cửa sổ |
| C19 | 18m | đồng bộ phím chuột |
| C20 | 18m | test đồng thời 3 HWND như ảnh |

Output:

`WINDOW_BEHAVIOR_MATRIX.md`

với format:

```text id="z8qe2b"
Nút
↓
callback
↓
WinAPI/internal call
↓
HWND affected
↓
tọa độ/kích thước
↓
kết quả thực tế
```

---

# 25. GIAI ĐOẠN D — Module inventory

| Task | ~18 phút | Công việc |
|---|---:|---|
| D01 | 18m | Extract toàn bộ module names |
| D02 | 18m | import relationships |
| D03 | 18m | third-party dependencies |
| D04 | 18m | TLM internal dependencies |
| D05 | 18m | strings theo module |
| D06 | 18m | config/data files |
| D07 | 18m | JS/helper executables |
| D08 | 18m | module architecture diagram |

---

# 26. GIAI ĐOẠN E — Core

| Task | ~18 phút | Nội dung |
|---|---:|---|
| E01 | 18m | Main application lifecycle |
| E02 | 18m | Tk root/window creation |
| E03 | 18m | tab loader |
| E04 | 18m | shared state |
| E05 | 18m | config management |
| E06 | 18m | logging |
| E07 | 18m | task/thread management |
| E08 | 18m | shutdown/reload |
| E09 | 18m | error handling |
| E10 | 18m | start/stop coordinator |

---

# 27. GIAI ĐOẠN F — Login

| Task | ~18 phút |
|---|---:|
| F01 UI reconstruction | 18m |
| F02 account storage | 18m |
| F03 password behavior | 18m |
| F04 game path | 18m |
| F05 launcher | 18m |
| F06 account login action | 18m |
| F07 captcha option | 18m |
| F08 proxy — **PHÂN TÍCH/TÀI LIỆU ONLY, KHÔNG PHÁT TRIỂN RUNTIME** | 18m |
| F09 scheduler | 18m |
| F10 post-login routing | 18m |
| F11 parity test | 18m |

---

# 28. GIAI ĐOẠN G — Party

Tương tự nhưng tuyệt đối tách:

- UI
- tìm HWND
- character state
- grid layout
- preview
- sync keyboard
- sync mouse
- configuration
- action buttons
- parity test.

Ước tính **12–15 task × 18 phút**.

---

# 29. GIAI ĐOẠN H — Train

Tách riêng:

- UI
- return-town conditions
- inventory-full
- periodic town
- train coordinates
- heal
- death recovery
- reconnect
- loot filtering
- mount actions
- saved coordinates
- per-account data
- all-account commands
- start/stop FSM
- runtime verification.

Khoảng **15 task × 18 phút**.

---

# 30. GIAI ĐOẠN I — Train LSV

Tách:

- LSV navigation
- Lạc Dương LSV
- train point
- leave LSV
- mount schedule
- item pickup
- treatment
- reconnect
- death handling
- coordinate management
- all-account commands
- parity tests.

Khoảng **12 task × 18 phút**.

---

# 31. GIAI ĐOẠN J — Phó Bản

Không dùng logic phó bản từ những project cũ để tự thay TLM.

TLM là chuẩn.

Tách:

- party formation
- leader
- followers
- schedule
- dungeon list
- number of runs
- status machine
- drop settings
- loot settings
- Nga My buff
- multiple groups
- start/stop
- failure/recovery
- runtime tests.

Khoảng **14 task × 18 phút**.

---

# 32. GIAI ĐOẠN K — Daily

Tách Trừng Ác và Tàng Bảo Đồ.

Khoảng:

- 7 task Trừng Ác
- 6 task Tàng Bảo Đồ
- 2 task shared logic
- 2 task runtime tests

≈ **17 task**.

---

# 33. GIAI ĐOẠN L — Đồn

Tách:

- return mechanism
- return priority
- inventory logic
- coordinates
- receiver accounts
- train state
- heal/reconnect
- all-account actions
- parity test

≈ **10–12 task**.

---

# 34. GIAI ĐOẠN M — Rao

Nhỏ hơn:

- UI
- message storage
- channel selection
- interval
- account assignment
- start/stop worker
- parity test

≈ **7 task**.

---

# 35. GIAI ĐOẠN N — Tối ưu

Phải phân biệt rõ:

- UI monitor
- CPU collection
- GPU collection
- detached monitor
- graphics configuration
- `Thấp vừa`
- `Cực thấp`
- `Cực đại`
- per-account action
- multi-account action
- parity test

≈ **10 task**.

---

# 36. GIAI ĐOẠN O — Memory / item subsystem

Phân tích các module:
```text id="3r1u9y"
memory_reader
memory_items
bag_filter
item_meta_data
weapon_ids
```

Không được dựa vào code dự án cũ nếu TLM khác.

Cần xác định:

- process selection
- addresses/offsets
- read strategy
- validation
- inventory structure
- item classification
- filter behavior.

---

# 37. GIAI ĐOẠN P — Emulator subsystem

Các module:

```text id="ej6t9d"
emu_input
emu_reader
emu_remote
emu_setup
emu_chat
emu_farm_tab
debug_android_tab
```

Phải xác định chúng có đang thực sự được dùng trong TLM 2.1.2 hay là code dormant.

Không tự hiển thị tính năng dormant lên UI.

---

# 38. GIAI ĐOẠN Q — Proxy/network

> **USER SCOPE LOCK — KHÔNG PHÁT TRIỂN PROXY (2026-10-04).**
> - Không implement, mở rộng, sửa logic runtime hoặc build mới các chức năng Proxy/network.
> - Không phát triển `proxy_tab`, `proxy_refresh`, `forwarder`, `forwarder.exe`, `Default.ppx`.
> - F08 đã hoàn thành ở mức **phân tích/tài liệu bằng chứng** để hiểu EXE gốc; không biến các bằng chứng đó thành task phát triển runtime.
> - Khi các phần khác tham chiếu Proxy, chỉ được giữ tài liệu/contract hoặc phần tương thích tối thiểu cần để không phá luồng khác; **không phát triển tính năng Proxy** trừ khi người dùng mở lại scope bằng yêu cầu mới.
> - Không xóa các tài liệu F08 đã có vì chúng là bằng chứng phục vụ đối chiếu/parity.

Các module:

```text id="mutq1c"
proxy_tab
proxy_refresh
forwarder
forwarder.exe
Default.ppx
```

Phân tích:

- protocol
- process launch
- port
- lifetime
- refresh
- account binding.

---

# 39. GIAI ĐOẠN R — Data/resources

Đối với `.dat`, `.old`, `.bak`, resource:

Không sửa.

Phải lập:

```text id="aonp4o"
filename
size
hash
magic/header
readers
writers
runtime usage
```

Unknown thì ghi:

`UNKNOWN`

không đoán.

---

# 40. GIAI ĐOẠN S — Dựng source

Chỉ bắt đầu khi đủ thông tin.

Cấu trúc có thể đi theo module gốc:

```text id="58tg6y"
src/
    TLMTool.py
    login_tab.py
    party_tab.py
    farm_tab.py
    train_lsv_tab.py
    phoban_tab.py
    daily_tab.py
    donvang_tab.py
    rao_tab.py
    toiuu_tab.py
    ...
```

Nhưng tên/chia module cuối cùng phải dựa trên manifest TLM.

---

# 41. Không “clean architecture” ở giai đoạn clone

Mục tiêu đầu tiên:

> giống TLM.

Không phải:

> code đẹp nhất.

Nếu TLM có shared global state, không được tự biến thành dependency injection trước khi parity hoàn tất.

Sau khi bản clone được khóa mới có thể tạo nhánh refactor riêng — nếu bạn yêu cầu.

---

# 42. GIAI ĐOẠN T — Build Nuitka

Phải xác định chính xác:

- Python 3.10.x
- Nuitka version tương thích
- standalone
- Windows target
- Tk/Tcl plugins
- icon
- data includes
- PYD/DLL
- output folder
- launcher.

Phải tạo script kiểu:

```text id="cfkezx"
build.bat
build.ps1
requirements-build.txt
```

để AI khác cũng build được.

---

# 43. GIAI ĐOẠN U — So sánh static

So:

- file count
- module count
- resource
- DLL
- package layout
- startup imports
- strings quan trọng
- config defaults.

Kết quả:

`STATIC_PARITY_REPORT.md`

---

# 44. GIAI ĐOẠN V — So sánh giao diện

Từng tab:

```text id="ejb9r8"
TLM screenshot
vs
new build screenshot
```

Kiểm:

- width/height
- tab position
- widgets
- label
- alignment
- spacing
- colors
- visible state.

Không đánh giá bằng “nhìn khá giống”.

Phải có checklist.

---

# 45. GIAI ĐOẠN W — Functional parity

Tạo ma trận:

| Chức năng | TLM | New | PASS |
|---|---|---|---|
| Login | hành vi thật | hành vi thật | ✓/✗ |
| Reload | ... | ... | |
| Xếp gọn | ... | ... | |
| Train | ... | ... | |
| Bán đồ | ... | ... | |
| Tới LSV | ... | ... | |
| Trừng ác | ... | ... | |
| ... | ... | ... | |

Một ô chưa test = `UNVERIFIED`.

Không tính là PASS.

---

# 46. GIAI ĐOẠN X — Multi-account stress test

Ít nhất test:

- 1 game
- 2 game
- 3 game như ảnh
- nhiều hơn nếu môi trường cho phép.

Kiểm:

- CPU
- memory
- preview
- grid
- control
- start/stop
- hidden/minimized window
- resize
- game đóng bất ngờ
- game reconnect.

---

# 47. GIAI ĐOẠN Y — GitHub

Repo:

`ngmthang-g/2222222222222222222222222222222`

Sau khi đủ điều kiện mới đưa lên.

Cấu trúc gợi ý:

```text id="rbrvs0"
/
├─ src/
├─ resources/
├─ build/
├─ docs/
├─ tests/
├─ tools/
├─ original_manifest/
├─ build.bat
├─ requirements.txt
├─ README.md
└─ .github/workflows/
```

Không push file rác reverse engineering tạm thời vào root.

---

# 48. GitHub Actions

Workflow phải:

1. checkout
2. setup Python
3. install pinned deps
4. build
5. validate artifacts
6. package
7. upload artifact.

Không để workflow build phiên bản khác với local.

---

# 49. Versioning

Bản đầu nên đặt rõ:

`TLM_REBUILD_0.1`

Trong giai đoạn reverse engineering.

Khi đạt parity đầy đủ mới coi là:

`TLMTool_2.1.2_REBUILT`

Không tự gọi `2.1.3`, vì không có phát triển mới.

---

# 50. Quy tắc Git commit

Mỗi task một commit nhỏ.

Ví dụ:

```text id="zlvmp7"
task/A01-freeze-original
task/B05-train-ui-baseline
task/C11-window-diagonal-layout
task/H07-train-healing-analysis
```

Không commit 20 thay đổi không liên quan cùng lúc.

---

# 51. Báo cáo cho mỗi task

Mỗi task kết thúc bằng tối thiểu:

```text id="4flw1c"
TASK:
STATUS:
FILES READ:
FILES MODIFIED:
WHAT WAS VERIFIED:
WHAT IS STILL UNKNOWN:
TEST:
NEXT TASK:
```

Điều này cực quan trọng vì mỗi phiên chỉ khoảng 20 phút.

---

# 52. File trạng thái trung tâm

Tạo:

`PROJECT_STATUS.md`

Ví dụ:

```text id="3emdye"
A01 DONE
A02 DONE
A03 VERIFIED
A04 TODO

Current:
C07 - Party Auto layout

Do not touch:
Train
Train LSV
Phó Bản
```

Phiên AI sau mở file này là biết tiếp tục từ đâu.

---

# 53. Một file cấm sửa

Tạo:

`SCOPE_LOCK.md`

Nội dung chính:

> Dự án này là reconstruction TLMTool 2.1.2.
>
> CẤM tự thêm chức năng.
>
> CẤM sửa module ngoài task hiện tại.
>
> CẤM đổi UI nếu không có bằng chứng.
>
> CẤM đánh dấu DONE nếu chỉ có UI.
>
> Mọi hành vi phải được đối chiếu với TLM.

---

# 54. Definition of Done cuối dự án

Dự án chỉ được coi là hoàn thành khi:

- Source build được từ máy sạch.
- EXE chạy.
- Không thiếu tab.
- Không thiếu nút.
- Không có nút giả.
- Layout giống baseline.
- Multi-window thực sự hoạt động.
- Preview thực sự hoạt động.
- Các tính năng chính hoạt động như TLM.
- Config lưu/nạp đúng.
- Multi-account chạy.
- Artifact GitHub build được.
- Có manifest.
- Có báo cáo parity.
- Mọi mục chưa xác minh được liệt kê rõ.

---

# 55. Thứ tự bắt đầu thực tế

Không nên bắt đầu ngay từ Train hoặc Phó Bản.

Thứ tự đúng là:

**Original package → fingerprint → UI baseline → HWND/Party → module inventory → core → từng tab → build → parity → GitHub.**

Lý do: Party/HWND và core rất có khả năng là nền mà nhiều tab khác dùng chung.

---

## Chốt phạm vi

Kể từ plan này, yêu cầu chính thức là:

> **Tái tạo TLMTool 2.1.2 thành source + EXE mới, không tự phát triển ngoài TLM; giao diện phải bám ảnh gốc; chức năng phải hoạt động thật giống TLM; multi-window và preview phải hoạt động thật; mọi task chia khoảng 18 phút; kết quả đưa lên repo `2222222222222222222222222222222`; mọi thứ chưa xác minh phải ghi rõ chứ không được tự bịa.**

Và điểm quan trọng nhất: **“giống giao diện” không đồng nghĩa “hoàn thành”. Chỉ khi UI + logic + runtime đều tương đương thì mới được đánh PASS.**