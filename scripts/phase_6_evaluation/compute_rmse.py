#!/usr/bin/env python3
"""Compute 2D RMSE between timestamped trajectory CSV files."""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd


NAME_RE = re.compile(
    r"(?P<system>gmapping|cartographer|slam_toolbox)_(?P<scenario>[ABC])_run(?P<run>[1-5])_imu_(?P<imu>on|off)"
)


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute x/y RMSE with timestamp interpolation.")
    parser.add_argument("--reference_csv", required=True, type=Path)
    parser.add_argument("--estimated_csv", required=True, type=Path)
    parser.add_argument(
        "--relative_time",
        action="store_true",
        help="Compare trajectories after shifting each CSV timestamp to start at 0.",
    )
    parser.add_argument(
        "--association",
        choices=("time", "arc_length"),
        default="time",
        help="Match poses by timestamp or normalized distance along the path.",
    )
    parser.add_argument(
        "--align",
        choices=("none", "se2"),
        default="none",
        help="Optionally remove one constant 2D rotation/translation before RMSE.",
    )
    return parser.parse_args()


def load_trajectory(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = {"timestamp", "x", "y"} - set(df.columns)
    if missing:
        raise SystemExit(f"{path} is missing required columns: {', '.join(sorted(missing))}")
    df = df[["timestamp", "x", "y"]].dropna().sort_values("timestamp")
    if df.empty:
        raise SystemExit(f"{path} has no trajectory rows")
    return df


def shift_to_relative_time(df: pd.DataFrame) -> pd.DataFrame:
    shifted = df.copy()
    shifted["timestamp"] = shifted["timestamp"] - float(shifted["timestamp"].min())
    return shifted


def parse_case(*paths: Path) -> dict[str, object]:
    joined = " ".join(path.stem for path in paths)
    match = NAME_RE.search(joined)
    if not match:
        return {"system": "", "scenario": "", "run": "", "imu": ""}
    values: dict[str, object] = match.groupdict()
    values["run"] = int(values["run"])
    return values


def resample_by_arc_length(df: pd.DataFrame, samples: int = 300) -> np.ndarray:
    points = df[["x", "y"]].to_numpy(dtype=float)
    if len(points) < 2:
        raise SystemExit("Trajectory needs at least two points for arc-length association")
    segment_lengths = np.linalg.norm(np.diff(points, axis=0), axis=1)
    cumulative = np.concatenate(([0.0], np.cumsum(segment_lengths)))
    keep = np.concatenate(([True], np.diff(cumulative) > 1e-9))
    cumulative, points = cumulative[keep], points[keep]
    if cumulative[-1] <= 0 or len(points) < 2:
        raise SystemExit("Trajectory has no measurable motion")
    targets = np.linspace(0.0, cumulative[-1], samples)
    return np.column_stack(
        (
            np.interp(targets, cumulative, points[:, 0]),
            np.interp(targets, cumulative, points[:, 1]),
        )
    )


def align_se2(reference: np.ndarray, estimated: np.ndarray) -> np.ndarray:
    ref_center = reference.mean(axis=0)
    est_center = estimated.mean(axis=0)
    covariance = (estimated - est_center).T @ (reference - ref_center)
    u_matrix, _, vt_matrix = np.linalg.svd(covariance)
    rotation = vt_matrix.T @ u_matrix.T
    if np.linalg.det(rotation) < 0:
        vt_matrix[-1, :] *= -1
        rotation = vt_matrix.T @ u_matrix.T
    return (estimated - est_center) @ rotation.T + ref_center


def main() -> int:
    args = parse_args()
    ref = load_trajectory(args.reference_csv)
    est = load_trajectory(args.estimated_csv)
    if args.relative_time:
        ref = shift_to_relative_time(ref)
        est = shift_to_relative_time(est)

    if args.association == "arc_length":
        ref_points = resample_by_arc_length(ref)
        est_points = resample_by_arc_length(est)
    else:
        start = max(float(ref["timestamp"].min()), float(est["timestamp"].min()))
        end = min(float(ref["timestamp"].max()), float(est["timestamp"].max()))
        ref_window = ref[(ref["timestamp"] >= start) & (ref["timestamp"] <= end)]
        if ref_window.empty:
            raise SystemExit("No overlapping timestamp range between reference and estimated CSV files")
        ref_points = ref_window[["x", "y"]].to_numpy(dtype=float)
        est_points = np.column_stack(
            (
                np.interp(ref_window["timestamp"], est["timestamp"], est["x"]),
                np.interp(ref_window["timestamp"], est["timestamp"], est["y"]),
            )
        )

    if args.align == "se2":
        est_points = align_se2(ref_points, est_points)
    delta = ref_points - est_points
    dx, dy = delta[:, 0], delta[:, 1]
    rmse = math.sqrt(float(np.mean(dx * dx + dy * dy)))

    output = project_root() / "data" / "results" / "rmse_results.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    case = parse_case(args.reference_csv, args.estimated_csv)
    row = {
        **case,
        "reference_csv": str(args.reference_csv),
        "estimated_csv": str(args.estimated_csv),
        "time_mode": "relative" if args.relative_time else "absolute",
        "association": args.association,
        "alignment": args.align,
        "samples": len(ref_points),
        "rmse": rmse,
    }
    new_df = pd.DataFrame([row])
    if output.exists():
        old_df = pd.read_csv(output)
        if case["system"]:
            same_case = (
                (old_df["system"] == case["system"])
                & (old_df["scenario"] == case["scenario"])
                & (pd.to_numeric(old_df["run"], errors="coerce") == case["run"])
                & (old_df["imu"] == case["imu"])
            )
            old_df = old_df[~same_case]
        new_df = pd.concat([old_df, new_df], ignore_index=True)
    new_df.to_csv(output, index=False)
    print(f"Saved RMSE result: {output}")
    print(f"RMSE: {rmse:.6f} m ({len(ref_points)} samples)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
