from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from scripts.common import ensure_parent, read_jsonl


def adapter_name(record: dict[str, object]) -> str:
    return str(record.get("adapter_name") or record.get("adapter") or "").strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    records = read_jsonl(Path(args.metadata))
    reasons = []
    decision = "go"
    if not records:
        decision = "no_go"
        reasons.append("no pilot metadata records")
    adapters = {adapter_name(record) for record in records if adapter_name(record)}
    if records and adapters <= {"mock"}:
        decision = "no_go"
        reasons.append("mock adapter records cannot unlock real pilot/core")
    if "mock" in adapters and len(adapters) > 1:
        decision = "no_go"
        reasons.append("pilot metadata mixes mock and real adapter records")

    by_model: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        by_model[str(record.get("model_id", ""))].append(record)

    if records and not (5 <= len(by_model) <= 8):
        decision = "no_go"
        reasons.append("pilot must include 5-8 models")
    for model_id, rows in by_model.items():
        if not (100 <= len(rows) <= 300):
            decision = "no_go"
            reasons.append(f"{model_id}: pilot case count must be 100-300")
        failures = sum(1 for row in rows if row.get("status") != "success")
        if rows and failures / len(rows) > 0.40:
            decision = "no_go"
            reasons.append(f"{model_id}: failure_rate_high")
        for row in rows:
            missing = [
                field
                for field in ["source_image", "prompt", "output_path", "raw_response_path", "adapter", "version_lock"]
                if not row.get(field)
            ]
            if missing:
                decision = "no_go"
                reasons.append(f"{model_id}/{row.get('case_id')}: metadata_missing:{'|'.join(missing)}")
                break

    lines = ["# Pilot Gate Decision", "", f"gate_decision: {decision}", ""]
    if reasons:
        lines.extend(["## Blocking Reasons", ""])
        lines.extend(f"- {reason}" for reason in sorted(set(reasons)))
    else:
        lines.append("Pilot metadata passed the implemented engineering gate. Human factual review is still required.")
    out = Path(args.output)
    ensure_parent(out)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"pilot gate: {decision}")


if __name__ == "__main__":
    main()
