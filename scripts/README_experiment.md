# Hướng dẫn thí nghiệm SLAM LIMO ROS 2 Humble

> Quy trình bên dưới là bản cũ. Với dữ liệu mới, hãy dùng
> `../huong_dan/chay_lai_3_slam_sau_khi_sua.md`. Bản mới dùng cấu hình thống
> nhất, quỹ đạo `*_slam.csv` và căn map theo metadata `.yaml`.

Thư mục này dùng đường dẫn tương đối theo project root `scripts`, nên có thể copy từ máy cá nhân sang LIMO mà không cần sửa hard-code `/home/datbolac`.

## 1. Kiểm tra nhanh trên máy cá nhân

Từ thư mục `/home/datbolac/limo/scripts`:

```bash
chmod +x phase_4_data_collection/*.sh
chmod +x phase_7_imu_analysis/*.sh
chmod +x phase_6_evaluation/*.py
python3 -m py_compile phase_6_evaluation/*.py phase_7_imu_analysis/*.py
```

Nếu muốn kiểm tra help:

```bash
phase_4_data_collection/run_record_experiment.sh --help
phase_4_data_collection/save_map.sh --help
phase_6_evaluation/compute_rmse.py --help
```

Các lệnh có `ros2`, đọc rosbag, hoặc lưu map chỉ chạy đầy đủ sau khi source môi trường ROS 2 trên LIMO.

## 2. Copy sang LIMO

Ví dụ copy toàn bộ thư mục `scripts` sang LIMO:

```bash
scp -r /home/datbolac/limo/scripts agilex@<LIMO_IP>:/home/agilex/Documents/LimoDATN20252/Resource
```

Trên LIMO:

```bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
chmod +x phase_4_data_collection/*.sh
chmod +x phase_7_imu_analysis/*.sh
chmod +x phase_6_evaluation/*.py
```

## 3. Quy trình chạy trên LIMO

Source ROS 2 và workspace:

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
```

Start bringup robot theo package LIMO đang dùng. Sau đó start hệ SLAM cần đo, ví dụ Gmapping, Cartographer hoặc SLAM Toolbox.

Record bag:

```bash
phase_4_data_collection/run_record_experiment.sh --system gmapping --scenario A --run 1 --imu on
```

Monitor CPU/RAM trong terminal khác:

```bash
resource_monitoring/measure_process_resources.py \
  --keyword slam_gmapping \
  --output data/resources/gmapping_A_run1_imu_on_resource.csv \
  --interval 1
```

Lưu map sau khi chạy xong:

```bash
phase_4_data_collection/save_map.sh --system gmapping --scenario A --run 1 --imu on
```

Đánh giá entropy, và SSIM nếu có ground-truth:

```bash
phase_6_evaluation/evaluate_maps.py
phase_6_evaluation/evaluate_maps.py --ground_truth data/maps/ground_truth.pgm
```

Trích xuất trajectory từ bag:

```bash
phase_6_evaluation/extract_trajectory_from_bag.py --bag data/bags/gmapping_A_run1_imu_on
```

Tính RMSE:

```bash
phase_6_evaluation/compute_rmse.py \
  --reference_csv data/results/trajectories/reference_A_run1.csv \
  --estimated_csv data/results/trajectories/gmapping_A_run1_imu_on_slam.csv
```

Ghép kết quả cuối:

```bash
phase_6_evaluation/merge_results.py
```

So sánh IMU on/off:

```bash
phase_7_imu_analysis/compare_imu_results.py
```

Kiểm tra cấu hình IMU trong workspace:

```bash
phase_7_imu_analysis/check_imu_usage.sh --workspace /home/agilex/agilex_ws
```

## 4. Ví dụ đầy đủ: gmapping_A_run1_imu_on

Terminal 1:

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
# start bringup LIMO
# start Gmapping
phase_4_data_collection/run_record_experiment.sh --system gmapping --scenario A --run 1 --imu on
```

Terminal 2:

```bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
resource_monitoring/measure_process_resources.py \
  --keyword slam_gmapping \
  --output data/resources/gmapping_A_run1_imu_on_resource.csv \
  --interval 1
```

Sau khi dừng record và monitor:

```bash
phase_4_data_collection/save_map.sh --system gmapping --scenario A --run 1 --imu on
phase_6_evaluation/evaluate_maps.py
phase_6_evaluation/extract_trajectory_from_bag.py --bag data/bags/gmapping_A_run1_imu_on
phase_6_evaluation/compute_rmse.py \
  --reference_csv data/results/trajectories/reference_A_run1.csv \
  --estimated_csv data/results/trajectories/gmapping_A_run1_imu_on_slam.csv
phase_6_evaluation/merge_results.py
phase_7_imu_analysis/compare_imu_results.py
```
