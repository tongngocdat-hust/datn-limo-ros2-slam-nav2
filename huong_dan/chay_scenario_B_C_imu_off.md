# Huong dan chay scenario B va C voi IMU off

Tai lieu nay dung cho 3 he thong:

```text
Cartographer
Gmapping
SLAM Toolbox
```

Moi scenario dung mot baseline rieng:

```text
Scenario B:
  trajectory: data/results/trajectories/reference_B.csv
  map:        data/maps/cartographer_B_run1_imu_off.pgm

Scenario C:
  trajectory: data/results/trajectories/reference_C.csv
  map:        data/maps/cartographer_C_run1_imu_off.pgm
```

Day la baseline Cartographer, khong phai ground truth tuyet doi.

## 1. Chuan bi

```bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
source /opt/ros/humble/setup.bash
```

Source workspace phu hop voi he thong SLAM dang chay. Cap quyen neu can:

```bash
chmod +x phase_4_data_collection/*.sh
chmod +x phase_6_evaluation/*.py
chmod +x resource_monitoring/*.py
```

Truoc moi lan record, xac nhan IMU off:

```bash
ros2 topic info /imu --verbose
```

Ket qua mong doi khi chua record bag:

```text
Subscription count: 0
```

Neu dang record, co the thay `rosbag2_recorder` subscribe `/imu`; node nay chi ghi bag, khong co nghia SLAM dang dung IMU.

Moi lan thi nghiem can:

- Terminal chay bringup va thuat toan SLAM.
- Terminal record bag.
- Terminal do CPU/RAM.
- Robot di dung duong cua scenario, voi vi tri va huong xuat phat gan giong nhau.

## 2. Scenario B - tao baseline Cartographer run 1

Khi Cartographer scenario B dang mapping, record bag:

```bash
phase_4_data_collection/run_record_experiment.sh \
  --system cartographer \
  --scenario B \
  --run 1 \
  --imu off
```

Terminal do CPU/RAM:

```bash
resource_monitoring/measure_process_resources.py \
  --keyword cartographer \
  --output data/resources/cartographer_B_run1_imu_off_resource.csv \
  --interval 1
```

Khi robot di xong, luu map trong luc Cartographer con chay:

```bash
phase_4_data_collection/save_map.sh \
  --system cartographer \
  --scenario B \
  --run 1 \
  --imu off
```

Dung record va monitor bang `Ctrl+C`, sau do trich trajectory:

```bash
phase_6_evaluation/extract_trajectory_from_bag.py \
  --bag data/bags/cartographer_B_run1_imu_off
```

Tao trajectory reference cho scenario B:

```bash
cp data/results/trajectories/cartographer_B_run1_imu_off_odom.csv \
   data/results/trajectories/reference_B.csv
```

Tinh RMSE baseline Cartographer voi chinh reference:

```bash
phase_6_evaluation/compute_rmse.py \
  --relative_time \
  --reference_csv data/results/trajectories/reference_B.csv \
  --estimated_csv data/results/trajectories/cartographer_B_run1_imu_off_odom.csv
```

RMSE baseline nay se gan bang `0`.

## 3. Scenario B - Gmapping run 1

Record:

```bash
phase_4_data_collection/run_record_experiment.sh \
  --system gmapping \
  --scenario B \
  --run 1 \
  --imu off
```

Do CPU/RAM:

```bash
resource_monitoring/measure_process_resources.py \
  --keyword gmapping \
  --output data/resources/gmapping_B_run1_imu_off_resource.csv \
  --interval 1
```

Luu map khi Gmapping con chay:

```bash
phase_4_data_collection/save_map.sh \
  --system gmapping \
  --scenario B \
  --run 1 \
  --imu off
```

Dung record va monitor, sau do trich trajectory va tinh RMSE:

```bash
phase_6_evaluation/extract_trajectory_from_bag.py \
  --bag data/bags/gmapping_B_run1_imu_off

phase_6_evaluation/compute_rmse.py \
  --relative_time \
  --reference_csv data/results/trajectories/reference_B.csv \
  --estimated_csv data/results/trajectories/gmapping_B_run1_imu_off_odom.csv
```

## 4. Scenario B - SLAM Toolbox run 1

Record:

```bash
phase_4_data_collection/run_record_experiment.sh \
  --system slam_toolbox \
  --scenario B \
  --run 1 \
  --imu off
```

Do CPU/RAM:

```bash
resource_monitoring/measure_process_resources.py \
  --keyword slam_toolbox \
  --output data/resources/slam_toolbox_B_run1_imu_off_resource.csv \
  --interval 1
```

Luu map:

```bash
phase_4_data_collection/save_map.sh \
  --system slam_toolbox \
  --scenario B \
  --run 1 \
  --imu off
```

Dung record va monitor, sau do trich trajectory va tinh RMSE:

```bash
phase_6_evaluation/extract_trajectory_from_bag.py \
  --bag data/bags/slam_toolbox_B_run1_imu_off

phase_6_evaluation/compute_rmse.py \
  --relative_time \
  --reference_csv data/results/trajectories/reference_B.csv \
  --estimated_csv data/results/trajectories/slam_toolbox_B_run1_imu_off_odom.csv
```

## 5. Scenario B - tinh SSIM va tong hop

Chi danh gia map scenario B IMU off, giu nguyen metric scenario A/C:

```bash
phase_6_evaluation/evaluate_maps.py \
  --ground_truth data/maps/cartographer_B_run1_imu_off.pgm \
  --scenario B \
  --imu off
```

Ghep ket qua:

```bash
phase_6_evaluation/merge_results.py
cat data/results/final_summary_table.txt
```

## 6. Scenario C - tao baseline Cartographer run 1

Record:

```bash
phase_4_data_collection/run_record_experiment.sh \
  --system cartographer \
  --scenario C \
  --run 1 \
  --imu off
```

Do CPU/RAM:

```bash
resource_monitoring/measure_process_resources.py \
  --keyword cartographer \
  --output data/resources/cartographer_C_run1_imu_off_resource.csv \
  --interval 1
```

Luu map, dung record/monitor, roi trich trajectory:

```bash
phase_4_data_collection/save_map.sh \
  --system cartographer \
  --scenario C \
  --run 1 \
  --imu off

phase_6_evaluation/extract_trajectory_from_bag.py \
  --bag data/bags/cartographer_C_run1_imu_off
```

Tao reference C va tinh RMSE baseline:

```bash
cp data/results/trajectories/cartographer_C_run1_imu_off_odom.csv \
   data/results/trajectories/reference_C.csv

phase_6_evaluation/compute_rmse.py \
  --relative_time \
  --reference_csv data/results/trajectories/reference_C.csv \
  --estimated_csv data/results/trajectories/cartographer_C_run1_imu_off_odom.csv
```

## 7. Scenario C - Gmapping run 1

```bash
phase_4_data_collection/run_record_experiment.sh \
  --system gmapping \
  --scenario C \
  --run 1 \
  --imu off

resource_monitoring/measure_process_resources.py \
  --keyword gmapping \
  --output data/resources/gmapping_C_run1_imu_off_resource.csv \
  --interval 1
```

Luu map, dung record/monitor, trich trajectory va tinh RMSE:

```bash
phase_4_data_collection/save_map.sh \
  --system gmapping \
  --scenario C \
  --run 1 \
  --imu off

phase_6_evaluation/extract_trajectory_from_bag.py \
  --bag data/bags/gmapping_C_run1_imu_off

phase_6_evaluation/compute_rmse.py \
  --relative_time \
  --reference_csv data/results/trajectories/reference_C.csv \
  --estimated_csv data/results/trajectories/gmapping_C_run1_imu_off_odom.csv
```

## 8. Scenario C - SLAM Toolbox run 1

```bash
phase_4_data_collection/run_record_experiment.sh \
  --system slam_toolbox \
  --scenario C \
  --run 1 \
  --imu off

resource_monitoring/measure_process_resources.py \
  --keyword slam_toolbox \
  --output data/resources/slam_toolbox_C_run1_imu_off_resource.csv \
  --interval 1
```

Luu map, dung record/monitor, trich trajectory va tinh RMSE:

```bash
phase_4_data_collection/save_map.sh \
  --system slam_toolbox \
  --scenario C \
  --run 1 \
  --imu off

phase_6_evaluation/extract_trajectory_from_bag.py \
  --bag data/bags/slam_toolbox_C_run1_imu_off

phase_6_evaluation/compute_rmse.py \
  --relative_time \
  --reference_csv data/results/trajectories/reference_C.csv \
  --estimated_csv data/results/trajectories/slam_toolbox_C_run1_imu_off_odom.csv
```

## 9. Scenario C - tinh SSIM va tong hop

```bash
phase_6_evaluation/evaluate_maps.py \
  --ground_truth data/maps/cartographer_C_run1_imu_off.pgm \
  --scenario C \
  --imu off

phase_6_evaluation/merge_results.py
cat data/results/final_summary_table.txt
```

## 10. Run 2 va run 3

Sau khi da co `reference_B.csv` va `reference_C.csv`, khong tao reference moi.

Khi chay run 2/3, chi doi:

```text
--run 1 -> --run 2 hoac --run 3
run1    -> run2 hoac run3
```

RMSE scenario B luon dung:

```text
data/results/trajectories/reference_B.csv
```

RMSE scenario C luon dung:

```text
data/results/trajectories/reference_C.csv
```

SSIM scenario B luon dung:

```text
data/maps/cartographer_B_run1_imu_off.pgm
```

SSIM scenario C luon dung:

```text
data/maps/cartographer_C_run1_imu_off.pgm
```

## 11. Kiem tra file

```bash
ls -lh data/results/trajectories/reference_B.csv
ls -lh data/results/trajectories/reference_C.csv
ls -lh data/maps/cartographer_B_run1_imu_off.pgm
ls -lh data/maps/cartographer_C_run1_imu_off.pgm
cat data/results/final_summary_table.txt
```

Khong dung `reference_A.csv` hoac map Cartographer A de danh gia scenario B/C.
> **Cảnh báo:** đây là quy trình cũ. Với dữ liệu chạy lại, dùng
> `chay_lai_3_slam_sau_khi_sua.md` và chỉ tính RMSE từ `*_slam.csv`.
