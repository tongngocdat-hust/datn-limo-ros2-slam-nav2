#!/usr/bin/env bash
set -euo pipefail

DOMAIN="${ROS_DOMAIN_ID:-99}"

set +u
source /opt/ros/humble/setup.bash
set -u
export ROS_DOMAIN_ID="$DOMAIN"

echo "[nav2] ROS_DOMAIN_ID=$ROS_DOMAIN_ID"
exec rviz2 -d "$(ros2 pkg prefix nav2_bringup)/share/nav2_bringup/rviz/nav2_default_view.rviz"
