# Workflow Navigation2

Thư mục `nav2/` chứa script cài đặt, reset, chạy Nav2 và kiểm tra robot trên
LIMO thật.

## 1. Chuẩn bị

Copy thư mục `nav2` lên LIMO theo đường dẫn:

```text
/home/agilex/Documents/LimoDATN20252/nav2
```

Trên LIMO:

```bash
cd /home/agilex/Documents/LimoDATN20252/nav2
chmod +x *.sh
```

Cài các package cần thiết:

```bash
./install_all.sh
```

## 2. Bringup base và lidar

Terminal base:

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
export ROS_DOMAIN_ID=99
ros2 launch limo_base limo_base.launch.py port_name:=ttyUSB0 pub_odom_tf:=true
```

Terminal lidar:

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
export ROS_DOMAIN_ID=99
ros2 launch ydlidar_ros2_driver ydlidar.launch.py
```

## 3. Kiểm tra trước khi chạy Nav2

```bash
timeout 3 ros2 topic echo /odom_raw --once
timeout 3 ros2 topic echo /scan --once
timeout 3 ros2 run tf2_ros tf2_echo odom base_link
```

Ba lệnh trên phải có dữ liệu thật. Chỉ thấy topic trong `ros2 topic list` là
chưa đủ.

## 4. Chạy Nav2

```bash
cd /home/agilex/Documents/LimoDATN20252/nav2
export ROS_DOMAIN_ID=99
./reset_nav2.sh
./run_nav2_clean.sh
```

Mở RViz trong terminal khác nếu cần:

```bash
./run_rviz.sh
```

## 5. Kiểm tra vận tốc và TF

```bash
./check_tf.sh
./check_nav2.sh
./watch_cmd_vel.sh
```

Gửi thử velocity:

```bash
./test_cmd_vel.sh
```

## Tài liệu chi tiết

Xem đầy đủ tại `nav2/README.md`.
