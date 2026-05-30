from __future__ import annotations

import argparse
from pathlib import Path

from scripts.common import is_missing, read_csv_rows, write_csv_rows


FIELDNAMES = [
    "company",
    "product",
    "public_model_name",
    "underlying_model",
    "review_reason",
    "source_url",
    "evidence_quote",
    "evidence_level",
    "last_verified_date",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    rows = []
    for row in read_csv_rows(Path(args.input)):
        reasons = []
        if row.get("underlying_model") == "unknown":
            reasons.append("underlying_model_unknown")
        for field in ["source_url", "evidence_quote", "evidence_level", "last_verified_date"]:
            if is_missing(row.get(field)):
                reasons.append(f"missing_{field}")
        if str(row.get("evidence_level", "")).strip() in {"E4", "E5"}:
            reasons.append("weak_evidence")
        if reasons:
            rows.append({**row, "review_reason": ";".join(reasons)})
    write_csv_rows(Path(args.output), rows, FIELDNAMES)
    print(f"exported {len(rows)} company review records")


if __name__ == "__main__":
    main()
