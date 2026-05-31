from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) != sys.path[0]:
    while str(ROOT) in sys.path:
        sys.path.remove(str(ROOT))
    sys.path.insert(0, str(ROOT))

from scripts.adapters.base import ImageEditRequest
from scripts.adapters.registry import available_adapters, create_adapter
from scripts.common import read_csv_rows, read_jsonl, sha256_file, write_jsonl


PHASES = {"pilot", "core_smoke", "core_full"}


def safe_id(value: str, fallback: str) -> str:
    text = (value or fallback).strip()
    return "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in text)


def gate_decision(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"gate file does not exist: {path}")
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if text.lower().startswith("gate_decision:"):
            return text.split(":", 1)[1].strip().lower()
    raise SystemExit(f"gate_decision missing in gate file: {path}")


def require_gate(path_value: str | None, gate_name: str, phase: str) -> None:
    if not path_value:
        raise SystemExit(f"--{gate_name} is required for phase={phase}")
    path = Path(path_value)
    decision = gate_decision(path)
    if decision != "go":
        raise SystemExit(f"phase={phase} requires {gate_name} with gate_decision: go; found {decision}")


def require_real_metadata(path_value: str | None, metadata_name: str, phase: str) -> None:
    if not path_value:
        raise SystemExit(f"--{metadata_name} is required for phase={phase}")
    records = read_jsonl(Path(path_value))
    adapters = {str(row.get("adapter_name") or row.get("adapter") or "").strip() for row in records}
    adapters.discard("")
    if not records or not adapters or "mock" in adapters:
        raise SystemExit(f"phase={phase} requires {metadata_name} with real adapter metadata")


def enforce_phase_gates(
    phase: str,
    pilot_gate: str | None,
    core_smoke_gate: str | None,
    pilot_metadata: str | None,
    core_smoke_metadata: str | None,
) -> None:
    if phase not in PHASES:
        raise SystemExit(f"invalid phase: {phase}")
    if phase in {"core_smoke", "core_full"}:
        require_gate(pilot_gate, "pilot-gate", phase)
    if phase == "core_full":
        require_gate(core_smoke_gate, "core-smoke-gate", phase)
    if phase in {"core_smoke", "core_full"}:
        require_real_metadata(pilot_metadata, "pilot-metadata", phase)
    if phase == "core_full":
        require_real_metadata(core_smoke_metadata, "core-smoke-metadata", phase)


def read_existing_metadata(path: Path) -> list[dict[str, object]]:
    try:
        return read_jsonl(path)
    except ValueError:
        return []


def source_hash(case: dict[str, str]) -> str:
    path = Path(case.get("image_path", ""))
    if path.exists():
        return sha256_file(path)
    return case.get("image_sha256", "")


def mask_hash(case: dict[str, str]) -> str:
    mask = case.get("mask_path", "")
    if not mask:
        return ""
    path = Path(mask)
    if path.exists():
        return sha256_file(path)
    return case.get("mask_sha256", "")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=sorted(PHASES), default="pilot")
    parser.add_argument("--cases", required=True)
    parser.add_argument("--models", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--adapter", choices=sorted(available_adapters() + ["auto"]), default="mock")
    parser.add_argument("--pilot-gate")
    parser.add_argument("--core-smoke-gate")
    parser.add_argument("--pilot-metadata")
    parser.add_argument("--core-smoke-metadata")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--max-retries", type=int, default=0)
    parser.add_argument("--cost-limit-usd", type=float, default=None)
    args = parser.parse_args()

    enforce_phase_gates(args.phase, args.pilot_gate, args.core_smoke_gate, args.pilot_metadata, args.core_smoke_metadata)

    cases = read_csv_rows(Path(args.cases))
    models = read_csv_rows(Path(args.models))
    metadata_path = Path(args.metadata)
    output_dir = Path(args.output_dir)
    run_id = output_dir.name
    existing = read_existing_metadata(metadata_path) if args.resume and metadata_path.exists() else []
    done = {(str(row.get("model_id", "")), str(row.get("case_id", ""))) for row in existing}
    new_records: list[dict[str, object]] = []
    total_cost = sum(float(row.get("cost_usd", 0.0) or 0.0) for row in existing)
    adapters = {}

    for model in models:
        model_id = safe_id(model.get("model_id", ""), "model")
        adapter_name = model.get("adapter", "mock") if args.adapter == "auto" else args.adapter
        if adapter_name not in adapters:
            adapters[adapter_name] = create_adapter(adapter_name)
        adapter = adapters[adapter_name]
        output_suffix = ".txt" if adapter_name == "mock" else ".png"
        version_lock = model.get("version_lock") or "D_unversioned"
        version_risk = model.get("version_risk") or ("version_unlocked" if version_lock == "D_unversioned" else "")
        for case in cases:
            case_id = safe_id(case.get("case_id", ""), "case")
            if args.resume and (model_id, case_id) in done:
                continue
            if args.cost_limit_usd is not None and total_cost > args.cost_limit_usd:
                break
            prompt = case.get("prompt_en") or case.get("prompt_zh") or ""
            output_path = output_dir / model_id / f"{case_id}{output_suffix}"
            raw_response_path = output_dir / model_id / f"{case_id}.raw.json"
            request = ImageEditRequest(
                source_image=case.get("image_path", ""),
                mask=case.get("mask_path", ""),
                prompt=prompt,
                seed=0,
                config={
                    "dry_run": args.dry_run,
                    "output_path": output_path.as_posix(),
                    "raw_response_path": raw_response_path.as_posix(),
                    "run_id": run_id,
                    "phase": args.phase,
                    "model_id": model_id,
                    "case_id": case_id,
                    "provider_model_ref": model.get("provider_model_ref", ""),
                    "input_schema_ref": model.get("input_schema_ref", ""),
                    "version_risk": version_risk,
                },
            )
            result = adapter.generate(request)
            total_cost += result.cost_usd
            new_records.append(
                {
                    "run_id": run_id,
                    "phase": args.phase,
                    "model_id": model_id,
                    "model_name": model.get("model_name", model_id),
                    "case_id": case_id,
                    "task_id": case.get("task_id", ""),
                    "source_image": case.get("image_path", ""),
                    "source_image_sha256": source_hash(case),
                    "mask": case.get("mask_path", ""),
                    "mask_sha256": mask_hash(case),
                    "prompt": prompt,
                    "seed_requested": 0,
                    "seed_effective": result.seed_effective,
                    "output_path": result.output_path,
                    "runtime_seconds": result.runtime_seconds,
                    "cost_usd": result.cost_usd,
                    "raw_response_path": result.raw_response_path,
                    "status": result.status,
                    "version_lock": version_lock,
                    "version_risk": result.version_risk or version_risk,
                    "risk_flags": model.get("risk_flags", ""),
                    "adapter": adapter.adapter_name,
                    "adapter_name": adapter.adapter_name,
                    "adapter_kind": result.adapter_kind,
                    "provider_request_id": result.provider_request_id,
                    "cost_estimate_status": result.cost_estimate_status,
                    "provider_model_ref": model.get("provider_model_ref", ""),
                    "input_schema_ref": model.get("input_schema_ref", ""),
                    "dry_run": args.dry_run,
                    "error": result.error,
                }
            )

    write_jsonl(metadata_path, existing + new_records)
    print(f"wrote {len(new_records)} new metadata records to {metadata_path}")


if __name__ == "__main__":
    main()
