from __future__ import annotations

import argparse
from pathlib import Path

from scripts.common import fail_with_errors, is_missing, read_csv_rows, read_jsonl, split_values


BLOCKED_FAMILY_TYPES = {
    "wrapper",
    "api_wrapper",
    "api wrapper",
    "product",
    "product_feature",
    "product feature",
    "demo",
    "implementation",
}
ARCH_FIELDS = ["base_architecture", "control_mechanism", "training_or_inference", "deployment"]


def validate_model_family(path: Path) -> list[str]:
    errors: list[str] = []
    for index, row in enumerate(read_csv_rows(path), start=2):
        family_type = row.get("family_type", "").strip().lower()
        if family_type in BLOCKED_FAMILY_TYPES:
            errors.append(f"{path}:{index}: {family_type} must not be registered as model_family")
    return errors


def validate_model_registry(path: Path) -> list[str]:
    errors: list[str] = []
    for index, record in enumerate(read_jsonl(path), start=1):
        record_type = str(record.get("record_type", "")).strip().lower()
        family_kind = str(record.get("family_type", "")).strip().lower()
        if record_type in BLOCKED_FAMILY_TYPES and str(record.get("is_model_family", "")).lower() in {"true", "1", "yes"}:
            errors.append(f"{path}:{index}: {record_type} must not be counted as independent model family")
        if family_kind in BLOCKED_FAMILY_TYPES:
            errors.append(f"{path}:{index}: family_type {family_kind} is not allowed")
    return errors


def validate_architecture(path: Path) -> list[str]:
    errors: list[str] = []
    for index, record in enumerate(read_jsonl(path), start=1):
        needs_evidence = False
        for field in ARCH_FIELDS:
            for value in split_values(record.get(field)):
                if value != "unknown":
                    needs_evidence = True
        if needs_evidence and is_missing(record.get("evidence_quote")):
            errors.append(f"{path}:{index}: non-unknown architecture label requires evidence_quote")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-family", default="data/registry/model_family.csv")
    parser.add_argument("--model-registry", default="data/registry/model_registry.jsonl")
    parser.add_argument("--architecture", default="data/registry/architecture_labels.jsonl")
    args = parser.parse_args()
    errors: list[str] = []
    errors.extend(validate_model_family(Path(args.model_family)))
    errors.extend(validate_model_registry(Path(args.model_registry)))
    errors.extend(validate_architecture(Path(args.architecture)))
    fail_with_errors(errors)


if __name__ == "__main__":
    main()
