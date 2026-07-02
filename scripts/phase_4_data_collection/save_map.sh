#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
MAPS_DIR="${PROJECT_ROOT}/data/maps"

usage() {
    cat <<EOF
Usage: $0 --system gmapping|cartographer|slam_toolbox --scenario A|B|C --run 1|2|3|4|5 --imu on|off
EOF
}

SYSTEM=""
SCENARIO=""
RUN_ID=""
IMU=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --system) SYSTEM="${2:-}"; shift 2 ;;
        --scenario) SCENARIO="${2:-}"; shift 2 ;;
        --run) RUN_ID="${2:-}"; shift 2 ;;
        --imu) IMU="${2:-}"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
    esac
done

case "${SYSTEM}" in gmapping|cartographer|slam_toolbox) ;; *) echo "Invalid --system: ${SYSTEM}" >&2; usage; exit 2 ;; esac
case "${SCENARIO}" in A|B|C) ;; *) echo "Invalid --scenario: ${SCENARIO}" >&2; usage; exit 2 ;; esac
case "${RUN_ID}" in 1|2|3|4|5) ;; *) echo "Invalid --run: ${RUN_ID}" >&2; usage; exit 2 ;; esac
case "${IMU}" in on|off) ;; *) echo "Invalid --imu: ${IMU}" >&2; usage; exit 2 ;; esac

if ! command -v ros2 >/dev/null 2>&1; then
    echo "ros2 command not found. Source your ROS 2 environment first." >&2
    exit 1
fi

mkdir -p "${MAPS_DIR}"
MAP_NAME="${SYSTEM}_${SCENARIO}_run${RUN_ID}_imu_${IMU}"
OUTPUT_BASE="${MAPS_DIR}/${MAP_NAME}"

if [[ -e "${OUTPUT_BASE}.pgm" || -e "${OUTPUT_BASE}.yaml" ]]; then
    echo "Map output already exists: ${OUTPUT_BASE}.pgm or ${OUTPUT_BASE}.yaml" >&2
    echo "Choose another --run value or move the old map manually." >&2
    exit 1
fi

ros2 run nav2_map_server map_saver_cli -f "${OUTPUT_BASE}"
