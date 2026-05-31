from __future__ import annotations

import argparse
from pathlib import Path

from scripts.common import read_jsonl, write_csv_rows


FIELDNAMES = [
    "candidate_id",
    "candidate_name",
    "candidate_label",
    "record_type",
    "source_type",
    "source_url",
    "evidence_quote",
    "evidence_level",
    "last_verified_date",
    "review_status",
    "notes",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="data/registry/raw_entries.csv")
    args = parser.parse_args()

    rows = []
    for record in read_jsonl(Path(args.input)):
        rows.append({field: record.get(field, "") for field in FIELDNAMES})
    write_csv_rows(Path(args.output), rows, FIELDNAMES)
    print(f"merged {len(rows)} records")


if __name__ == "__main__":
    main()
