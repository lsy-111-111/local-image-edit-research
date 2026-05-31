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
from scripts.validate_benchmark_cases import referenced_asset_paths, validate, validate_provenance_manifest, validate_subset


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default="data/benchmark/benchmark_cases.csv")
    parser.add_argument("--pilot-cases")
    parser.add_argument("--core-cases")
    parser.add_argument("--provenance")
    parser.add_argument("--output", default="reports/benchmark_gate.md")
    parser.add_argument("--min-cases", type=int, default=80)
    parser.add_argument("--require-api-assets", action="store_true")
    parser.add_argument("--allow-no-go", action="store_true")
    args = parser.parse_args()

    path = Path(args.cases)
    errors = validate(path, min_cases=args.min_cases, require_api_assets=args.require_api_assets)
    rows = read_csv_rows(path)
    task_ids = sorted({row.get("task_id", "") for row in rows if row.get("task_id")})
    pilot_count = ""
    core_count = ""
    if args.pilot_cases:
        pilot_path = Path(args.pilot_cases)
        errors.extend(validate_subset(pilot_path, path, expected_cases=100, require_api_assets=args.require_api_assets))
        pilot_count = str(len(read_csv_rows(pilot_path)))
    if args.core_cases:
        core_path = Path(args.core_cases)
        errors.extend(validate_subset(core_path, path, expected_cases=100, require_api_assets=args.require_api_assets))
        core_count = str(len(read_csv_rows(core_path)))
    if args.provenance:
        required_assets = referenced_asset_paths(rows)
        if args.pilot_cases:
            required_assets |= referenced_asset_paths(read_csv_rows(Path(args.pilot_cases)))
        if args.core_cases:
            required_assets |= referenced_asset_paths(read_csv_rows(Path(args.core_cases)))
        errors.extend(validate_provenance_manifest(Path(args.provenance), required_assets=required_assets))
    decision = "no_go" if errors else "go"
    lines = [
        "# Benchmark Gate",
        "",
        f"benchmark_gate_decision: {decision}",
        "",
        "summary:",
        f"- cases: {len(rows)}",
        f"- pilot_cases: {pilot_count or 'not_checked'}",
        f"- core_cases: {core_count or 'not_checked'}",
        f"- provenance_manifest: {args.provenance or 'not_checked'}",
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
