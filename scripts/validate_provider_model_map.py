from __future__ import annotations

import argparse
from pathlib import Path

from scripts.common import fail_with_errors, is_missing, read_csv_rows, valid_iso_date


REQUIRED_COLUMNS = [
    "model_id",
    "adapter",
    "provider_model_ref",
    "input_schema_ref",
    "version_lock",
    "source_url",
    "evidence_quote",
    "evidence_level",
    "last_verified_date",
    "review_status",
]
ALLOWED_ADAPTERS = {"openai_images", "replicate"}
ALLOWED_SCHEMAS = {"openai_images_edit_json", "replicate_image_prompt", "replicate_image_mask_prompt"}
ALLOWED_REVIEW = {"approved", "needs_review", "blocked"}


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    rows = read_csv_rows(path)
    if not rows:
        return [f"{path}: provider model map is empty"]
    header = list(rows[0].keys())
    for column in REQUIRED_COLUMNS:
        if column not in header:
            errors.append(f"{path}: missing column {column}")
    seen: set[str] = set()
    for index, row in enumerate(rows, start=2):
        model_id = row.get("model_id", "")
        if is_missing(model_id):
            errors.append(f"{path}:{index}: missing model_id")
        if model_id in seen:
            errors.append(f"{path}:{index}: duplicate model_id {model_id}")
        seen.add(model_id)
        if row.get("adapter") not in ALLOWED_ADAPTERS:
            errors.append(f"{path}:{index}: invalid adapter {row.get('adapter')}")
        if row.get("input_schema_ref") not in ALLOWED_SCHEMAS:
            errors.append(f"{path}:{index}: invalid input_schema_ref {row.get('input_schema_ref')}")
        for field in ["provider_model_ref", "version_lock", "source_url", "evidence_quote", "evidence_level", "last_verified_date"]:
            if is_missing(row.get(field)):
                errors.append(f"{path}:{index}: missing {field}")
        if not is_missing(row.get("last_verified_date")) and not valid_iso_date(row.get("last_verified_date")):
            errors.append(f"{path}:{index}: invalid last_verified_date")
        if row.get("review_status") not in ALLOWED_REVIEW:
            errors.append(f"{path}:{index}: invalid review_status {row.get('review_status')}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", default="data/registry/provider_model_map.csv")
    args = parser.parse_args()
    fail_with_errors(validate(Path(args.input)))


if __name__ == "__main__":
    main()
