# Quyết định 2026-10-12 — Chấp nhận tạm thời S164 để tiếp tục xây dựng TLMTool

**Nguồn quyết định:** Người dùng trực tiếp yêu cầu: "Có thể coi như nó đã OK (đánh dấu để nhớ mốc này cho sau này) rồi tiếp tục hoàn thiện tool mới được không".

## Trạng thái phải phân biệt
- **S164: USER_ACCEPTED_DEFERRED_EXTERNAL_VERIFICATION**: chấp nhận **để dời việc kiểm chứng** và cho phép triển khai tiếp các chức năng không phụ thuộc; KHÔNG phải VERIFIED/DONE/PASS, KHÔNG phải bản quyền hợp lệ.
- **S163 vẫn là milestone source đã kiểm thử mới nhất** cho tới khi có milestone code mới vượt đủ CI.
- **Info service/issuer/RSA-HMAC/heartbeat, F05 game launch/injection và F06 login thực**: giữ nguyên `UNVERIFIED / BLOCKED` trong danh sách nợ kiểm chứng cuối dự án.
- S01 `main()` tiếp tục **fail-closed/exit=2**, không bật GUI bằng token giả, không tự cấp quyền, không vô hiệu hóa hoặc giả định license, không sao chép khóa/token bí mật, không phát hành EXE "hoàn chỉnh".
- PLAN.md/SCOPE_LOCK.md, baseline ảnh, gói EXE/ZIP gốc và DATA-2222 giữ nguyên; Proxy vẫn excluded.

## Chính sách CONTINUE từ quyết định này
Không lặp lại vòng S164 blocker nếu không có dữ liệu mới. Chuyển `NEXT_ACTION` sang task phát triển kế tiếp **độc lập với dịch vụ/ game**, chọn đúng logic đã có bằng chứng TLM gốc; không tự nhận runtime-parity. Mỗi thay đổi source cần test CI Windows thực, không refactor/sửa code đã đúng. Nếu tính năng buộc phải sử dụng Info/game đang thiếu, giữ `BLOCKED` riêng và chọn công việc độc lập khác.

## Mục tiêu kế tiếp S165
Kiểm tra và tích hợp **TkTrainComposition** đã xây dựng (H01 Train configuration) vào cơ chế lazy builders E03 **chỉ với opt-in PermissionGuard và running_count được truyền tường minh**. Không sửa `TLMTool.py main()`, không tự hiện Train cho khách không có Info, không tạo nút Bắt đầu/Bán đồ/Đánh giả. Bắt đầu từ source/test hiện có, giữ toàn bộ thử nghiệm cũ; nếu chưa thể xác nhận, ghi rõ blocker thay vì tự bịa.

## Điều kiện quay lại S164
Một phiên thử nghiệm gốc được cấp hợp lệ với chứng cứ xác minh ký số đáng tin cậy hoặc runtime game Thần Long khớp phiên bản để quan sát giao diện/Win32 trong phạm vi được cho phép. Không đăng khóa bí mật, token thực, thông tin máy/tài khoản lên GitHub.

**Định nghĩa hoàn thành sản phẩm không thay đổi:** phải có UI + behavior + runtime parity đo được và EXE chức năng thực, không chỉ unit-tests hay bản diagnostic.
