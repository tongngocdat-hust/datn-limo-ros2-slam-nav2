#!/usr/bin/env python3
"""Summarize Nav2 trial CSV files using only the Python standard library."""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path


SUMMARY_FIELDS = [
    "algorithm",
    "total_trials",
    "successful_trials",
    "success_rate_percent",
    "navigation_time_s",
    "path_length_m",
    "goal_error_m",
    "recovery_count",
    "collision_count",
]


def as_float(row: dict[str, str], key: str) -> float | None:
    try:
        value = float(row.get(key, ""))
        return value if math.isfinite(value) else None
    except (TypeError, ValueError):
        return None


def is_success(row: dict[str, str]) -> bool:
    return row.get("success", "").strip().lower() in {"1", "true", "yes", "y"}


def mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def fmt(value: float | None, digits: int = 2) -> str:
    return "" if value is None else f"{value:.{digits}f}"


def load_rows(paths: list[Path]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(path)
        with path.open(newline="", encoding="utf-8-sig") as stream:
            rows.extend(csv.DictReader(stream))
    return rows


def summarize(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    display_names: dict[str, str] = {}
    for row in rows:
        name = row.get("algorithm", "").strip()
        if not name:
            continue
        key = name.casefold().replace("-", "_").replace(" ", "_")
        display_names.setdefault(key, name)
        groups[key].append(row)

    output: list[dict[str, object]] = []
    for key in groups:
        trials = groups[key]
        successful = [row for row in trials if is_success(row)]

        def successful_values(column: str) -> list[float]:
            return [
                value
                for row in successful
                if (value := as_float(row, column)) is not None
            ]

        def total(column: str) -> int:
            return int(
                sum(
                    value
                    for row in trials
                    if (value := as_float(row, column)) is not None
                )
            )

        output.append(
            {
                "algorithm": display_names[key],
                "total_trials": len(trials),
                "successful_trials": len(successful),
                "success_rate_percent": 100.0 * len(successful) / len(trials),
                "navigation_time_s": mean(successful_values("navigation_time_s")),
                "path_length_m": mean(successful_values("path_length_m")),
                "goal_error_m": mean(successful_values("goal_error_m")),
                "recovery_count": total("recovery_count"),
                "collision_count": total("collision_count"),
            }
        )
    return output


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    **row,
                    "success_rate_percent": fmt(
                        float(row["success_rate_percent"]), 1
                    ),
                    "navigation_time_s": fmt(row["navigation_time_s"]),
                    "path_length_m": fmt(row["path_length_m"]),
                    "goal_error_m": fmt(row["goal_error_m"]),
                }
            )


def markdown(rows: list[dict[str, object]]) -> str:
    lines = [
        "| Thuật toán SLAM | Số lần thử | Thành công | Success Rate (%) | "
        "Navigation Time (s) | Path Length (m) | Goal Error (m) | "
        "Recovery Count | Collision Count |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['algorithm']} | {row['total_trials']} | "
            f"{row['successful_trials']} | "
            f"{float(row['success_rate_percent']):.1f} | "
            f"{fmt(row['navigation_time_s'])} | {fmt(row['path_length_m'])} | "
            f"{fmt(row['goal_error_m'])} | {row['recovery_count']} | "
            f"{row['collision_count']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Tong hop cac lan thu Nav2 thanh bang ket qua."
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        type=Path,
        default=[root / "results" / "trials.csv"],
        help="Mot hoac nhieu file trials.csv",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=root / "results"
    )
    args = parser.parse_args()

    try:
        rows = load_rows(args.inputs)
    except FileNotFoundError as exc:
        print(f"ERROR: Khong tim thay file: {exc.filename}")
        return 2
    if not rows:
        print("ERROR: Khong co du lieu de tong hop.")
        return 2

    summary = summarize(rows)
    csv_path = args.output_dir / "navigation_summary.csv"
    md_path = args.output_dir / "navigation_summary.md"
    write_csv(csv_path, summary)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    md_path.write_text(markdown(summary), encoding="utf-8")

    print(markdown(summary))
    print(f"Da luu:\n  {csv_path}\n  {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
