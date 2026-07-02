#!/usr/bin/env python3
"""Run one Nav2 goal and append its navigation metrics to a CSV file."""

from __future__ import annotations

import argparse
import csv
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import rclpy
    from action_msgs.msg import GoalStatus
    from geometry_msgs.msg import PoseStamped
    from nav2_msgs.action import NavigateToPose
    from rclpy.action import ActionClient
    from rclpy.duration import Duration
    from rclpy.node import Node
    from rclpy.time import Time
    from std_msgs.msg import Bool
    from tf2_ros import Buffer, TransformException, TransformListener
except ImportError as exc:
    print(
        "ERROR: Khong tim thay ROS 2 Python packages.\n"
        "Hay chay:\n"
        "  source /opt/ros/humble/setup.bash\n"
        "  source <workspace_limo>/install/setup.bash",
        file=sys.stderr,
    )
    raise SystemExit(2) from exc


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

STATUS_NAMES = {
    GoalStatus.STATUS_UNKNOWN: "UNKNOWN",
    GoalStatus.STATUS_ACCEPTED: "ACCEPTED",
    GoalStatus.STATUS_EXECUTING: "EXECUTING",
    GoalStatus.STATUS_CANCELING: "CANCELING",
    GoalStatus.STATUS_SUCCEEDED: "SUCCEEDED",
    GoalStatus.STATUS_CANCELED: "CANCELED",
    GoalStatus.STATUS_ABORTED: "ABORTED",
}


def duration_seconds(value: object) -> float:
    return float(value.sec) + float(value.nanosec) / 1_000_000_000.0


def append_csv(path: Path, row: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    needs_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS)
        if needs_header:
            writer.writeheader()
        writer.writerow(row)


class TrialNode(Node):
    def __init__(self, args: argparse.Namespace) -> None:
        super().__init__("tudong_navigation_metrics")
        self.args = args
        self.action_client = ActionClient(self, NavigateToPose, args.action_name)
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.timer = self.create_timer(1.0 / args.sample_rate, self.sample_position)

        self.active = False
        self.previous_xy: tuple[float, float] | None = None
        self.path_length = 0.0
        self.navigation_time = 0.0
        self.recovery_count = 0
        self.collision_count = 0
        self.collision_active = False

        if args.collision_topic:
            self.create_subscription(
                Bool, args.collision_topic, self.collision_callback, 10
            )

    def lookup_xy(self, reference_frame: str) -> tuple[float, float] | None:
        try:
            transform = self.tf_buffer.lookup_transform(
                reference_frame,
                self.args.base_frame,
                Time(),
                timeout=Duration(seconds=0.05),
            )
        except TransformException:
            return None
        translation = transform.transform.translation
        return float(translation.x), float(translation.y)

    def sample_position(self) -> None:
        if not self.active:
            return
        xy = self.lookup_xy(self.args.path_frame)
        if xy is None:
            return
        if self.previous_xy is not None:
            step = math.dist(self.previous_xy, xy)
            if step <= self.args.max_tf_step:
                self.path_length += step
            else:
                self.get_logger().warning(
                    f"Bo qua buoc nhay TF bat thuong: {step:.3f} m"
                )
        self.previous_xy = xy

    def feedback_callback(self, message: object) -> None:
        feedback = message.feedback
        self.navigation_time = duration_seconds(feedback.navigation_time)
        self.recovery_count = int(feedback.number_of_recoveries)

    def collision_callback(self, message: Bool) -> None:
        current = bool(message.data)
        if self.active and current and not self.collision_active:
            self.collision_count += 1
            self.get_logger().warning(
                f"Phat hien va cham #{self.collision_count}"
            )
        self.collision_active = current


def build_goal(args: argparse.Namespace, node: Node) -> NavigateToPose.Goal:
    goal = NavigateToPose.Goal()
    pose = PoseStamped()
    pose.header.frame_id = args.global_frame
    pose.header.stamp = node.get_clock().now().to_msg()
    pose.pose.position.x = args.x
    pose.pose.position.y = args.y
    pose.pose.orientation.z = math.sin(args.yaw / 2.0)
    pose.pose.orientation.w = math.cos(args.yaw / 2.0)
    goal.pose = pose
    goal.behavior_tree = args.behavior_tree
    return goal


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gui mot goal Nav2 va tu dong ghi cac chi so thi nghiem."
    )
    parser.add_argument("--algorithm", required=True, help="gmapping, cartographer...")
    parser.add_argument("--run", required=True, type=int, help="So lan thu, bat dau tu 1")
    parser.add_argument("--x", required=True, type=float, help="Goal X trong global frame")
    parser.add_argument("--y", required=True, type=float, help="Goal Y trong global frame")
    parser.add_argument("--yaw", type=float, default=0.0, help="Goal yaw (radian)")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "results" / "trials.csv",
    )
    parser.add_argument("--global-frame", default="map")
    parser.add_argument(
        "--path-frame",
        default="odom",
        help="Frame dung de cong don quang duong; odom thuong on dinh nhat",
    )
    parser.add_argument("--base-frame", default="base_link")
    parser.add_argument("--action-name", default="/navigate_to_pose")
    parser.add_argument(
        "--collision-topic",
        default="/collision_detected",
        help="Topic std_msgs/Bool; truyen chuoi rong de tat",
    )
    parser.add_argument("--behavior-tree", default="")
    parser.add_argument("--sample-rate", type=float, default=10.0)
    parser.add_argument(
        "--max-tf-step",
        type=float,
        default=1.0,
        help="Bo qua buoc nhay TF lon hon gia tri nay (m)",
    )
    parser.add_argument("--server-timeout", type=float, default=30.0)
    parser.add_argument(
        "--timeout",
        type=float,
        default=300.0,
        help="Huy goal neu vuot qua so giay nay; 0 la khong gioi han",
    )
    args = parser.parse_args()
    if args.run < 1 or args.sample_rate <= 0 or args.max_tf_step <= 0:
        parser.error("--run, --sample-rate va --max-tf-step phai lon hon 0")
    return args


def main() -> int:
    args = parse_args()
    rclpy.init()
    node = TrialNode(args)

    try:
        print(f"Dang cho action server {args.action_name}...")
        if not node.action_client.wait_for_server(timeout_sec=args.server_timeout):
            print("ERROR: Khong tim thay Nav2 action server.", file=sys.stderr)
            return 3

        send_future = node.action_client.send_goal_async(
            build_goal(args, node), feedback_callback=node.feedback_callback
        )
        rclpy.spin_until_future_complete(node, send_future)
        goal_handle = send_future.result()
        if goal_handle is None or not goal_handle.accepted:
            print("ERROR: Goal bi Nav2 tu choi.", file=sys.stderr)
            return 4

        node.previous_xy = node.lookup_xy(args.path_frame)
        node.active = True
        started = time.monotonic()
        result_future = goal_handle.get_result_async()
        timed_out = False

        print("Goal da duoc chap nhan. Dang do so lieu...")
        while rclpy.ok() and not result_future.done():
            rclpy.spin_once(node, timeout_sec=0.1)
            if args.timeout > 0 and time.monotonic() - started >= args.timeout:
                timed_out = True
                print("Het thoi gian, dang huy goal...")
                cancel_future = goal_handle.cancel_goal_async()
                rclpy.spin_until_future_complete(node, cancel_future, timeout_sec=5.0)
                break

        if not result_future.done():
            rclpy.spin_until_future_complete(node, result_future, timeout_sec=5.0)

        node.active = False
        wall_time = time.monotonic() - started
        final_xy = node.lookup_xy(args.global_frame)
        goal_error = (
            math.dist(final_xy, (args.x, args.y)) if final_xy is not None else math.nan
        )

        if result_future.done() and result_future.result() is not None:
            status = int(result_future.result().status)
        else:
            status = GoalStatus.STATUS_CANCELED if timed_out else GoalStatus.STATUS_UNKNOWN
        status_name = "TIMEOUT" if timed_out else STATUS_NAMES.get(status, str(status))
        success = status == GoalStatus.STATUS_SUCCEEDED and not timed_out

        row = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "algorithm": args.algorithm,
            "run": args.run,
            "success": int(success),
            "navigation_time_s": f"{node.navigation_time or wall_time:.3f}",
            "path_length_m": f"{node.path_length:.3f}",
            "goal_error_m": "" if math.isnan(goal_error) else f"{goal_error:.3f}",
            "recovery_count": node.recovery_count,
            "collision_count": node.collision_count,
            "result_status": status_name,
            "goal_x": args.x,
            "goal_y": args.y,
            "goal_yaw": args.yaw,
            "global_frame": args.global_frame,
            "path_frame": args.path_frame,
            "base_frame": args.base_frame,
        }
        append_csv(args.output, row)

        print(
            f"Da luu: {args.output}\n"
            f"success={int(success)}, time={row['navigation_time_s']} s, "
            f"path={row['path_length_m']} m, error={row['goal_error_m']} m, "
            f"recovery={node.recovery_count}, collision={node.collision_count}"
        )
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\nDa dung boi nguoi dung; lan thu nay chua duoc ghi.", file=sys.stderr)
        return 130
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
