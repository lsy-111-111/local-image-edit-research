from __future__ import annotations

import argparse
from pathlib import Path

from scripts.common import (
    ALLOWED_CANDIDATE_LABELS,
    A_LABELS,
    evidence_missing,
    fail_with_errors,
    read_csv_rows,
)


REQUIRED_COLUMNS = [
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


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    rows = read_csv_rows(path)
    if path.exists():
        header = path.read_text(encoding="utf-8").splitlines()[0].split(",")
        for column in REQUIRED_COLUMNS:
            if column not in header:
                errors.append(f"{path}: missing column {column}")
    for index, row in enumerate(rows, start=2):
        label = row.get("candidate_label", "").strip()
        if label not in ALLOWED_CANDIDATE_LABELS:
            errors.append(f"{path}:{index}: invalid candidate_label {label}")
        if label in A_LABELS:
            missing = evidence_missing(row)
            if missing:
                errors.append(f"{path}:{index}: {label} row missing evidence fields: {', '.join(missing)}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", default="data/registry/raw_entries.csv")
    args = parser.parse_args()
    fail_with_errors(validate(Path(args.input)))


if __name__ == "__main__":
    main()
