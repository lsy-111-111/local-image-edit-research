from __future__ import annotations

import argparse
from pathlib import Path

from scripts.adapters.base import ImageEditRequest
from scripts.adapters.mock_adapter import MockImageEditAdapter
from scripts.common import read_csv_rows, read_jsonl, sha256_file, write_jsonl


def safe_id(value: str, fallback: str) -> str:
    text = (value or fallback).strip()
    return "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in text)


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
    parser.add_argument("--cases", required=True)
    parser.add_argument("--models", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--max-retries", type=int, default=0)
    parser.add_argument("--cost-limit-usd", type=float, default=None)
    args = parser.parse_args()

    cases = read_csv_rows(Path(args.cases))
    models = read_csv_rows(Path(args.models))
    metadata_path = Path(args.metadata)
    output_dir = Path(args.output_dir)
    run_id = output_dir.name
    existing = read_existing_metadata(metadata_path) if args.resume and metadata_path.exists() else []
    done = {(str(row.get("model_id", "")), str(row.get("case_id", ""))) for row in existing}
    new_records: list[dict[str, object]] = []
    total_cost = sum(float(row.get("cost_usd", 0.0) or 0.0) for row in existing)
    adapter = MockImageEditAdapter()

    for model in models:
        model_id = safe_id(model.get("model_id", ""), "model")
        for case in cases:
            case_id = safe_id(case.get("case_id", ""), "case")
            if args.resume and (model_id, case_id) in done:
                continue
            if args.cost_limit_usd is not None and total_cost > args.cost_limit_usd:
                break
            prompt = case.get("prompt_en") or case.get("prompt_zh") or ""
            output_path = output_dir / model_id / f"{case_id}.txt"
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
                    "model_id": model_id,
                    "case_id": case_id,
                },
            )
            result = adapter.generate(request)
            total_cost += result.cost_usd
            new_records.append(
                {
                    "run_id": run_id,
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
                    "version_lock": model.get("version_lock") or "D_unversioned",
                    "risk_flags": model.get("risk_flags", ""),
                    "adapter": adapter.adapter_name,
                    "dry_run": args.dry_run,
                    "error": result.error,
                }
            )

    write_jsonl(metadata_path, existing + new_records)
    print(f"wrote {len(new_records)} new metadata records to {metadata_path}")


if __name__ == "__main__":
    main()
