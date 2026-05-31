from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from scripts.common import ensure_parent, read_csv_rows, read_jsonl


def allowed_claims(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"missing claim manifest: {path}")
    rows = [row for row in read_csv_rows(path) if row.get("allowed_in_report", "").strip().lower() == "yes"]
    if not rows:
        raise SystemExit("claim manifest has no allowed_in_report=yes rows")
    return rows


def summarize_runs(path: Path) -> list[str]:
    records = read_jsonl(path)
    if not records:
        return ["No run metadata is available."]
    adapters = {str(row.get("adapter_name") or row.get("adapter") or "").strip() for row in records}
    mock_only = bool(records) and adapters <= {"mock"}
    by_model: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        by_model[str(record.get("model_id", ""))].append(record)
    lines = [
        "mock_only_no_model_capability_claim: " + ("yes" if mock_only else "no"),
        "",
        "| model_id | adapter | cases | failures | failure_rate | cost_usd | cost_status | version_risk_records |",
        "|---|---|---:|---:|---:|---:|---|---:|",
    ]
    for model_id, rows in sorted(by_model.items()):
        total = len(rows)
        failures = sum(1 for row in rows if row.get("status") != "success")
        cost = sum(float(row.get("cost_usd", 0.0) or 0.0) for row in rows)
        model_adapters = sorted({str(row.get("adapter_name") or row.get("adapter") or "") for row in rows})
        cost_statuses = sorted({str(row.get("cost_estimate_status") or "legacy_or_unknown") for row in rows})
        version_risk_records = sum(1 for row in rows if row.get("version_risk") or row.get("version_lock") == "D_unversioned")
        lines.append(
            f"| {model_id} | {';'.join(model_adapters)} | {total} | {failures} | "
            f"{failures / total if total else 0.0:.3f} | {cost:.4f} | {';'.join(cost_statuses)} | {version_risk_records} |"
        )
    return lines


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-manifest", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    claims = allowed_claims(Path(args.claim_manifest))
    company_rows = read_csv_rows(Path("data/registry/company_product_api.csv"))
    pilot_gate = Path("reports/pilot_RUN_001_gate.md")
    core_gate = Path("reports/core_SMOKE_001_gate.md")
    gate_lines = []
    for label, path in [("pilot", pilot_gate), ("core_smoke", core_gate)]:
        decision = "missing"
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip().lower().startswith("gate_decision:"):
                    decision = line.split(":", 1)[1].strip().lower()
                    break
        gate_lines.append(f"- {label}: {decision}")
    lines = [
        "# Final Report Draft",
        "",
        "This draft is generated from repository data only. It releases no strong model capability statements without human approval.",
        "",
        "## Approved Claims",
        "",
    ]
    for row in claims:
        lines.append(f"CLAIM: {row.get('claim_text', '')}")
    lines.extend(
        [
            "",
        "## Evidence Status",
        "",
        ]
    )
    lines.extend(
        [
        "- Strong model capability claims released: 0",
        "- Missing-evidence strong claims: 0",
        "- Company/API rows present: " + str(len(company_rows)),
        "- Report mode: scaffold/no-go/needs_review unless pilot and core gates are go with real adapter metadata.",
        "",
        "## Gate Status",
        "",
        *gate_lines,
        "",
        "## Pilot Metadata Summary",
        "",
        ]
    )
    lines.extend(summarize_runs(Path("data/runs/pilot_RUN_001.jsonl")))
    lines.extend(["", "## Core Smoke Metadata Summary", ""])
    lines.extend(summarize_runs(Path("data/runs/core_SMOKE_001.jsonl")))
    lines.extend(
        [
            "",
            "## Required Risk Sections",
            "",
            "- Failure rate: reported only from run metadata tables above.",
            "- Cost: reported only from run metadata `cost_usd`; rows with `dry_run`, `legacy_or_unknown`, or `no_pricing_applied` cost status are not real cost conclusions.",
            "- Version risk: `D_unversioned` records require human review.",
            "- Blind human review: no aggregate comparison table is released unless coverage audit passes.",
            "- Evidence audit: see `reports/report_evidence_audit.csv` and `reports/missing_evidence_claims.csv`.",
        ]
    )
    out = Path(args.output)
    ensure_parent(out)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
