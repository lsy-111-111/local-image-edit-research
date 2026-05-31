from __future__ import annotations

import argparse
from pathlib import Path

from scripts.common import (
    ALLOWED_CANDIDATE_LABELS,
    A_LABELS,
    evidence_missing,
    fail_with_errors,
    read_jsonl,
)


def audit_records(records: list[dict[str, object]], source: Path) -> list[str]:
    errors: list[str] = []
    for index, record in enumerate(records, start=1):
        label = str(record.get("candidate_label", "")).strip()
        name = str(record.get("candidate_name", f"record_{index}"))
        if label not in ALLOWED_CANDIDATE_LABELS:
            errors.append(f"{source}:{index}: invalid candidate_label for {name}: {label}")
        if str(record.get("source_type", "")).strip() not in {
            "official_docs",
            "official_model_card",
            "official_api_docs",
            "paper",
            "official_github",
            "release_note",
        }:
            errors.append(f"{source}:{index}: invalid source_type for {name}: {record.get('source_type')}")
        if label in A_LABELS:
            missing = evidence_missing(record)
            if not str(record.get("evidence_quote_context", "")).strip():
                missing.append("evidence_quote_context")
            if missing:
                errors.append(f"{source}:{index}: {label} record {name} missing evidence fields: {', '.join(missing)}")
            if str(record.get("review_status", "")).strip() != "needs_review":
                errors.append(f"{source}:{index}: {label} record {name} must default to review_status=needs_review")
        if str(record.get("claim_strength", "")).lower() in {"strong", "high"}:
            if str(record.get("evidence_level", "")).strip() in {"E4", "E5"}:
                errors.append(f"{source}:{index}: E4/E5 evidence cannot support strong claim for {name}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", default="data/evidence/extracted_entries.jsonl")
    args = parser.parse_args()
    path = Path(args.input)
    records = read_jsonl(path)
    fail_with_errors(audit_records(records, path))


if __name__ == "__main__":
    main()
