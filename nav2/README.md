# Huong dan chay Navigation2 cho xe LIMO ROS 2 Humble

Thu muc nay chua huong dan va cau hinh mau de chay Nav2 tren xe LIMO that. Cach chay duoi day gia dinh ban dang dung ROS 2 Humble, workspace LIMO o:

```bash
/home/agilex/agilex_ws
```

Va thu muc Nav2 cua de tai o:

```bash
/home/agilex/Documents/LimoDATN20252/nav2
```

Neu workspace hoac package bringup cua ban khac, chi can thay duong dan/package tuong ung.

## Chay nhanh tu thu muc nav2

Neu muon cai dat lai day du va chay gon hon, copy thu muc `nav2` nay len LIMO theo dung duong dan:

```bash
/home/agilex/Documents/LimoDATN20252/nav2
```

Sau do:

```bash
cd /home/agilex/Documents/LimoDATN20252/nav2
chmod +x *.sh
```

### 1. Cai day du package Nav2

```bash
./install_all.sh
```

Lenh nay cai Nav2, AMCL, map server, planner, controller, DWB, RViz va cac goi lien quan.

### 2. Terminal bringup robot LIMO

Terminal nay van source `agilex_ws`:

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
export ROS_DOMAIN_ID=99

# Tren xe hien tai, phai truyen dung port serial. Neu khong, limo_base_node
# co the crash voi exit code -11 va xe khong nhan /cmd_vel.
ros2 launch limo_base limo_base.launch.py port_name:=ttyUSB0 pub_odom_tf:=true
```

Lenh tren dam bao base driver, `/cmd_vel`, `/odom_raw` va TF `odom -> base_link`. Neu sau do chua co `/scan`, mo them terminal rieng de chay lidar/bringup lidar dang dung, nhung tranh chay them mot `limo_base_node` trung.

Neu `ttyUSB0` khong dung, kiem tra port:

```bash
ls -l /dev/limo_base /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
```

Neu `/dev/limo_base -> ttyUSB0` thi dung `port_name:=ttyUSB0`. Neu link tro sang port khac, thay `ttyUSB0` bang port do.

Mot so workspace LIMO co bringup tong hop duoi day, nhung voi xe nay chi dung khi chac chan launch do da truyen dung `port_name` cho `limo_base`:

```bash
ros2 launch limo_bringup limo_start.launch.py
```

De terminal nay chay nguyen.

### 3. Terminal lidar

Mo terminal rieng cho lidar:

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
export ROS_DOMAIN_ID=99

ros2 launch ydlidar_ros2_driver ydlidar.launch.py
```

De terminal nay chay nguyen. Neu ten launch khac, tim bang:

```bash
find /home/agilex/agilex_ws/src -name "*.launch.py" | grep -i ydlidar
find /home/agilex/agilex_ws/install -name "*.launch.py" | grep -i ydlidar
```

### 4. Kiem tra robot truoc khi chay Nav2

Trong terminal moi:

```bash
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=99

timeout 3 ros2 topic echo /odom_raw --once
timeout 3 ros2 topic echo /scan --once
timeout 3 ros2 run tf2_ros tf2_echo odom base_link
```

Ca 3 lenh tren phai co du lieu. Chi thay ten topic trong `ros2 topic list` la chua du; neu `echo --once` bi treo hoac timeout thi topic chua publish message that.

### 5. Terminal Nav2

Trong terminal moi:

```bash
cd /home/agilex/Documents/LimoDATN20252/nav2
export ROS_DOMAIN_ID=99
./reset_nav2.sh
./run_nav2_clean.sh
```

`run_nav2_clean.sh` se chay Nav2 bang shell sach de tranh loi DWB bi `agilex_ws` che. De terminal nay chay nguyen.

### 6. Terminal kiem tra Nav2

```bash
cd /home/agilex/Documents/LimoDATN20252/nav2
export ROS_DOMAIN_ID=99
./check_nav2.sh
```

Can thay:

```text
active [3]
active [3]
active [3]
Action servers: 1
```

Neu `controller_server`, `planner_server` hoac `bt_navigator` van `inactive [2]`, thu activate lai:

```bash
cd /home/agilex/Documents/LimoDATN20252/nav2
export ROS_DOMAIN_ID=99
./activate_nav2.sh
```

### 7. Mo RViz

```bash
cd /home/agilex/Documents/LimoDATN20252/nav2
export ROS_DOMAIN_ID=99
./run_rviz.sh
```

Trong RViz, bam `2D Pose Estimate` truoc, doi hat AMCL gom lai, roi bam `Nav2 Goal`.

### 8. Neu Nav2 co `/cmd_vel` nhung xe khong chay

Neu `ros2 topic echo /cmd_vel` co lenh, vi du:

```text
linear.x: 0.0
angular.z: 1.0
```

thi Nav2 da phat lenh. Hay test driver/motor truc tiep:

```bash
cd /home/agilex/Documents/LimoDATN20252/nav2
export ROS_DOMAIN_ID=99
./test_cmd_vel.sh
```

Ket qua:

- Neu test di thang/rotate deu khong nhuc nhich: loi nam o bringup LIMO, motor lock, E-stop, mode xe, hoac driver khong subscribe `/cmd_vel`.
- Neu test di thang chay duoc nhung rotate khong chay: xe co the dang o Ackermann/car mode, khong quay tai cho duoc.
- Neu test chay duoc nhung Nav2 khong chay: set lai `2D Pose Estimate`, dat goal xa hon 0.5-1 m va cung huong voi dau xe.

Kiem tra ai subscribe `/cmd_vel`:

```bash
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=99
ros2 topic info /cmd_vel -v
```

Phai co subscriber tu driver LIMO. Neu khong co subscriber, bringup robot chua dung hoac driver dang nghe topic khac.

Neu `ros2 launch limo_base limo_base.launch.py` vua chay da chet voi log:

```text
process has died ... exit code -11
port name: limo_base
```

thi thuong la sai `port_name`. Chay lai bang port serial that:

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
export ROS_DOMAIN_ID=99
ros2 launch limo_base limo_base.launch.py port_name:=ttyUSB0 pub_odom_tf:=true
```

Sau do kiem tra lai:

```bash
ros2 node list | grep limo
ros2 topic info /cmd_vel -v
ros2 topic echo /odom_raw --once
ros2 run tf2_ros tf2_echo odom base_link
```

### 9. Neu RViz bi lag va TF hien mau vang/cam

Neu map van hien, `Global Status: Ok`, nhung RViz bao TF warning hoac terminal co log:

```text
Message Filter dropping message
queue is full
Lookup would require extrapolation
```

thi thuong la RViz/NoMachine dang qua tai vi hien thi qua nhieu display tan so cao. Cach xu ly:

1. Tat bot display trong RViz, chi de lai cac muc can thiet:

```text
Map                bat
Global Planner     bat khi can xem path
Controller         bat khi can xem local plan
Amcl Particle Swarm bat luc set pose, tat sau khi hat da gom
TF                 tat neu bi lag
LaserScan          tat neu bi lag
Bumper Hit         tat
MarkerArray        tat neu bi lag
```

2. Neu RViz van lag, dong het RViz cu:

```bash
pkill -f rviz2
```

3. Dam bao chi co mot Nav2 dang chay:

```bash
cd /home/agilex/Documents/LimoDATN20252/nav2
export ROS_DOMAIN_ID=99
./reset_nav2.sh
./run_nav2_clean.sh
```

4. Mo RViz lai trong terminal khac:

```bash
cd /home/agilex/Documents/LimoDATN20252/nav2
export ROS_DOMAIN_ID=99
./run_rviz.sh
```

5. Sau khi set `2D Pose Estimate`, tat `Amcl Particle Swarm` de giam lag.

Neu TF warning chi xuat hien trong RViz nhung `ros2 run tf2_ros tf2_echo odom base_link` van co du lieu lien tuc, co the tam bo qua warning do.

Neu trong RViz `map` va `odom` OK nhung `base_link`, `laser_link`, `imu_link` bao `No transform`, chay:

```bash
cd /home/agilex/Documents/LimoDATN20252/nav2
chmod +x *.sh
export ROS_DOMAIN_ID=99
./check_tf.sh
```

Doc ket qua:

- `odom -> base_link` loi: bringup LIMO/odometry TF chua chay hoac Nav2/RViz khong cung `ROS_DOMAIN_ID`.
- `odom -> base_link` OK nhung `map -> base_link` loi: AMCL chua co pose, bam lai `2D Pose Estimate`.
- `base_link -> laser_link` loi: thieu static TF lidar, can start robot_state_publisher/bringup dung cua LIMO hoac them static transform.
- `base_link -> imu_link` loi: thieu static TF IMU, khong nhat thiet lam Nav2 dung neu khong dung IMU, nhung nen sua trong bringup.

## 0. Chay lai tu dau khi Nav2 bi loi

Dung khi gap cac loi nhu:

```text
controller_server unconfigured
navigate_to_pose action server is not available
Timed out waiting for transform from base_link to odom
```

Mo 4 terminal va chay theo dung thu tu duoi day.

### Terminal 1: chay bringup robot LIMO

Terminal nay dung workspace LIMO nen co source `agilex_ws`:

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
export ROS_DOMAIN_ID=99

# Base driver LIMO. Tren xe hien tai can port_name:=ttyUSB0.
ros2 launch limo_base limo_base.launch.py port_name:=ttyUSB0 pub_odom_tf:=true
```

Neu `/scan` chua co, chay them lidar launch dang dung trong terminal rieng. Khong chay trung hai `limo_base_node`.

De terminal nay chay nguyen, khong tat.

### Terminal 2: chay lidar

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
export ROS_DOMAIN_ID=99

ros2 launch ydlidar_ros2_driver ydlidar.launch.py
```

De terminal nay chay nguyen.

### Terminal 3: lay ROS_DOMAIN_ID va kiem tra robot

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
export ROS_DOMAIN_ID=99

echo $ROS_DOMAIN_ID
ros2 topic list | grep -E "odom|scan|cmd_vel"
timeout 3 ros2 topic echo /odom_raw --once
timeout 3 ros2 topic echo /scan --once
ros2 run tf2_ros tf2_echo odom base_link
```

Neu lenh TF `odom base_link` khong chay, thu:

```bash
ros2 run tf2_ros tf2_echo odom base_footprint
```

Neu `base_footprint` moi dung, sua params:

```bash
sed -i 's/base_link/base_footprint/g' \
  /home/agilex/Documents/LimoDATN20252/nav2/params/limo_nav2_params.yaml
```

Ghi nho gia tri `ROS_DOMAIN_ID`. Neu `echo $ROS_DOMAIN_ID` khong in gi thi bo qua buoc export domain o terminal Nav2.

### Terminal 4: chay Nav2 bang shell sach

Vao shell sach de tranh loi DWB bi workspace `agilex_ws` che:

```bash
env -i HOME=$HOME USER=$USER LOGNAME=$LOGNAME SHELL=/bin/bash TERM=$TERM \
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
bash --noprofile --norc
```

Neu prompt doi thanh `bash-5.1$` la dung. Chay tiep trong chinh terminal do:

```bash
source /opt/ros/humble/setup.bash

# Chi can dong nay neu Terminal 2 co ROS_DOMAIN_ID, vi du 5
# export ROS_DOMAIN_ID=5

export NAV2_DIR=/home/agilex/Documents/LimoDATN20252/nav2
export MAP_FILE=$NAV2_DIR/maps/maps.yaml
export PARAMS_FILE=$NAV2_DIR/params/limo_nav2_params.yaml
```

Kiem tra shell Nav2 thay robot:

```bash
ros2 topic list | grep -E "odom|scan|cmd_vel"
ros2 run tf2_ros tf2_echo odom base_link
```

Neu params da doi sang `base_footprint`, kiem tra:

```bash
ros2 run tf2_ros tf2_echo odom base_footprint
```

Kiem tra DWB phai deu la `/opt/ros/humble`:

```bash
ros2 pkg prefix dwb_core
ros2 pkg prefix dwb_plugins
ros2 pkg prefix dwb_critics
```

Chay Nav2:

```bash
ros2 launch nav2_bringup bringup_launch.py \
  map:=$MAP_FILE \
  params_file:=$PARAMS_FILE \
  use_sim_time:=false \
  autostart:=true
```

De terminal nay chay nguyen, khong tat. Neu no quay ve prompt la Nav2 da bi loi, can doc log do.

### Terminal 4: kiem tra active va mo RViz

```bash
source /opt/ros/humble/setup.bash

# Neu Terminal 2 co ROS_DOMAIN_ID thi export y het o day
# export ROS_DOMAIN_ID=5

ros2 lifecycle get /controller_server
ros2 lifecycle get /planner_server
ros2 lifecycle get /bt_navigator
ros2 action info /navigate_to_pose
```

Ket qua dung:

```text
active [3]
active [3]
active [3]
Action servers: 1
```

Mo RViz:

```bash
rviz2 -d $(ros2 pkg prefix nav2_bringup)/share/nav2_bringup/rviz/nav2_default_view.rviz
```

Trong RViz:

1. Bam `2D Pose Estimate` dung vi tri robot tren map.
2. Cho hat AMCL gom lai quanh robot.
3. Bam `Nav2 Goal` gan robot truoc, khoang 0.5 den 1 m.

### Neu bao duplicate node hoac planner_server bi treo

Neu thay canh bao:

```text
WARNING: Be aware that are nodes in the graph that share an exact name
```

hoac `ros2 lifecycle get /planner_server` bi treo, thuong la da chay chong nhieu lan Nav2. Hay tat het cac terminal dang chay Nav2/RViz bang `Ctrl+C`, chi de lai terminal bringup robot LIMO.

Kiem tra con node Nav2 nao khong:

```bash
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=99

ros2 node list | grep -E "amcl|map_server|controller_server|planner_server|bt_navigator|waypoint|smoother|behavior|velocity_smoother"
```

Neu van con node Nav2 sau khi da `Ctrl+C`, kill cac process Nav2 cu:

```bash
pkill -f "bringup_launch.py"
pkill -f "localization_launch.py"
pkill -f "navigation_launch.py"
pkill -f "planner_server"
pkill -f "controller_server"
pkill -f "bt_navigator"
pkill -f "waypoint_follower"
pkill -f "behavior_server"
pkill -f "smoother_server"
```

Cho 5 giay roi kiem tra lai:

```bash
ros2 node list | grep -E "controller_server|planner_server|bt_navigator"
```

Neu khong con gi, chay lai duy nhat mot lenh `bringup_launch.py` o Terminal 3. Khong chay them `localization_launch.py` hoac `navigation_launch.py` song song voi `bringup_launch.py`.

### Neu van ket o planner_server

Neu `/controller_server` active nhung `/planner_server` bi treo hoac inactive, can xem planner co load duoc plugin khong:

```bash
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=99

ros2 pkg prefix nav2_navfn_planner
ros2 pkg prefix nav2_planner
ros2 node list | grep planner
ros2 service list | grep planner_server
```

Neu thieu package planner:

```bash
sudo apt update
sudo apt install -y ros-humble-nav2-navfn-planner ros-humble-nav2-planner
```

Kiem tra log cua terminal dang chay Nav2, tim dong co:

```text
[planner_server]
[global_costmap]
[ERROR]
[FATAL]
```

Neu can reset ROS discovery vi lifecycle command bi treo:

```bash
ros2 daemon stop
ros2 daemon start
```

Sau do chay lai:

```bash
timeout 5 ros2 lifecycle get /planner_server
timeout 5 ros2 lifecycle set /planner_server activate
```

## 1. Cai Nav2 neu may chua co

Tren LIMO:

```bash
sudo apt update
sudo apt install -y ros-humble-navigation2 ros-humble-nav2-bringup ros-humble-tf-transformations
```

Source moi truong:

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
```

Kiem tra Nav2 co san:

```bash
ros2 pkg list | grep nav2_bringup
```

## 2. Kiem tra robot truoc khi chay navigation

Start bringup cua LIMO trong Terminal 1. Ten launch phu thuoc workspace ban dang cai. Hay tim launch hien co:

```bash
ros2 pkg list | grep -i limo
ros2 pkg executables | grep -i limo
find /home/agilex/agilex_ws/src -name "*.launch.py" | grep -i limo
```

Mot so workspace LIMO thuong co lenh bringup gan giong:

```bash
ros2 launch limo_base limo_base.launch.py port_name:=ttyUSB0 pub_odom_tf:=true
```

Hoac bringup tong hop, neu workspace cua ban da cau hinh dung port cho base:

```bash
ros2 launch limo_bringup limo_start.launch.py
```

Sau khi bringup, mo Terminal 2 va kiem tra cac topic/frame bat buoc:

```bash
ros2 topic list | grep -E "scan|odom|cmd_vel"
ros2 topic echo /scan --once
ros2 topic echo /odom_raw --once
ros2 run tf2_ros tf2_echo odom base_link
```

Nav2 can it nhat:

```text
/scan       LaserScan tu lidar
/odom_raw   odometry cua robot
/cmd_vel    topic dieu khien van toc
TF          odom -> base_link
```

Neu robot dung frame khac, vi du `base_footprint`, hay sua `robot_base_frame` trong `params/limo_nav2_params.yaml`.

## 3. Chuan bi map va params

Theo cau truc hien tai, map va params de tai nam o:

```text
/home/agilex/Documents/LimoDATN20252/nav2/maps
/home/agilex/Documents/LimoDATN20252/nav2/params
```

Dat bien duong dan de cac lenh ngan hon:

```bash
export NAV2_DIR=/home/agilex/Documents/LimoDATN20252/nav2
export MAP_FILE=$NAV2_DIR/maps/maps.yaml
export PARAMS_FILE=$NAV2_DIR/params/limo_nav2_params.yaml
```

Kiem tra ten file thuc te:

```bash
ls -lh $NAV2_DIR/maps
ls -lh $NAV2_DIR/params
```

Neu file map cua ban khong ten la `maps.yaml`, sua lai bien `MAP_FILE`. Vi du:

```bash
export MAP_FILE=$NAV2_DIR/maps/cartographer_A_run1_imu_on.yaml
```

Neu chua co map, hay chay SLAM truoc roi luu map vao dung thu muc:

```bash
mkdir -p $NAV2_DIR/maps

ros2 run nav2_map_server map_saver_cli \
  -f $NAV2_DIR/maps/maps
```

Lenh tren se tao:

```text
$NAV2_DIR/maps/maps.yaml
$NAV2_DIR/maps/maps.pgm
```

Nav2 voi AMCL can file `.yaml` va anh map `.pgm`/`.png` nam dung duong dan trong YAML.

## 4. Chay Nav2 voi map co san

Mo cac terminal rieng cho base, lidar, localization/navigation va RViz.

### Terminal 1: bringup LIMO

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
export ROS_DOMAIN_ID=99

# Tren xe hien tai can port_name:=ttyUSB0 de limo_base_node khong crash.
ros2 launch limo_base limo_base.launch.py port_name:=ttyUSB0 pub_odom_tf:=true
```

Neu terminal nay chi chay base va chua co `/scan`, mo them terminal lidar rieng truoc khi chay Nav2.

### Terminal 2: lidar

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
export ROS_DOMAIN_ID=99

ros2 launch ydlidar_ros2_driver ydlidar.launch.py
```

Kiem tra nhanh trong terminal khac neu can:

```bash
timeout 3 ros2 topic echo /odom_raw --once
timeout 3 ros2 topic echo /scan --once
timeout 3 ros2 run tf2_ros tf2_echo odom base_link
```

### Terminal 3: chay localization AMCL

Tren LIMO:

```bash
export NAV2_DIR=/home/agilex/Documents/LimoDATN20252/nav2
export MAP_FILE=$NAV2_DIR/maps/maps.yaml
export PARAMS_FILE=$NAV2_DIR/params/limo_nav2_params.yaml

source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash

ros2 launch nav2_bringup localization_launch.py \
  map:=$MAP_FILE \
  params_file:=$PARAMS_FILE \
  use_sim_time:=false
```

Dat pose ban dau cho robot trong RViz bang nut `2D Pose Estimate`. Robot tren RViz nen trung voi vi tri that tren map.

### Terminal 4: chay navigation

```bash
export NAV2_DIR=/home/agilex/Documents/LimoDATN20252/nav2
export PARAMS_FILE=$NAV2_DIR/params/limo_nav2_params.yaml

source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash

ros2 launch nav2_bringup navigation_launch.py \
  params_file:=$PARAMS_FILE \
  use_sim_time:=false
```

### Terminal 5: mo RViz

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash

rviz2 -d $(ros2 pkg prefix nav2_bringup)/share/nav2_bringup/rviz/nav2_default_view.rviz
```

Trong RViz:

1. Chon `2D Pose Estimate` de set vi tri ban dau.
2. Chon `Nav2 Goal` de gui diem dich.
3. Dat goal gan truoc, toc do thap, san phang va co nguoi dung gan nut E-stop.

## 5. Chay bang mot lenh bringup Nav2

Neu muon start AMCL + Nav2 trong mot terminal:

```bash
export NAV2_DIR=/home/agilex/Documents/LimoDATN20252/nav2
export MAP_FILE=$NAV2_DIR/maps/maps.yaml
export PARAMS_FILE=$NAV2_DIR/params/limo_nav2_params.yaml

source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash

ros2 launch nav2_bringup bringup_launch.py \
  map:=$MAP_FILE \
  params_file:=$PARAMS_FILE \
  use_sim_time:=false \
  autostart:=true
```

Lenh nay van can Terminal rieng de chay bringup robot LIMO.

## 6. Navigation khi dang SLAM

Neu ban muon robot vua SLAM vua navigation, khong chay AMCL/map_server. Chay:

1. Bringup LIMO.
2. SLAM Toolbox hoac Cartographer.
3. Nav2 `navigation_launch.py` voi cung file params.

Ví dụ với bộ cấu hình thí nghiệm mới (chạy từ thư mục `scripts`):

```bash
phase_3_slam/preflight_slam.sh
phase_3_slam/start_slam.sh --system slam_toolbox --imu off
```

Sau do:

```bash
export NAV2_DIR=/home/agilex/Documents/LimoDATN20252/nav2
export PARAMS_FILE=$NAV2_DIR/params/limo_nav2_params.yaml

ros2 launch nav2_bringup navigation_launch.py \
  params_file:=$PARAMS_FILE \
  use_sim_time:=false
```

Can dam bao SLAM dang publish TF `map -> odom`.

## 7. Cac tham so nen chinh cho LIMO

File cau hinh mau:

```text
/home/agilex/Documents/LimoDATN20252/nav2/params/limo_nav2_params.yaml
```

Cac dong hay phai sua:

```yaml
robot_base_frame: base_link
odom_topic: /odom_raw
scan.topic: /scan
robot_radius: 0.25
max_vel_x: 0.35
max_vel_theta: 1.0
```

Neu LIMO cua ban chay che do Ackermann, nen giu toc do cham va tranh goal co quay tai cho qua gat. Neu LIMO chay differential mode, cau hinh DWB trong file mau thuong de test ban dau duoc.

## 8. Lenh debug nhanh

Kiem tra lifecycle:

```bash
ros2 lifecycle nodes
ros2 lifecycle get /controller_server
ros2 lifecycle get /planner_server
ros2 lifecycle get /bt_navigator
```

Neu node dang `inactive`, co the activate thu:

```bash
ros2 lifecycle set /controller_server configure
ros2 lifecycle set /controller_server activate
ros2 lifecycle set /planner_server configure
ros2 lifecycle set /planner_server activate
ros2 lifecycle set /bt_navigator configure
ros2 lifecycle set /bt_navigator activate
```

Kiem tra TF:

```bash
ros2 run tf2_ros tf2_echo map odom
ros2 run tf2_ros tf2_echo odom base_link
```

Kiem tra command velocity:

```bash
ros2 topic echo /cmd_vel
```

Kiem tra costmap:

```bash
ros2 topic list | grep costmap
ros2 topic echo /local_costmap/costmap --once
ros2 topic echo /global_costmap/costmap --once
```

## 9. Loi hay gap

### Khong thay map trong RViz

- Sai duong dan file map `.yaml`.
- File `.yaml` tro den anh `.pgm`/`.png` khong dung duong dan.
- Chua co TF `map -> odom`.

Sua nhanh neu log co dang:

```text
Failed to load image file /home/agilex/Documents/LimoDATN20252/nav2/maps.pgm
Failed to load map yaml file: /home/agilex/Documents/LimoDATN20252/nav2/maps/maps.yaml
```

Loi nay nghia la `maps.yaml` dang tro sai anh map. Sua file map YAML:

```bash
gedit /home/agilex/Documents/LimoDATN20252/nav2/maps/maps.yaml
```

Doi dong `image:` thanh mot trong hai cach sau.

Cach khuyen dung:

```yaml
image: maps.pgm
```

Hoac dung duong dan tuyet doi:

```yaml
image: /home/agilex/Documents/LimoDATN20252/nav2/maps/maps.pgm
```

Sau do kiem tra lai:

```bash
cat /home/agilex/Documents/LimoDATN20252/nav2/maps/maps.yaml
ls -lh /home/agilex/Documents/LimoDATN20252/nav2/maps/maps.pgm
```

Tat Nav2 cu bang `Ctrl+C`, roi chay lai `bringup_launch.py`.

### Set goal nhung robot khong chay

- Chua set `2D Pose Estimate`.
- Nav2 lifecycle chua active.
- Khong co `/cmd_vel` hoac bringup LIMO khong subscribe `/cmd_vel`.
- Costmap bi obstacle che het xung quanh robot.

Neu RViz bao:

```text
navigate_to_pose action server is not available. Is the initial pose set?
```

thi thuong la `bt_navigator`/Nav2 chua active, hoac terminal chay Nav2 da abort va quay ve prompt. Kiem tra:

```bash
ros2 action list | grep navigate
ros2 action info /navigate_to_pose
ros2 lifecycle get /controller_server
ros2 lifecycle get /planner_server
ros2 lifecycle get /bt_navigator
```

Neu `ros2 action list` co `/navigate_to_pose` nhung `ros2 action info /navigate_to_pose` khong co `Action servers`, do co the chi la client tu RViz, chua co server Nav2 that. Kiem tra node that:

```bash
ros2 node list | grep -E "controller|planner|bt_navigator|navigator|lifecycle"
```

Neu `lifecycle get` bao `Node not found`, hay cac node khong phai `active [3]`, phai xem lai terminal chay Nav2. Terminal do phai dang giu process launch, khong duoc quay ve prompt. Chay lai Nav2:

```bash
export NAV2_DIR=/home/agilex/Documents/LimoDATN20252/nav2
export MAP_FILE=$NAV2_DIR/maps/maps.yaml
export PARAMS_FILE=$NAV2_DIR/params/limo_nav2_params.yaml

source /opt/ros/humble/setup.bash

ros2 launch nav2_bringup bringup_launch.py \
  map:=$MAP_FILE \
  params_file:=$PARAMS_FILE \
  use_sim_time:=false \
  autostart:=true
```

Sau khi thay `active [3]`, set lai `2D Pose Estimate`, doi hat AMCL gom lai quanh vi tri robot, roi moi bam `Nav2 Goal`.

Neu log co dang:

```text
Could not create object of class type dwb_plugins::StandardTrajectoryGenerator
Failed to change state for node: controller_server
unconfigured [1]
```

Loi nay lam `controller_server`, `planner_server`, `bt_navigator` bi dung o trang thai `unconfigured`. Khong activate tay luc nay, vi configure dang fail. Can cai/thay plugin controller truoc.

Kiem tra DWB plugin:

```bash
ros2 pkg list | grep -E "dwb|nav2_dwb"
```

Neu khong thay package DWB, cai them cac package DWB:

```bash
sudo apt update
sudo apt install -y ros-humble-dwb-core ros-humble-dwb-plugins ros-humble-dwb-critics
```

Kiem tra lai:

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
ros2 pkg prefix dwb_core
ros2 pkg prefix dwb_plugins
ros2 pkg prefix dwb_critics
```

Neu ket qua bi lech kieu:

```text
/opt/ros/humble
/home/agilex/agilex_ws/install/dwb_plugins
/home/agilex/agilex_ws/install/dwb_critics
```

thi workspace `agilex_ws` dang che package DWB cua ROS apt. Cach test nhanh la chay Nav2 trong terminal moi chi source `/opt/ros/humble`, khong source `agilex_ws`:

```bash
bash --noprofile --norc
```

Neu prompt doi thanh `bash-5.1$` thi dung, tiep tuc chay cac lenh ben duoi trong chinh terminal do:

```bash

export NAV2_DIR=/home/agilex/Documents/LimoDATN20252/nav2
export MAP_FILE=$NAV2_DIR/maps/maps.yaml
export PARAMS_FILE=$NAV2_DIR/params/limo_nav2_params.yaml

source /opt/ros/humble/setup.bash

ros2 pkg prefix dwb_core
ros2 pkg prefix dwb_plugins
ros2 pkg prefix dwb_critics

ros2 launch nav2_bringup bringup_launch.py \
  map:=$MAP_FILE \
  params_file:=$PARAMS_FILE \
  use_sim_time:=false \
  autostart:=true
```

Trong truong hop nay, terminal bringup robot LIMO van source `agilex_ws` rieng nhu binh thuong. Chi terminal chay Nav2 tranh source `agilex_ws` de khong bi override DWB.

Neu da source `agilex_ws` trong terminal hien tai, chi `source /opt/ros/humble/setup.bash` lai la chua du, vi cac bien overlay cu van con. Hay dung `bash --noprofile --norc` nhu tren, hoac mo terminal moi va dam bao `.bashrc` khong tu dong source `agilex_ws`.

Sau khi cai xong, tat Nav2 cu bang `Ctrl+C`, mo terminal moi, source lai va chay lai:

```bash
export NAV2_DIR=/home/agilex/Documents/LimoDATN20252/nav2
export MAP_FILE=$NAV2_DIR/maps/maps.yaml
export PARAMS_FILE=$NAV2_DIR/params/limo_nav2_params.yaml

source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash

ros2 launch nav2_bringup bringup_launch.py \
  map:=$MAP_FILE \
  params_file:=$PARAMS_FILE \
  use_sim_time:=false \
  autostart:=true
```

Khi chay dung, cac node phai la `active [3]`:

```bash
ros2 lifecycle get /controller_server
ros2 lifecycle get /planner_server
ros2 lifecycle get /bt_navigator
```

### Robot quay/di qua nhanh

Giam trong `params/limo_nav2_params.yaml`:

```yaml
max_vel_x
max_vel_theta
acc_lim_x
acc_lim_theta
```

### Bao loi frame

So sanh frame thuc te:

```bash
ros2 run tf2_tools view_frames
```

Mo file PDF tao ra va sua cac tham so:

```yaml
global_frame: map
robot_base_frame: base_link
odom_frame_id: odom
base_frame_id: base_link
```

Neu terminal Nav2 bao:

```text
Timed out waiting for transform from base_link to odom
Invalid frame ID "odom" passed to canTransform argument target_frame - frame does not exist
```

thi Nav2 khong nhin thay TF `odom -> base_link`. Co 3 nguyen nhan hay gap:

1. Chua chay bringup robot LIMO.
2. Shell Nav2 sach bi thieu `ROS_DOMAIN_ID`, nen khong thay topic/TF cua robot.
3. Robot dung frame khac, vi du `base_footprint` thay vi `base_link`.

Kiem tra trong terminal bringup LIMO:

```bash
echo $ROS_DOMAIN_ID
ros2 topic list | grep -E "odom|scan|cmd_vel"
ros2 run tf2_ros tf2_echo odom base_link
```

Neu `ROS_DOMAIN_ID` co gia tri, vi du `5`, thi trong terminal Nav2 shell sach cung phai set:

```bash
export ROS_DOMAIN_ID=5
```

Kiem tra trong terminal Nav2:

```bash
ros2 topic list | grep -E "odom|scan|cmd_vel"
ros2 run tf2_ros tf2_echo odom base_link
```

Neu `odom base_link` loi, thu:

```bash
ros2 run tf2_ros tf2_echo odom base_footprint
ros2 topic echo /odom_raw --once
```

Neu `/odom_raw` co `child_frame_id: base_footprint`, sua `base_link` thanh `base_footprint` trong:

```text
/home/agilex/Documents/LimoDATN20252/nav2/params/limo_nav2_params.yaml
```

Sua nhanh:

```bash
sed -i 's/base_link/base_footprint/g' \
  /home/agilex/Documents/LimoDATN20252/nav2/params/limo_nav2_params.yaml
```

Sau do tat Nav2 cu va chay lai.

## 10. Quy trinh test an toan

1. Ke robot len gia hoac de banh khong cham dat, gui goal nho de kiem tra `/cmd_vel`.
2. Chay tren san rong, toc do thap.
3. Luon co nguoi dung gan robot de dung khan cap.
4. Dat goal cach robot 0.5 den 1.0 m truoc.
5. Sau khi on dinh moi tang toc do.
