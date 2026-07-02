#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAV2_DIR="${NAV2_DIR:-$SCRIPT_DIR}"
DOMAIN="${ROS_DOMAIN_ID:-99}"
MAP_FILE="${MAP_FILE:-$NAV2_DIR/maps/maps.yaml}"
PARAMS_FILE="${PARAMS_FILE:-$NAV2_DIR/params/limo_nav2_params.yaml}"

if [[ ! -f "$MAP_FILE" ]]; then
  echo "[nav2] ERROR: map file not found: $MAP_FILE" >&2
  exit 1
fi

if [[ ! -f "$PARAMS_FILE" ]]; then
  echo "[nav2] ERROR: params file not found: $PARAMS_FILE" >&2
  exit 1
fi

echo "[nav2] Starting clean Nav2 environment"
echo "[nav2] ROS_DOMAIN_ID=$DOMAIN"
echo "[nav2] MAP_FILE=$MAP_FILE"
echo "[nav2] PARAMS_FILE=$PARAMS_FILE"
echo
echo "[nav2] Keep this terminal open. Stop with Ctrl+C."

env -i \
  HOME="$HOME" \
  USER="${USER:-agilex}" \
  LOGNAME="${LOGNAME:-${USER:-agilex}}" \
  SHELL=/bin/bash \
  TERM="${TERM:-xterm-256color}" \
  DISPLAY="${DISPLAY:-}" \
  XAUTHORITY="${XAUTHORITY:-}" \
  ROS_DOMAIN_ID="$DOMAIN" \
  NAV2_DIR="$NAV2_DIR" \
  MAP_FILE="$MAP_FILE" \
  PARAMS_FILE="$PARAMS_FILE" \
  PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
  bash --noprofile --norc -c '
    set -euo pipefail
    set +u
    source /opt/ros/humble/setup.bash
    set -u

    echo "[nav2] Checking DWB packages. These should usually be /opt/ros/humble:"
    ros2 pkg prefix dwb_core
    ros2 pkg prefix dwb_plugins
    ros2 pkg prefix dwb_critics
    echo

    echo "[nav2] Checking robot topics:"
    ros2 topic list | grep -E "odom|scan|cmd_vel" || true
    echo

    echo "[nav2] Launching Nav2..."
    exec ros2 launch nav2_bringup bringup_launch.py \
      map:="$MAP_FILE" \
      params_file:="$PARAMS_FILE" \
      use_sim_time:=false \
      autostart:=true \
      use_composition:=False \
      log_level:=info
  '
