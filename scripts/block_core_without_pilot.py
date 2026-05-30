from __future__ import annotations

import argparse
from pathlib import Path


def pilot_gate_go(path: Path) -> bool:
    if not path.exists():
        return False
    return "gate_decision: go" in path.read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-gate", default="reports/pilot_RUN_001_gate.md")
    args = parser.parse_args()
    if not pilot_gate_go(Path(args.pilot_gate)):
        raise SystemExit("Core is blocked: pilot gate is not go")
    print("OK")


if __name__ == "__main__":
    main()
