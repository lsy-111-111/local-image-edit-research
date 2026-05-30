from __future__ import annotations

import argparse
from pathlib import Path

from scripts.common import fail_with_errors, is_missing, read_csv_rows, valid_iso_date


FIELDNAMES = [
    "company",
    "product",
    "public_model_name",
    "underlying_model",
    "capability",
    "input_mode",
    "api_available",
    "batch_available",
    "version_lock",
    "pricing",
    "rate_limit",
    "watermark",
    "content_policy_effect",
    "architecture_public",
    "evidence_level",
    "source_url",
    "evidence_quote",
    "test_level",
    "last_verified_date",
]


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    if path.exists():
        header = path.read_text(encoding="utf-8").splitlines()[0].split(",")
        for column in FIELDNAMES:
            if column not in header:
                errors.append(f"{path}: missing column {column}")
    for index, row in enumerate(read_csv_rows(path), start=2):
        has_fact = any(not is_missing(row.get(field)) for field in ["capability", "api_available", "pricing", "rate_limit"])
        if has_fact:
            for field in ["source_url", "evidence_quote", "evidence_level", "last_verified_date"]:
                if is_missing(row.get(field)):
                    errors.append(f"{path}:{index}: factual product/API row missing {field}")
        if not is_missing(row.get("last_verified_date")) and not valid_iso_date(row.get("last_verified_date")):
            errors.append(f"{path}:{index}: invalid last_verified_date")
        if str(row.get("evidence_level", "")).strip() in {"E4", "E5"} and str(row.get("test_level", "")).lower() in {"strong", "conclusion"}:
            errors.append(f"{path}:{index}: E4/E5 evidence cannot support strong company/API conclusion")
        if is_missing(row.get("underlying_model")):
            errors.append(f"{path}:{index}: unknown underlying model must be written as unknown")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", default="data/registry/company_product_api.csv")
    args = parser.parse_args()
    fail_with_errors(validate(Path(args.input)))


if __name__ == "__main__":
    main()
