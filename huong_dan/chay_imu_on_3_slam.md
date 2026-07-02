# Hướng dẫn chạy IMU on cho Cartographer, Gmapping và SLAM Toolbox

Tài liệu này dành cho LIMO chạy ROS 2 Humble. Thực hiện các lệnh từ thư mục
project trên robot, ví dụ:

```bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
```

Đối với Gmapping và SLAM Toolbox, project có bộ cấu hình/script thực thi sẵn
tại:

```text
../imu on/README.md
```

Bộ này gồm cấu hình EKF, kiểm tra topic/TF/subscriber, khởi động SLAM, record,
đo CPU/RAM, lưu map và trích trajectory.

## 1. Hiểu đúng về `--imu on`

Trong các script hiện tại, tham số:

```bash
--imu on
```

chủ yếu dùng để đặt tên bag, map, trajectory và kết quả. Tham số này **không tự
động làm thuật toán sử dụng IMU**.

Một lần chạy chỉ được ghi nhãn `imu_on` khi thỏa một trong hai điều kiện:

1. Cartographer trực tiếp subscribe `/imu` và Lua đang có
   `TRAJECTORY_BUILDER_2D.use_imu_data = true`; hoặc
2. IMU được `robot_localization` hợp nhất với wheel odometry, sau đó SLAM dùng
   TF `odom -> base_link` do EKF tạo ra.

Việc `rosbag2_recorder` subscribe `/imu` chỉ chứng minh IMU được ghi vào bag,
không chứng minh SLAM sử dụng IMU.

## 2. Kiến trúc dùng cho ba hệ SLAM

### Cartographer dùng IMU trực tiếp

```text
/scan ───────────────────────────────┐
/odom và TF odom -> base_link ──────┼──> Cartographer
/imu ────────────────────────────────┘
```

Cartographer có hỗ trợ IMU trực tiếp bằng tùy chọn
`TRAJECTORY_BUILDER_2D.use_imu_data`.

### Gmapping và SLAM Toolbox

```text
wheel odometry (/odom_raw) ──┐
                             ├──> robot_localization EKF
IMU (/imu) ──────────────────┘              │
                                            ├──> /odometry/filtered
                                            └──> TF odom -> base_link
                                                        │
                                                        v
                                         Gmapping hoặc SLAM Toolbox
```

Gmapping và cấu hình SLAM Toolbox đang dùng trong project không trực tiếp nhận
`/imu`. IMU phải tác động gián tiếp thông qua odometry đã được EKF hợp nhất.

## 3. Quy trình khởi động từ đầu

Mỗi thành phần nên chạy trong một terminal riêng. Không đóng terminal bringup
trong suốt thí nghiệm. Chỉ chạy **một thuật toán SLAM tại một thời điểm**; trước
khi đổi sang thuật toán khác, dừng SLAM cũ bằng `Ctrl+C` nhưng giữ bringup robot
đang chạy.

### Terminal 1 — bringup robot LIMO

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
ros2 launch limo_bringup limo_start.launch.py
```

Chờ bringup khởi động xong, sau đó mở terminal khác và kiểm tra nhanh:

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash

ros2 topic list
ros2 topic hz /scan
ros2 topic hz /imu
ros2 topic hz /odom
ros2 run tf2_ros tf2_echo odom base_link
```

Bringup phải cung cấp tối thiểu `/scan`, `/imu`, odometry, `/tf` và
`/tf_static`. Nếu `limo_start.launch.py` không có trên robot, tìm launch đúng
bằng:

```bash
ros2 pkg prefix limo_bringup
find "$(ros2 pkg prefix limo_bringup)/share/limo_bringup" \
  -type f -name '*.launch.py'
```

### Chọn đúng nhánh khởi động IMU on

Không thể khởi động SLAM ở chế độ thường rồi chỉ đổi nhãn thành `--imu on`.
Nguồn IMU phải được cấu hình trước khi node SLAM bắt đầu xử lý dữ liệu.

#### Cartographer

Thứ tự là:

```text
bringup LIMO
-> chọn Lua use_imu_data=true
-> chạy Cartographer
-> kiểm tra Cartographer subscribe /imu
-> kiểm tra map trong RViz
-> record
```

Sau khi xác nhận launcher đang nạp cấu hình IMU on, chạy ở Terminal 2:

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts

phase_3_slam/start_slam.sh --system cartographer --imu on
```

Sau đó mở Terminal 3 để kiểm tra:

```bash
ros2 topic info /imu --verbose
ros2 node info /cartographer_node
ros2 topic hz /map
```

Nếu Cartographer không xuất hiện trong subscriber của `/imu`, dừng node bằng
`Ctrl+C`, sửa launch/Lua rồi khởi động lại. Không thể bật
`use_imu_data=true` cho trajectory đang chạy chỉ bằng lệnh record.

#### Gmapping

Thứ tự là:

```text
bringup LIMO xuất /odom_raw
-> chạy EKF nhận /odom_raw và /imu
-> kiểm tra EKF và TF odom -> base_link
-> chạy Gmapping
-> kiểm tra map trong RViz
-> record
```

Terminal 2 chạy EKF:

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash

ros2 run robot_localization ekf_node --ros-args \
  --params-file /duong/dan/toi/ekf_imu_on.yaml
```

Terminal 3 kiểm tra EKF:

```bash
ros2 node info /ekf_filter_node
ros2 topic info /imu --verbose
ros2 topic hz /odometry/filtered
ros2 run tf2_ros tf2_echo odom base_link
```

Chỉ khi EKF hoạt động đúng, Terminal 4 mới chạy Gmapping:

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
source /home/agilex/gmapping_ws/install/setup.bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts

phase_3_slam/start_slam.sh --system gmapping --imu on
```

Sau đó kiểm tra:

```bash
ros2 node list
ros2 topic hz /map
ros2 run tf2_ros tf2_echo map odom
```

#### SLAM Toolbox

Thứ tự giống Gmapping:

```text
bringup LIMO xuất /odom_raw
-> chạy EKF nhận /odom_raw và /imu
-> kiểm tra EKF và TF odom -> base_link
-> chạy SLAM Toolbox
-> kiểm tra map trong RViz
-> record
```

Giữ terminal EKF chạy. Trong terminal mới:

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts

phase_3_slam/start_slam.sh --system slam_toolbox --imu on
```

Sau đó kiểm tra:

```bash
ros2 node list | grep slam_toolbox
ros2 topic hz /map
ros2 run tf2_ros tf2_echo map odom
```

### Preflight sau khi các node cần thiết đã chạy

Mở terminal mới:

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts

phase_3_slam/preflight_slam.sh
```

Chỉ bắt đầu di chuyển theo kịch bản và record khi:

- preflight báo `PASS`;
- `/map` có dữ liệu;
- subscriber IMU đúng với kiến trúc đã chọn;
- TF không bị trùng nguồn;
- laser không xòe hình quạt trong RViz.

Khi đạt các điều kiện trên, mở terminal record:

```bash
phase_4_data_collection/run_record_experiment.sh \
  --system gmapping \
  --scenario A \
  --run 1 \
  --imu on
```

Đổi `gmapping` thành `cartographer` hoặc `slam_toolbox` tương ứng. Tóm tắt thứ
tự bắt buộc:

```text
source môi trường
-> bringup robot
-> cấu hình/bật đường dữ liệu IMU
-> chạy EKF nếu là Gmapping hoặc SLAM Toolbox
-> chạy một thuật toán SLAM
-> kiểm tra topic, subscriber, TF và RViz
-> record
-> lưu map
```

## 4. Kiểm tra IMU chi tiết

### 4.1. Kiểm tra topic và kiểu message

```bash
ros2 topic list | grep -E '(^|/)imu'
ros2 topic type /imu
ros2 topic info /imu --verbose
```

Kết quả cần có:

- `/imu` tồn tại;
- kiểu message là `sensor_msgs/msg/Imu`;
- có ít nhất một publisher từ driver;
- sau khi bật SLAM/EKF phải có subscriber phù hợp.

### 4.2. Kiểm tra dữ liệu và tần số

```bash
ros2 topic echo /imu --once
ros2 topic hz /imu
```

Kiểm tra:

- `header.stamp` thay đổi liên tục và không nhảy ngược;
- `angular_velocity.z` thay đổi dấu và độ lớn khi xoay robot;
- `linear_acceleration` không chứa `nan` hoặc `inf`;
- tần số ổn định, nên từ 20 Hz trở lên;
- khi robot đứng yên, vận tốc góc không được trôi quá lớn.

Không tiếp tục thu dữ liệu nếu `/imu` mất message, timestamp lỗi hoặc giá trị
không thay đổi khi robot chuyển động.

### 4.3. Kiểm tra frame IMU

Đọc tên frame:

```bash
ros2 topic echo /imu --once --field header.frame_id
```

Giả sử kết quả là `imu_link`, kiểm tra:

```bash
ros2 run tf2_ros tf2_echo base_link imu_link
```

TF phải tồn tại, ổn định và thể hiện đúng vị trí/hướng lắp IMU. Không dùng một
static TF giả chỉ để hết báo lỗi nếu hướng trục cảm biến chưa được xác nhận.

Có thể xem toàn bộ cây TF:

```bash
ros2 run tf2_tools view_frames
```

### 4.4. Kiểm tra covariance

```bash
ros2 topic echo /imu --once
```

Kiểm tra ba trường:

- `orientation_covariance`;
- `angular_velocity_covariance`;
- `linear_acceleration_covariance`.

Giá trị `orientation_covariance[0] = -1` nghĩa là driver không cung cấp
orientation. Điều này không nhất thiết ngăn dùng `angular_velocity.z`, nhưng
không được cấu hình EKF hợp nhất orientation từ message đó.

## 5. Bật IMU trực tiếp cho Cartographer

Project có sẵn:

```text
scripts/config/cartographer_limo_imu_on.lua
```

Nội dung quan trọng là:

```lua
TRAJECTORY_BUILDER_2D.use_imu_data = true
```

Tuy nhiên, script hiện tại chạy:

```bash
ros2 launch limo_bringup limo_cartographer.launch.py
```

Do đó phải kiểm tra launch file trong workspace LIMO thực sự nạp file Lua nào:

```bash
phase_7_imu_analysis/check_imu_usage.sh \
  --workspace /home/agilex/agilex_ws

grep -RniE 'configuration_(directory|basename)|use_imu_data' \
  /home/agilex/agilex_ws/src
```

Launch IMU on phải nạp một Lua có:

```lua
TRAJECTORY_BUILDER_2D.use_imu_data = true
```

Khi dùng IMU trực tiếp, nên đặt `tracking_frame` tại frame của IMU, ví dụ:

```lua
tracking_frame = "imu_link"
```

Nếu vẫn dùng `tracking_frame = "base_link"`, Cartographer cần lấy được static
TF chính xác giữa `base_link` và `imu_link`. Đặt tracking frame tại vị trí IMU
giúp tránh sai số do khoảng cách giữa tâm robot và cảm biến khi robot quay.

Launch IMU off phải nạp một Lua có:

```lua
TRAJECTORY_BUILDER_2D.use_imu_data = false
```

Nếu launch hỗ trợ argument `configuration_basename`, có thể chạy theo mẫu:

```bash
ros2 launch limo_bringup limo_cartographer.launch.py \
  configuration_basename:=cartographer_limo_imu_on.lua
```

Tên argument thực tế phải lấy từ:

```bash
ros2 launch limo_bringup limo_cartographer.launch.py --show-args
```

Nếu launch không có argument này, cần sửa launch hoặc file Lua mà launch đang
nạp. Không ghi hai bộ `imu_on` và `imu_off` nếu cả hai lệnh vẫn nạp cùng một
cấu hình.

Cartographer mặc định thường nhận topic tên `imu`. Nếu driver dùng tên khác,
kiểm tra subscriber rồi remap đúng topic trong launch, ví dụ:

```bash
-r imu:=/imu
```

Sau khi Cartographer chạy, xác nhận:

```bash
ros2 node list
ros2 node info /cartographer_node
ros2 topic info /imu --verbose
```

Phải thấy Cartographer là subscriber của `/imu`. Nếu chỉ thấy recorder thì IMU
chưa được Cartographer dùng.

Ngoài ra, theo dõi terminal Cartographer. Các lỗi sau phải được sửa trước:

- không tìm thấy transform từ `imu_link` đến `tracking_frame`;
- IMU data quá cũ hoặc timestamp không tăng;
- extrapolator chờ IMU;
- queue dữ liệu bị block.

Khi đã xác nhận cấu hình và subscriber:

```bash
phase_3_slam/start_slam.sh --system cartographer --imu on
```

Lưu ý: lệnh trên chỉ đúng nghĩa sau khi
`limo_cartographer.launch.py` đã được cấu hình để nạp bản IMU on.

## 6. Tạo odometry có IMU cho Gmapping và SLAM Toolbox

### 6.1. Chuẩn bị topic odometry gốc

Odometry từ encoder nên được xuất thành:

```text
/odom_raw
```

EKF sẽ đọc `/odom_raw` và `/imu`, sau đó xuất:

```text
/odometry/filtered
TF odom -> base_link
```

Không để driver và EKF cùng phát TF `odom -> base_link`. Nếu driver có tham số
như `publish_tf`, `enable_odom_tf` hoặc tương tự, hãy tắt nó khi EKF
`publish_tf: true`.

Tên tham số phụ thuộc driver của LIMO. Tìm bằng:

```bash
grep -RniE 'publish_tf|odom_tf|enable.*tf|/odom' \
  /home/agilex/agilex_ws/src
```

Nếu driver chỉ xuất `/odom`, có thể remap output của driver thành `/odom_raw`.
Không remap toàn hệ thống vì có thể vô tình đổi cả output của EKF.

### 6.2. Cấu hình EKF IMU on mẫu

Tạo file `ekf_imu_on.yaml` trong package bringup của LIMO hoặc thư mục cấu hình
có thể truy cập trên robot:

```yaml
ekf_filter_node:
  ros__parameters:
    frequency: 30.0
    sensor_timeout: 0.2
    two_d_mode: true

    map_frame: map
    odom_frame: odom
    base_link_frame: base_link
    world_frame: odom

    publish_tf: true
    publish_acceleration: false

    odom0: /odom_raw
    odom0_config: [
      false, false, false,
      false, false, false,
      true,  false, false,
      false, false, true,
      false, false, false
    ]
    odom0_differential: false

    imu0: /imu
    imu0_config: [
      false, false, false,
      false, false, false,
      false, false, false,
      false, false, true,
      false, false, false
    ]
    imu0_differential: false
    imu0_relative: false
    imu0_remove_gravitational_acceleration: false
```

Thứ tự 15 giá trị trong mỗi `_config` là:

```text
x, y, z,
roll, pitch, yaw,
vx, vy, vz,
vroll, vpitch, vyaw,
ax, ay, az
```

Cấu hình mẫu hợp nhất:

- `vx` và `vyaw` từ wheel odometry;
- `vyaw`, tức `angular_velocity.z`, từ IMU;
- không dùng orientation và acceleration của IMU ở bước đầu.

Đây là cấu hình khởi đầu an toàn, không phải bộ thông số hiệu chỉnh cuối cùng.
Nếu wheel odometry không cung cấp `twist.twist.angular.z` đáng tin cậy, có thể
đặt phần tử `vyaw` của `odom0_config` thành `false`.

### 6.3. Chạy EKF

Kiểm tra package:

```bash
ros2 pkg prefix robot_localization
```

Nếu package đã có, chạy:

```bash
ros2 run robot_localization ekf_node --ros-args \
  --params-file /duong/dan/toi/ekf_imu_on.yaml
```

Thay `/duong/dan/toi/ekf_imu_on.yaml` bằng đường dẫn thật trên LIMO.

Xác nhận EKF subscribe đúng:

```bash
ros2 node info /ekf_filter_node
ros2 topic info /imu --verbose
ros2 topic info /odom_raw --verbose
ros2 topic hz /odometry/filtered
ros2 run tf2_ros tf2_echo odom base_link
```

Phải thấy:

- `/ekf_filter_node` subscribe `/imu` và `/odom_raw`;
- `/odometry/filtered` có dữ liệu liên tục;
- TF `odom -> base_link` thay đổi mượt;
- không có hai nguồn cùng phát TF `odom -> base_link`.

## 7. Chạy Gmapping với IMU on

Gmapping không cần thêm `imu_topic` vào
`scripts/config/gmapping_limo.yaml`. Nó nhận hiệu ứng của IMU qua TF do EKF
phát.

Thứ tự chạy:

1. Bringup robot, xuất wheel odometry thành `/odom_raw`.
2. Chạy EKF với `ekf_imu_on.yaml`.
3. Xác nhận TF `odom -> base_link`.
4. Chạy Gmapping:

```bash
phase_3_slam/start_slam.sh --system gmapping --imu on
```

Kiểm tra:

```bash
ros2 node info /slam_gmapping
ros2 run tf2_ros tf2_echo odom base_link
ros2 topic hz /scan
ros2 topic hz /odometry/filtered
```

Tên node Gmapping có thể khác. Nếu `/slam_gmapping` không tồn tại, lấy tên thật
từ:

```bash
ros2 node list
```

Gmapping không cần xuất hiện trong danh sách subscriber của `/imu`; EKF mới là
subscriber IMU. Bằng chứng IMU on là:

```text
/imu -> ekf_filter_node -> TF odom -> base_link -> Gmapping
```

## 8. Chạy SLAM Toolbox với IMU on

Không thêm tùy ý các tham số `use_imu` hoặc `imu_topic` vào
`scripts/config/slam_toolbox_limo.yaml`. Cấu hình hiện tại sử dụng odometry qua
TF, nên IMU phải được hợp nhất bởi EKF.

Thứ tự chạy:

1. Bringup robot, xuất wheel odometry thành `/odom_raw`.
2. Chạy EKF với `ekf_imu_on.yaml`.
3. Xác nhận TF `odom -> base_link`.
4. Chạy SLAM Toolbox:

```bash
phase_3_slam/start_slam.sh --system slam_toolbox --imu on
```

Kiểm tra:

```bash
ros2 node list | grep slam_toolbox
ros2 run tf2_ros tf2_echo odom base_link
ros2 topic hz /scan
ros2 topic hz /odometry/filtered
```

SLAM Toolbox không cần subscribe `/imu`. Bằng chứng IMU on là:

```text
/imu -> ekf_filter_node -> TF odom -> base_link -> SLAM Toolbox
```

## 9. Kiểm tra TF trùng nguồn

Chỉ một thành phần được phát TF `odom -> base_link`. Khi dùng EKF, thành phần đó
nên là `ekf_filter_node`.

Kiểm tra node đang publish `/tf`:

```bash
ros2 topic info /tf --verbose
```

Lệnh này có thể liệt kê nhiều publisher vì các node phát các TF khác nhau. Sau
đó kiểm tra cấu hình của driver odometry và EKF để chắc chắn chỉ một node sở hữu
`odom -> base_link`.

Dấu hiệu TF bị phát trùng:

- robot hoặc laser rung/giật trong RViz;
- tường bị xòe thành hình quạt khi robot xoay;
- TF nhảy qua lại giữa hai pose;
- log báo transform cũ, tương lai hoặc không liên tục.

## 10. Kiểm tra trực quan trước khi record

Chạy preflight:

```bash
phase_3_slam/preflight_slam.sh
```

Kiểm tra riêng:

```bash
ros2 topic hz /imu
ros2 topic hz /scan
ros2 topic hz /odom_raw
ros2 topic hz /odometry/filtered
ros2 run tf2_ros tf2_echo base_link imu_link
ros2 run tf2_ros tf2_echo odom base_link
```

Trong RViz:

1. đặt `Fixed Frame` thành `odom`;
2. thêm display `LaserScan` với topic `/scan`;
3. cho robot đứng yên rồi xoay chậm tại chỗ;
4. các điểm tường phải gần như đứng yên;
5. không được xuất hiện tường kép hoặc hình quạt rõ rệt.

Nếu scan trượt mạnh, dừng thu dữ liệu và kiểm tra:

- hướng trục IMU;
- timestamp IMU, scan và odometry;
- static TF `base_link -> imu_link`;
- covariance;
- nguồn TF trùng;
- độ trễ hoặc tần số EKF.

## 11. Record và xác nhận bag IMU on

Sau khi SLAM và EKF/IMU đã được xác nhận:

```bash
phase_4_data_collection/run_record_experiment.sh \
  --system gmapping \
  --scenario A \
  --run 1 \
  --imu on
```

Thay `gmapping` bằng `cartographer` hoặc `slam_toolbox` khi cần.

Sau khi dừng record:

```bash
ros2 bag info data/bags/gmapping_A_run1_imu_on
```

Bag cần có ít nhất:

- `/imu`;
- `/scan`;
- `/tf` và `/tf_static`;
- `/map`;
- `/odom` hoặc odometry phù hợp với cấu hình thực tế.

Script record hiện ghi `/odom`, nhưng kiến trúc EKF mẫu xuất
`/odometry/filtered` và nhận `/odom_raw`. Để có đủ bằng chứng tái lập thí
nghiệm, nên bổ sung cả hai topic này vào lệnh record:

```text
/odom_raw
/odometry/filtered
```

Việc bag có `/imu` vẫn chưa đủ; phải lưu lại kết quả kiểm tra subscriber và cấu
hình dùng trong từng lần chạy.

## 12. Checklist xác nhận IMU on thật

Trước mỗi lần chạy, đánh dấu đủ:

- [ ] `/imu` là `sensor_msgs/msg/Imu`.
- [ ] Tần số `/imu` ổn định.
- [ ] `angular_velocity.z` phản ứng đúng khi xoay robot.
- [ ] Không có `nan` hoặc `inf`.
- [ ] TF `base_link -> imu_link` tồn tại và đúng hướng.
- [ ] Chỉ có một nguồn TF `odom -> base_link`.
- [ ] Cartographer trực tiếp subscribe `/imu`; hoặc EKF subscribe `/imu`.
- [ ] Với Gmapping/SLAM Toolbox, EKF cũng subscribe wheel odometry.
- [ ] `/odometry/filtered` và TF `odom -> base_link` liên tục.
- [ ] Laser không xòe hình quạt trong RViz khi xoay.
- [ ] Cấu hình IMU on khác IMU off về nguồn dữ liệu, không chỉ khác tên file.
- [ ] Chỉ sau các bước trên mới chạy script với `--imu on`.

## 13. So sánh IMU on và IMU off công bằng

Đối với Gmapping và SLAM Toolbox, nên giữ EKF ở cả hai chế độ:

- **IMU off:** EKF chỉ nhận `/odom_raw`;
- **IMU on:** EKF nhận `/odom_raw` và `/imu`.

Như vậy node xuất odometry, tần số output và chuỗi TF được giữ giống nhau; biến
thay đổi chính là dữ liệu IMU.

Đối với Cartographer có hai lựa chọn:

1. so sánh khả năng IMU tích hợp trực tiếp của Cartographer bằng
   `use_imu_data=false/true`; hoặc
2. cho Cartographer dùng cùng odometry EKF như hai hệ còn lại và giữ
   `use_imu_data=false`.

Không nên vừa đưa IMU vào EKF, vừa bật `use_imu_data=true` trong Cartographer
khi mục tiêu là một phép so sánh đơn giản, vì cùng một IMU sẽ đi vào hệ thống
qua hai đường và kết quả khó diễn giải.

Trước khi chạy toàn bộ thí nghiệm, thử một đoạn ngắn và lưu:

```bash
ros2 topic info /imu --verbose
ros2 node info /ekf_filter_node
ros2 topic info /tf --verbose
ros2 bag info <duong_dan_bag_thu>
```

Chỉ khi lần thử đạt toàn bộ checklist mới chạy các scenario A, B, C và các run
còn lại.
