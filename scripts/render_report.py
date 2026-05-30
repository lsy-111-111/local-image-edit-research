from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from scripts.common import ensure_parent, read_csv_rows, read_jsonl


def summarize_runs(path: Path) -> list[str]:
    records = read_jsonl(path)
    if not records:
        return ["No run metadata is available."]
    by_model: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        by_model[str(record.get("model_id", ""))].append(record)
    lines = ["| model_id | cases | failures | failure_rate | cost_usd |", "|---|---:|---:|---:|---:|"]
    for model_id, rows in sorted(by_model.items()):
        total = len(rows)
        failures = sum(1 for row in rows if row.get("status") != "success")
        cost = sum(float(row.get("cost_usd", 0.0) or 0.0) for row in rows)
        lines.append(f"| {model_id} | {total} | {failures} | {failures / total if total else 0.0:.3f} | {cost:.4f} |")
    return lines


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    company_rows = read_csv_rows(Path("data/registry/company_product_api.csv"))
    lines = [
        "# Final Report Draft",
        "",
        "This draft is generated from repository data only. It releases no strong model capability conclusions without human approval.",
        "",
        "## Evidence Status",
        "",
        "- Strong claims released: 0",
        "- Missing-evidence strong claims: 0",
        "- Company/API rows present: " + str(len(company_rows)),
        "",
        "## Pilot Metadata Summary",
        "",
    ]
    lines.extend(summarize_runs(Path("data/runs/pilot_RUN_001.jsonl")))
    lines.extend(["", "## Core Smoke Metadata Summary", ""])
    lines.extend(summarize_runs(Path("data/runs/core_SMOKE_001.jsonl")))
    lines.extend(
        [
            "",
            "## Required Risk Sections",
            "",
            "- Failure rate: reported only from run metadata tables above.",
            "- Cost: reported only from run metadata `cost_usd`.",
            "- Version risk: `D_unversioned` records require human review.",
            "- Blind human review: no aggregate leaderboard is released unless coverage audit passes.",
            "- Evidence audit: see `reports/report_evidence_audit.csv` and `reports/missing_evidence_claims.csv`.",
        ]
    )
    out = Path(args.output)
    ensure_parent(out)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
