from __future__ import annotations

import argparse
from pathlib import Path

from scripts.common import read_jsonl, write_csv_rows


ALLOWED_LABELS = {"A0", "A1", "A2"}
FIELDNAMES = [
    "model_id",
    "model_name",
    "family_id",
    "adapter",
    "version_lock",
    "architecture_bucket",
    "risk_flags",
    "source_url",
    "evidence_quote",
    "evidence_level",
    "last_verified_date",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--architecture", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    records = read_jsonl(Path(args.registry))
    selected = []
    seen_families = set()
    for record in records:
        record_type = str(record.get("record_type", "")).lower()
        candidate_label = str(record.get("candidate_label", "")).strip()
        family_id = str(record.get("family_id", "")).strip()
        if candidate_label and candidate_label not in ALLOWED_LABELS:
            continue
        if record_type in {"wrapper", "api_wrapper", "product", "product_feature", "demo"}:
            continue
        if family_id and family_id in seen_families:
            continue
        if family_id:
            seen_families.add(family_id)
        version_lock = str(record.get("version_lock", "")).strip()
        risk_flags = str(record.get("risk_flags", "")).strip()
        if not version_lock:
            version_lock = "D_unversioned"
            risk_flags = ";".join(part for part in [risk_flags, "version_unlocked"] if part)
        selected.append(
            {
                "model_id": record.get("model_id") or record.get("candidate_id") or f"model_{len(selected)+1}",
                "model_name": record.get("model_name") or record.get("candidate_name") or "",
                "family_id": family_id,
                "adapter": record.get("adapter", "mock"),
                "version_lock": version_lock,
                "architecture_bucket": record.get("architecture_bucket", ""),
                "risk_flags": risk_flags,
                "source_url": record.get("source_url", ""),
                "evidence_quote": record.get("evidence_quote", ""),
                "evidence_level": record.get("evidence_level", ""),
                "last_verified_date": record.get("last_verified_date", ""),
            }
        )
        if len(selected) >= 8:
            break
    write_csv_rows(Path(args.output), selected, FIELDNAMES)
    if selected and len(selected) < 5:
        print("warning: fewer than 5 pilot candidates; human review required")
    print(f"selected {len(selected)} pilot models")


if __name__ == "__main__":
    main()
