#!/usr/bin/env bash
set -euo pipefail

BASE_FRAME="${BASE_FRAME:-base_link}"
ODOM_FRAME="${ODOM_FRAME:-odom}"
SCAN_TOPIC="${SCAN_TOPIC:-/scan}"
IMU_TOPIC="${IMU_TOPIC:-/imu}"

if ! command -v ros2 >/dev/null 2>&1; then
    echo "ERROR: ros2 command not found. Source ROS 2 and the LIMO workspace first." >&2
    exit 1
fi

topics="$(ros2 topic list)"
for topic in "${SCAN_TOPIC}" /odom /tf /tf_static; do
    if ! printf '%s\n' "${topics}" | grep -Fxq "${topic}"; then
        echo "ERROR: required topic is missing: ${topic}" >&2
        exit 1
    fi
done

if printf '%s\n' "${topics}" | grep -Fxq "${IMU_TOPIC}"; then
    echo "OK: IMU topic exists: ${IMU_TOPIC}"
else
    echo "WARNING: IMU topic is missing: ${IMU_TOPIC}"
fi

laser_frame="$(
    timeout 5 ros2 topic echo "${SCAN_TOPIC}" --once --field header.frame_id 2>/dev/null |
    head -n 1 |
    tr -d "'\"[:space:]"
)" || true
if [[ -z "${laser_frame}" ]]; then
    echo "ERROR: could not read frame_id from ${SCAN_TOPIC}" >&2
    exit 1
fi

echo "Laser frame: ${laser_frame}"
echo "Checking ${BASE_FRAME} -> ${laser_frame} ..."
laser_tf="$(
    timeout 5 ros2 run tf2_ros tf2_echo "${BASE_FRAME}" "${laser_frame}" 2>&1 || true
)"
if ! printf '%s\n' "${laser_tf}" | grep -q "Translation:"; then
    echo "ERROR: TF ${BASE_FRAME} -> ${laser_frame} is unavailable." >&2
    printf '%s\n' "${laser_tf}" | tail -n 5 >&2
    exit 1
fi

echo "Checking ${ODOM_FRAME} -> ${BASE_FRAME} ..."
odom_tf="$(
    timeout 5 ros2 run tf2_ros tf2_echo "${ODOM_FRAME}" "${BASE_FRAME}" 2>&1 || true
)"
if ! printf '%s\n' "${odom_tf}" | grep -q "Translation:"; then
    echo "ERROR: TF ${ODOM_FRAME} -> ${BASE_FRAME} is unavailable." >&2
    printf '%s\n' "${odom_tf}" | tail -n 5 >&2
    exit 1
fi

scan_hz="$(timeout 8 ros2 topic hz "${SCAN_TOPIC}" 2>/dev/null | tail -n 1 || true)"
odom_hz="$(timeout 8 ros2 topic hz /odom 2>/dev/null | tail -n 1 || true)"
echo "Scan rate: ${scan_hz:-not measured}"
echo "Odom rate: ${odom_hz:-not measured}"
echo "PASS: required topics and TF links are available."
echo "Next: in RViz use Fixed Frame=${ODOM_FRAME}, display ${SCAN_TOPIC}, and rotate slowly."
echo "The wall points should remain nearly stationary instead of opening into a fan."
