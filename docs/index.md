---
layout: home

hero:
  name: LIMO Dev Docs
  text: ROS 2 Humble toolkit cho Navigation2 và SLAM
  tagline: Tài liệu vận hành, dev workflow và lệnh kiểm tra cho thí nghiệm trên xe AgileX LIMO.
  image:
    src: /logo.svg
    alt: LIMO
  actions:
    - theme: brand
      text: Bắt đầu
      link: /getting-started
    - theme: alt
      text: Lệnh nhanh
      link: /reference/commands

features:
  - title: Navigation2 trên LIMO thật
    details: Cài package, bringup base/lidar, reset Nav2, chạy RViz và kiểm tra cmd_vel/TF.
  - title: Pipeline SLAM có kiểm soát
    details: Dùng chung frame, scan, độ phân giải map và quy trình record để so sánh Gmapping, Cartographer, SLAM Toolbox.
  - title: Đo kiểm định lượng
    details: Tính entropy, RMSE, resource usage và metric navigation như success rate, path length, goal error.
  - title: Tài liệu thao tác nhanh
    details: Gom các lệnh thường dùng thành checklist để giảm sai lệch khi chạy trên nhiều terminal.
---

## Mục tiêu repo

Repo này giữ các script và hướng dẫn cần thiết để tái lập thí nghiệm trên LIMO:

- Chạy Navigation2 ổn định trên ROS 2 Humble.
- Chạy ba hệ SLAM với cấu hình đầu vào thống nhất.
- Record rosbag, lưu map, trích trajectory và tính metric.
- Thu số liệu navigation tự động theo từng thuật toán.

::: tip Nên đọc trước
Bắt đầu từ [Bắt đầu](/getting-started), sau đó chọn workflow theo việc cần làm:
[Thí nghiệm SLAM](/workflows/slam), [Navigation2](/workflows/nav2) hoặc
[Đo navigation tự động](/workflows/navigation-metrics).
:::
