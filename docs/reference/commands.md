# Lệnh nhanh

## Source môi trường

```bash
source /opt/ros/humble/setup.bash
source /home/agilex/agilex_ws/install/setup.bash
export ROS_DOMAIN_ID=99
```

## Kiểm tra topic và TF

```bash
ros2 topic list
timeout 3 ros2 topic echo /scan --once
timeout 3 ros2 topic echo /odom --once
ros2 run tf2_ros tf2_echo odom base_link
```

## SLAM preflight

```bash
cd /home/agilex/Documents/LimoDATN20252/Resource/scripts
phase_3_slam/preflight_slam.sh
```

## Start SLAM

```bash
phase_3_slam/start_slam.sh --system cartographer --imu off
phase_3_slam/start_slam.sh --system gmapping --imu off
phase_3_slam/start_slam.sh --system slam_toolbox --imu off
```

## Record experiment

```bash
phase_4_data_collection/run_record_experiment.sh \
  --system slam_toolbox \
  --scenario A \
  --run 1 \
  --imu off
```

## Save map

```bash
phase_4_data_collection/save_map.sh \
  --system slam_toolbox \
  --scenario A \
  --run 1 \
  --imu off
```

## Extract trajectory

```bash
phase_6_evaluation/extract_trajectory_from_bag.py \
  --bag data/bags/slam_toolbox_A_run1_imu_off
```

## Compute RMSE

```bash
phase_6_evaluation/compute_rmse.py \
  --reference_csv data/results/trajectories/reference_A_run1.csv \
  --estimated_csv data/results/trajectories/slam_toolbox_A_run1_imu_off_slam.csv
```

## Merge results

```bash
phase_6_evaluation/evaluate_maps.py
phase_6_evaluation/merge_results.py
phase_7_imu_analysis/compare_imu_results.py
```

## Navigation2

```bash
cd /home/agilex/Documents/LimoDATN20252/nav2
./reset_nav2.sh
./run_nav2_clean.sh
./check_tf.sh
./check_nav2.sh
```

## Navigation metric

```bash
cd /home/agilex/Documents/LimoDATN20252/tudong
./run_trial.py --algorithm gmapping --run 1 --x 2.0 --y 1.0 --yaw 0.0
./summarize.py results/trials.csv --output-dir results
```
