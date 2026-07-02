#!/usr/bin/env python3
"""Export resource summary CSV as rounded Markdown or plain-text table."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


HEADERS = [
    "Thuat toan",
    "So mau",
    "So process TB",
    "CPU TB (%)",
    "CPU std",
    "CPU max (%)",
    "RAM TB (MB)",
    "RAM std",
    "RAM max (MB)",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert resource_summary.csv to a Markdown table."
    )
    parser.add_argument(
        "summary_csv",
        type=Path,
        help="Input resource_summary.csv produced by summarize_resource_csv.py.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("resource_table.md"),
        help="Output Markdown path. Default: resource_table.md.",
    )
    parser.add_argument(
        "--digits",
        type=int,
        default=2,
        help="Decimal digits for numeric values. Default: 2.",
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "text"),
        default="markdown",
        help="Output table format. Default: markdown.",
    )
    return parser.parse_args()


def fmt(value: str, digits: int) -> str:
    try:
        return f"{float(value):.{digits}f}"
    except ValueError:
        return value


def algorithm_name(row: dict[str, str]) -> str:
    names = {
        "cartographer": "Cartographer",
        "gmapping": "Gmapping",
        "slam_toolbox": "Slam Toolbox",
    }
    key = row.get("keyword") or row.get("run_label", "")
    return names.get(key, key)


def markdown_table(rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(HEADERS) + " |",
        "| " + " | ".join(["---"] + ["---:"] * (len(HEADERS) - 1)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines) + "\n"


def text_table(rows: list[list[str]]) -> str:
    all_rows = [HEADERS, *rows]
    widths = [
        max(len(row[index]) for row in all_rows)
        for index in range(len(HEADERS))
    ]

    def format_row(row: list[str]) -> str:
        cells = []
        for index, cell in enumerate(row):
            if index == 0:
                cells.append(cell.ljust(widths[index]))
            else:
                cells.append(cell.rjust(widths[index]))
        return " | ".join(cells)

    separator = "-+-".join("-" * width for width in widths)
    lines = [format_row(HEADERS), separator]
    lines.extend(format_row(row) for row in rows)
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    with args.summary_csv.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        rows = []
        for row in reader:
            rows.append(
                [
                    algorithm_name(row),
                    row["samples"],
                    fmt(row["process_count_mean"], 1),
                    fmt(row["cpu_mean"], args.digits),
                    fmt(row["cpu_std"], args.digits),
                    fmt(row["cpu_max"], args.digits),
                    fmt(row["ram_mean_mb"], args.digits),
                    fmt(row["ram_std_mb"], args.digits),
                    fmt(row["ram_max_mb"], args.digits),
                ]
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    table = text_table(rows) if args.format == "text" else markdown_table(rows)
    args.output.write_text(table, encoding="utf-8")
    print(table)
    print(f"Saved table: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
