# Workflow thí nghiệm SLAM

Workflow này dùng cho Gmapping, Cartographer và SLAM Toolbox trên LIMO ROS 2
Humble. Mục tiêu là chạy cùng dữ liệu đầu vào, cùng frame và cùng naming
convention để so sánh công bằng.

## 1. Bringup robot

Terminal 1:

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
ros2 launch limo_bringup limo_start.launch.py
```

## 2. Preflight

Terminal 2:

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
phase_3_slam/preflight_slam.sh
```

Chỉ tiếp tục khi preflight báo `PASS`. Nếu LaserScan trong RViz bị xòe khi robot
quay tại chỗ, cần sửa odometry, timestamp hoặc static TF trước khi chạy SLAM.

## 3. Chạy SLAM

Chọn một hệ tại một thời điểm:

```bash
phase_3_slam/start_slam.sh --system cartographer --imu off
phase_3_slam/start_slam.sh --system gmapping --imu off
phase_3_slam/start_slam.sh --system slam_toolbox --imu off
```

Gmapping được source từ workspace riêng mặc định:

```text
/home/agilex/gmapping_ws/install/setup.bash
```

Nếu khác đường dẫn, set biến:

```bash
export GMAPPING_SETUP=/path/to/gmapping_ws/install/setup.bash
```

## 4. Record bag

Terminal record:

```bash
phase_4_data_collection/run_record_experiment.sh \
  --system slam_toolbox \
  --scenario A \
  --run 1 \
  --imu off
```

Script record các topic:

```text
/scan /imu /odom /tf /tf_static /map
```

Tên bag có dạng:

```text
<system>_<scenario>_run<run>_imu_<on|off>
```

## 5. Đo CPU/RAM

Terminal monitor:

```bash
resource_monitoring/measure_process_resources.py \
  --keyword slam_toolbox \
  --output data/resources/slam_toolbox_A_run1_imu_off_resource.csv \
  --interval 1
```

Đổi `--keyword` theo process cần đo, ví dụ `cartographer` hoặc `slam_gmapping`.

## 6. Lưu map và đánh giá

Khi SLAM và record vẫn đang chạy:

```bash
phase_4_data_collection/save_map.sh \
  --system slam_toolbox \
  --scenario A \
  --run 1 \
  --imu off
```

Sau khi dừng record:

```bash
phase_6_evaluation/extract_trajectory_from_bag.py \
  --bag data/bags/slam_toolbox_A_run1_imu_off

phase_6_evaluation/evaluate_maps.py

phase_6_evaluation/compute_rmse.py \
  --reference_csv data/results/trajectories/reference_A_run1.csv \
  --estimated_csv data/results/trajectories/slam_toolbox_A_run1_imu_off_slam.csv

phase_6_evaluation/merge_results.py
```

## Tài liệu chi tiết

Xem bản thao tác đầy đủ tại:

- `huong_dan/chay_lai_3_slam_sau_khi_sua.md`
- `scripts/README_experiment.md`
