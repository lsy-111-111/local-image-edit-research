from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from scripts.common import ensure_parent, read_csv_rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", required=True)
    parser.add_argument("--human", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    metric_rows = read_csv_rows(Path(args.metrics))
    human_rows = read_csv_rows(Path(args.human))
    by_task: dict[str, list[dict[str, str]]] = defaultdict(list)
    human_by_task: dict[str, int] = defaultdict(int)
    for row in metric_rows:
        by_task[row.get("task_id", "")].append(row)
    for row in human_rows:
        human_by_task[row.get("task_id", "")] += 1

    lines = [
        "# Pilot Eval Task-Level Summary",
        "",
        "mock_only_no_model_capability_claim: yes",
        "",
        "No aggregate leaderboard is generated.",
        "",
        "| task_id | metric_rows | human_eval_rows | coverage_status |",
        "|---|---:|---:|---|",
    ]
    for task_id in sorted(set(by_task) | set(human_by_task)):
        statuses = sorted({row.get("coverage_status", "") for row in by_task.get(task_id, []) if row.get("coverage_status", "")})
        lines.append(f"| {task_id} | {len(by_task.get(task_id, []))} | {human_by_task.get(task_id, 0)} | {';'.join(statuses) or 'none'} |")

    out = Path(args.output)
    ensure_parent(out)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
