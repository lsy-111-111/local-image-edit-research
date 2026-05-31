from __future__ import annotations

import argparse
from pathlib import Path

from scripts.common import fail_with_errors, is_missing, read_csv_rows, sha256_file


FIELDNAMES = [
    "case_id",
    "image_path",
    "image_sha256",
    "mask_path",
    "mask_sha256",
    "task_id",
    "image_type",
    "target_size",
    "mask_quality",
    "language",
    "difficulty",
    "copyright_status",
    "prompt_en",
    "prompt_zh",
    "expected_change",
    "preserve_requirements",
    "safety_notes",
]
TASK_IDS = {f"T{i:02d}" for i in range(1, 17)}
API_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


def validate(path: Path, min_cases: int = 1, require_api_assets: bool = False) -> list[str]:
    errors: list[str] = []
    rows = read_csv_rows(path)
    if path.exists():
        header = path.read_text(encoding="utf-8").splitlines()[0].split(",")
        for column in FIELDNAMES:
            if column not in header:
                errors.append(f"{path}: missing column {column}")
    if len(rows) < min_cases:
        errors.append(f"{path}: expected at least {min_cases} cases, found {len(rows)}")
    seen_case_ids: set[str] = set()
    seen_rows: set[tuple[str, ...]] = set()
    for index, row in enumerate(rows, start=2):
        case_id = row.get("case_id", "")
        if case_id in seen_case_ids:
            errors.append(f"{path}:{index}: duplicate case_id {case_id}")
        seen_case_ids.add(case_id)
        row_fingerprint = tuple(row.get(field, "") for field in FIELDNAMES if field != "case_id")
        if row_fingerprint in seen_rows:
            errors.append(f"{path}:{index}: duplicate benchmark row content")
        seen_rows.add(row_fingerprint)
        for field in ["case_id", "image_path", "image_sha256", "task_id", "copyright_status", "expected_change", "preserve_requirements"]:
            if is_missing(row.get(field)):
                errors.append(f"{path}:{index}: missing {field}")
        if row.get("task_id") not in TASK_IDS:
            errors.append(f"{path}:{index}: invalid task_id {row.get('task_id')}")
        if row.get("copyright_status") == "unknown":
            errors.append(f"{path}:{index}: copyright_status=unknown is not allowed in benchmark cases")
        image_path = Path(row.get("image_path", ""))
        if require_api_assets and image_path.suffix.lower() not in API_IMAGE_SUFFIXES:
            errors.append(f"{path}:{index}: image_path must be PNG/JPEG/WebP for real adapters")
        if image_path.exists() and row.get("image_sha256") != sha256_file(image_path):
            errors.append(f"{path}:{index}: image_sha256 mismatch")
        mask_path = row.get("mask_path", "")
        if not mask_path and row.get("mask_quality") != "none":
            errors.append(f"{path}:{index}: empty mask_path requires mask_quality=none")
        if mask_path and row.get("mask_quality") == "none":
            errors.append(f"{path}:{index}: mask_quality=none requires empty mask_path")
        if mask_path:
            if require_api_assets and Path(mask_path).suffix.lower() not in API_IMAGE_SUFFIXES:
                errors.append(f"{path}:{index}: mask_path must be PNG/JPEG/WebP for real adapters")
            if is_missing(row.get("mask_sha256")):
                errors.append(f"{path}:{index}: mask_path requires mask_sha256")
            elif Path(mask_path).exists() and row.get("mask_sha256") != sha256_file(Path(mask_path)):
                errors.append(f"{path}:{index}: mask_sha256 mismatch")
        elif not is_missing(row.get("mask_sha256")):
            errors.append(f"{path}:{index}: empty mask_path requires empty mask_sha256")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", default="data/benchmark/benchmark_cases.csv")
    parser.add_argument("--min-cases", type=int, default=1)
    parser.add_argument("--require-api-assets", action="store_true")
    args = parser.parse_args()
    fail_with_errors(validate(Path(args.input), min_cases=args.min_cases, require_api_assets=args.require_api_assets))


if __name__ == "__main__":
    main()
