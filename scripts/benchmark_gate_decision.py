from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) != sys.path[0]:
    while str(ROOT) in sys.path:
        sys.path.remove(str(ROOT))
    sys.path.insert(0, str(ROOT))

from scripts.common import ensure_parent, read_csv_rows
from scripts.validate_benchmark_cases import validate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default="data/benchmark/benchmark_cases.csv")
    parser.add_argument("--output", default="reports/benchmark_gate.md")
    parser.add_argument("--min-cases", type=int, default=100)
    parser.add_argument("--require-api-assets", action="store_true")
    parser.add_argument("--allow-no-go", action="store_true")
    args = parser.parse_args()

    path = Path(args.cases)
    errors = validate(path, min_cases=args.min_cases, require_api_assets=args.require_api_assets)
    rows = read_csv_rows(path)
    task_ids = sorted({row.get("task_id", "") for row in rows if row.get("task_id")})
    decision = "no_go" if errors else "go"
    lines = [
        "# Benchmark Gate",
        "",
        f"benchmark_gate_decision: {decision}",
        "",
        "summary:",
        f"- cases: {len(rows)}",
        f"- task_count: {len(task_ids)}",
        f"- min_cases_required: {args.min_cases}",
        f"- require_api_assets: {str(args.require_api_assets).lower()}",
        "- scope: data readiness only; this gate does not support model ranking or capability claims",
        "",
        "blocking_reasons:",
    ]
    lines.extend(f"- {error}" for error in errors)
    if not errors:
        lines.append("- none")
    out = Path(args.output)
    ensure_parent(out)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if errors and not args.allow_no_go:
        raise SystemExit(f"benchmark gate decision: {decision}")
    print(f"benchmark gate decision: {decision}")


if __name__ == "__main__":
    main()
