# Ảnh bằng chứng

Đủ 9 ảnh bắt buộc theo hướng dẫn nộp VLearn. Cloud Run không thực hiện nên không có ảnh tùy chọn `05-cloud-run.png`.

| Ảnh | Nội dung |
|---|---|
| `01-function-calling.png` | Gemini qua 9router chọn hàm; app thực thi mock và tổng hợp kết quả. |
| `02-mcp-client.png` | MCP stdio discovery và gọi tool cho ba thành phố. |
| `03a-auth-ok.png` | Token hợp lệ khám phá và gọi tool thành công. |
| `03a-auth-fail.png` | Thiếu/sai token đều bị từ chối HTTP 401. |
| `03b-registry.png` | Tìm theo tag/keyword và chọn tool v2. |
| `03c-versioning.png` | Metadata server://info, tool v1 và v2 cùng hoạt động. |
| `04-verify-setup.png` | Kiểm tra model, dependency, MCP initialize/discovery/health đạt. |
| `04-adk-current.png` | ADK Web: thời tiết Hà Nội từ WeatherAPI thật. |
| `04-adk-forecast.png` | ADK Web: dự báo Tokyo ba ngày từ WeatherAPI thật. |

Bảy ảnh output là ảnh chụp trang trình duyệt đọc stdout đã lưu từ chương trình chạy thực tế, không giả giao diện terminal và không thay đổi kết quả. Nhãn nguồn log trong ảnh là tài liệu kiểm chứng giữ local, không nằm trong repo nộp. Hai ảnh ADK là ảnh giao diện chat thực tế. Phần 01–03 dùng mock; Lab 04 dùng WeatherAPI thật. Không hiển thị key hoặc token thật.
