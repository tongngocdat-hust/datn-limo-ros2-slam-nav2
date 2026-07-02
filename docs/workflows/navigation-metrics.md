# Đo navigation tự động

Thư mục `tudong/` dùng để gửi goal Nav2 và ghi metric cho từng lần thử.

## Metric được ghi

| Metric | Ý nghĩa |
| --- | --- |
| `Success Rate (%)` | Số goal thành công / tổng số lần thử. |
| `Navigation Time (s)` | Thời gian Nav2 xử lý goal. |
| `Path Length (m)` | Tổng quãng đường từ TF `odom -> base_link`. |
| `Goal Error (m)` | Khoảng cách vị trí cuối tới goal. |
| `Recovery Count` | Số recovery lấy từ feedback `NavigateToPose`. |
| `Collision Count` | Số cạnh lên của topic `std_msgs/Bool`. |

## Chạy thử không cần ROS 2

Trên máy cá nhân:

```bash
cd tudong
python3 make_demo_data.py
python3 summarize.py demo/trials.csv --output-dir demo/results
```

Kết quả:

```text
demo/results/navigation_summary.csv
demo/results/navigation_summary.md
```

## Chạy trên LIMO

Sau khi bringup, SLAM/localization và Nav2 đã chạy:

```bash
cd /home/agilex/Documents/LimoDATN20252/tudong
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
export ROS_DOMAIN_ID=99

./run_trial.py \
  --algorithm gmapping \
  --run 1 \
  --x 2.0 \
  --y 1.0 \
  --yaw 0.0
```

Mỗi lần thử nối thêm một dòng vào:

```text
results/trials.csv
```

Tổng hợp:

```bash
./summarize.py results/trials.csv --output-dir results
```

## Collision topic

Mặc định script nghe:

```text
/collision_detected
```

Nếu robot có topic Bool khác:

```bash
./run_trial.py ... --collision-topic /ten_topic_bool
```

Nếu cần đánh dấu va chạm thủ công:

```bash
./publish_collision.py
```

## Tài liệu chi tiết

Xem đầy đủ tại `tudong/README.md`.
