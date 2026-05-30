from __future__ import annotations

import argparse
from pathlib import Path

from scripts.common import read_jsonl, write_jsonl


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    suggestions = []
    for record in read_jsonl(Path(args.input)):
        record_type = str(record.get("record_type", "")).strip().lower()
        suggestion = {
            "candidate_id": record.get("candidate_id", ""),
            "candidate_name": record.get("candidate_name", ""),
            "record_type": record.get("record_type", ""),
            "suggested_family_id": "",
            "duplicate_status": "needs_review",
            "duplicate_reason": "no automatic merge; human evidence review required",
            "source_url": record.get("source_url", ""),
            "evidence_quote": record.get("evidence_quote", ""),
        }
        if record_type in {"api_wrapper", "wrapper", "product_feature", "product", "demo", "implementation"}:
            suggestion["duplicate_reason"] = f"{record_type} must not be counted as an independent model family"
        suggestions.append(suggestion)
    write_jsonl(Path(args.output), suggestions)
    print(f"wrote {len(suggestions)} dedupe suggestions")


if __name__ == "__main__":
    main()
