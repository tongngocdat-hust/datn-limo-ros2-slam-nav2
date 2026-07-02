#!/usr/bin/env python3
"""Publish collision events manually for installations without a bumper topic."""

from __future__ import annotations

import argparse
import sys
import time

try:
    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import Bool
except ImportError as exc:
    print("ERROR: Hay source ROS 2 truoc khi chay.", file=sys.stderr)
    raise SystemExit(2) from exc


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phat mot xung std_msgs/Bool de ghi nhan mot va cham."
    )
    parser.add_argument("--topic", default="/collision_detected")
    args = parser.parse_args()

    rclpy.init()
    node = Node("tudong_manual_collision")
    publisher = node.create_publisher(Bool, args.topic, 10)
    try:
        # Allow DDS discovery before sending the short pulse.
        for _ in range(10):
            rclpy.spin_once(node, timeout_sec=0.05)
            time.sleep(0.05)
        for value in (True, False):
            message = Bool()
            message.data = value
            for _ in range(3):
                publisher.publish(message)
                rclpy.spin_once(node, timeout_sec=0.05)
                time.sleep(0.05)
        print(f"Da phat mot su kien va cham tren {args.topic}")
    finally:
        node.destroy_node()
        rclpy.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
