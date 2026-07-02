# Kiến trúc repo

## Sơ đồ thư mục

| Đường dẫn | Vai trò |
| --- | --- |
| `nav2/` | Script triển khai Navigation2 trên LIMO: cài dependency, reset lifecycle, chạy Nav2/RViz, kiểm tra TF và velocity. |
| `scripts/config/` | Cấu hình Gmapping, Cartographer và SLAM Toolbox dùng cho thí nghiệm. |
| `scripts/phase_3_slam/` | Preflight và launcher thống nhất cho các hệ SLAM. |
| `scripts/phase_4_data_collection/` | Record rosbag và lưu map theo naming convention. |
| `scripts/phase_6_evaluation/` | Đánh giá map, trích trajectory, tính RMSE và merge kết quả. |
| `scripts/phase_7_imu_analysis/` | So sánh IMU on/off và kiểm tra cấu hình IMU trong workspace. |
| `scripts/resource_monitoring/` | Đo CPU/RAM, tổng hợp bảng resource và plot so sánh. |
| `tudong/` | Đo navigation tự động qua action `NavigateToPose`. |
| `huong_dan/` | Tài liệu thao tác chi tiết theo từng lần sửa/thí nghiệm. |
| `docs/` | Website tài liệu dev bằng VitePress. |

## Quy ước dữ liệu

Các artifact sinh ra khi chạy thí nghiệm nên nằm dưới `scripts/data/` hoặc
`tudong/results/`, ví dụ:

```text
scripts/data/bags/
scripts/data/maps/
scripts/data/results/
scripts/data/resources/
tudong/results/
```

Những thư mục này đã được ignore để repo không lưu rosbag, map và bảng kết quả
nặng theo mặc định.

## Quy ước frame và topic

Pipeline SLAM mới dùng chung các quy ước:

| Thành phần | Giá trị |
| --- | --- |
| Global frame | `map` |
| Odom frame | `odom` |
| Base frame | `base_link` |
| Laser topic | `/scan` |
| Map resolution | `0.05 m/pixel` |
| Laser range hữu ích | `0.10-12.0 m` |

Nếu các quy ước này bị lệch giữa thuật toán, metric map/trajectory sẽ không còn
so sánh được trực tiếp.
