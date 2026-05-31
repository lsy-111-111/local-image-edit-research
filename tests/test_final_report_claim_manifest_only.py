from __future__ import annotations

import csv
from pathlib import Path


def test_final_report_claims_are_manifest_allowed() -> None:
    manifest_rows = list(csv.DictReader(Path("reports/claim_manifest.csv").open(encoding="utf-8", newline="")))
    allowed_claims = {
        row["claim_text"]
        for row in manifest_rows
        if row.get("allowed_in_report", "").strip().lower() == "yes"
    }
    blocked_claims = {
        row["claim_text"]
        for row in manifest_rows
        if row.get("allowed_in_report", "").strip().lower() != "yes"
    }

    report = Path("reports/final_report_draft.md").read_text(encoding="utf-8")
    report_claims = [
        line.removeprefix("CLAIM: ").strip()
        for line in report.splitlines()
        if line.startswith("CLAIM: ")
    ]

    assert report_claims
    assert set(report_claims) <= allowed_claims
    assert not any(claim in report for claim in blocked_claims)

