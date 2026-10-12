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

Bản Windows được đóng gói trên GitHub Actions ở [workflow S168](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/workflows/s168-independent-tool.yml), artifact `S168_INDEPENDENT_PARTIAL_WINDOWS_X64_NOT_GAME_PARITY`, file `S168_TLMTOOL_INDEPENDENT_PARTIAL.exe` cùng thư viện bên trong thư mục `S168_TLMTOOL_INDEPENDENT_PARTIAL`. **Phải giữ nguyên cả thư mục**, không chỉ chép riêng EXE.

Các tab source-backed đang có: **▶ Start, Login, Party, Train (cấu hình và quan sát read-only một phần), Thông tin độc lập**. Tab chưa có điều khiển game thật được giữ ẩn. Tab hiển thị theo module đã được triển khai, **không theo giấy phép TLM gốc**.

Chế độ độc lập dùng `src/local_feature_policy.py`, `src/local_tool_status_tab.py`, `src/TLMToolIndependent.py`; các mục Train offline sử dụng source đã xây dựng tại S132/S165/S166/S167 và không chờ Info issuer. Vẫn kiểm tra HWND/PID, thao tác file an toàn, thread teardown và giới hạn của giao diện đang có.

## Phân biệt source lịch sử

- `src/TLMTool.py` **là entrypoint lịch sử cho bài test/đóng gói chẩn đoán S36**; nó vẫn trả mã 2 do thiếu dịch vụ Info gốc. **Không dùng nó để chạy tool mới.**
- `src/permission_guard.py`, `src/info_state.py` và các unit test token chỉ giữ để đối chiếu TLM gốc và bảo vệ hồi quy source cũ. Chúng **không được gọi làm điều kiện mở tab trên đường chạy `TLMToolIndependent.py`**.
- [PLAN.md](PLAN.md) là thẩm quyền thay đổi chính sách; [STATE.md](STATE.md) cho biết đúng milestone/NEXT_ACTION; [S168](docs/tasks/S168.md) là tài liệu chi tiết sửa source.

## Giới hạn hiện tại

**S168 là source + GUI/EXE Windows chạy độc lập ở mức MỘT PHẦN, không phải bản TLM 2.1.2 hoàn chỉnh.** Hoạt động gameplay (Train tự động, bán đồ, Phó Bản, Daily, Train LSV...) và parity với game thực còn thiếu/chưa kiểm chứng. Không có nút điều khiển game giả; không patch/inject/sửa TLM gốc hay gọi máy chủ bản quyền của bên thứ ba. DATA-2222 là nguồn CHỈ ĐỌC; Proxy không phát triển.

**Kết quả S168:** [Windows CI 2558/2558 + native Tk/INI/HWND + independent EXE artifact](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38190676711); Stage S và S36 diagnostic độc lập đều PASS. Trước mỗi CONTINUE, đọc PLAN và STATE, không dựng lại license/Info gốc trong tool mới.
