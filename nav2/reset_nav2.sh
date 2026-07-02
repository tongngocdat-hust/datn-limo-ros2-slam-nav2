#!/usr/bin/env bash
set -euo pipefail

DOMAIN="${ROS_DOMAIN_ID:-99}"

echo "[nav2] ROS_DOMAIN_ID=$DOMAIN"
echo "[nav2] Stopping old Nav2/RViz processes..."

pkill -f "bringup_launch.py" || true
pkill -f "localization_launch.py" || true
pkill -f "navigation_launch.py" || true
pkill -f "nav2_container" || true
pkill -f "lifecycle_manager_navigation" || true
pkill -f "nav2_lifecycle_manager" || true
pkill -f "planner_server" || true
pkill -f "controller_server" || true
pkill -f "bt_navigator" || true
pkill -f "waypoint_follower" || true
pkill -f "behavior_server" || true
pkill -f "smoother_server" || true
pkill -f "velocity_smoother" || true
pkill -f "map_server" || true
pkill -f "amcl" || true

sleep 3

env -i \
  HOME="$HOME" \
  USER="${USER:-agilex}" \
  LOGNAME="${LOGNAME:-${USER:-agilex}}" \
  SHELL=/bin/bash \
  TERM="${TERM:-xterm-256color}" \
  ROS_DOMAIN_ID="$DOMAIN" \
  PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
  bash --noprofile --norc -c '
    set -eo pipefail
    set +u
    source /opt/ros/humble/setup.bash
    set -u

    ros2 daemon stop >/dev/null 2>&1 || true
    ros2 daemon start >/dev/null 2>&1 || true

    echo "[nav2] Remaining Nav2 nodes:"
    ros2 node list | grep -E "nav2_container|amcl|map_server|controller_server|planner_server|bt_navigator|waypoint|smoother|behavior|velocity_smoother|lifecycle" || true
  '

echo "[nav2] Reset complete."
