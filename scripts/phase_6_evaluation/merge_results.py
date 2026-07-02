#!/usr/bin/env python3
"""Merge map, trajectory, and resource metrics into one summary CSV."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


NAME_RE = re.compile(
    r"(?P<system>gmapping|cartographer|slam_toolbox)_(?P<scenario>[ABC])_run(?P<run>[1-5])_imu_(?P<imu>on|off)"
)
KEY_COLUMNS = ["system", "scenario", "run", "imu"]
OUTPUT_COLUMNS = [
    "system",
    "scenario",
    "run",
    "imu",
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
    "alignment_status",
    "rmse",
]
TABLE_COLUMNS = [
    ("system", "system", "text"),
    ("scenario", "scenario", "text"),
    ("run", "run", "int"),
    ("imu", "imu", "text"),
    ("cpu_mean", "cpu_mean_%", "float"),
    ("cpu_std", "cpu_std", "float"),
    ("ram_mean", "ram_mean_MB", "float"),
    ("ram_max", "ram_max_MB", "float"),
    ("entropy", "entropy", "float"),
    ("ssim_raw", "ssim_raw", "float"),
    ("ssim", "ssim_aligned", "float"),
    ("occupied_iou_raw", "iou_raw", "float"),
    ("occupied_iou", "iou_aligned", "float"),
    ("known_coverage", "known_coverage", "float"),
    ("known_area_m2", "known_area_m2", "float"),
    ("alignment_dx_m", "align_dx_m", "float"),
    ("alignment_dy_m", "align_dy_m", "float"),
    ("alignment_yaw_deg", "align_yaw_deg", "float"),
    ("rmse", "rmse_m", "float"),
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_case(text: str) -> dict[str, object]:
    match = NAME_RE.search(text)
    if not match:
        return {"system": "", "scenario": "", "run": "", "imu": ""}
    values: dict[str, object] = match.groupdict()
    values["run"] = int(values["run"])
    return values


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    for column in KEY_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    if "run" in df.columns:
        df["run"] = pd.to_numeric(df["run"], errors="coerce").astype("Int64")
    return df


def load_metric_csv(path: Path, value_columns: list[str]) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=KEY_COLUMNS + value_columns)
    df = pd.read_csv(path)
    for column in value_columns:
        if column not in df.columns:
            df[column] = pd.NA
    return normalize_keys(df)[KEY_COLUMNS + value_columns]


def load_rmse_csv(path: Path, root: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=KEY_COLUMNS + ["rmse"])
    df = pd.read_csv(path)
    if "estimated_csv" in df.columns:
        def source_exists(value: object) -> bool:
            if pd.isna(value):
                return False
            source = Path(str(value))
            return source.exists() if source.is_absolute() else (root / source).exists()

        df = df[df["estimated_csv"].map(source_exists)]
    return normalize_keys(df)[KEY_COLUMNS + ["rmse"]]


def summarize_resource_file(path: Path) -> dict[str, object] | None:
    df = pd.read_csv(path)
    case = parse_case(path.stem)
    if not case["system"]:
        text = " ".join(str(value) for value in df.head(1).to_dict("records"))
        case = parse_case(f"{path.stem} {text}")

    if {"cpu_mean", "cpu_std"}.issubset(df.columns):
        cpu_mean = float(df["cpu_mean"].iloc[0])
        cpu_std = float(df["cpu_std"].iloc[0])
    elif "cpu_percent" in df.columns:
        cpu_mean = float(pd.to_numeric(df["cpu_percent"], errors="coerce").mean())
        cpu_std = float(pd.to_numeric(df["cpu_percent"], errors="coerce").std(ddof=0))
    else:
        cpu_mean = pd.NA
        cpu_std = pd.NA

    ram_col = "ram_mean_mb" if "ram_mean_mb" in df.columns else "ram_mb"
    ram_max_col = "ram_max_mb" if "ram_max_mb" in df.columns else "ram_mb"
    ram_mean = float(pd.to_numeric(df[ram_col], errors="coerce").mean()) if ram_col in df.columns else pd.NA
    ram_max = float(pd.to_numeric(df[ram_max_col], errors="coerce").max()) if ram_max_col in df.columns else pd.NA

    return {**case, "cpu_mean": cpu_mean, "cpu_std": cpu_std, "ram_mean": ram_mean, "ram_max": ram_max}


def load_resources(resources_dir: Path) -> pd.DataFrame:
    rows = []
    if resources_dir.exists():
        for path in sorted(resources_dir.glob("*_resource.csv")):
            row = summarize_resource_file(path)
            if row:
                rows.append(row)
    return normalize_keys(pd.DataFrame(rows, columns=KEY_COLUMNS + ["cpu_mean", "cpu_std", "ram_mean", "ram_max"]))


def merge(left: pd.DataFrame, right: pd.DataFrame) -> pd.DataFrame:
    if left.empty:
        return right
    if right.empty:
        return left
    return pd.merge(left, right, on=KEY_COLUMNS, how="outer")


def format_value(value: object, value_type: str) -> str:
    if pd.isna(value):
        return ""
    if value_type == "int":
        return str(int(value))
    if value_type == "float":
        return f"{float(value):.3f}"
    return str(value)


def final_table_rows(df: pd.DataFrame) -> tuple[list[str], list[list[str]]]:
    headers = [header for _, header, _ in TABLE_COLUMNS]
    rows = [
        [format_value(row[column], value_type) for column, _, value_type in TABLE_COLUMNS]
        for _, row in df.iterrows()
    ]
    return headers, rows


def text_table(headers: list[str], rows: list[list[str]]) -> str:
    all_rows = [headers, *rows]
    widths = [max(len(row[index]) for row in all_rows) for index in range(len(headers))]

    def format_row(row: list[str]) -> str:
        return " | ".join(cell.ljust(widths[index]) for index, cell in enumerate(row))

    separator = "-+-".join("-" * width for width in widths)
    return "\n".join([format_row(headers), separator, *(format_row(row) for row in rows)]) + "\n"


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines) + "\n"


def main() -> int:
    root = project_root()
    results_dir = root / "data" / "results"
    map_df = load_metric_csv(
        results_dir / "map_metrics.csv",
        [
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
            "alignment_status",
        ],
    )
    rmse_df = load_rmse_csv(results_dir / "rmse_results.csv", root)
    resource_df = load_resources(root / "data" / "resources")

    merged = merge(resource_df, map_df)
    merged = merge(merged, rmse_df)
    if merged.empty:
        merged = pd.DataFrame(columns=OUTPUT_COLUMNS)
    else:
        merged = merged.reindex(columns=OUTPUT_COLUMNS).sort_values(KEY_COLUMNS, na_position="last")

    missing_resources = merged[
        merged[["cpu_mean", "cpu_std", "ram_mean", "ram_max"]].isna().all(axis=1)
    ]
    for row in missing_resources.itertuples(index=False):
        print(
            "WARNING: No matching resource file for "
            f"{row.system}_{row.scenario}_run{row.run}_imu_{row.imu}"
        )

    output = results_dir / "final_summary.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(output, index=False)
    headers, rows = final_table_rows(merged)
    table_txt = results_dir / "final_summary_table.txt"
    table_md = results_dir / "final_summary_table.md"
    table_txt.write_text(text_table(headers, rows), encoding="utf-8")
    table_md.write_text(markdown_table(headers, rows), encoding="utf-8")
    print(f"Saved final summary: {output}")
    print(f"Saved final summary table: {table_txt}")
    print(f"Saved final summary markdown: {table_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
