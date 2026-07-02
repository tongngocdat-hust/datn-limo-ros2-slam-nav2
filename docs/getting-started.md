# Bắt đầu

## Yêu cầu môi trường

| Nhóm | Yêu cầu |
| --- | --- |
| Robot | AgileX LIMO chạy ROS 2 Humble |
| Workspace | `/home/agilex/agilex_ws` đã build và source được |
| Python | Python 3, `numpy`, `pandas`, `Pillow`, `scikit-image`, `matplotlib`, `psutil` |
| Node docs | Node.js 18+ để chạy VitePress |

## Chạy website docs

Tại root repo:

```bash
npm install
npm run docs:dev
```

Build bản static:

```bash
npm run docs:build
npm run docs:preview
```

## Cài Python dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Các script đọc rosbag cần chạy trong terminal đã source ROS 2:

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
```

## Copy code sang LIMO

Ví dụ đồng bộ thư mục `scripts`:

```bash
rsync -av --progress \
  /home/datbolac/limo/scripts/ \
  agilex@<LIMO_IP>:/home/agilex/Documents/LimoDATN20252/Resource/scripts/
```

Trên LIMO:

```bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
chmod +x phase_3_slam/*.sh
chmod +x phase_4_data_collection/*.sh
chmod +x phase_6_evaluation/*.py
chmod +x phase_6_evaluation/*.sh
```

## Quy ước terminal

Mỗi terminal điều khiển robot nên bắt đầu bằng:

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
export ROS_DOMAIN_ID=99
```

Sau đó chuyển vào thư mục script:

```bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
```

::: warning Không chạy chồng thuật toán
Khi đo SLAM hoặc Nav2, chỉ chạy một thuật toán/launcher chính tại một thời điểm.
Chạy song song nhiều node phát `/map`, `/tf` hoặc `/cmd_vel` sẽ làm metric sai.
:::
