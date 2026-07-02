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

    echo "[nav2] Topics from robot:"
    ros2 topic list | grep -E "odom|scan|cmd_vel" || true
    echo

    echo "[nav2] Nav2 nodes:"
    ros2 node list | grep -E "amcl|map_server|controller_server|planner_server|bt_navigator|waypoint|smoother|behavior|velocity_smoother|lifecycle" || true
    echo

    echo "[nav2] Duplicate node names:"
    ros2 node list | sort | uniq -d || true
    echo

    echo "[nav2] Planner lifecycle services:"
    ros2 service list | grep -E "^/planner_server/(change_state|get_state)" || true
    echo

    echo "[nav2] Lifecycle states:"
    for node in /controller_server /planner_server /bt_navigator; do
      echo "[nav2] $node"
      if ! timeout 5 ros2 lifecycle get "$node"; then
        if [ "$node" = "/planner_server" ] && timeout 5 ros2 action info /compute_path_to_pose 2>/dev/null | grep -q "/planner_server"; then
          echo "lifecycle timeout, but planner action server is available"
        else
          echo "timeout or not found"
        fi
      fi
    done
    echo

    echo "[nav2] Navigation actions:"
    timeout 5 ros2 action info /compute_path_to_pose || true
    echo
    timeout 5 ros2 action info /follow_path || true
    echo
    timeout 5 ros2 action info /navigate_to_pose || true
    echo

    echo "[nav2] DWB package prefixes:"
    ros2 pkg prefix dwb_core || true
    ros2 pkg prefix dwb_plugins || true
    ros2 pkg prefix dwb_critics || true
  '
