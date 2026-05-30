from __future__ import annotations

import argparse
from pathlib import Path

from scripts.common import is_missing, read_jsonl, split_values, write_csv_rows


FIELDNAMES = [
    "model_id",
    "review_reason",
    "base_architecture",
    "control_mechanism",
    "training_or_inference",
    "deployment",
    "architecture_public",
    "source_url",
    "evidence_quote",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    rows = []
    for record in read_jsonl(Path(args.input)):
        reasons = []
        for field in ["base_architecture", "control_mechanism", "training_or_inference", "deployment"]:
            if "unknown" in split_values(record.get(field)):
                reasons.append(f"{field}:unknown")
        has_non_unknown = any(
            value != "unknown"
            for field in ["base_architecture", "control_mechanism", "training_or_inference", "deployment"]
            for value in split_values(record.get(field))
        )
        if has_non_unknown and is_missing(record.get("evidence_quote")):
            reasons.append("missing_evidence_quote")
        if reasons:
            rows.append({**record, "review_reason": ";".join(reasons)})
    write_csv_rows(Path(args.output), rows, FIELDNAMES)
    print(f"exported {len(rows)} architecture review records")


if __name__ == "__main__":
    main()
