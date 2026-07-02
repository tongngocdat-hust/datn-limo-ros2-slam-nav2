#!/usr/bin/env bash
set -euo pipefail

DOMAIN="${ROS_DOMAIN_ID:-99}"
CMD_TOPIC="${CMD_TOPIC:-/cmd_vel}"

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

    echo "[nav2] ROS_DOMAIN_ID=$ROS_DOMAIN_ID"
    echo "[nav2] Watching $CMD_TOPIC. Send a Nav2 Goal in RViz now."
    echo "[nav2] linear.x should be positive when the robot is trying to drive forward."
    echo
    ros2 topic echo "$CMD_TOPIC"
  '
