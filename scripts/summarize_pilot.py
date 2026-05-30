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
    by_model: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        by_model[str(record.get("model_id", ""))].append(record)

    lines = ["# Pilot Run Summary", "", "This summary is generated from run metadata only.", ""]
    lines.append("| model_id | cases | failures | failure_rate | cost_usd |")
    lines.append("|---|---:|---:|---:|---:|")
    for model_id, rows in sorted(by_model.items()):
        total = len(rows)
        failures = sum(1 for row in rows if row.get("status") != "success")
        cost = sum(float(row.get("cost_usd", 0.0) or 0.0) for row in rows)
        rate = failures / total if total else 0.0
        lines.append(f"| {model_id} | {total} | {failures} | {rate:.3f} | {cost:.4f} |")
    if not records:
        lines.append("| none | 0 | 0 | 0.000 | 0.0000 |")
    out = Path(args.output)
    ensure_parent(out)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
