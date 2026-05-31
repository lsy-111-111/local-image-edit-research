from __future__ import annotations

import argparse
from pathlib import Path

from scripts.common import read_csv_rows, write_csv_rows


FIELDNAMES = [
    "case_id",
    "image_path",
    "image_sha256",
    "mask_path",
    "mask_sha256",
    "task_id",
    "image_type",
    "target_size",
    "mask_quality",
    "language",
    "difficulty",
    "copyright_status",
    "prompt_en",
    "prompt_zh",
    "expected_change",
    "preserve_requirements",
    "safety_notes",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/benchmark/benchmark_cases.csv")
    parser.add_argument("--output", default="data/benchmark/pilot_cases_100.csv")
    parser.add_argument("--target-count", type=int, default=100)
    args = parser.parse_args()

    rows = read_csv_rows(Path(args.input))
    if not rows:
        raise SystemExit("cannot build pilot cases from an empty benchmark case file")
    output = []
    index = 0
    while len(output) < args.target_count:
        source = dict(rows[index % len(rows)])
        if len(output) >= len(rows):
            source["case_id"] = f"{source.get('case_id', 'case')}_pilot_repeat_{(len(output) // len(rows)) + 1:02d}"
            source["safety_notes"] = "; ".join(
                part for part in [source.get("safety_notes", ""), "pilot repeat uses the same synthetic asset with a distinct case_id"] if part
            )
        output.append(source)
        index += 1
    write_csv_rows(Path(args.output), output, FIELDNAMES)
    print(f"built {len(output)} pilot cases")


if __name__ == "__main__":
    main()
