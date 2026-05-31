from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) != sys.path[0]:
    while str(ROOT) in sys.path:
        sys.path.remove(str(ROOT))
    sys.path.insert(0, str(ROOT))

from scripts.common import ensure_parent, read_csv_rows, read_jsonl


COUNT_RE = re.compile(r"\b(\d+)\s+(?:records?|metadata records?)\b", re.IGNORECASE)
GATE_GO_RE = re.compile(r"\b(?:pilot\s+)?gate(?:\s+decision)?\s+is\s+go\b|gate_decision:\s*go", re.IGNORECASE)
MOCK_UNSUPPORTED_CLAIM_RE = re.compile(
    r"\b(real\s+(?:model|pilot|result)|core[- ]?ready|recommend(?:s|ed)?\s+(?:model|provider)|best\s+model|"
    r"(?:rank|ranking|leaderboard)\s+(?:is|shows|selects)|outperform(?:s|ed)?)\b",
    re.IGNORECASE,
)


def gate_decision(path: Path) -> str:
    if not path.exists():
        return "missing"
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip().lower().startswith("gate_decision:"):
            return line.split(":", 1)[1].strip().lower()
    return "missing"


def valid_case_count(path: Path) -> int:
    rows = read_csv_rows(path)
    return sum(1 for row in rows if row.get("case_id") and row.get("image_path") and row.get("task_id"))


def jsonl_errors(root: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted(root.rglob("*.jsonl")):
        try:
            read_jsonl(path)
        except ValueError as exc:
            errors.append(str(exc))
    return errors


def adapter_name(record: dict[str, object]) -> str:
    return str(record.get("adapter_name") or record.get("adapter") or "").strip()


def find_claim_conflicts(manifest: Path, pilot_count: int, gate: str, mock_only: bool) -> list[dict[str, str]]:
    conflicts: list[dict[str, str]] = []
    for row in read_csv_rows(manifest):
        claim_id = row.get("claim_id", "")
        text = row.get("claim_text", "")
        allowed = row.get("allowed_in_report", "").strip().lower()
        if allowed != "yes":
            continue
        for match in COUNT_RE.finditer(text):
            claimed = int(match.group(1))
            if claimed != pilot_count:
                conflicts.append(
                    {
                        "claim_id": claim_id,
                        "reason": f"metadata count claim {claimed} != actual pilot records {pilot_count}",
                    }
                )
        if GATE_GO_RE.search(text) and gate != "go":
            conflicts.append({"claim_id": claim_id, "reason": f"pilot gate claim go != actual {gate}"})
        if GATE_GO_RE.search(text) and mock_only:
            conflicts.append({"claim_id": claim_id, "reason": "mock-only pilot cannot unlock real pilot/core"})
        if mock_only and MOCK_UNSUPPORTED_CLAIM_RE.search(text):
            conflicts.append({"claim_id": claim_id, "reason": "mock-only metadata cannot support real/result/core/ranking claim"})
    return conflicts


def write_markdown(
    output: Path,
    decision: str,
    blocking: list[str],
    warnings: list[str],
    record_counts: dict[str, int],
    claim_conflicts: list[dict[str, str]],
    jsonl_parse_errors: list[str],
) -> None:
    lines = [
        "# Repo Truth Audit",
        "",
        f"repo_truth_decision: {decision}",
        "",
        "blocking_reasons:",
    ]
    lines.extend(f"- {reason}" for reason in blocking)
    if not blocking:
        lines.append("- none")
    lines.extend(["", "warnings:"])
    lines.extend(f"- {warning}" for warning in warnings)
    if not warnings:
        lines.append("- none")
    lines.extend(["", "record_counts:"])
    for key, value in record_counts.items():
        lines.append(f"  {key}: {value}")
    lines.extend(["", "claim_conflicts:"])
    if claim_conflicts:
        for conflict in claim_conflicts:
            lines.append(f"- claim_id: {conflict['claim_id']}")
            lines.append(f"  reason: {conflict['reason']}")
    else:
        lines.append("- none")
    lines.extend(["", "jsonl_parse_errors:"])
    lines.extend(f"- {error}" for error in jsonl_parse_errors)
    if not jsonl_parse_errors:
        lines.append("- none")
    ensure_parent(output)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-metadata", required=True)
    parser.add_argument("--pilot-gate", required=True)
    parser.add_argument("--claim-manifest", required=True)
    parser.add_argument("--benchmark", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--evidence", default="data/evidence/extracted_entries.jsonl")
    parser.add_argument("--registry", default="data/registry/model_registry.jsonl")
    parser.add_argument("--final-report")
    parser.add_argument("--root", default=".")
    parser.add_argument("--allow-no-go", action="store_true")
    args = parser.parse_args()

    root = Path(args.root)
    pilot_metadata = Path(args.pilot_metadata)
    pilot_records = read_jsonl(pilot_metadata)
    pilot_count = len(pilot_records)
    benchmark_count = valid_case_count(Path(args.benchmark))
    evidence_count = len(read_jsonl(Path(args.evidence)))
    registry_count = len(read_jsonl(Path(args.registry)))
    gate = gate_decision(Path(args.pilot_gate))
    adapters = {adapter_name(record) for record in pilot_records if adapter_name(record)}
    mock_only = bool(pilot_records) and adapters <= {"mock"}
    parse_errors = jsonl_errors(root)
    claim_conflicts = find_claim_conflicts(Path(args.claim_manifest), pilot_count, gate, mock_only)

    blocking: list[str] = []
    warnings: list[str] = []
    if pilot_count == 0:
        blocking.append("no pilot metadata records")
    if mock_only:
        blocking.append("mock adapter records cannot unlock real pilot/core")
    if pilot_count == 0 and gate == "go":
        blocking.append("pilot gate go conflicts with empty pilot metadata")
    if mock_only and gate == "go":
        blocking.append("pilot gate go conflicts with mock-only pilot metadata")
    if benchmark_count < 80:
        blocking.append(f"benchmark has fewer than 80 valid cases: {benchmark_count}")
    if parse_errors:
        blocking.append("one or more JSONL files are invalid")
    if claim_conflicts:
        blocking.append("claim manifest contains conflicts with repository truth")
    if not Path(args.claim_manifest).exists():
        blocking.append("claim manifest missing")
    if args.final_report and not Path(args.final_report).exists():
        warnings.append("final report draft missing")
    if adapters == {"mock"}:
        warnings.append("adapter registry/pilot is mock-only; real adapter pilot is still required")
    record_counts = {
        "pilot_RUN_001": pilot_count,
        "benchmark_cases": benchmark_count,
        "extracted_evidence_entries": evidence_count,
        "model_registry_records": registry_count,
    }

    decision = "no_go" if blocking else "go"
    write_markdown(
        Path(args.output),
        decision,
        sorted(set(blocking)),
        sorted(set(warnings)),
        record_counts,
        claim_conflicts,
        parse_errors,
    )
    if blocking and not args.allow_no_go:
        raise SystemExit(f"repo truth decision: {decision}")
    print(f"repo truth decision: {decision}")


if __name__ == "__main__":
    main()
