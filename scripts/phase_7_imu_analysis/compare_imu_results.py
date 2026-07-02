#!/usr/bin/env python3
"""Compare final summary rows for IMU on/off pairs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


KEY_COLUMNS = ["system", "scenario", "run"]
METRIC_COLUMNS = [
    "cpu_mean",
    "cpu_std",
    "ram_mean",
    "ram_max",
    "entropy",
    "ssim_raw",
    "occupied_iou_raw",
    "known_coverage_raw",
    "ssim",
    "occupied_iou",
    "known_coverage",
    "known_area_m2",
    "alignment_dx_m",
    "alignment_dy_m",
    "alignment_yaw_deg",
    "rmse",
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def main() -> int:
    root = project_root()
    input_csv = root / "data" / "results" / "final_summary.csv"
    output_csv = root / "data" / "results" / "imu_comparison.csv"
    if not input_csv.exists():
        raise SystemExit(f"Missing final summary: {input_csv}")

    df = pd.read_csv(input_csv)
    missing = set(KEY_COLUMNS + ["imu"]) - set(df.columns)
    if missing:
        raise SystemExit(f"{input_csv} is missing required columns: {', '.join(sorted(missing))}")

    rows = []
    for key, group in df.groupby(KEY_COLUMNS, dropna=False):
        on = group[group["imu"] == "on"]
        off = group[group["imu"] == "off"]
        if on.empty or off.empty:
            continue
        on_row = on.iloc[0]
        off_row = off.iloc[0]
        row = dict(zip(KEY_COLUMNS, key))
        for metric in METRIC_COLUMNS:
            if metric not in df.columns:
                continue
            on_value = pd.to_numeric(pd.Series([on_row[metric]]), errors="coerce").iloc[0]
            off_value = pd.to_numeric(pd.Series([off_row[metric]]), errors="coerce").iloc[0]
            row[f"{metric}_imu_on"] = on_value
            row[f"{metric}_imu_off"] = off_value
            row[f"{metric}_delta_on_minus_off"] = on_value - off_value
        rows.append(row)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output_csv, index=False)
    print(f"Saved IMU comparison: {output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
