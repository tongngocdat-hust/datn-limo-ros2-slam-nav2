#!/usr/bin/env bash
set -euo pipefail

DOMAIN="${ROS_DOMAIN_ID:-99}"

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

    echo "[nav2] ROS_DOMAIN_ID=$ROS_DOMAIN_ID"
    echo

    echo "[nav2] Topics:"
    ros2 topic list | grep -E "^/tf$|^/tf_static$|odom|scan|cmd_vel" || true
    echo

    echo "[nav2] /scan frame_id:"
    timeout 3 ros2 topic echo /scan --once --field header.frame_id || true
    echo

    echo "[nav2] /odom child_frame_id:"
    timeout 3 ros2 topic echo /odom --once --field child_frame_id || true
    echo

    check_tf() {
      parent="$1"
      child="$2"
      echo "[nav2] TF $parent -> $child"
      timeout 4 ros2 run tf2_ros tf2_echo "$parent" "$child" || true
      echo
    }

    check_tf map odom
    check_tf odom base_link
    check_tf map base_link
    check_tf base_link laser_link
    check_tf base_link imu_link
  '
