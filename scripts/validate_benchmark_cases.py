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


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    if path.exists():
        header = path.read_text(encoding="utf-8").splitlines()[0].split(",")
        for column in FIELDNAMES:
            if column not in header:
                errors.append(f"{path}: missing column {column}")
    for index, row in enumerate(read_csv_rows(path), start=2):
        for field in ["case_id", "image_path", "image_sha256", "task_id", "copyright_status", "expected_change", "preserve_requirements"]:
            if is_missing(row.get(field)):
                errors.append(f"{path}:{index}: missing {field}")
        if row.get("task_id") not in TASK_IDS:
            errors.append(f"{path}:{index}: invalid task_id {row.get('task_id')}")
        if row.get("copyright_status") == "unknown":
            errors.append(f"{path}:{index}: copyright_status=unknown is not allowed in benchmark cases")
        image_path = Path(row.get("image_path", ""))
        if image_path.exists() and row.get("image_sha256") != sha256_file(image_path):
            errors.append(f"{path}:{index}: image_sha256 mismatch")
        mask_path = row.get("mask_path", "")
        if mask_path:
            if is_missing(row.get("mask_sha256")):
                errors.append(f"{path}:{index}: mask_path requires mask_sha256")
            elif Path(mask_path).exists() and row.get("mask_sha256") != sha256_file(Path(mask_path)):
                errors.append(f"{path}:{index}: mask_sha256 mismatch")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", default="data/benchmark/benchmark_cases.csv")
    args = parser.parse_args()
    fail_with_errors(validate(Path(args.input)))


if __name__ == "__main__":
    main()
