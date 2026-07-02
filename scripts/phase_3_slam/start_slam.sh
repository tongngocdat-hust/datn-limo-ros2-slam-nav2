#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CONFIG_DIR="${PROJECT_ROOT}/config"

usage() {
    cat <<EOF
Usage: $0 --system gmapping|cartographer|slam_toolbox [--imu on|off]

Run phase_3_slam/preflight_slam.sh before this command.
All three configurations use map, odom, base_link, /scan and 0.05 m map resolution.
EOF
}

SYSTEM=""
IMU="off"
while [[ $# -gt 0 ]]; do
    case "$1" in
        --system) SYSTEM="${2:-}"; shift 2 ;;
        --imu) IMU="${2:-}"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
    esac
done

case "${SYSTEM}" in gmapping|cartographer|slam_toolbox) ;; *) usage; exit 2 ;; esac
case "${IMU}" in on|off) ;; *) usage; exit 2 ;; esac

if ! command -v ros2 >/dev/null 2>&1; then
    echo "ERROR: ros2 command not found. Source ROS 2 and the LIMO workspace first." >&2
    exit 1
fi

case "${SYSTEM}" in
    slam_toolbox)
        exec ros2 launch slam_toolbox online_sync_launch.py \
            use_sim_time:=false \
            slam_params_file:="${CONFIG_DIR}/slam_toolbox_limo.yaml"
        ;;
    gmapping)
        GMAPPING_SETUP="${GMAPPING_SETUP:-${HOME}/gmapping_ws/install/setup.bash}"
        if [[ ! -f "${GMAPPING_SETUP}" ]]; then
            echo "ERROR: Gmapping workspace setup was not found: ${GMAPPING_SETUP}" >&2
            echo "Set GMAPPING_SETUP to the correct install/setup.bash path." >&2
            exit 1
        fi
        # Gmapping is installed in a separate workspace on the LIMO.
        set +u
        source "${GMAPPING_SETUP}"
        set -u
        if ! ros2 pkg executables slam_gmapping 2>/dev/null |
            grep -q "slam_gmapping_node"; then
            echo "ERROR: slam_gmapping/slam_gmapping_node is unavailable after sourcing:" >&2
            echo "  ${GMAPPING_SETUP}" >&2
            exit 1
        fi
        exec ros2 run slam_gmapping slam_gmapping_node --ros-args \
            --params-file "${CONFIG_DIR}/gmapping_limo.yaml" \
            -r scan:=/scan
        ;;
    cartographer)
        if ! ros2 pkg prefix limo_bringup >/dev/null 2>&1; then
            echo "ERROR: package limo_bringup is unavailable." >&2
            echo "Source /home/agilex/agilex_ws/install/setup.bash first." >&2
            exit 1
        fi
        echo "Using the LIMO Cartographer launch (includes the vehicle-tuned config and RViz)."
        echo "Note: --imu is only a data label here; this launch controls actual IMU usage."
        exec ros2 launch limo_bringup limo_cartographer.launch.py
        ;;
esac
