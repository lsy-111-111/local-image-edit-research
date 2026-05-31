# Benchmark Data Pilot Summary

Step 05 generated a synthetic PNG benchmark data pilot for API-compatible adapter testing.

## Coverage

- Task coverage: T01-T16, 7 cases each.
- Total benchmark cases: 112.
- Pilot case subset: 100 validated cases.
- Core smoke case subset: 100 validated cases.
- Mask coverage: high, medium, rough, and none.
- Language coverage: every case includes English and Chinese prompts.
- Copyright status: `synthetic_codex_generated` for every case.
- Image format: self-generated PNG source assets and PNG masks.

## Outputs

- `data/benchmark/source_images/`: synthetic source PNG files.
- `data/benchmark/masks/`: synthetic mask PNG files.
- `data/benchmark/task_prompts.csv`: prompt rows.
- `data/benchmark/benchmark_cases.csv`: 112 validated case rows.
- `data/benchmark/pilot_cases_100.csv`: 100 validated case rows.
- `data/benchmark/core_cases_smoke_100.csv`: 100 validated case rows.
- `data/benchmark/image_hashes.csv`: source image hashes.

## Decision

Benchmark Gate status: `go_for_real_adapter_dry_run`.

This synthetic benchmark supports pipeline and metadata validation only. It does not support model capability, ranking, or production-readiness claims.
