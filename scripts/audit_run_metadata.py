from __future__ import annotations

import argparse
from pathlib import Path

from scripts.adapters.base import STATUSES
from scripts.common import fail_with_errors, is_missing, read_jsonl, sha256_file


REQUIRED = [
    "run_id",
    "model_id",
    "case_id",
    "source_image",
    "source_image_sha256",
    "prompt",
    "seed_requested",
    "seed_effective",
    "output_path",
    "runtime_seconds",
    "cost_usd",
    "raw_response_path",
    "status",
    "version_lock",
    "version_risk",
    "adapter",
    "adapter_name",
    "adapter_kind",
    "cost_estimate_status",
]


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    records = read_jsonl(path)
    if not records:
        errors.append(f"{path}: no metadata records")
    for index, record in enumerate(records, start=1):
        for field in REQUIRED:
            if is_missing(record.get(field)):
                errors.append(f"{path}:{index}: missing {field}")
        if str(record.get("status", "")) not in STATUSES:
            errors.append(f"{path}:{index}: invalid status {record.get('status')}")
        for numeric in ["runtime_seconds", "cost_usd"]:
            try:
                value = float(record.get(numeric, ""))
            except (TypeError, ValueError):
                errors.append(f"{path}:{index}: {numeric} must be numeric")
                continue
            if value < 0:
                errors.append(f"{path}:{index}: {numeric} must be non-negative")
        source_value = record.get("source_image", "")
        source_image = Path(str(source_value))
        if not is_missing(source_value) and source_image.is_file() and record.get("source_image_sha256") != sha256_file(source_image):
            errors.append(f"{path}:{index}: source_image_sha256 mismatch")
        mask = str(record.get("mask", ""))
        if mask and is_missing(record.get("mask_sha256")):
            errors.append(f"{path}:{index}: mask requires mask_sha256")
        if str(record.get("status")) == "success":
            output_path = Path(str(record.get("output_path", "")))
            raw_response_path = Path(str(record.get("raw_response_path", "")))
            if not output_path.exists():
                errors.append(f"{path}:{index}: output_path does not exist")
            if not raw_response_path.exists():
                errors.append(f"{path}:{index}: raw_response_path does not exist")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    args = parser.parse_args()
    fail_with_errors(validate(Path(args.input)))


if __name__ == "__main__":
    main()
