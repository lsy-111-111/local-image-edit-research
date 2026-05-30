from __future__ import annotations

import argparse
from pathlib import Path

from scripts.common import fail_with_errors, read_csv_rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", required=True)
    parser.add_argument("--human", required=True)
    args = parser.parse_args()
    errors = []
    metrics = read_csv_rows(Path(args.metrics))
    human = read_csv_rows(Path(args.human))
    metric_tasks = {row.get("task_id", "") for row in metrics if row.get("task_id", "")}
    human_tasks = {row.get("task_id", "") for row in human if row.get("task_id", "")}
    if metrics and human and metric_tasks != human_tasks:
        errors.append("metric and human task coverage differ; do not generate aggregate leaderboard")
    for row in human:
        if "model_name" in row or "model_id" in row:
            errors.append("blind human eval table must not include model_name or model_id")
            break
    fail_with_errors(errors)


if __name__ == "__main__":
    main()
