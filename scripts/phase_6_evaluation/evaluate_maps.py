#!/usr/bin/env python3
"""Evaluate occupancy maps in their metric coordinate frames."""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import cv2
from PIL import Image
from scipy.ndimage import distance_transform_edt
from skimage.metrics import structural_similarity


NAME_RE = re.compile(
    r"^(?P<system>gmapping|cartographer|slam_toolbox)_(?P<scenario>[ABC])_run(?P<run>[1-5])_imu_(?P<imu>on|off)$"
)


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute entropy and optional SSIM for maps in data/maps.")
    parser.add_argument("--ground_truth", type=Path, help="Optional ground-truth .pgm/.png map for SSIM.")
    parser.add_argument(
        "--ground_truth_yaml",
        type=Path,
        help="Map YAML for --ground_truth. Default: same path with .yaml suffix.",
    )
    parser.add_argument("--scenario", choices=("A", "B", "C"), help="Only evaluate this scenario.")
    parser.add_argument("--run", type=int, choices=range(1, 6), help="Only evaluate this run.")
    parser.add_argument("--imu", choices=("on", "off"), help="Only evaluate this IMU state.")
    parser.add_argument(
        "--max_alignment_translation",
        type=float,
        default=2.0,
        help="Maximum accepted map-registration translation in metres (default: 2.0).",
    )
    parser.add_argument(
        "--max_alignment_rotation",
        type=float,
        default=20.0,
        help="Maximum accepted map-registration rotation in degrees (default: 20).",
    )
    return parser.parse_args()


def parse_case(stem: str) -> dict[str, object]:
    match = NAME_RE.match(stem)
    if not match:
        return {"system": "", "scenario": "", "run": "", "imu": ""}
    values: dict[str, object] = match.groupdict()
    values["run"] = int(values["run"])
    return values


def load_gray(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("L"), dtype=np.uint8)


def known_mask(image: np.ndarray) -> np.ndarray:
    # nav2_map_server writes unknown cells near value 205.
    return (image < 200) | (image > 210)


def entropy(image: np.ndarray) -> float:
    values = image[known_mask(image)]
    if values.size == 0:
        return math.nan
    counts = np.bincount(values.ravel(), minlength=256).astype(float)
    probabilities = counts[counts > 0] / values.size
    return float(-(probabilities * np.log2(probabilities)).sum())


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        return [float(item.strip()) for item in value[1:-1].split(",")]
    try:
        return float(value)
    except ValueError:
        return value.strip("'\"")


def load_map_metadata(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Map metadata does not exist: {path}")
    metadata: dict[str, Any] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = parse_scalar(value)
    if "resolution" not in metadata or "origin" not in metadata:
        raise SystemExit(f"{path} must contain resolution and origin")
    return metadata


def metadata_for_image(image_path: Path, explicit_yaml: Path | None = None) -> dict[str, Any]:
    return load_map_metadata(explicit_yaml or image_path.with_suffix(".yaml"))


def project_to_reference(
    image: np.ndarray,
    image_metadata: dict[str, Any],
    reference_shape: tuple[int, int],
    reference_metadata: dict[str, Any],
) -> np.ndarray:
    ref_height, ref_width = reference_shape
    rows, cols = np.indices((ref_height, ref_width), dtype=float)
    ref_resolution = float(reference_metadata["resolution"])
    ref_origin = np.asarray(reference_metadata["origin"], dtype=float)
    ref_local_x = (cols + 0.5) * ref_resolution
    ref_local_y = (ref_height - rows - 0.5) * ref_resolution
    ref_cos, ref_sin = math.cos(ref_origin[2]), math.sin(ref_origin[2])
    world_x = ref_origin[0] + ref_cos * ref_local_x - ref_sin * ref_local_y
    world_y = ref_origin[1] + ref_sin * ref_local_x + ref_cos * ref_local_y

    image_resolution = float(image_metadata["resolution"])
    image_origin = np.asarray(image_metadata["origin"], dtype=float)
    dx, dy = world_x - image_origin[0], world_y - image_origin[1]
    image_cos, image_sin = math.cos(image_origin[2]), math.sin(image_origin[2])
    image_local_x = image_cos * dx + image_sin * dy
    image_local_y = -image_sin * dx + image_cos * dy
    image_cols = np.floor(image_local_x / image_resolution).astype(int)
    image_rows = image.shape[0] - 1 - np.floor(image_local_y / image_resolution).astype(int)

    valid = (
        (image_rows >= 0)
        & (image_rows < image.shape[0])
        & (image_cols >= 0)
        & (image_cols < image.shape[1])
    )
    projected = np.full(reference_shape, 205, dtype=np.uint8)
    projected[valid] = image[image_rows[valid], image_cols[valid]]
    return projected


def comparison_metrics(reference: np.ndarray, candidate: np.ndarray) -> tuple[float, float, float]:
    ref_known = known_mask(reference)
    candidate_known = known_mask(candidate)
    union_known = ref_known | candidate_known
    if not union_known.any():
        return math.nan, math.nan, 0.0

    union_rows, union_cols = np.where(union_known)
    row_min, row_max = int(union_rows.min()), int(union_rows.max()) + 1
    col_min, col_max = int(union_cols.min()), int(union_cols.max()) + 1
    ref_crop = reference[row_min:row_max, col_min:col_max]
    candidate_crop = candidate[row_min:row_max, col_min:col_max]
    if min(ref_crop.shape) < 7:
        ssim = math.nan
    else:
        ssim = float(structural_similarity(ref_crop, candidate_crop, data_range=255))

    ref_occupied = reference < 100
    candidate_occupied = candidate < 100
    occupied_union = ref_occupied | candidate_occupied
    occupied_iou = (
        float((ref_occupied & candidate_occupied).sum() / occupied_union.sum())
        if occupied_union.any()
        else math.nan
    )
    known_coverage = float((ref_known & candidate_known).sum() / max(1, ref_known.sum()))
    return ssim, occupied_iou, known_coverage


def registration_feature(image: np.ndarray) -> np.ndarray:
    occupied = image < 100
    if not occupied.any():
        return np.zeros(image.shape, dtype=np.float32)
    distance = distance_transform_edt(~occupied)
    feature = np.exp(-distance / 6.0).astype(np.float32)
    feature[~known_mask(image)] *= 0.25
    return cv2.GaussianBlur(feature, (5, 5), 0)


def occupied_centroid(image: np.ndarray) -> tuple[float, float] | None:
    rows, cols = np.where(image < 100)
    if rows.size == 0:
        return None
    return float(cols.mean()), float(rows.mean())


def warp_candidate(candidate: np.ndarray, warp: np.ndarray) -> np.ndarray:
    height, width = candidate.shape
    return cv2.warpAffine(
        candidate,
        warp,
        (width, height),
        flags=cv2.INTER_NEAREST | cv2.WARP_INVERSE_MAP,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=205,
    )


def registration_cost(reference: np.ndarray, candidate: np.ndarray) -> float:
    ref_occupied = reference < 100
    candidate_occupied = candidate < 100
    if not ref_occupied.any() or not candidate_occupied.any():
        return math.inf
    ref_distance = distance_transform_edt(~ref_occupied)
    candidate_distance = distance_transform_edt(~candidate_occupied)
    symmetric_chamfer = 0.5 * (
        float(ref_distance[candidate_occupied].mean())
        + float(candidate_distance[ref_occupied].mean())
    )
    _, occupied_iou, known_coverage = comparison_metrics(reference, candidate)
    iou_penalty = 5.0 * (1.0 - occupied_iou) if math.isfinite(occupied_iou) else 5.0
    coverage_penalty = 2.0 * (1.0 - min(1.0, known_coverage))
    return symmetric_chamfer + iou_penalty + coverage_penalty


def register_map_se2(
    reference: np.ndarray,
    candidate: np.ndarray,
    resolution: float,
    max_translation_m: float,
    max_rotation_deg: float,
) -> tuple[np.ndarray, float, float, float, str]:
    if reference.shape != candidate.shape:
        raise ValueError("Reference and candidate must share a canvas before registration")

    max_dimension = max(reference.shape)
    scale = min(1.0, 700.0 / max_dimension)
    if scale < 1.0:
        size = (
            max(32, int(round(reference.shape[1] * scale))),
            max(32, int(round(reference.shape[0] * scale))),
        )
        ref_work = cv2.resize(reference, size, interpolation=cv2.INTER_NEAREST)
        candidate_work = cv2.resize(candidate, size, interpolation=cv2.INTER_NEAREST)
    else:
        ref_work, candidate_work = reference, candidate

    template = registration_feature(ref_work)
    moving = registration_feature(candidate_work)
    if not np.any(template) or not np.any(moving):
        identity = np.eye(2, 3, dtype=np.float32)
        return candidate, 0.0, 0.0, 0.0, "no_occupied_cells"

    initial_warps = [np.eye(2, 3, dtype=np.float32)]
    ref_centroid = occupied_centroid(ref_work)
    candidate_centroid = occupied_centroid(candidate_work)
    if ref_centroid is not None and candidate_centroid is not None:
        centroid_warp = np.eye(2, 3, dtype=np.float32)
        # findTransformECC uses a template-to-input warp with WARP_INVERSE_MAP.
        centroid_warp[0, 2] = candidate_centroid[0] - ref_centroid[0]
        centroid_warp[1, 2] = candidate_centroid[1] - ref_centroid[1]
        initial_warps.append(centroid_warp)

    best: tuple[float, np.ndarray, np.ndarray] | None = None
    criteria = (
        cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,
        250,
        1e-6,
    )
    for initial_warp in initial_warps:
        warp = initial_warp.copy()
        try:
            cv2.findTransformECC(
                template,
                moving,
                warp,
                cv2.MOTION_EUCLIDEAN,
                criteria,
                None,
                5,
            )
        except cv2.error:
            continue

        angle_deg = math.degrees(math.atan2(float(warp[1, 0]), float(warp[0, 0])))
        dx_m = float(warp[0, 2]) / scale * resolution
        # Image rows point downward; report Cartesian Y pointing upward.
        dy_m = -float(warp[1, 2]) / scale * resolution
        if abs(angle_deg) > max_rotation_deg:
            continue
        if math.hypot(dx_m, dy_m) > max_translation_m:
            continue

        full_warp = warp.copy()
        full_warp[:, 2] /= scale
        aligned = warp_candidate(candidate, full_warp)
        cost = registration_cost(reference, aligned)
        if best is None or cost < best[0]:
            best = (cost, full_warp, aligned)

    identity = np.eye(2, 3, dtype=np.float32)
    raw_cost = registration_cost(reference, candidate)
    if best is None or best[0] >= raw_cost:
        return candidate, 0.0, 0.0, 0.0, "identity"

    _, best_warp, aligned = best
    angle_deg = math.degrees(
        math.atan2(float(best_warp[1, 0]), float(best_warp[0, 0]))
    )
    dx_m = float(best_warp[0, 2]) * resolution
    dy_m = -float(best_warp[1, 2]) * resolution
    return aligned, dx_m, dy_m, angle_deg, "aligned"


def matches_filters(case: dict[str, object], args: argparse.Namespace) -> bool:
    if args.scenario and case["scenario"] != args.scenario:
        return False
    if args.run and case["run"] != args.run:
        return False
    if args.imu and case["imu"] != args.imu:
        return False
    return True


def main() -> int:
    args = parse_args()
    root = project_root()
    maps_dir = root / "data" / "maps"
    output = root / "data" / "results" / "map_metrics.csv"
    output.parent.mkdir(parents=True, exist_ok=True)

    if not maps_dir.exists():
        raise SystemExit(f"Maps directory does not exist: {maps_dir}")

    ground_truth = load_gray(args.ground_truth) if args.ground_truth else None
    ground_truth_metadata = (
        metadata_for_image(args.ground_truth, args.ground_truth_yaml)
        if args.ground_truth
        else None
    )
    rows = []
    for map_path in sorted(maps_dir.glob("*.pgm")):
        case = parse_case(map_path.stem)
        if not matches_filters(case, args):
            continue
        image = load_gray(map_path)
        map_metadata = metadata_for_image(map_path)
        resolution = float(map_metadata["resolution"])
        row = {
            "map_name": map_path.stem,
            **case,
            "entropy": entropy(image),
            "ssim_raw": math.nan,
            "occupied_iou_raw": math.nan,
            "known_coverage_raw": math.nan,
            "ssim": math.nan,
            "occupied_iou": math.nan,
            "known_coverage": math.nan,
            "known_area_m2": float(known_mask(image).sum()) * resolution * resolution,
            "alignment_dx_m": math.nan,
            "alignment_dy_m": math.nan,
            "alignment_yaw_deg": math.nan,
            "alignment_status": "",
        }
        if ground_truth is not None and ground_truth_metadata is not None:
            comparable = project_to_reference(
                image,
                map_metadata,
                ground_truth.shape,
                ground_truth_metadata,
            )
            (
                row["ssim_raw"],
                row["occupied_iou_raw"],
                row["known_coverage_raw"],
            ) = comparison_metrics(
                ground_truth,
                comparable,
            )
            (
                aligned,
                row["alignment_dx_m"],
                row["alignment_dy_m"],
                row["alignment_yaw_deg"],
                row["alignment_status"],
            ) = register_map_se2(
                ground_truth,
                comparable,
                float(ground_truth_metadata["resolution"]),
                args.max_alignment_translation,
                args.max_alignment_rotation,
            )
            row["ssim"], row["occupied_iou"], row["known_coverage"] = comparison_metrics(
                ground_truth,
                aligned,
            )
        rows.append(row)

    columns = [
        "map_name",
        "system",
        "scenario",
        "run",
        "imu",
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
    ]
    result = pd.DataFrame(rows, columns=columns)
    if result.empty:
        raise SystemExit("No maps matched the selected filters")

    filters_used = args.scenario or args.run or args.imu
    if filters_used and output.exists():
        previous = pd.read_csv(output)
        existing_maps = {path.stem for path in maps_dir.glob("*.pgm")}
        previous = previous[previous["map_name"].isin(existing_maps)]
        previous = previous[~previous["map_name"].isin(result["map_name"])]
        result = pd.concat([previous, result], ignore_index=True)

    result.sort_values(["scenario", "run", "imu", "system"], na_position="last").to_csv(
        output, index=False
    )
    print(f"Saved map metrics: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
