#!/usr/bin/env python3
"""Extract odometry and SLAM TF trajectories from rosbag2 SQLite bags."""

from __future__ import annotations

import argparse
import bisect
import csv
import math
from pathlib import Path
from typing import Iterable


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract /odom and map->base trajectories from rosbag2 bags.")
    parser.add_argument("--bag", type=Path, help="Specific bag directory. Default: all bags in data/bags.")
    return parser.parse_args()


def import_rosbag_tools():
    try:
        import rosbag2_py
        from rclpy.serialization import deserialize_message
        from rosidl_runtime_py.utilities import get_message
    except ImportError as exc:
        raise SystemExit(
            "Missing ROS 2 Python packages. Run this on a ROS 2 Humble environment "
            "after sourcing setup.bash."
        ) from exc
    return rosbag2_py, deserialize_message, get_message


def bag_directories(bags_root: Path, selected: Path | None) -> list[Path]:
    if selected:
        return [selected.resolve()]
    return sorted(path for path in bags_root.iterdir() if path.is_dir())


def timestamp_from_msg(default_ns: int, msg: object) -> float:
    header = getattr(msg, "header", None)
    stamp = getattr(header, "stamp", None)
    if stamp and (stamp.sec or stamp.nanosec):
        return float(stamp.sec) + float(stamp.nanosec) / 1_000_000_000.0
    return float(default_ns) / 1_000_000_000.0


def yaw_from_quaternion(q: object) -> float:
    siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
    cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    return math.atan2(siny_cosp, cosy_cosp)


def write_csv(path: Path, rows: Iterable[dict[str, float]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["timestamp", "x", "y", "yaw"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            count += 1
    return count


def normalize_frame(frame: str) -> str:
    return frame.lstrip("/")


def interpolate_odom(rows: list[dict[str, float]], timestamp: float) -> dict[str, float] | None:
    if not rows:
        return None
    timestamps = [row["timestamp"] for row in rows]
    index = bisect.bisect_left(timestamps, timestamp)
    if index == 0:
        return rows[0] if abs(rows[0]["timestamp"] - timestamp) <= 0.25 else None
    if index == len(rows):
        return rows[-1] if abs(rows[-1]["timestamp"] - timestamp) <= 0.25 else None
    before, after = rows[index - 1], rows[index]
    span = after["timestamp"] - before["timestamp"]
    if span <= 0 or min(timestamp - before["timestamp"], after["timestamp"] - timestamp) > 0.25:
        return None
    ratio = (timestamp - before["timestamp"]) / span
    yaw_delta = math.atan2(
        math.sin(after["yaw"] - before["yaw"]),
        math.cos(after["yaw"] - before["yaw"]),
    )
    return {
        "timestamp": timestamp,
        "x": before["x"] + ratio * (after["x"] - before["x"]),
        "y": before["y"] + ratio * (after["y"] - before["y"]),
        "yaw": before["yaw"] + ratio * yaw_delta,
    }


def compose_planar(parent: dict[str, float], child: dict[str, float]) -> dict[str, float]:
    cosine, sine = math.cos(parent["yaw"]), math.sin(parent["yaw"])
    return {
        "timestamp": parent["timestamp"],
        "x": parent["x"] + cosine * child["x"] - sine * child["y"],
        "y": parent["y"] + sine * child["x"] + cosine * child["y"],
        "yaw": math.atan2(
            math.sin(parent["yaw"] + child["yaw"]),
            math.cos(parent["yaw"] + child["yaw"]),
        ),
    }


def extract_bag(bag_path: Path, output_dir: Path) -> None:
    rosbag2_py, deserialize_message, get_message = import_rosbag_tools()
    if not bag_path.exists():
        raise SystemExit(f"Bag does not exist: {bag_path}")

    storage_options = rosbag2_py.StorageOptions(uri=str(bag_path), storage_id="sqlite3")
    converter_options = rosbag2_py.ConverterOptions("", "")
    reader = rosbag2_py.SequentialReader()
    reader.open(storage_options, converter_options)

    topic_types = {topic.name: topic.type for topic in reader.get_all_topics_and_types()}
    message_types = {topic: get_message(type_name) for topic, type_name in topic_types.items()}

    odom_rows: list[dict[str, float]] = []
    direct_slam_rows: list[dict[str, float]] = []
    map_to_odom_rows: list[dict[str, float]] = []
    target_children = {"base_link", "base_footprint"}

    while reader.has_next():
        topic, data, timestamp_ns = reader.read_next()
        if topic not in message_types:
            continue
        msg = deserialize_message(data, message_types[topic])

        if topic == "/odom":
            position = msg.pose.pose.position
            orientation = msg.pose.pose.orientation
            odom_rows.append(
                {
                    "timestamp": timestamp_from_msg(timestamp_ns, msg),
                    "x": float(position.x),
                    "y": float(position.y),
                    "yaw": yaw_from_quaternion(orientation),
                }
            )
        elif topic in {"/tf", "/tf_static"}:
            for transform in msg.transforms:
                parent_frame = normalize_frame(transform.header.frame_id)
                child_frame = normalize_frame(transform.child_frame_id)
                if parent_frame != "map":
                    continue
                translation = transform.transform.translation
                rotation = transform.transform.rotation
                row = {
                    "timestamp": timestamp_from_msg(timestamp_ns, transform),
                    "x": float(translation.x),
                    "y": float(translation.y),
                    "yaw": yaw_from_quaternion(rotation),
                }
                if child_frame in target_children:
                    direct_slam_rows.append(row)
                elif child_frame == "odom":
                    map_to_odom_rows.append(row)

    odom_rows.sort(key=lambda row: row["timestamp"])
    direct_slam_rows.sort(key=lambda row: row["timestamp"])
    map_to_odom_rows.sort(key=lambda row: row["timestamp"])
    composed_rows = []
    for map_to_odom in map_to_odom_rows:
        odom_to_base = interpolate_odom(odom_rows, map_to_odom["timestamp"])
        if odom_to_base is not None:
            composed_rows.append(compose_planar(map_to_odom, odom_to_base))
    slam_rows = composed_rows if composed_rows else direct_slam_rows

    odom_count = write_csv(output_dir / f"{bag_path.name}_odom.csv", odom_rows)
    print(f"Saved /odom trajectory: {output_dir / f'{bag_path.name}_odom.csv'} ({odom_count} rows)")
    if slam_rows:
        slam_count = write_csv(output_dir / f"{bag_path.name}_slam.csv", slam_rows)
        print(f"Saved SLAM trajectory: {output_dir / f'{bag_path.name}_slam.csv'} ({slam_count} rows)")
    else:
        print(
            "WARNING: Could not build a SLAM trajectory. The bag needs either map->base_link "
            "or both map->odom TF and /odom."
        )


def main() -> int:
    args = parse_args()
    root = project_root()
    bags_root = root / "data" / "bags"
    output_dir = root / "data" / "results" / "trajectories"
    if not bags_root.exists():
        raise SystemExit(f"Bags directory does not exist: {bags_root}")

    bags = bag_directories(bags_root, args.bag)
    if not bags:
        print(f"No bags found in {bags_root}")
        return 0
    for bag in bags:
        extract_bag(bag, output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
