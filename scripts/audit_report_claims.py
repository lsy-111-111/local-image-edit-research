from __future__ import annotations

import argparse
import csv
from pathlib import Path

from scripts.common import ensure_parent


AUDIT_FIELDS = ["line_no", "claim", "status", "evidence_ref", "notes"]


def audit(report_path: Path) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    audit_rows: list[dict[str, str]] = []
    missing_rows: list[dict[str, str]] = []
    if not report_path.exists():
        missing_rows.append({"line_no": "0", "claim": "report_missing", "status": "missing", "evidence_ref": "", "notes": str(report_path)})
        return audit_rows, missing_rows
    for line_no, line in enumerate(report_path.read_text(encoding="utf-8").splitlines(), start=1):
        text = line.strip()
        if not text.startswith("CLAIM:"):
            continue
        has_evidence = ("source_url=" in text and "evidence_quote=" in text) or "run_metadata=" in text or "eval_metadata=" in text
        row = {
            "line_no": str(line_no),
            "claim": text.removeprefix("CLAIM:").strip(),
            "status": "pass" if has_evidence else "missing",
            "evidence_ref": "present" if has_evidence else "",
            "notes": "",
        }
        audit_rows.append(row)
        if not has_evidence:
            missing_rows.append(row)
    return audit_rows, missing_rows


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=AUDIT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--missing", required=True)
    args = parser.parse_args()
    audit_rows, missing_rows = audit(Path(args.report))
    write_rows(Path(args.output), audit_rows)
    write_rows(Path(args.missing), missing_rows)
    if missing_rows:
        raise SystemExit(f"missing evidence for {len(missing_rows)} report claims")
    print("OK")


if __name__ == "__main__":
    main()
