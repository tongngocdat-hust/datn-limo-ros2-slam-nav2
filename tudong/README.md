# Tự động thu số liệu Navigation2

Thư mục này chạy độc lập, có thể copy nguyên thư mục từ máy cá nhân sang
LIMO ROS 2 Humble. Không cần `colcon build`.

Các chỉ số được tạo:

- `Success Rate (%)`: số goal thành công / tổng số lần thử.
- `Navigation Time (s)`: thời gian Nav2 xử lý goal.
- `Path Length (m)`: tổng quãng đường từ TF `odom -> base_link`.
- `Goal Error (m)`: khoảng cách từ vị trí cuối tới tọa độ goal.
- `Recovery Count`: lấy từ feedback của action `NavigateToPose`.
- `Collision Count`: số cạnh lên của topic `std_msgs/Bool`.

## 1. Kiểm tra trên máy cá nhân (không cần ROS 2)

```bash
cd /home/datbolac/limo/tudong
python3 make_demo_data.py
python3 summarize.py demo/trials.csv --output-dir demo/results
```

Kết quả nằm trong:

```text
demo/results/navigation_summary.csv
demo/results/navigation_summary.md
```

Lưu ý: dữ liệu mẫu dùng 9/10 lần thành công cho Cartographer nên Success
Rate đúng theo công thức là `90%`. Hai hình tham khảo đang không thống nhất:
một bảng ghi `95%`, bảng còn lại ghi 9/10 và `90%`.

## 2. Copy sang LIMO

Từ máy cá nhân:

```bash
scp -r /home/datbolac/limo/tudong \
  agilex@<LIMO_IP>:/home/agilex/Documents/LimoDATN20252/
```

Trên LIMO:

```bash
cd /home/agilex/Documents/LimoDATN20252/tudong
chmod +x *.py
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
export ROS_DOMAIN_ID=99
```

Hãy dùng đúng `ROS_DOMAIN_ID` đang chạy Nav2.

## 3. Chạy một lần thử

Khởi động bringup, thuật toán SLAM, Nav2 và localization trước. Sau đó chạy:

```bash
./run_trial.py \
  --algorithm gmapping \
  --run 1 \
  --x 2.0 \
  --y 1.0 \
  --yaw 0.0
```

Mỗi lần chạy sẽ tự nối thêm một dòng vào:

```text
results/trials.csv
```

Chạy đủ 10 lần cho từng thuật toán, đổi `--run` từ 1 đến 10:

```bash
./run_trial.py --algorithm gmapping      --run 2 --x 2.0 --y 1.0
./run_trial.py --algorithm cartographer  --run 1 --x 2.0 --y 1.0
./run_trial.py --algorithm slam_toolbox  --run 1 --x 2.0 --y 1.0
```

Nên dùng cùng vị trí xuất phát, goal, map và cấu hình Nav2 để so sánh công
bằng. Script tính trung bình thời gian, quãng đường và sai số trên các lần
**thành công**; recovery và collision là tổng của tất cả lần thử.

Nếu frame thân xe là `base_footprint`:

```bash
./run_trial.py \
  --algorithm gmapping --run 1 --x 2.0 --y 1.0 \
  --base-frame base_footprint
```

Mặc định goal/sai số dùng frame `map`, còn quãng đường dùng `odom` để tránh
bị cộng thêm các bước hiệu chỉnh của SLAM. Có thể đổi bằng `--global-frame`
và `--path-frame`.

## 4. Ghi nhận va chạm

Mặc định bộ đo nghe topic:

```text
/collision_detected  (std_msgs/msg/Bool)
```

Nếu LIMO đã có bumper/collision node xuất Bool, truyền topic thật:

```bash
./run_trial.py ... --collision-topic /ten_topic_bool
```

Nếu chưa có cảm biến/topic phù hợp, khi quan sát thấy va chạm hãy mở terminal
khác và chạy một lần:

```bash
./publish_collision.py
```

Muốn bỏ đo va chạm:

```bash
./run_trial.py ... --collision-topic ""
```

## 5. Tạo bảng tổng hợp

```bash
./summarize.py
```

Kết quả:

```text
results/navigation_summary.csv
results/navigation_summary.md
```

Có thể ghép nhiều file CSV:

```bash
./summarize.py ngay_1.csv ngay_2.csv --output-dir ket_qua
```

## 6. Kiểm tra trước khi đo

```bash
ros2 action list | grep navigate_to_pose
ros2 action info /navigate_to_pose
ros2 run tf2_ros tf2_echo map base_link
ros2 run tf2_ros tf2_echo odom base_link
```

Nếu TF cuối không lấy được, `goal_error_m` sẽ để trống. Nếu TF nhảy bất
thường do reset localization, bước nhảy lớn hơn 1 m bị loại khỏi Path Length;
có thể đổi ngưỡng bằng `--max-tf-step`.
