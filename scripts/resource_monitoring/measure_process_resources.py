#!/usr/bin/env python3
"""Measure CPU/RAM usage for ROS 2 SLAM processes matched by keyword."""

from __future__ import annotations

import argparse
import csv
import time
from datetime import datetime
from pathlib import Path
from typing import Iterable

import psutil


CSV_FIELDS = [
    "timestamp",
    "elapsed_sec",
    "keyword",
    "process_count",
    "matched_pids",
    "cpu_percent",
    "ram_mb",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Measure aggregate CPU/RAM for processes whose name or command line "
            "contains a keyword, then append samples to CSV."
        )
    )
    parser.add_argument(
        "-k",
        "--keyword",
        required=True,
        help="Process keyword, for example: slam_toolbox, cartographer, slam_gmapping.",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        type=Path,
        help="Output CSV path.",
    )
    parser.add_argument(
        "-i",
        "--interval",
        type=float,
        default=1.0,
        help="Sampling interval in seconds. Default: 1.0.",
    )
    parser.add_argument(
        "-d",
        "--duration",
        type=float,
        default=0.0,
        help="Measurement duration in seconds. Use 0 to run until Ctrl+C. Default: 0.",
    )
    parser.add_argument(
        "--case-sensitive",
        action="store_true",
        help="Match keyword with case sensitivity.",
    )
    return parser.parse_args()


def process_text(proc: psutil.Process) -> str:
    try:
        name = proc.name()
        cmdline = " ".join(proc.cmdline())
        return f"{name} {cmdline}"
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return ""


def matches_keyword(proc: psutil.Process, keyword: str, case_sensitive: bool) -> bool:
    text = process_text(proc)
    if not case_sensitive:
        text = text.lower()
        keyword = keyword.lower()
    return keyword in text


def matching_processes(keyword: str, case_sensitive: bool) -> list[psutil.Process]:
    procs: list[psutil.Process] = []
    current_pid = psutil.Process().pid
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        if proc.pid == current_pid:
            continue
        if matches_keyword(proc, keyword, case_sensitive):
            procs.append(proc)
    return procs


def initialize_cpu_counters(procs: Iterable[psutil.Process]) -> None:
    for proc in procs:
        try:
            proc.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue


def sample(keyword: str, case_sensitive: bool, interval: float) -> tuple[list[int], float, float]:
    procs = matching_processes(keyword, case_sensitive)
    initialize_cpu_counters(procs)
    time.sleep(interval)

    total_cpu = 0.0
    total_ram_bytes = 0
    live_pids: list[int] = []

    for proc in procs:
        try:
            total_cpu += proc.cpu_percent(interval=None)
            total_ram_bytes += proc.memory_info().rss
            live_pids.append(proc.pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    return live_pids, total_cpu, total_ram_bytes / (1024 * 1024)


def ensure_header(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0:
        return
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS)
        writer.writeheader()


def main() -> int:
    args = parse_args()
    if args.interval <= 0:
        raise SystemExit("--interval must be greater than 0")
    if args.duration < 0:
        raise SystemExit("--duration must be greater than or equal to 0")

    ensure_header(args.output)
    started = time.monotonic()

    try:
        with args.output.open("a", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS)
            while True:
                elapsed = time.monotonic() - started
                if args.duration and elapsed >= args.duration:
                    break

                pids, cpu_percent, ram_mb = sample(
                    args.keyword,
                    args.case_sensitive,
                    args.interval,
                )
                elapsed = time.monotonic() - started
                writer.writerow(
                    {
                        "timestamp": datetime.now().isoformat(timespec="seconds"),
                        "elapsed_sec": f"{elapsed:.3f}",
                        "keyword": args.keyword,
                        "process_count": len(pids),
                        "matched_pids": " ".join(str(pid) for pid in sorted(pids)),
                        "cpu_percent": f"{cpu_percent:.3f}",
                        "ram_mb": f"{ram_mb:.3f}",
                    }
                )
                csv_file.flush()
    except KeyboardInterrupt:
        print("\nStopped by user.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
