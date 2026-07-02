#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

usage() {
    cat <<EOF
Usage: $0 --scenario A|B|C --imu on|off [--reference-system SYSTEM]

Defaults:
  reference system:     slam_toolbox
  map reference:        data/maps/<reference-system>_<scenario>_run1_imu_<imu>.pgm
  trajectory reference: data/results/trajectories/reference_<scenario>.csv

The script reports raw map metrics, registers maps with a bounded SE(2)
transform, reports aligned metrics, and computes trajectory RMSE from
*_slam.csv using arc-length association plus SE(2) alignment.
EOF
}

SCENARIO=""
IMU=""
REFERENCE_SYSTEM="slam_toolbox"
while [[ $# -gt 0 ]]; do
    case "$1" in
        --scenario) SCENARIO="${2:-}"; shift 2 ;;
        --imu) IMU="${2:-}"; shift 2 ;;
        --reference-system) REFERENCE_SYSTEM="${2:-}"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
    esac
done

case "${SCENARIO}" in A|B|C) ;; *) usage; exit 2 ;; esac
case "${IMU}" in on|off) ;; *) usage; exit 2 ;; esac
case "${REFERENCE_SYSTEM}" in
    gmapping|cartographer|slam_toolbox) ;;
    *) echo "Invalid --reference-system: ${REFERENCE_SYSTEM}" >&2; usage; exit 2 ;;
esac

REFERENCE_MAP="${PROJECT_ROOT}/data/maps/${REFERENCE_SYSTEM}_${SCENARIO}_run1_imu_${IMU}.pgm"
REFERENCE_TRAJECTORY="${PROJECT_ROOT}/data/results/trajectories/reference_${SCENARIO}.csv"

if [[ ! -f "${REFERENCE_MAP}" || ! -f "${REFERENCE_MAP%.pgm}.yaml" ]]; then
    echo "ERROR: map reference or its YAML is missing: ${REFERENCE_MAP}" >&2
    exit 1
fi
if [[ ! -f "${REFERENCE_TRAJECTORY}" ]]; then
    echo "ERROR: trajectory reference is missing: ${REFERENCE_TRAJECTORY}" >&2
    echo "Create it once from Cartographer run 1 *_slam.csv." >&2
    exit 1
fi

echo "Map reference system: ${REFERENCE_SYSTEM}"
echo "Map reference: ${REFERENCE_MAP}"
echo "Trajectory reference: ${REFERENCE_TRAJECTORY}"

"${SCRIPT_DIR}/evaluate_maps.py" \
    --ground_truth "${REFERENCE_MAP}" \
    --scenario "${SCENARIO}" \
    --imu "${IMU}"

matched=0
for trajectory in "${PROJECT_ROOT}"/data/results/trajectories/*_"${SCENARIO}"_run*_imu_"${IMU}"_slam.csv; do
    [[ -e "${trajectory}" ]] || continue
    matched=1
    "${SCRIPT_DIR}/compute_rmse.py" \
        --association arc_length \
        --align se2 \
        --reference_csv "${REFERENCE_TRAJECTORY}" \
        --estimated_csv "${trajectory}"
done

if [[ "${matched}" -eq 0 ]]; then
    echo "WARNING: no matching *_slam.csv trajectories were found." >&2
fi

"${SCRIPT_DIR}/merge_results.py"
