#!/usr/bin/env bash
set -euo pipefail

DOMAIN="${ROS_DOMAIN_ID:-99}"
CMD_TOPIC="${CMD_TOPIC:-/cmd_vel}"

echo "[nav2] This test will move the robot."
echo "[nav2] Put LIMO on open floor, keep emergency stop ready."
echo "[nav2] ROS_DOMAIN_ID=$DOMAIN"
echo "[nav2] CMD_TOPIC=$CMD_TOPIC"
read -r -p "[nav2] Press Enter to publish a slow forward command, or Ctrl+C to cancel..."

env -i \
  HOME="$HOME" \
  USER="${USER:-agilex}" \
  LOGNAME="${LOGNAME:-${USER:-agilex}}" \
  SHELL=/bin/bash \
  TERM="${TERM:-xterm-256color}" \
  ROS_DOMAIN_ID="$DOMAIN" \
  CMD_TOPIC="$CMD_TOPIC" \
  PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
  bash --noprofile --norc -c '
    set -eo pipefail
    set +u
    source /opt/ros/humble/setup.bash
    set -u

    echo "[nav2] Topic info:"
    ros2 topic info "$CMD_TOPIC" -v || true
    echo

    echo "[nav2] Forward 2 seconds..."
    timeout 2 ros2 topic pub -r 10 "$CMD_TOPIC" geometry_msgs/msg/Twist \
      "{linear: {x: 0.12, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" || true

    echo "[nav2] Stop..."
    timeout 1 ros2 topic pub -r 10 "$CMD_TOPIC" geometry_msgs/msg/Twist \
      "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" || true

    echo "[nav2] Rotate 2 seconds..."
    timeout 2 ros2 topic pub -r 10 "$CMD_TOPIC" geometry_msgs/msg/Twist \
      "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.4}}" || true

    echo "[nav2] Stop..."
    timeout 1 ros2 topic pub -r 10 "$CMD_TOPIC" geometry_msgs/msg/Twist \
      "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" || true

    echo "[nav2] Test done."
  '
