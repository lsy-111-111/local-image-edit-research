from __future__ import annotations

import argparse
from pathlib import Path

from scripts.common import read_jsonl


def gate_decision(path: Path) -> str:
    if not path.exists():
        return "missing"
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if text.lower().startswith("gate_decision:"):
            return text.split(":", 1)[1].strip().lower()
    return "missing"


def pilot_gate_go(path: Path) -> bool:
    return gate_decision(path) == "go"


def metadata_has_real_adapter(path: Path) -> bool:
    records = read_jsonl(path)
    if not records:
        return False
    adapters = {str(row.get("adapter_name") or row.get("adapter") or "").strip() for row in records}
    adapters.discard("")
    return bool(adapters) and "mock" not in adapters


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-gate", default="reports/pilot_RUN_001_gate.md")
    parser.add_argument("--pilot-metadata", default="data/runs/pilot_RUN_001.jsonl")
    args = parser.parse_args()
    if not pilot_gate_go(Path(args.pilot_gate)):
        raise SystemExit("Core is blocked: pilot gate is not go")
    if not metadata_has_real_adapter(Path(args.pilot_metadata)):
        raise SystemExit("Core is blocked: pilot metadata is empty or mock-only")
    print("OK")


if __name__ == "__main__":
    main()
