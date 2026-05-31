# Adapter Pilot Summary

Step 5 added explicit adapter selection and kept the pilot on `mock`.

## Supported

- `run_generation.py --adapter mock`
- Adapter registry with a single registered adapter: `mock`
- Dry-run generation
- Resume without duplicate metadata
- Stable output and raw-response paths
- Metadata fields for source hash, mask hash, seed, runtime, cost, raw response, status, adapter, and version lock

## Limits

- No real local model or API adapter was connected.
- All mock outputs are engineering artifacts only.
- Version lock remains `D_unversioned` unless a future real adapter can pin a version.

## Decision

Adapter Gate status: `go_for_mock_formal_pilot`.

This step does not support any model capability claim.
