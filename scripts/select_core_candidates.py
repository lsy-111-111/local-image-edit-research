from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) != sys.path[0]:
    while str(ROOT) in sys.path:
        sys.path.remove(str(ROOT))
    sys.path.insert(0, str(ROOT))

from scripts.block_core_without_pilot import pilot_gate_go
from scripts.common import read_csv_rows, write_csv_rows


FIELDNAMES = [
    "model_id",
    "model_name",
    "family_id",
    "adapter",
    "version_lock",
    "architecture_bucket",
    "risk_flags",
    "source_url",
    "evidence_quote",
    "evidence_level",
    "last_verified_date",
    "provider_model_ref",
    "input_schema_ref",
    "review_status",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-gate", required=True)
    parser.add_argument("--pilot-metadata", default="data/runs/pilot_RUN_001.jsonl")
    parser.add_argument("--pilot-models", default="data/registry/pilot_models.csv")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if not pilot_gate_go(Path(args.pilot_gate)):
        write_csv_rows(Path(args.output), [], FIELDNAMES)
        print("pilot gate is not go; wrote empty core candidate file")
        return
    from scripts.block_core_without_pilot import metadata_has_real_adapter

    if not metadata_has_real_adapter(Path(args.pilot_metadata)):
        write_csv_rows(Path(args.output), [], FIELDNAMES)
        print("pilot metadata is empty or mock-only; wrote empty core candidate file")
        return
    rows = read_csv_rows(Path(args.pilot_models))
    allowed = [row for row in rows if "version_unlocked" not in row.get("risk_flags", "")]
    write_csv_rows(Path(args.output), allowed, FIELDNAMES)
    print(f"selected {len(allowed)} core candidates")


if __name__ == "__main__":
    main()
