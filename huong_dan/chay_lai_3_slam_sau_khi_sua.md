# Chạy lại ba hệ SLAM trên LIMO sau khi sửa

Mục tiêu của bộ cấu hình này là cho Gmapping, Cartographer và SLAM Toolbox dùng
cùng dữ liệu đầu vào và cùng quy ước:

- `map`, `odom`, `base_link`
- laser `/scan`
- độ phân giải map `0.05 m/pixel`
- tầm laser hữu ích `0.10–12.0 m`

Không thể bảo đảm ba map đẹp như nhau vì thuật toán khác nhau, nhưng quy trình
này loại bỏ các sai lệch lớn do frame, cấu hình mặc định và cách tính metric.

## 1. Copy toàn bộ scripts từ máy cá nhân sang LIMO

Chạy trên **máy cá nhân**, không chạy trong terminal của LIMO:

```bash
rsync -av --progress \
  /home/datbolac/limo/scripts/ \
  agilex@192.168.1.117:/home/agilex/Documents/LimoDATN20252/Resource/scripts/
```

Copy cả file hướng dẫn này sang LIMO:

```bash
ssh agilex@192.168.1.117 \
  'mkdir -p /home/agilex/Documents/LimoDATN20252/Resource/huong_dan'

scp /home/datbolac/limo/huong_dan/chay_lai_3_slam_sau_khi_sua.md \
  agilex@192.168.1.117:/home/agilex/Documents/LimoDATN20252/Resource/huong_dan/
```

Lệnh này cập nhật code và giữ lại dữ liệu đang có trên LIMO. Nếu máy cá nhân
không có `rsync`, dùng:

```bash
scp -r /home/datbolac/limo/scripts \
  agilex@192.168.1.117:/home/agilex/Documents/LimoDATN20252/Resource/
```

SSH vào LIMO:

```bash
ssh agilex@192.168.1.117
```

Sau đó chạy trên **LIMO**:

```bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
chmod +x phase_3_slam/*.sh
chmod +x phase_4_data_collection/*.sh
chmod +x phase_6_evaluation/*.py
chmod +x phase_6_evaluation/*.sh
```

Mỗi terminal đều cần:

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
```

Gmapping nằm trong workspace riêng. Script mới sẽ tự source:

```text
/home/agilex/gmapping_ws/install/setup.bash
```

Có thể kiểm tra:

```bash
source /home/agilex/gmapping_ws/install/setup.bash
ros2 pkg executables slam_gmapping
```

Kết quả phải có `slam_gmapping slam_gmapping_node`.

## 2. Khởi động LIMO và kiểm tra trước khi chạy SLAM

### Terminal 1 — bringup LIMO

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
ros2 launch limo_bringup limo_start.launch.py
```

### Terminal 2 — preflight

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
phase_3_slam/preflight_slam.sh
```

Chỉ tiếp tục khi script báo `PASS`.

Trong RViz:

1. Đặt `Fixed Frame` thành `odom`.
2. Thêm display `LaserScan`, topic `/scan`.
3. Quay robot chậm tại chỗ.

Các điểm laser của tường phải gần như đứng yên. Nếu chúng xoè thành hình quạt,
phải sửa odometry, timestamp hoặc static TF `base_link -> laser` trước. Chỉnh
tham số SLAM không thể bù được TF sai.

Kiểm tra chỉ có một nguồn phát transform odometry:

```bash
ros2 topic info /odom -v
ros2 run tf2_ros tf2_echo odom base_link
```

## 3. Quy trình đầy đủ scenario A, IMU off

Chạy đủ Cartographer, Gmapping và SLAM Toolbox trên cùng tuyến đường. SLAM
Toolbox run 1 được dùng làm baseline cố định vì map của nó gần bố cục thực tế
hơn trong thí nghiệm này. Chỉ chạy một thuật toán tại một thời điểm.

Trước khi chạy lại từ đầu, nên chuyển dữ liệu thử cũ sang thư mục backup để
không bị báo trùng tên. Không xóa dữ liệu nếu vẫn cần dùng.

## 4. Cartographer A run 1

Giữ Terminal 1 chạy bringup LIMO.

### Terminal 3 — chạy Cartographer

Ưu tiên launcher sẵn có của LIMO vì nó chứa cấu hình Cartographer phù hợp với
sensor/TF của xe và tự mở RViz. Script dưới đây gọi đúng launcher đó:

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
phase_3_slam/start_slam.sh --system cartographer --imu off
```

Lệnh trực tiếp tương đương:

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
ros2 launch limo_bringup limo_cartographer.launch.py
```

Không chạy thêm Cartographer node hoặc RViz khác trong lúc launcher này đang
hoạt động.

### Terminal 4 — record Cartographer

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
phase_4_data_collection/run_record_experiment.sh \
  --system cartographer --scenario A --run 1 --imu off
```

### Terminal 5 — đo CPU/RAM Cartographer

```bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
resource_monitoring/measure_process_resources.py \
  --keyword cartographer \
  --output data/resources/cartographer_A_run1_imu_off_resource.csv \
  --interval 1
```

Đi hết tuyến scenario A. Lưu map khi Cartographer và record vẫn đang chạy:

```bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
phase_4_data_collection/save_map.sh \
  --system cartographer --scenario A --run 1 --imu off
```

Sau đó `Ctrl+C` terminal record, monitor và Cartographer.

Trích trajectory:

```bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
phase_6_evaluation/extract_trajectory_from_bag.py \
  --bag data/bags/cartographer_A_run1_imu_off
```

Kiểm tra file SLAM:

```bash
ls -lh data/results/trajectories/cartographer_A_run1_imu_off_slam.csv
```

## 5. Gmapping A run 1

Giữ Terminal 1 chạy bringup LIMO. Đảm bảo Cartographer đã dừng.

### Terminal 3 — chạy Gmapping

Script tự source `~/gmapping_ws/install/setup.bash`:

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
phase_3_slam/start_slam.sh --system gmapping --imu off
```

Nếu cần chạy trực tiếp thay vì script:

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
source /home/agilex/gmapping_ws/install/setup.bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts

ros2 run slam_gmapping slam_gmapping_node --ros-args \
  --params-file config/gmapping_limo.yaml \
  -r scan:=/scan
```

### Terminal 4 — record Gmapping

```bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
phase_4_data_collection/run_record_experiment.sh \
  --system gmapping --scenario A --run 1 --imu off
```

### Terminal 5 — đo CPU/RAM Gmapping

```bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
resource_monitoring/measure_process_resources.py \
  --keyword slam_gmapping \
  --output data/resources/gmapping_A_run1_imu_off_resource.csv \
  --interval 1
```

Đi đúng tuyến scenario A như Cartographer. Lưu map trước khi dừng:

```bash
phase_4_data_collection/save_map.sh \
  --system gmapping --scenario A --run 1 --imu off
```

Sau đó dừng record, monitor và Gmapping. Trích trajectory:

```bash
phase_6_evaluation/extract_trajectory_from_bag.py \
  --bag data/bags/gmapping_A_run1_imu_off
```

Kết quả phải có:

```text
data/results/trajectories/gmapping_A_run1_imu_off_slam.csv
```

## 6. SLAM Toolbox A run 1

Giữ Terminal 1 chạy bringup LIMO. Đảm bảo Gmapping đã dừng.

### Terminal 3 — chạy SLAM Toolbox

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
phase_3_slam/start_slam.sh --system slam_toolbox --imu off
```

### Terminal 4 — record SLAM Toolbox

```bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
phase_4_data_collection/run_record_experiment.sh \
  --system slam_toolbox --scenario A --run 1 --imu off
```

### Terminal 5 — đo CPU/RAM SLAM Toolbox

```bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
resource_monitoring/measure_process_resources.py \
  --keyword slam_toolbox \
  --output data/resources/slam_toolbox_A_run1_imu_off_resource.csv \
  --interval 1
```

Đi đúng tuyến scenario A. Lưu map trước khi dừng:

```bash
phase_4_data_collection/save_map.sh \
  --system slam_toolbox --scenario A --run 1 --imu off
```

Sau đó dừng record, monitor và SLAM Toolbox. Trích trajectory:

```bash
phase_6_evaluation/extract_trajectory_from_bag.py \
  --bag data/bags/slam_toolbox_A_run1_imu_off
```

Kết quả phải có:

```text
data/results/trajectories/slam_toolbox_A_run1_imu_off_slam.csv
```

Tạo `reference_A.csv` cố định từ SLAM Toolbox run 1:

```bash
cp data/results/trajectories/slam_toolbox_A_run1_imu_off_slam.csv \
   data/results/trajectories/reference_A.csv
```

Kiểm tra:

```bash
head data/results/trajectories/reference_A.csv
```

Không tạo lại `reference_A.csv` từ run 2 hoặc run 3.

## 7. Cách điều khiển robot

Dùng cùng vị trí và hướng xuất phát cho cả ba thuật toán:

- tốc độ tiến khoảng `0.10–0.20 m/s`;
- tốc độ quay khoảng `0.15–0.25 rad/s`;
- không vừa tiến nhanh vừa quay gấp;
- dừng khoảng 1 giây trước và sau góc cua;
- quay lại gần vị trí cũ với tốc độ thấp để hỗ trợ loop closure;
- dùng cùng một tuyến đường và thứ tự góc cua cho mọi run.

## 8. Kiểm tra đủ dữ liệu trước khi đánh giá

```bash
ls -lh data/maps/*_A_run1_imu_off.pgm
ls -lh data/maps/*_A_run1_imu_off.yaml
ls -lh data/resources/*_A_run1_imu_off_resource.csv
ls -lh data/results/trajectories/*_A_run1_imu_off_slam.csv
ls -lh data/results/trajectories/reference_A.csv
```

Phải có đủ ba system: `cartographer`, `gmapping`, `slam_toolbox`.

## 9. Đánh giá scenario A

Tạo môi trường Python riêng cho phần đánh giá một lần trên LIMO. Không cài/hạ
NumPy trực tiếp vào Python hệ thống vì ROS 2 cũng sử dụng môi trường đó:

```bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
python3 -m venv phase_6_evaluation/.venv
source phase_6_evaluation/.venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r phase_6_evaluation/requirements.txt
```

Kiểm tra:

```bash
python -c "import numpy, cv2, scipy, skimage, pandas; print(numpy.__version__, 'OK')"
```

Mỗi lần mở terminal mới để đánh giá, kích hoạt lại môi trường:

```bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
source phase_6_evaluation/.venv/bin/activate
phase_6_evaluation/evaluate_scenario.sh --scenario A --imu off
```

Không cần thêm `--reference-system` vì script mặc định dùng SLAM Toolbox.
Lệnh đầy đủ tương đương:

```bash
phase_6_evaluation/evaluate_scenario.sh \
  --scenario A --imu off --reference-system slam_toolbox
```

Script sẽ:

1. đọc cả `.pgm` và `.yaml`;
2. đặt map vào cùng hệ tọa độ theo `origin` và `resolution`;
3. tính entropy chỉ trên vùng đã biết, không để canvas xám làm sai kết quả;
4. tính `ssim_raw` và `iou_raw` trước khi căn chỉnh;
5. căn map bằng SE(2), giới hạn mặc định trong 2 m và 20 độ;
6. tính `ssim_aligned`, `iou_aligned` và known coverage sau căn chỉnh;
7. ghi lại `align_dx_m`, `align_dy_m`, `align_yaw_deg`;
8. tính RMSE từ quỹ đạo SLAM bằng quãng đường chuẩn hoá và căn chỉnh SE(2);
9. tạo lại bảng `data/results/final_summary_table.txt`.

Xem kết quả:

```bash
cat data/results/final_summary_table.txt
```

## 10. Run 2 và run 3

Lặp lại ba thuật toán, chỉ đổi:

```text
--run 1  thành  --run 2
--run 1  thành  --run 3
```

Không copy đè `reference_A.csv`. Sau khi trích đủ `_slam.csv`, chạy lại:

```bash
phase_6_evaluation/evaluate_scenario.sh --scenario A --imu off
```

## 11. Scenario B và C

Mỗi scenario cần baseline riêng:

```bash
cp data/results/trajectories/slam_toolbox_B_run1_imu_off_slam.csv \
   data/results/trajectories/reference_B.csv

cp data/results/trajectories/slam_toolbox_C_run1_imu_off_slam.csv \
   data/results/trajectories/reference_C.csv
```

Đánh giá:

```bash
phase_6_evaluation/evaluate_scenario.sh --scenario B --imu off
phase_6_evaluation/evaluate_scenario.sh --scenario C --imu off
```

Không dùng `reference_A.csv` cho scenario B hoặc C.

Các lệnh đánh giá B/C mặc định dùng map:

```text
data/maps/slam_toolbox_B_run1_imu_off.pgm
data/maps/slam_toolbox_C_run1_imu_off.pgm
```

Dòng SLAM Toolbox run 1 sẽ có `SSIM/IoU = 1` và `RMSE = 0` vì đang so với
chính baseline. Đây là baseline tương đối, không phải ground truth đo đạc.
Không dùng riêng các giá trị này để kết luận SLAM Toolbox thắng.

## 12. Cách đọc kết quả

- `ssim_raw`, `iou_raw`: so sánh theo metadata gốc, chưa đăng ký map.
- `ssim_aligned`, `iou_aligned`: so sánh sau khi căn xoay/dịch có giới hạn.
- `align_dx_m`, `align_dy_m`, `align_yaw_deg`: mức hiệu chỉnh đã áp dụng.
- `known_coverage` gần 1 nghĩa là diện tích quan sát phủ gần bằng reference.
- `entropy` chỉ nên so khi map đã được tính bằng code mới.
- `rmse_m` càng thấp thì hình dạng quỹ đạo càng gần reference.

Nếu phép căn chỉnh thường xuyên chạm gần giới hạn 2 m hoặc 20 độ, không nên chỉ
dùng metric aligned để kết luận. Khi đó cần kiểm tra lại vị trí xuất phát,
`origin`, TF và tuyến đường.

SLAM Toolbox run 1 so với chính nó có `SSIM/IoU = 1` và `RMSE = 0`; đây là
baseline tương đối, không phải ground truth tuyệt đối.

## 13. Ghi chú IMU

Với launcher của LIMO, tham số `--imu on/off` trong script chỉ dùng để đặt nhãn
dữ liệu. Việc Cartographer có thực sự dùng IMU hay không phụ thuộc cấu hình bên
trong `limo_cartographer.launch.py` và file Lua mà launcher nạp.

```bash
phase_3_slam/start_slam.sh --system cartographer --imu off
phase_3_slam/start_slam.sh --system cartographer --imu on
```

Không ghi hai bộ kết quả on/off nếu launcher thực tế dùng cùng một cấu hình.

SLAM Toolbox và Gmapping không tự sử dụng topic `/imu` chỉ nhờ đổi tên file.
Muốn so sánh IMU on/off có ý nghĩa, phải hợp nhất encoder và IMU thành `/odom`
bằng `robot_localization`, rồi bảo đảm chỉ có một nguồn TF
`odom -> base_link`.

## 14. Nếu SLAM Toolbox vẫn tạo tường hình quạt

Không tiếp tục lấy số liệu. Kiểm tra lần lượt:

```bash
ros2 run tf2_ros tf2_echo odom base_link
ros2 topic echo /scan --once --field header.frame_id
ros2 topic hz /scan
ros2 topic hz /odom
```

Nếu laser trong RViz vẫn trượt khi quay với `Fixed Frame=odom`, nguyên nhân nằm
ở odometry/TF/thời gian của robot. Khi đó cần hiệu chỉnh encoder hoặc hợp nhất
IMU vào odometry trước khi chạy lại cả ba hệ.
