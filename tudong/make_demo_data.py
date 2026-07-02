#!/usr/bin/env python3
"""Create deterministic sample data for testing summarize.py without ROS 2."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path


CSV_FIELDS = [
    "timestamp_utc",
    "algorithm",
    "run",
    "success",
    "navigation_time_s",
    "path_length_m",
    "goal_error_m",
    "recovery_count",
    "collision_count",
    "result_status",
    "goal_x",
    "goal_y",
    "goal_yaw",
    "global_frame",
    "path_frame",
    "base_frame",
]

CASES = [
    ("Gmapping", 8, 35.2, 12.8, 0.22, {1, 4, 7}, {5}),
    ("Cartographer", 9, 31.4, 12.1, 0.11, {3}, set()),
    ("SLAM Toolbox", 10, 29.7, 11.9, 0.08, set(), set()),
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Tao 30 dong du lieu mau.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "demo" / "trials.csv",
    )
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for algorithm, successes, nav_time, path, error, recoveries, collisions in CASES:
            for run in range(1, 11):
                success = run <= successes
                writer.writerow(
                    {
                        "timestamp_utc": timestamp,
                        "algorithm": algorithm,
                        "run": run,
                        "success": int(success),
                        "navigation_time_s": nav_time if success else nav_time + 20,
                        "path_length_m": path if success else path + 2,
                        "goal_error_m": error if success else error + 1,
                        "recovery_count": int(run in recoveries),
                        "collision_count": int(run in collisions),
                        "result_status": "SUCCEEDED" if success else "ABORTED",
                        "goal_x": 2.0,
                        "goal_y": 1.0,
                        "goal_yaw": 0.0,
                        "global_frame": "map",
                        "path_frame": "odom",
                        "base_frame": "base_link",
                    }
                )
    print(f"Da tao du lieu mau: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
