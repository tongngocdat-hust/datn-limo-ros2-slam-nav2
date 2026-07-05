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

## Quy trình thí nghiệm SLAM khuyến nghị

Pipeline hiện tại dùng ba hệ SLAM chính: Cartographer, Gmapping và SLAM
Toolbox. Khi so sánh, chỉ chạy một thuật toán tại một thời điểm, dùng cùng
tuyến đường, cùng scenario và cùng trạng thái IMU để kết quả có ý nghĩa.

Trình tự tổng quát:

1. Bringup LIMO và kiểm tra `/scan`, `/odom`, TF `odom -> base_link`.
2. Chạy `phase_3_slam/preflight_slam.sh` và chỉ tiếp tục khi preflight báo
   `PASS`.
3. Chạy thuật toán SLAM bằng `phase_3_slam/start_slam.sh`.
4. Record rosbag bằng `phase_4_data_collection/run_record_experiment.sh`.
5. Đo CPU/RAM song song bằng `resource_monitoring/measure_process_resources.py`.
6. Lưu map bằng `phase_4_data_collection/save_map.sh` khi SLAM vẫn đang chạy.
7. Dừng record, monitor và SLAM, sau đó trích trajectory từ bag.

Ví dụ tên dữ liệu được chuẩn hóa theo mẫu:

```text
<system>_<scenario>_run<run>_imu_<on|off>
```

Ví dụ:

```text
slam_toolbox_A_run1_imu_off
cartographer_C_run2_imu_off
gmapping_B_run3_imu_on
```

## Đánh giá kết quả

Các script đánh giá nằm trong `scripts/phase_6_evaluation/`:

| Script | Chức năng |
| --- | --- |
| `extract_trajectory_from_bag.py` | Trích quỹ đạo từ rosbag ra CSV. |
| `compute_rmse.py` | Tính RMSE giữa trajectory đánh giá và trajectory reference. |
| `evaluate_maps.py` | Tính metric map như entropy và SSIM khi có map reference. |
| `merge_results.py` | Ghép các kết quả riêng lẻ thành bảng tổng hợp. |

Với dữ liệu mới, ưu tiên dùng trajectory `*_slam.csv` thay vì `_odom.csv`.
Reference nên được tạo một lần từ run baseline, thường là SLAM Toolbox run 1
theo từng scenario:

```bash
cp data/results/trajectories/slam_toolbox_A_run1_imu_off_slam.csv \
   data/results/trajectories/reference_A.csv
```

Không ghi đè `reference_A.csv`, `reference_B.csv` hoặc `reference_C.csv` bằng
run 2/run 3 để giữ mốc so sánh ổn định.

## Navigation2 và đo goal tự động

Thư mục `nav2/` chứa script cài đặt, reset, chạy và kiểm tra Nav2 trên LIMO
thật. Sau khi Nav2 chạy ổn, thư mục `tudong/` có thể dùng để tự động gửi goal
và tổng hợp các chỉ số:

- success rate;
- navigation time;
- path length;
- goal error;
- recovery count;
- collision count.

Luôn dùng cùng map, cùng vị trí xuất phát, cùng goal và cùng cấu hình Nav2 khi
so sánh các thuật toán.

## Ghi chú dữ liệu

Repo này ưu tiên lưu script, cấu hình và tài liệu. Các file nặng hoặc sinh ra
khi chạy thí nghiệm như rosbag, map, kết quả CSV, cache Python/Node và build
artifact đã được đưa vào `.gitignore`.

## Checklist trước khi commit/push

Trước khi commit, nên kiểm tra nhanh:

```bash
git status --short
python3 -m py_compile scripts/phase_6_evaluation/*.py scripts/phase_7_imu_analysis/*.py
npm run docs:build
```

Nếu chỉ sửa tài liệu, ít nhất chạy:

```bash
git diff -- README.md
git status --short
```

Các dữ liệu thí nghiệm nặng như `data/bags/`, `data/maps/`, `data/results/`,
`data/resources/`, `*.db3`, `*.mcap`, `node_modules/` và cache Python không nên
đưa vào commit.

Gợi ý commit:

```bash
git add README.md
git commit -m "docs: update LIMO experiment README"
git push
```
