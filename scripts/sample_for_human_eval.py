from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from scripts.common import read_jsonl, write_csv_rows


FIELDNAMES = ["blind_id", "case_id", "task_id", "output_path", "prompt", "status"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--sample-per-task", type=int, default=30)
    parser.add_argument("--blind", action="store_true")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    by_task: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in read_jsonl(Path(args.metadata)):
        by_task[str(record.get("task_id", ""))].append(record)
    rows = []
    for task_id, records in sorted(by_task.items()):
        for record in records[: args.sample_per_task]:
            rows.append(
                {
                    "blind_id": f"blind_{len(rows)+1:06d}",
                    "case_id": record.get("case_id", ""),
                    "task_id": task_id,
                    "output_path": record.get("output_path", ""),
                    "prompt": record.get("prompt", ""),
                    "status": record.get("status", ""),
                }
            )
    write_csv_rows(Path(args.output), rows, FIELDNAMES)
    print(f"wrote {len(rows)} blind review rows")


if __name__ == "__main__":
    main()
