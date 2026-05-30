from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from scripts.common import read_jsonl, write_csv_rows


FIELDNAMES = ["model_id", "task_id", "metric_name", "metric_value", "n", "coverage_status"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    groups: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for record in read_jsonl(Path(args.metadata)):
        groups[(str(record.get("model_id", "")), str(record.get("task_id", "")))].append(record)
    rows = []
    for (model_id, task_id), records in sorted(groups.items()):
        total = len(records)
        success = sum(1 for record in records if record.get("status") == "success")
        rows.append(
            {
                "model_id": model_id,
                "task_id": task_id,
                "metric_name": "metadata_success_rate",
                "metric_value": success / total if total else 0.0,
                "n": total,
                "coverage_status": "metadata_only",
            }
        )
    write_csv_rows(Path(args.output), rows, FIELDNAMES)
    print(f"wrote {len(rows)} metric rows")


if __name__ == "__main__":
    main()
