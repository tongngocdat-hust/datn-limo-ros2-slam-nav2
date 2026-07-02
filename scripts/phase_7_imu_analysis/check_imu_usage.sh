#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="/home/agilex/agilex_ws"

usage() {
    cat <<EOF
Usage: $0 [--workspace PATH]
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --workspace) WORKSPACE="${2:-}"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
    esac
done

if [[ ! -d "${WORKSPACE}" ]]; then
    echo "Workspace does not exist: ${WORKSPACE}" >&2
    exit 1
fi

echo "Searching IMU-related settings in: ${WORKSPACE}"
find "${WORKSPACE}" -type f \( -name "*.lua" -o -name "*.yaml" -o -name "*.yml" \) -print0 \
    | xargs -0 grep -nEi "imu|use_imu|use_imu_data|imu_topic" || true

cat <<'EOF'

Cartographer:
  Edit the Lua configuration and set:
    TRAJECTORY_BUILDER_2D.use_imu_data = true
  or:
    TRAJECTORY_BUILDER_2D.use_imu_data = false

SLAM Toolbox:
  If these parameters exist in the YAML file, set:
    use_imu: true
  or:
    use_imu: false
    imu_topic: /imu
EOF
