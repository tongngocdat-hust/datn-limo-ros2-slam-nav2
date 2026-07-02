#!/usr/bin/env python3
"""Summarize resource-monitoring CSV files with mean/std/max metrics."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read one or more resource CSV files and compute mean/std/max."
    )
    parser.add_argument(
        "csv_files",
        nargs="+",
        type=Path,
        help="Input CSV files produced by measure_process_resources.py.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("resource_summary.csv"),
        help="Output summary CSV path. Default: resource_summary.csv.",
    )
    parser.add_argument(
        "--drop-zero-process",
        action="store_true",
        help="Ignore samples where no matching process was found.",
    )
    return parser.parse_args()


def label_from_path(path: Path) -> str:
    return path.stem


def read_csv(path: Path, drop_zero_process: bool) -> pd.DataFrame:
    df = pd.read_csv(path)
    required_columns = {"keyword", "process_count", "cpu_percent", "ram_mb"}
    missing = required_columns - set(df.columns)
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ValueError(f"{path} is missing required columns: {missing_text}")

    df["source_file"] = str(path)
    df["run_label"] = label_from_path(path)
    df["cpu_percent"] = pd.to_numeric(df["cpu_percent"], errors="coerce")
    df["ram_mb"] = pd.to_numeric(df["ram_mb"], errors="coerce")
    df["process_count"] = pd.to_numeric(df["process_count"], errors="coerce")
    df = df.dropna(subset=["cpu_percent", "ram_mb", "process_count"])
    if drop_zero_process:
        df = df[df["process_count"] > 0]
    return df


def main() -> int:
    args = parse_args()
    frames = [read_csv(path, args.drop_zero_process) for path in args.csv_files]
    data = pd.concat(frames, ignore_index=True)
    if data.empty:
        raise SystemExit("No valid samples found.")

    summary = (
        data.groupby(["run_label", "keyword", "source_file"], as_index=False)
        .agg(
            samples=("cpu_percent", "count"),
            process_count_mean=("process_count", "mean"),
            cpu_mean=("cpu_percent", "mean"),
            cpu_std=("cpu_percent", "std"),
            cpu_max=("cpu_percent", "max"),
            ram_mean_mb=("ram_mb", "mean"),
            ram_std_mb=("ram_mb", "std"),
            ram_max_mb=("ram_mb", "max"),
        )
        .sort_values(["keyword", "run_label"])
    )
    summary[["cpu_std", "ram_std_mb"]] = summary[["cpu_std", "ram_std_mb"]].fillna(0.0)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.output, index=False)
    print(summary.to_string(index=False))
    print(f"\nSaved summary: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
