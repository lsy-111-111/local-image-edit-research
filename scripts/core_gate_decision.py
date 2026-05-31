from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from scripts.common import ensure_parent, read_jsonl


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    records = read_jsonl(Path(args.metadata))
    decision = "go"
    reasons = []
    if not records:
        decision = "no_go"
        reasons.append("no core smoke metadata records")
    adapters = {str(row.get("adapter_name") or row.get("adapter") or "").strip() for row in records}
    adapters.discard("")
    if records and ("mock" in adapters or not adapters):
        decision = "no_go"
        reasons.append("core smoke requires real adapter metadata")
    if records and len({row.get("case_id") for row in records}) != 100:
        decision = "no_go"
        reasons.append("core smoke must cover exactly 100 cases before expansion")
    by_model: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        by_model[str(record.get("model_id", ""))].append(record)
        if record.get("version_lock") == "D_unversioned":
            reasons.append(f"{record.get('model_id')}: version_unlocked")
        for field in ["source_image", "prompt", "output_path", "raw_response_path"]:
            if not record.get(field):
                reasons.append(f"{record.get('model_id')}/{record.get('case_id')}: metadata_missing")
    for model_id, rows in by_model.items():
        failures = sum(1 for row in rows if row.get("status") != "success")
        if rows and failures / len(rows) > 0.40:
            decision = "no_go"
            reasons.append(f"{model_id}: failure_rate_high")
    if any("version_unlocked" in reason or "metadata_missing" in reason for reason in reasons):
        decision = "no_go"
    lines = ["# Core Smoke Gate Decision", "", f"gate_decision: {decision}", ""]
    if reasons:
        lines.extend(["## Flags", ""])
        lines.extend(f"- {reason}" for reason in sorted(set(reasons)))
    else:
        lines.append("Core smoke metadata passed the implemented engineering gate. Human review is still required before expansion.")
    out = Path(args.output)
    ensure_parent(out)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"core gate: {decision}")


if __name__ == "__main__":
    main()
