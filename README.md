# LIMO ROS 2 Humble Toolkit

Bộ tài liệu và script hỗ trợ triển khai Navigation2, chạy thí nghiệm SLAM và
thu số liệu định lượng trên xe AgileX LIMO dùng ROS 2 Humble.

## Nội dung chính

| Khu vực | Mục đích |
| --- | --- |
| `nav2/` | Script cài đặt, reset, chạy và kiểm tra Navigation2 trên LIMO thật. |
| `scripts/` | Pipeline thí nghiệm SLAM: preflight, chạy SLAM, record bag, lưu map, đánh giá RMSE/entropy/resource. |
| `tudong/` | Công cụ tự động đo goal navigation: success rate, thời gian, path length, goal error, recovery, collision. |
| `huong_dan/` | Các hướng dẫn thao tác chi tiết theo từng kịch bản thí nghiệm. |
| `docs/` | Tài liệu dev dạng website bằng VitePress. |

## Cài đặt dự án

### 1. Cài công cụ hệ thống

Trên Ubuntu/ROS 2 Humble, cài Python, pip, venv, Node.js và npm:

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nodejs npm
```

Kiểm tra phiên bản:

```bash
python3 --version
pip3 --version
node --version
npm --version
```

VitePress khuyến nghị Node.js 18+. Nếu `node --version` thấp hơn 18, nên cài
Node.js 18/20 bằng NodeSource hoặc `nvm` trước khi chạy docs.

### 2. Cài thư viện Python

Tại root repo:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Các thư viện trong `requirements.txt` phục vụ đánh giá map, RMSE, xử lý dữ liệu
và resource monitoring. Riêng script đọc rosbag cần chạy trong môi trường ROS 2
Humble đã source để có `rosbag2_py`, `rclpy` và `rosidl_runtime_py`.

### 3. Cài thư viện Node/VitePress

```bash
npm install
```

Lệnh này cài VitePress và tạo/cập nhật `node_modules/` từ `package-lock.json`.

## Chạy nhanh tài liệu VitePress

```bash
npm run docs:dev
```

Sau đó mở địa chỉ VitePress in ra trong terminal, thường là:

```text
http://localhost:5173
```

Build bản static:

```bash
npm run docs:build
npm run docs:preview
```

## Quy trình LIMO tối thiểu

Trên LIMO, mỗi terminal nên source ROS 2 và workspace trước:

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
export ROS_DOMAIN_ID=99
```

Chạy bringup robot, kiểm tra topic/TF, sau đó chạy từng nhóm script:

```bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
phase_3_slam/preflight_slam.sh
phase_3_slam/start_slam.sh --system slam_toolbox --imu off
phase_4_data_collection/run_record_experiment.sh --system slam_toolbox --scenario A --run 1 --imu off
```

Navigation2 có hướng dẫn riêng trong `nav2/README.md`, còn quy trình thí nghiệm
SLAM mới nhất nằm tại `huong_dan/chay_lai_3_slam_sau_khi_sua.md`.

## Ghi chú dữ liệu

Repo này ưu tiên lưu script, cấu hình và tài liệu. Các file nặng hoặc sinh ra
khi chạy thí nghiệm như rosbag, map, kết quả CSV, cache Python/Node và build
artifact đã được đưa vào `.gitignore`.
