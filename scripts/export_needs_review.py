from __future__ import annotations

import argparse
from pathlib import Path

from scripts.common import A_LABELS, evidence_missing, read_jsonl, write_csv_rows


FIELDNAMES = [
    "candidate_id",
    "candidate_name",
    "candidate_label",
    "record_type",
    "review_reason",
    "source_url",
    "evidence_quote",
    "evidence_level",
    "last_verified_date",
    "notes",
]


def review_reason(record: dict[str, object]) -> str:
    reasons: list[str] = []
    if str(record.get("review_status", "")).strip() == "needs_review":
        reasons.append("review_status")
    if str(record.get("candidate_label", "")).strip() in A_LABELS:
        missing = evidence_missing(record)
        if missing:
            reasons.append("missing_evidence:" + "|".join(missing))
    if str(record.get("candidate_label", "")).strip() == "X":
        reasons.append("excluded_or_unknown")
    return ";".join(reasons)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    rows = []
    for record in read_jsonl(Path(args.input)):
        reason = review_reason(record)
        if reason:
            rows.append({**record, "review_reason": reason})
    write_csv_rows(Path(args.output), rows, FIELDNAMES)
    print(f"exported {len(rows)} needs-review records")


if __name__ == "__main__":
    main()
