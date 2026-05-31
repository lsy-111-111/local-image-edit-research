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
PROVENANCE_FIELDNAMES = [
    "asset_path",
    "asset_type",
    "copyright_status",
    "generation_method",
    "generated_by",
    "created_at",
    "sha256",
    "license_notes",
]


def header_columns(path: Path) -> list[str]:
    if not path.exists():
        return []
    first_line = path.read_text(encoding="utf-8-sig").splitlines()[0]
    return [column.strip().strip('"') for column in first_line.split(",")]


def referenced_asset_paths(rows: list[dict[str, str]]) -> set[str]:
    paths: set[str] = set()
    for row in rows:
        for field in ["image_path", "mask_path"]:
            value = row.get(field, "").strip()
            if value:
                paths.add(value)
    return paths


def validate(path: Path, min_cases: int = 1, require_api_assets: bool = False, exact_cases: int | None = None) -> list[str]:
    errors: list[str] = []
    rows = read_csv_rows(path)
    if path.exists():
        header = header_columns(path)
        for column in FIELDNAMES:
            if column not in header:
                errors.append(f"{path}: missing column {column}")
    if len(rows) < min_cases:
        errors.append(f"{path}: expected at least {min_cases} cases, found {len(rows)}")
    if exact_cases is not None and len(rows) != exact_cases:
        errors.append(f"{path}: expected exactly {exact_cases} cases, found {len(rows)}")
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
        image_path_value = row.get("image_path", "")
        image_path = Path(image_path_value)
        if is_missing(image_path_value):
            pass
        elif not image_path.exists():
            errors.append(f"{path}:{index}: image_path does not exist: {image_path}")
        elif require_api_assets and image_path.suffix.lower() not in API_IMAGE_SUFFIXES:
            errors.append(f"{path}:{index}: image_path must be PNG/JPEG/WebP for real adapters")
        elif row.get("image_sha256") != sha256_file(image_path):
            errors.append(f"{path}:{index}: image_sha256 mismatch")
        mask_path = row.get("mask_path", "")
        if not mask_path and row.get("mask_quality") != "none":
            errors.append(f"{path}:{index}: empty mask_path requires mask_quality=none")
        if mask_path and row.get("mask_quality") == "none":
            errors.append(f"{path}:{index}: mask_quality=none requires empty mask_path")
        if mask_path:
            mask_file = Path(mask_path)
            if not mask_file.exists():
                errors.append(f"{path}:{index}: mask_path does not exist: {mask_path}")
            elif require_api_assets and mask_file.suffix.lower() not in API_IMAGE_SUFFIXES:
                errors.append(f"{path}:{index}: mask_path must be PNG/JPEG/WebP for real adapters")
            elif is_missing(row.get("mask_sha256")):
                errors.append(f"{path}:{index}: mask_path requires mask_sha256")
            elif row.get("mask_sha256") != sha256_file(mask_file):
                errors.append(f"{path}:{index}: mask_sha256 mismatch")
        elif not is_missing(row.get("mask_sha256")):
            errors.append(f"{path}:{index}: empty mask_path requires empty mask_sha256")
    return errors


def validate_subset(subset_path: Path, main_path: Path, expected_cases: int = 100, require_api_assets: bool = False) -> list[str]:
    errors = validate(subset_path, min_cases=expected_cases, exact_cases=expected_cases, require_api_assets=require_api_assets)
    main_case_ids = {row.get("case_id", "") for row in read_csv_rows(main_path)}
    for index, row in enumerate(read_csv_rows(subset_path), start=2):
        case_id = row.get("case_id", "")
        if case_id not in main_case_ids:
            errors.append(f"{subset_path}:{index}: case_id {case_id} is not present in {main_path}")
    return errors


def validate_provenance_manifest(path: Path, required_assets: set[str] | None = None) -> list[str]:
    errors: list[str] = []
    rows = read_csv_rows(path)
    if not path.exists():
        return [f"{path}: provenance manifest missing"]
    header = header_columns(path)
    for column in PROVENANCE_FIELDNAMES:
        if column not in header:
            errors.append(f"{path}: missing column {column}")

    seen_assets: set[str] = set()
    for index, row in enumerate(rows, start=2):
        asset_path = row.get("asset_path", "").strip()
        seen_assets.add(asset_path)
        for field in PROVENANCE_FIELDNAMES:
            if field in {"license_notes"}:
                continue
            if is_missing(row.get(field)):
                errors.append(f"{path}:{index}: missing {field}")
        if row.get("copyright_status", "").strip().lower() == "unknown":
            errors.append(f"{path}:{index}: copyright_status=unknown is not allowed")
        file_path = Path(asset_path)
        if is_missing(asset_path):
            continue
        if not file_path.exists():
            errors.append(f"{path}:{index}: asset_path does not exist: {asset_path}")
        elif row.get("sha256", "") != sha256_file(file_path):
            errors.append(f"{path}:{index}: sha256 mismatch")

    if required_assets is not None:
        for asset in sorted(required_assets - seen_assets):
            errors.append(f"{path}: missing provenance for asset {asset}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", default="data/benchmark/benchmark_cases.csv")
    parser.add_argument("--min-cases", type=int, default=1)
    parser.add_argument("--exact-cases", type=int, default=None)
    parser.add_argument("--require-api-assets", action="store_true")
    args = parser.parse_args()
    fail_with_errors(
        validate(
            Path(args.input),
            min_cases=args.min_cases,
            exact_cases=args.exact_cases,
            require_api_assets=args.require_api_assets,
        )
    )


if __name__ == "__main__":
    main()
