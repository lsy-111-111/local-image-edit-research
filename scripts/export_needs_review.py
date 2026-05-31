from __future__ import annotations

import argparse
from pathlib import Path

from scripts.common import A_LABELS, evidence_missing, read_jsonl, write_csv_rows


FIELDNAMES = [
    "entry_id",
    "candidate_id",
    "candidate_name",
    "candidate_label",
    "record_type",
    "review_reason",
    "source_type",
    "source_url",
    "evidence_quote",
    "evidence_quote_context",
    "evidence_level",
    "last_verified_date",
    "review_status",
    "notes",
]
HUMAN_REVIEW_FIELDNAMES = [
    "entry_id",
    "reviewer",
    "review_status",
    "decision",
    "decision_reason",
    "reviewed_at",
    "allowed_for_registry",
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


def entry_id(record: dict[str, object], index: int) -> str:
    return str(record.get("entry_id") or record.get("candidate_id") or f"entry_{index:04d}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--review-queue")
    parser.add_argument("--human-review")
    args = parser.parse_args()
    rows = []
    human_review_rows = []
    for index, record in enumerate(read_jsonl(Path(args.input)), start=1):
        reason = review_reason(record)
        if reason:
            current_entry_id = entry_id(record, index)
            rows.append({**record, "entry_id": current_entry_id, "review_reason": reason})
            human_review_rows.append(
                {
                    "entry_id": current_entry_id,
                    "reviewer": "",
                    "review_status": "needs_review",
                    "decision": "pending",
                    "decision_reason": "",
                    "reviewed_at": "",
                    "allowed_for_registry": "no",
                }
            )
    write_csv_rows(Path(args.output), rows, FIELDNAMES)
    if args.review_queue:
        write_csv_rows(Path(args.review_queue), rows, FIELDNAMES)
    if args.human_review:
        write_csv_rows(Path(args.human_review), human_review_rows, HUMAN_REVIEW_FIELDNAMES)
    print(f"exported {len(rows)} needs-review records")


if __name__ == "__main__":
    main()
