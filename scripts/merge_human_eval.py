from __future__ import annotations

import argparse
from pathlib import Path

from scripts.common import read_csv_rows, write_csv_rows


FIELDNAMES = ["blind_id", "case_id", "task_id", "output_path", "human_score", "failure_tags", "reviewer_notes"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    rows = []
    for row in read_csv_rows(Path(args.input)):
        rows.append({field: row.get(field, "") for field in FIELDNAMES})
    write_csv_rows(Path(args.output), rows, FIELDNAMES)
    print(f"merged {len(rows)} human eval rows")


if __name__ == "__main__":
    main()
