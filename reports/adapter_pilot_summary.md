# Adapter Pilot Summary

Adapter Gate status: `go_for_dry_run_contract_only`.

## Supported

- `run_generation.py --adapter auto` routes each model row to `openai_images` or `replicate`.
- Registered adapters: `mock`, `openai_images`, `replicate`.
- Dry-run generation writes stable PNG outputs and raw-response JSON without credentials.
- Resume does not duplicate metadata.
- Metadata includes source/mask hashes, seed, runtime, cost field, raw response, status, adapter, provider request id, version risk, and cost estimate status.

## Dry-run Result

- `data/runs/adapter_DRYRUN_001.jsonl`: 600 records across 6 provider-mapped candidates.
- `outputs/adapter_DRYRUN_001/`: stable placeholder PNG/raw JSON outputs.
- `cost_estimate_status`: `dry_run`; no real cost conclusion is released.

## External Prerequisites

- OpenAI live smoke requires `OPENAI_API_KEY`.
- Replicate live pilot requires `REPLICATE_API_TOKEN`.
- Provider model map rows remain `needs_review` until a human confirms exact hosted endpoints/versions.

This step does not support any model capability, ranking, or core-readiness claim.
