# Detection Approach — DESIGN.md

## Approach tôi dùng
Rule-based Thresholds kết hợp Sliding Window cơ bản.

## Tại sao chọn approach này
Vì data là streaming theo thời gian thực (real-time stream) nên việc dùng một số rules cố định (Static Thresholds) cho các metrics cơ bản và một Sliding Window (lưu trạng thái nhỏ trong RAM) rất hiệu quả, có độ trễ cực thấp và dễ triển khai/mở rộng.

## Cách hoạt động
Pipeline nhận POST requests chứa metrics. Mỗi metric sẽ được đi qua 3 rules kiểm tra tương ứng với 3 loại fault:
- **`memory_leak`**: Dựa vào `memory_usage_bytes`, nếu vượt ngưỡng 900MB sẽ được cảnh báo.
- **`traffic_spike`**: Dựa vào `http_requests_per_sec`, nếu vượt ngưỡng 200 (thông thường chỉ 80-160) sẽ được cảnh báo.
- **`dependency_timeout`**: Dựa vào `upstream_timeout_rate` và `http_5xx_rate`, nếu timeout hoặc tỷ lệ 5xx bất thường sẽ tạo cảnh báo.

## Parameters tôi chọn
- **Ngưỡng `memory_leak` (900,000,000 bytes)**: Khoảng bình thường là ~800MB ± 20MB. Chọn 900MB vì đây là mức chênh lệch rõ ràng so với bình thường và chưa đến mức OOM (2GB), đủ sớm để cảnh báo.
- **Ngưỡng `traffic_spike` (200 req/s)**: Ngưỡng bình thường là 80-160, khi vượt qua 200 có thể kết luận chắc chắn là có đột biến traffic.
- **Ngưỡng `dependency_timeout` (`upstream_timeout_rate` > 0.8% hoặc `http_5xx_rate` > 1.5%)**: Tỉ lệ bình thường lần lượt là 0-0.4% và 0-0.8%. Chọn mức ngưỡng khoảng gấp đôi mức bình thường để bắt lỗi.

## Cải thiện nếu có thêm thời gian
Nếu có thêm thời gian, có thể dùng các kỹ thuật phân tích xu hướng tĩnh (Statistical Outlier Detection) như Z-Score, hay Machine Learning nhẹ (như Isolation Forest) để không bị phụ thuộc vào Hardcoded Thresholds. Ngoài ra, việc dùng sliding window kết hợp tính độ dốc tăng của memory sẽ giúp bắt `memory_leak` sớm hơn thay vì chờ đạt mốc 900MB.
