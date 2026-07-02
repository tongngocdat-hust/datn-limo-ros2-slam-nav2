# Huong dan tao reference de tinh RMSE

Tai lieu nay huong dan cach tao trajectory reference bang cach dung mot thuat toan SLAM lam baseline, vi du Cartographer, roi so sanh cac lan chay khac voi reference do.

## 1. Y tuong

`compute_rmse.py` can 2 file CSV:

```bash
--reference_csv   trajectory chuan hoac baseline
--estimated_csv   trajectory can danh gia
```

Trong de tai nay, neu khong co ground truth tu motion capture, GPS, hoac he do ngoai, co the dung mot lan chay tot nhat lam reference. Vi du:

```text
Cartographer scenario A -> reference_A.csv
Gmapping scenario A     -> so sanh voi reference_A.csv
SLAM Toolbox scenario A -> so sanh voi reference_A.csv
```

Luu y: reference tao theo cach nay la baseline tu thuat toan khac, khong phai ground truth tuyet doi. Khi viet bao cao nen ghi:

```text
RMSE duoc tinh tuong doi so voi trajectory baseline cua Cartographer.
```

## 2. Chuan bi moi truong

Di chuyen vao thu muc scripts tren LIMO:

```bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
```

Cap quyen chay script neu can:

```bash
chmod +x phase_4_data_collection/*.sh
chmod +x phase_6_evaluation/*.py
chmod +x phase_7_imu_analysis/*.py
chmod +x resource_monitoring/*.py
```

## 3. Chay mot lan thi nghiem co do CPU/RAM

Khi chay thi nghiem, nen dung it nhat 2 terminal:

- Terminal 1: chay robot, SLAM va record bag.
- Terminal 2: do CPU/RAM trong luc SLAM dang chay.

Vi du chay Cartographer scenario A de tao baseline reference.

Terminal 1:

```bash
phase_4_data_collection/run_record_experiment.sh \
  --system cartographer \
  --scenario A \
  --run 1 \
  --imu on
```

Terminal 2, chay trong luc Cartographer dang mapping:

```bash
resource_monitoring/measure_process_resources.py \
  --keyword cartographer \
  --output data/resources/cartographer_A_run1_imu_on_resource.csv \
  --interval 1
```

Khi ket thuc duong chay:

1. Dung record bag o Terminal 1 bang `Ctrl+C`.
2. Dung monitor CPU/RAM o Terminal 2 bang `Ctrl+C`.
3. Luu map.

Luu map Cartographer:

```bash
phase_4_data_collection/save_map.sh \
  --system cartographer \
  --scenario A \
  --run 1 \
  --imu on
```

Sau buoc nay nen co:

```text
data/bags/cartographer_A_run1_imu_on/
data/maps/cartographer_A_run1_imu_on.pgm
data/maps/cartographer_A_run1_imu_on.yaml
data/resources/cartographer_A_run1_imu_on_resource.csv
```

## 4. Tao reference trajectory cho scenario A

Trich trajectory tu bag Cartographer:

```bash
phase_6_evaluation/extract_trajectory_from_bag.py \
  --bag data/bags/cartographer_A_run1_imu_on
```

Kiem tra file duoc tao:

```bash
ls -lh data/results/trajectories
```

Neu co file:

```text
cartographer_A_run1_imu_on_odom.csv
```

thi copy thanh reference chung cho scenario A:

```bash
cp data/results/trajectories/cartographer_A_run1_imu_on_odom.csv \
   data/results/trajectories/reference_A.csv
```

## 5. Tao reference map cho SSIM

Voi SSIM, co the dung map Cartographer lam map baseline cho scenario A:

```text
data/maps/cartographer_A_run1_imu_on.pgm
```

Khi danh gia map, truyen file nay vao `--ground_truth`:

```bash
phase_6_evaluation/evaluate_maps.py \
  --ground_truth data/maps/cartographer_A_run1_imu_on.pgm
```

Luu y: day la baseline reference, khong phai ground truth tuyet doi. Dong Cartographer so voi chinh no se co `ssim = 1.0`.

Ket qua map duoc ghi vao:

```text
data/results/map_metrics.csv
```

## 6. Chay gmapping va so sanh voi reference

Chay gmapping cung scenario A. Terminal 1:

```bash
phase_4_data_collection/run_record_experiment.sh \
  --system gmapping \
  --scenario A \
  --run 1 \
  --imu on
```

Terminal 2, do CPU/RAM trong luc gmapping dang chay:

```bash
resource_monitoring/measure_process_resources.py \
  --keyword gmapping \
  --output data/resources/gmapping_A_run1_imu_on_resource.csv \
  --interval 1
```

Neu keyword `gmapping` khong bat duoc process, kiem tra ten process:

```bash
ps aux | grep -i gmapping
```

Sau khi ket thuc duong chay, dung record va monitor bang `Ctrl+C`, roi luu map:

```bash
phase_4_data_collection/save_map.sh \
  --system gmapping \
  --scenario A \
  --run 1 \
  --imu on
```

Trich trajectory gmapping:

```bash
phase_6_evaluation/extract_trajectory_from_bag.py \
  --bag data/bags/gmapping_A_run1_imu_on
```

Sau khi da co trajectory cua gmapping:

```text
data/results/trajectories/gmapping_A_run1_imu_on_odom.csv
```

Tinh RMSE so voi reference Cartographer:

```bash
phase_6_evaluation/compute_rmse.py \
  --relative_time \
  --reference_csv data/results/trajectories/reference_A.csv \
  --estimated_csv data/results/trajectories/gmapping_A_run1_imu_on_odom.csv
```

Neu thanh cong, ket qua se duoc ghi vao:

```text
data/results/rmse_results.csv
```

Danh gia SSIM/entropy cho cac map, dung Cartographer lam map reference:

```bash
phase_6_evaluation/evaluate_maps.py \
  --ground_truth data/maps/cartographer_A_run1_imu_on.pgm
```

Sau do ghep CPU/RAM, entropy, SSIM va RMSE vao bang tong hop:

```bash
phase_6_evaluation/merge_results.py
column -s, -t data/results/final_summary.csv
```

## 7. Chay SLAM Toolbox va so sanh voi reference

Chay SLAM Toolbox cung scenario A. Terminal 1:

```bash
phase_4_data_collection/run_record_experiment.sh \
  --system slam_toolbox \
  --scenario A \
  --run 1 \
  --imu on
```

Terminal 2, do CPU/RAM trong luc SLAM Toolbox dang chay:

```bash
resource_monitoring/measure_process_resources.py \
  --keyword slam_toolbox \
  --output data/resources/slam_toolbox_A_run1_imu_on_resource.csv \
  --interval 1
```

Neu keyword `slam_toolbox` khong bat duoc process, kiem tra ten process:

```bash
ps aux | grep -i slam
ps aux | grep -i toolbox
```

Sau khi ket thuc duong chay, dung record va monitor bang `Ctrl+C`, roi luu map:

```bash
phase_4_data_collection/save_map.sh \
  --system slam_toolbox \
  --scenario A \
  --run 1 \
  --imu on
```

Trich trajectory SLAM Toolbox:

```bash
phase_6_evaluation/extract_trajectory_from_bag.py \
  --bag data/bags/slam_toolbox_A_run1_imu_on
```

Sau khi da co trajectory:

```text
data/results/trajectories/slam_toolbox_A_run1_imu_on_odom.csv
```

Tinh RMSE so voi reference Cartographer:

```bash
phase_6_evaluation/compute_rmse.py \
  --relative_time \
  --reference_csv data/results/trajectories/reference_A.csv \
  --estimated_csv data/results/trajectories/slam_toolbox_A_run1_imu_on_odom.csv
```

Danh gia lai SSIM/entropy cho tat ca map, van dung Cartographer lam map reference:

```bash
phase_6_evaluation/evaluate_maps.py \
  --ground_truth data/maps/cartographer_A_run1_imu_on.pgm
```

Ghep lai bang tong hop:

```bash
phase_6_evaluation/merge_results.py
cat data/results/final_summary_table.txt
```

Luc nay bang nen co 3 dong:

```text
cartographer
gmapping
slam_toolbox
```

## 8. Tao reference cho cac scenario khac

Moi scenario nen co reference rieng:

```text
reference_A.csv
reference_B.csv
reference_C.csv
```

Vi du voi scenario B:

```bash
phase_4_data_collection/run_record_experiment.sh \
  --system cartographer \
  --scenario B \
  --run 1 \
  --imu on

resource_monitoring/measure_process_resources.py \
  --keyword cartographer \
  --output data/resources/cartographer_B_run1_imu_on_resource.csv \
  --interval 1

phase_4_data_collection/save_map.sh \
  --system cartographer \
  --scenario B \
  --run 1 \
  --imu on

phase_6_evaluation/extract_trajectory_from_bag.py \
  --bag data/bags/cartographer_B_run1_imu_on

cp data/results/trajectories/cartographer_B_run1_imu_on_odom.csv \
   data/results/trajectories/reference_B.csv
```

## 9. Dieu kien de so sanh cong bang

Chi nen dung chung mot reference khi cac lan thu nghiem co cung dieu kien:

- Cung scenario, vi du deu la scenario A.
- Robot xuat phat gan cung mot vi tri va huong.
- Robot di cung mot duong, thoi gian va toc do khong lech qua nhieu.
- Moi lan chay deu dung cung loai trajectory de so sanh, vi du odom voi odom.

Khong nen lay chinh file estimated lam reference cho no, vi RMSE se gan bang 0 va khong co y nghia.

## 10. Neu cot CPU/RAM bi trong

Neu `final_summary.csv` co cac cot nay bi trong:

```text
cpu_mean,cpu_std,ram_mean,ram_max
```

thi thuong la do chua chay `measure_process_resources.py` trong luc SLAM dang chay, hoac keyword khong bat dung process.

Kiem tra file resource:

```bash
ls -lh data/resources
head data/resources/gmapping_A_run1_imu_on_resource.csv
```

Neu `process_count` toan bang 0, can doi keyword. Vi du:

```bash
ps aux | grep -i gmapping
ps aux | grep -i cartographer
ps aux | grep -i slam
```

Sau do chay monitor voi keyword phu hop.

## 11. Neu bi loi khong trung timestamp

Neu `compute_rmse.py` bao loi:

```text
No overlapping timestamp range between reference and estimated CSV files
```

nghia la hai file CSV duoc record o hai thoi diem khac nhau nen timestamp tuyet doi khong trung nhau. Khi do chay lai voi `--relative_time` de so sanh theo thoi gian tuong doi:

```bash
phase_6_evaluation/compute_rmse.py \
  --relative_time \
  --reference_csv data/results/trajectories/reference_A.csv \
  --estimated_csv data/results/trajectories/gmapping_A_run1_imu_on_odom.csv
```

Che do nay dua timestamp cua moi file ve bat dau tu 0.

Y tuong xu ly:

```text
timestamp_relative = timestamp - timestamp_dau_tien_cua_file
```

Sau khi lam vay, co the dung `reference_A.csv` cho nhieu lan chay scenario A de so sanh tuong doi.

## 12. Nen dung odom hay slam trajectory?

Hien tai neu script chi tao duoc:

```text
*_odom.csv
```

thi co the dung odom de so sanh tam thoi.

Neu sau nay trich duoc:

```text
*_slam.csv
```

thi nen dung slam trajectory de danh gia SLAM:

```bash
phase_6_evaluation/compute_rmse.py \
  --relative_time \
  --reference_csv data/results/trajectories/reference_A_slam.csv \
  --estimated_csv data/results/trajectories/gmapping_A_run1_imu_on_slam.csv
```
> **Cảnh báo:** tài liệu này dùng quy trình RMSE cũ dựa trên `_odom.csv`.
> Không dùng cho lần chạy mới. Xem `chay_lai_3_slam_sau_khi_sua.md`.
