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
    echo "[nav2] Asking lifecycle manager to start navigation nodes..."
    timeout 10 ros2 service call /lifecycle_manager_navigation/manage_nodes \
      nav2_msgs/srv/ManageLifecycleNodes "{command: 0}" || true

    echo
    echo "[nav2] Trying direct lifecycle activation for controller, planner and BT navigator..."

    get_state() {
      timeout 4 ros2 lifecycle get "$1" 2>/dev/null || true
    }

    action_has_server() {
      action="$1"
      server="$2"
      timeout 5 ros2 action info "$action" 2>/dev/null | grep -q "$server"
    }

    wait_for_lifecycle() {
      node="$1"
      seconds="${2:-15}"
      i=0
      while [ "$i" -lt "$seconds" ]; do
        state="$(get_state "$node")"
        if [ -n "$state" ]; then
          echo "$state"
          return 0
        fi
        i=$((i + 1))
        sleep 1
      done
      return 1
    }

    set_transition() {
      node="$1"
      transition="$2"
      echo "[nav2] $node -> $transition"
      timeout 8 ros2 lifecycle set "$node" "$transition" || true
      sleep 1
    }

    activate_node() {
      node="$1"
      echo
      echo "[nav2] Activating $node"

      if ! state="$(wait_for_lifecycle "$node" 15)"; then
        if [ "$node" = "/planner_server" ] && action_has_server /compute_path_to_pose /planner_server; then
          echo "[nav2] NOTE: $node lifecycle service timed out, but /compute_path_to_pose has /planner_server as action server."
          echo "[nav2] Planner is present in the ROS graph. If Nav2 Goal still works, this is a lifecycle CLI/graph issue, not a planner plugin failure."
          return 0
        fi
        echo "[nav2] ERROR: $node lifecycle service not found. Check the Nav2 launch terminal for crash logs."
        return 1
      fi

      echo "[nav2] $node state: $state"
      case "$state" in
        *"active [3]"*)
          echo "[nav2] $node already active"
          return 0
          ;;
        *"unconfigured [1]"*)
          set_transition "$node" configure
          ;;
      esac

      state="$(get_state "$node")"
      echo "[nav2] $node state: ${state:-unknown}"
      case "$state" in
        *"active [3]"*)
          echo "[nav2] $node already active"
          return 0
          ;;
        *"inactive [2]"*)
          set_transition "$node" activate
          ;;
        *)
          echo "[nav2] WARNING: $node is not inactive/active, still trying activate"
          set_transition "$node" activate
          ;;
      esac

      state="$(get_state "$node")"
      echo "[nav2] $node final state: ${state:-timeout or not found}"
    }

    activate_node /controller_server || true
    activate_node /planner_server || true
    activate_node /bt_navigator || true

    echo
    echo "[nav2] Current states:"
    for node in /controller_server /planner_server /bt_navigator; do
      echo "[nav2] $node"
      if ! timeout 5 ros2 lifecycle get "$node"; then
        if [ "$node" = "/planner_server" ] && action_has_server /compute_path_to_pose /planner_server; then
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
  '
