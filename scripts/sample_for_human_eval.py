from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from scripts.common import read_jsonl, write_csv_rows


FIELDNAMES = [
    "blind_id",
    "case_id",
    "task_id",
    "output_path",
    "prompt",
    "status",
    "instruction_following_score",
    "locality_score",
    "preservation_score",
    "visual_quality_score",
    "artifact_score",
    "safety_issue",
    "failure_tags",
    "reviewer_id",
    "reviewer_notes",
]
MAPPING_FIELDS = ["blind_id", "model_id", "case_id", "task_id", "output_path", "run_id"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--sample-per-task", type=int, default=30)
    parser.add_argument("--blind", action="store_true")
    parser.add_argument("--output", required=True)
    parser.add_argument("--mapping-output", "--mapping", dest="mapping_output", default="data/eval/blind_mapping_private.csv")
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
                    "instruction_following_score": "",
                    "locality_score": "",
                    "preservation_score": "",
                    "visual_quality_score": "",
                    "artifact_score": "",
                    "safety_issue": "",
                    "failure_tags": "",
                    "reviewer_id": "",
                    "reviewer_notes": "",
                }
            )
    mapping_rows = []
    if args.blind:
        by_key = {(row["case_id"], row["task_id"], row["output_path"]): row["blind_id"] for row in rows}
        for record in read_jsonl(Path(args.metadata)):
            key = (record.get("case_id", ""), record.get("task_id", ""), record.get("output_path", ""))
            blind_id = by_key.get(key)
            if blind_id:
                mapping_rows.append(
                    {
                        "blind_id": blind_id,
                        "model_id": record.get("model_id", ""),
                        "case_id": record.get("case_id", ""),
                        "task_id": record.get("task_id", ""),
                        "output_path": record.get("output_path", ""),
                        "run_id": record.get("run_id", ""),
                    }
                )
    write_csv_rows(Path(args.output), rows, FIELDNAMES)
    if args.blind:
        write_csv_rows(Path(args.mapping_output), mapping_rows, MAPPING_FIELDS)
    print(f"wrote {len(rows)} blind review rows")


if __name__ == "__main__":
    main()
