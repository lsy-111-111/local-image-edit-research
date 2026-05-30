from __future__ import annotations

import argparse
from pathlib import Path

from scripts.common import read_jsonl, write_csv_rows


FIELDNAMES = ["run_id", "model_id", "case_id", "task_id", "status", "error", "output_path", "raw_response_path"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    rows = [record for record in read_jsonl(Path(args.metadata)) if record.get("status") != "success"]
    write_csv_rows(Path(args.output), rows, FIELDNAMES)
    print(f"exported {len(rows)} failure cases")


if __name__ == "__main__":
    main()
