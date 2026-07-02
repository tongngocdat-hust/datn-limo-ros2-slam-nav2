#!/usr/bin/env python3
"""Plot CPU and RAM comparison charts from resource summary CSV."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-resource-monitoring")

import matplotlib.pyplot as plt
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot CPU/RAM comparison from summarize_resource_csv.py output."
    )
    parser.add_argument(
        "summary_csv",
        type=Path,
        help="Summary CSV produced by summarize_resource_csv.py.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("resource_comparison.png"),
        help="Output image path. Default: resource_comparison.png.",
    )
    parser.add_argument(
        "--title",
        default="ROS 2 SLAM CPU/RAM Comparison",
        help="Figure title.",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=150,
        help="Output image DPI. Default: 150.",
    )
    return parser.parse_args()


def display_labels(df: pd.DataFrame) -> list[str]:
    labels: list[str] = []
    duplicated_keywords = df["keyword"].duplicated(keep=False)
    for _, row in df.iterrows():
        if duplicated_keywords.loc[row.name]:
            labels.append(f"{row['keyword']}\n{row['run_label']}")
        else:
            labels.append(str(row["keyword"]))
    return labels


def bar_with_error(ax: plt.Axes, labels: list[str], mean_col: pd.Series, std_col: pd.Series) -> None:
    x_positions = range(len(labels))
    ax.bar(x_positions, mean_col, yerr=std_col, capsize=5, color="#4C78A8")
    ax.set_xticks(list(x_positions))
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.grid(axis="y", linestyle="--", alpha=0.35)


def main() -> int:
    args = parse_args()
    df = pd.read_csv(args.summary_csv)
    required_columns = {
        "run_label",
        "keyword",
        "cpu_mean",
        "cpu_std",
        "cpu_max",
        "ram_mean_mb",
        "ram_std_mb",
        "ram_max_mb",
    }
    missing = required_columns - set(df.columns)
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ValueError(f"{args.summary_csv} is missing required columns: {missing_text}")

    df = df.sort_values(["keyword", "run_label"]).reset_index(drop=True)
    labels = display_labels(df)

    fig, axes = plt.subplots(2, 1, figsize=(11, 8), constrained_layout=True)
    fig.suptitle(args.title, fontsize=14)

    bar_with_error(axes[0], labels, df["cpu_mean"], df["cpu_std"])
    axes[0].scatter(range(len(labels)), df["cpu_max"], color="#E45756", label="max", zorder=3)
    axes[0].set_ylabel("CPU (%)")
    axes[0].set_title("CPU mean/std with max marker")
    axes[0].legend()

    bar_with_error(axes[1], labels, df["ram_mean_mb"], df["ram_std_mb"])
    axes[1].scatter(range(len(labels)), df["ram_max_mb"], color="#E45756", label="max", zorder=3)
    axes[1].set_ylabel("RAM (MB)")
    axes[1].set_title("RAM mean/std with max marker")
    axes[1].legend()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=args.dpi)
    print(f"Saved plot: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
