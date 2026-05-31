from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) != sys.path[0]:
    while str(ROOT) in sys.path:
        sys.path.remove(str(ROOT))
    sys.path.insert(0, str(ROOT))

from scripts.audit_evidence import audit_records
from scripts.common import ensure_parent, evidence_missing, read_jsonl
from scripts.validate_raw_pages import validate as validate_pages


def registry_errors(path: Path) -> list[str]:
    errors: list[str] = []
    for index, row in enumerate(read_jsonl(path), start=1):
        missing = evidence_missing(row)
        if missing:
            errors.append(f"{path}:{index}: registry row missing evidence readiness fields: {', '.join(missing)}")
        if str(row.get("review_status", "")).strip() not in {"needs_review", "approved", "blocked", "engineering_review"}:
            errors.append(f"{path}:{index}: invalid review_status {row.get('review_status')}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", default="data/raw/pages.jsonl")
    parser.add_argument("--evidence", default="data/evidence/extracted_entries.jsonl")
    parser.add_argument("--registry", default="data/registry/model_registry.jsonl")
    parser.add_argument("--output", default="reports/evidence_pilot_readiness.md")
    parser.add_argument("--allow-needs-review", action="store_true")
    args = parser.parse_args()

    pages_path = Path(args.pages)
    evidence_path = Path(args.evidence)
    registry_path = Path(args.registry)
    page_errors = validate_pages(pages_path)
    evidence_records = read_jsonl(evidence_path)
    registry_records = read_jsonl(registry_path)
    evidence_errors = audit_records(evidence_records, evidence_path)
    reg_errors = registry_errors(registry_path)
    review_counts = Counter(str(row.get("review_status", "missing")).strip() or "missing" for row in evidence_records + registry_records)
    hard_errors = page_errors + evidence_errors + reg_errors
    decision = "no_go" if hard_errors else ("needs_review" if review_counts.get("needs_review", 0) else "go")
    lines = [
        "# Evidence Pilot Readiness",
        "",
        f"evidence_readiness_decision: {decision}",
        "",
        "summary:",
        f"- raw_pages: {len(read_jsonl(pages_path))}",
        f"- extracted_entries: {len(evidence_records)}",
        f"- registry_records: {len(registry_records)}",
        f"- needs_review_rows: {review_counts.get('needs_review', 0)}",
        "- scope: evidence/data readiness only; this report does not release model capability conclusions",
        "",
        "blocking_reasons:",
    ]
    lines.extend(f"- {error}" for error in hard_errors)
    if not hard_errors:
        lines.append("- none")
    ensure_parent(Path(args.output))
    Path(args.output).write_text("\n".join(lines) + "\n", encoding="utf-8")
    if hard_errors or (decision == "needs_review" and not args.allow_needs_review):
        raise SystemExit(f"evidence readiness decision: {decision}")
    print(f"evidence readiness decision: {decision}")


if __name__ == "__main__":
    main()
