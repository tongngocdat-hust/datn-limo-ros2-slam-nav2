# Hướng dẫn chạy run 2 và run 3

Tài liệu này dùng quy trình mới:

- chạy lần lượt Cartographer, Gmapping và SLAM Toolbox;
- dùng SLAM Toolbox run 1 làm baseline;
- trích quỹ đạo từ file `*_slam.csv`, không dùng `_odom.csv`;
- không tạo lại reference khi chạy run 2 hoặc run 3.

Các lệnh bên dưới dùng ví dụ:

```text
scenario: C
IMU:      off
```

Nếu chạy A hoặc B, thay toàn bộ `_C_` và `--scenario C` tương ứng.

## 1. Kiểm tra reference run 1

Trên LIMO:

```bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts

ls -lh data/maps/slam_toolbox_C_run1_imu_off.pgm
ls -lh data/maps/slam_toolbox_C_run1_imu_off.yaml
ls -lh data/results/trajectories/slam_toolbox_C_run1_imu_off_slam.csv
ls -lh data/results/trajectories/reference_C.csv
```

Nếu chưa có `reference_C.csv`, tạo một lần:

```bash
cp data/results/trajectories/slam_toolbox_C_run1_imu_off_slam.csv \
   data/results/trajectories/reference_C.csv
```

Không ghi đè `reference_C.csv` bằng run 2 hoặc run 3.

## 2. Chuẩn bị mỗi terminal

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
```

Cấp quyền nếu cần:

```bash
chmod +x phase_3_slam/*.sh
chmod +x phase_4_data_collection/*.sh
chmod +x phase_6_evaluation/*.py
chmod +x phase_6_evaluation/*.sh
chmod +x resource_monitoring/*.py
```

## 3. Terminal bringup LIMO

Giữ terminal này chạy trong toàn bộ thí nghiệm:

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
ros2 launch limo_bringup limo_start.launch.py
```

Chỉ chạy một thuật toán SLAM tại một thời điểm.

## 4. Run 2

### 4.1. Cartographer C run 2

Terminal SLAM:

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
phase_3_slam/start_slam.sh --system cartographer --imu off
```

Launcher Cartographer của LIMO sẽ tự mở RViz.

Terminal record:

```bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
phase_4_data_collection/run_record_experiment.sh \
  --system cartographer --scenario C --run 2 --imu off
```

Terminal CPU/RAM:

```bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
resource_monitoring/measure_process_resources.py \
  --keyword cartographer \
  --output data/resources/cartographer_C_run2_imu_off_resource.csv \
  --interval 1
```

Đi hết tuyến C. Khi SLAM và record vẫn đang chạy, lưu map:

```bash
phase_4_data_collection/save_map.sh \
  --system cartographer --scenario C --run 2 --imu off
```

Sau đó dừng record, monitor và Cartographer bằng `Ctrl+C`, rồi trích trajectory:

```bash
phase_6_evaluation/extract_trajectory_from_bag.py \
  --bag data/bags/cartographer_C_run2_imu_off
```

### 4.2. Gmapping C run 2

Terminal SLAM:

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
phase_3_slam/start_slam.sh --system gmapping --imu off
```

Terminal record:

```bash
phase_4_data_collection/run_record_experiment.sh \
  --system gmapping --scenario C --run 2 --imu off
```

Terminal CPU/RAM:

```bash
resource_monitoring/measure_process_resources.py \
  --keyword slam_gmapping \
  --output data/resources/gmapping_C_run2_imu_off_resource.csv \
  --interval 1
```

Đi hết cùng tuyến C, sau đó lưu map khi SLAM vẫn chạy:

```bash
phase_4_data_collection/save_map.sh \
  --system gmapping --scenario C --run 2 --imu off
```

Dừng record, monitor và Gmapping, rồi trích trajectory:

```bash
phase_6_evaluation/extract_trajectory_from_bag.py \
  --bag data/bags/gmapping_C_run2_imu_off
```

### 4.3. SLAM Toolbox C run 2

Terminal SLAM:

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
phase_3_slam/start_slam.sh --system slam_toolbox --imu off
```

Terminal record:

```bash
phase_4_data_collection/run_record_experiment.sh \
  --system slam_toolbox --scenario C --run 2 --imu off
```

Terminal CPU/RAM:

```bash
resource_monitoring/measure_process_resources.py \
  --keyword slam_toolbox \
  --output data/resources/slam_toolbox_C_run2_imu_off_resource.csv \
  --interval 1
```

Đi hết cùng tuyến C, sau đó lưu map khi SLAM vẫn chạy:

```bash
phase_4_data_collection/save_map.sh \
  --system slam_toolbox --scenario C --run 2 --imu off
```

Dừng record, monitor và SLAM Toolbox, rồi trích trajectory:

```bash
phase_6_evaluation/extract_trajectory_from_bag.py \
  --bag data/bags/slam_toolbox_C_run2_imu_off
```

## 5. Run 3

Lặp lại đúng quy trình run 2, nhưng thay tất cả:

```text
--run 2  → --run 3
run2     → run3
```

### 5.1. Cartographer C run 3

```bash
phase_3_slam/start_slam.sh --system cartographer --imu off
```

```bash
phase_4_data_collection/run_record_experiment.sh \
  --system cartographer --scenario C --run 3 --imu off
```

```bash
resource_monitoring/measure_process_resources.py \
  --keyword cartographer \
  --output data/resources/cartographer_C_run3_imu_off_resource.csv \
  --interval 1
```

```bash
phase_4_data_collection/save_map.sh \
  --system cartographer --scenario C --run 3 --imu off

phase_6_evaluation/extract_trajectory_from_bag.py \
  --bag data/bags/cartographer_C_run3_imu_off
```

### 5.2. Gmapping C run 3

```bash
phase_3_slam/start_slam.sh --system gmapping --imu off
```

```bash
phase_4_data_collection/run_record_experiment.sh \
  --system gmapping --scenario C --run 3 --imu off
```

```bash
resource_monitoring/measure_process_resources.py \
  --keyword slam_gmapping \
  --output data/resources/gmapping_C_run3_imu_off_resource.csv \
  --interval 1
```

```bash
phase_4_data_collection/save_map.sh \
  --system gmapping --scenario C --run 3 --imu off

phase_6_evaluation/extract_trajectory_from_bag.py \
  --bag data/bags/gmapping_C_run3_imu_off
```

### 5.3. SLAM Toolbox C run 3

```bash
phase_3_slam/start_slam.sh --system slam_toolbox --imu off
```

```bash
phase_4_data_collection/run_record_experiment.sh \
  --system slam_toolbox --scenario C --run 3 --imu off
```

```bash
resource_monitoring/measure_process_resources.py \
  --keyword slam_toolbox \
  --output data/resources/slam_toolbox_C_run3_imu_off_resource.csv \
  --interval 1
```

```bash
phase_4_data_collection/save_map.sh \
  --system slam_toolbox --scenario C --run 3 --imu off

phase_6_evaluation/extract_trajectory_from_bag.py \
  --bag data/bags/slam_toolbox_C_run3_imu_off
```

## 6. Kiểm tra đủ file

```bash
ls -lh data/maps/*_C_run{2,3}_imu_off.pgm
ls -lh data/maps/*_C_run{2,3}_imu_off.yaml
ls -lh data/resources/*_C_run{2,3}_imu_off_resource.csv
ls -lh data/results/trajectories/*_C_run{2,3}_imu_off_slam.csv
ls -lh data/results/trajectories/reference_C.csv
```

Phải có đủ `cartographer`, `gmapping`, `slam_toolbox` cho cả run 2 và run 3.

## 7. Đánh giá lại scenario C

Kích hoạt môi trường đánh giá:

```bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
source phase_6_evaluation/.venv/bin/activate
```

Chạy đánh giá. Script mặc định dùng SLAM Toolbox C run 1 làm map reference và
`reference_C.csv` làm trajectory reference:

```bash
phase_6_evaluation/evaluate_scenario.sh --scenario C --imu off
```

Xem riêng scenario C:

```bash
grep -E 'system|cartographer.*C|gmapping.*C|slam_toolbox.*C' \
  data/results/final_summary_table.txt
```

## 8. Nếu chạy scenario A hoặc B

Reference phải được tạo từ SLAM Toolbox run 1 của đúng scenario:

```bash
cp data/results/trajectories/slam_toolbox_A_run1_imu_off_slam.csv \
   data/results/trajectories/reference_A.csv

cp data/results/trajectories/slam_toolbox_B_run1_imu_off_slam.csv \
   data/results/trajectories/reference_B.csv
```

Sau đó thay `C` trong toàn bộ tên file và đối số `--scenario C`.

Đánh giá:

```bash
phase_6_evaluation/evaluate_scenario.sh --scenario A --imu off
phase_6_evaluation/evaluate_scenario.sh --scenario B --imu off
```

## 9. Quy tắc chạy để so sánh công bằng

- Cùng vị trí và hướng xuất phát.
- Cùng tuyến đường và điểm kết thúc.
- Tốc độ tiến khoảng `0.10–0.20 m/s`.
- Tốc độ quay khoảng `0.15–0.25 rad/s`.
- Không vừa chạy nhanh vừa quay gấp.
- Lưu map trước khi dừng node SLAM.
- Không chạy hai thuật toán SLAM cùng lúc.
- Không tạo lại hoặc ghi đè `reference_A/B/C.csv` bằng run 2/run 3.
- Không dùng `_odom.csv` để tính độ chính xác SLAM.
- SLAM Toolbox run 1 là baseline tương đối, không phải ground truth tuyệt đối.
