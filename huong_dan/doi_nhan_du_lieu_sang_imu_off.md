# Doi nhan du lieu cu tu IMU on sang IMU off

Chi lam theo huong dan nay khi da xac nhan cac lan chay cu khong co node nao subscribe `/imu`.

Vi du ben duoi doi du lieu scenario A, run 1 cua Cartographer, Gmapping va SLAM Toolbox.

## 1. Kiem tra truoc khi doi

Vao thu muc scripts:

```bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
```

Liet ke du lieu cu va du lieu dich:

```bash
find data -name '*_A_run1_imu_on*'
find data -name '*_A_run1_imu_off*'
```

Neu da co file `_imu_off` cung system/scenario/run thi dung lai, khong doi de tranh ghi de.

Sao luu cac file ket qua nho truoc khi xu ly:

```bash
mkdir -p data/results/before_imu_relabel
cp -a data/results/*.csv data/results/before_imu_relabel/
```

## 2. Doi ten Cartographer run 1

```bash
mv data/bags/cartographer_A_run1_imu_on \
   data/bags/cartographer_A_run1_imu_off

mv data/maps/cartographer_A_run1_imu_on.pgm \
   data/maps/cartographer_A_run1_imu_off.pgm

mv data/maps/cartographer_A_run1_imu_on.yaml \
   data/maps/cartographer_A_run1_imu_off.yaml

mv data/resources/cartographer_A_run1_imu_on_resource.csv \
   data/resources/cartographer_A_run1_imu_off_resource.csv

mv data/results/trajectories/cartographer_A_run1_imu_on_odom.csv \
   data/results/trajectories/cartographer_A_run1_imu_off_odom.csv
```

Cap nhat ten anh trong YAML map:

```bash
sed -i 's/cartographer_A_run1_imu_on.pgm/cartographer_A_run1_imu_off.pgm/' \
  data/maps/cartographer_A_run1_imu_off.yaml
```

Khong doi ten file `.db3` ben trong bag; `metadata.yaml` cua bag van tham chieu ten `.db3` cu.

## 3. Doi ten Gmapping run 1

```bash
mv data/bags/gmapping_A_run1_imu_on \
   data/bags/gmapping_A_run1_imu_off

mv data/maps/gmapping_A_run1_imu_on.pgm \
   data/maps/gmapping_A_run1_imu_off.pgm

mv data/maps/gmapping_A_run1_imu_on.yaml \
   data/maps/gmapping_A_run1_imu_off.yaml

mv data/resources/gmapping_A_run1_imu_on_resource.csv \
   data/resources/gmapping_A_run1_imu_off_resource.csv

mv data/results/trajectories/gmapping_A_run1_imu_on_odom.csv \
   data/results/trajectories/gmapping_A_run1_imu_off_odom.csv

sed -i 's/gmapping_A_run1_imu_on.pgm/gmapping_A_run1_imu_off.pgm/' \
  data/maps/gmapping_A_run1_imu_off.yaml
```

## 4. Doi ten SLAM Toolbox run 1

```bash
mv data/bags/slam_toolbox_A_run1_imu_on \
   data/bags/slam_toolbox_A_run1_imu_off

mv data/maps/slam_toolbox_A_run1_imu_on.pgm \
   data/maps/slam_toolbox_A_run1_imu_off.pgm

mv data/maps/slam_toolbox_A_run1_imu_on.yaml \
   data/maps/slam_toolbox_A_run1_imu_off.yaml

mv data/resources/slam_toolbox_A_run1_imu_on_resource.csv \
   data/resources/slam_toolbox_A_run1_imu_off_resource.csv

mv data/results/trajectories/slam_toolbox_A_run1_imu_on_odom.csv \
   data/results/trajectories/slam_toolbox_A_run1_imu_off_odom.csv

sed -i 's/slam_toolbox_A_run1_imu_on.pgm/slam_toolbox_A_run1_imu_off.pgm/' \
  data/maps/slam_toolbox_A_run1_imu_off.yaml
```

Neu co file `*_slam.csv`, doi tuong tu tu `_imu_on_slam.csv` thanh `_imu_off_slam.csv`.

## 5. Reference sau khi doi

Giu nguyen trajectory reference:

```text
data/results/trajectories/reference_A.csv
```

Reference nay bay gio co y nghia la baseline Cartographer run 1 IMU off.

Map reference moi:

```text
data/maps/cartographer_A_run1_imu_off.pgm
```

## 6. Tao lai RMSE

Chuyen file RMSE cu sang ban sao luu de tranh giu cac dong `imu=on` sai:

```bash
mv data/results/rmse_results.csv \
   data/results/before_imu_relabel/rmse_results.csv
```

Tinh lai Gmapping:

```bash
phase_6_evaluation/compute_rmse.py \
  --relative_time \
  --reference_csv data/results/trajectories/reference_A.csv \
  --estimated_csv data/results/trajectories/gmapping_A_run1_imu_off_odom.csv
```

Tinh lai SLAM Toolbox:

```bash
phase_6_evaluation/compute_rmse.py \
  --relative_time \
  --reference_csv data/results/trajectories/reference_A.csv \
  --estimated_csv data/results/trajectories/slam_toolbox_A_run1_imu_off_odom.csv
```

## 7. Tao lai SSIM va bang tong hop

```bash
phase_6_evaluation/evaluate_maps.py \
  --ground_truth data/maps/cartographer_A_run1_imu_off.pgm

phase_6_evaluation/merge_results.py
cat data/results/final_summary_table.txt
```

Bang moi phai hien thi:

```text
cartographer  A  1  off
gmapping      A  1  off
slam_toolbox  A  1  off
```

`imu_comparison.csv` chua co y nghia cho den khi chay them bo IMU on that su.

## 8. Neu doi run 2 hoac run 3

Lam tuong tu va thay tat ca:

```text
run1 -> run2
```

hoac:

```text
run1 -> run3
```

Khong tao reference moi neu van dung `reference_A.csv` lam baseline chung.
> **Cảnh báo:** đổi nhãn file không chứng minh rằng IMU đã được thuật toán sử
> dụng. Không dùng tài liệu này cho dữ liệu mới; xem
> `chay_lai_3_slam_sau_khi_sua.md`.
