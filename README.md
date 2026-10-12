# TLMTool — bản xây dựng lại độc lập

> **QUYẾT ĐỊNH CHỦ DỰ ÁN 2026-10-12: source/tool MỚI KHÔNG dùng giấy phép, quyền, token, heartbeat hoặc máy chủ bản quyền TLM gốc.** Đây là thay đổi có chủ đích so với bản gốc, chỉ áp dụng vào sản phẩm đang phát triển trong repository này.

## Đường chạy đúng cho TOOL MỚI

Trên Windows có Python 3.10 và Tkinter:

```powershell
python src/TLMToolIndependent.py
```

Để kiểm tra liên kết module mà không mở GUI:

```powershell
python src/TLMToolIndependent.py --self-check
```

Bản Windows **mới nhất S174** được đóng gói và đã **kiểm tra mở cửa sổ GUI từ EXE thật** tại [GitHub Actions S174](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38197634022), artifact [`S174_REAL_PACKAGED_INDEPENDENT_GUI_WIN64_PARTIAL_NOT_GAME`](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38197634022/artifacts/11723669511), có `S174_TLMTOOL_INDEPENDENT_GUI_PARTIAL.exe` và các thư viện trong cùng thư mục. **Giữ nguyên toàn bộ thư mục**; đừng chép riêng EXE.

Các tab source-backed đang có: **▶ Start, Login, Party, Train (cấu hình/quan sát read-only một phần), Train LSV (checkbox, radio, thêm/sửa/xóa tọa độ, **lịch buff thủ công có Sửa/Lưu/Xóa trong phiên** và **danh sách cửa sổ HWND/PID chỉ đọc từ S09**; bảo vệ dữ liệu cũ), Thông tin độc lập**. Tab chưa có điều khiển game thật được giữ ẩn. Tab hiển thị theo module đã được triển khai, **không theo giấy phép TLM gốc**.

Chế độ độc lập dùng `src/local_feature_policy.py`, `src/local_tool_status_tab.py`, `src/TLMToolIndependent.py`; các mục Train offline sử dụng source đã xây dựng tại S132/S165/S166/S167 và không chờ Info issuer. Vẫn kiểm tra HWND/PID, thao tác file an toàn, thread teardown và giới hạn của giao diện đang có.

## Phân biệt source lịch sử

- `src/TLMTool.py` **là entrypoint lịch sử cho bài test/đóng gói chẩn đoán S36**; nó vẫn trả mã 2 do thiếu dịch vụ Info gốc. **Không dùng nó để chạy tool mới.**
- `src/permission_guard.py`, `src/info_state.py` và các unit test token chỉ giữ để đối chiếu TLM gốc và bảo vệ hồi quy source cũ. Chúng **không được gọi làm điều kiện mở tab trên đường chạy `TLMToolIndependent.py`**.
- [PLAN.md](PLAN.md) là thẩm quyền thay đổi chính sách; [STATE.md](STATE.md) cho biết đúng milestone/NEXT_ACTION; [S168](docs/tasks/S168.md) là tài liệu chi tiết sửa source.

## Giới hạn hiện tại

**S174 đã kiểm chứng EXE thực:** GitHub Actions Win64 đã chạy EXE ở chế độ mở cửa sổ bình thường (không phải chỉ `--self-check`), nhận HWND/PID chính xác, chụp ảnh cửa sổ, xác nhận mutex ngăn mở trùng, `WM_CLOSE` đóng sạch và mở lại được. Ảnh thật, JSON và log nằm trong artifact. Chưa kiểm chứng toàn bộ tab của bản EXE bằng thao tác game hoặc với nhân vật Thần Long thật.

**Trị liệu `heal_map`:** theo I07, đây là khóa cấu hình tương thích cũ nhưng đường xử lý trị liệu gốc **bỏ qua khóa này**, dùng MapID `10000` (163,237) cố định. Không thêm bộ chọn đích trị liệu giả và không đổi giá trị `heal_map` lịch sử.

**S172 danh sách nhân vật:** hiện chỉ có cửa sổ game xác minh bằng HWND/PID. Chưa có nguồn đọc tên nhân vật (`RoleName`) từ game, do đó **chưa gắn tọa độ theo nhân vật hoặc ghi `acc_<character>_train`**. Bài native test dùng một cửa sổ Tk thật và metadata nhận diện game chỉ giả lập bên trong test; chưa xác nhận bằng Thần Long thực tế.

**Dạ Minh Châu:** chưa xác minh số thứ tự `buff_*` của dòng cố định. S173 cho Thêm/Sửa/Xóa **chỉ các dòng buff đã tạo trong phiên hiện tại**, không sửa/xóa dòng cũ; sau khi nạp lại hoặc mở lại tool, các dòng đã lưu được bảo vệ. Chưa có chức năng tự gửi phím vào game.

**S174 là source + GUI/EXE Windows chạy độc lập ở mức MỘT PHẦN, không phải bản TLM 2.1.2 hoàn chỉnh.** Hoạt động gameplay (Train tự động, bán đồ, Phó Bản, Daily, Train LSV điều khiển game...) và parity với game thực còn thiếu/chưa kiểm chứng. Không có nút điều khiển game giả; không patch/inject/sửa TLM gốc hay gọi máy chủ bản quyền của bên thứ ba. DATA-2222 là nguồn CHỈ ĐỌC; Proxy không phát triển.

**Kết quả S171:** [Windows CI 2614/2614 + native Train LSV buff/INI/HWND + independent partial EXE artifact](https://github.com/ngmthang-g/2222222222222222222222222222222222222/actions/runs/38194041101); Stage S và S36 diagnostic độc lập đều PASS. Trước mỗi CONTINUE, đọc PLAN và STATE, không dựng lại license/Info gốc trong tool mới.
