# Benchmark Data Pilot Summary

Step 05 generated a synthetic PNG benchmark data pilot for API-compatible adapter testing.

## Coverage

- Task coverage: 16 task IDs (T01-T16) in `data/benchmark/benchmark_cases.csv`.
- Total benchmark cases: 112.
- Pilot case subset: 100 validated cases, all present in the main benchmark.
- Core smoke case subset: 100 validated cases, all present in the main benchmark.
- Provenance manifest rows: 112 referenced assets.
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
- `data/benchmark/provenance_manifest.csv`: source image and mask provenance, with reproducible SHA-256 hashes.

## Decision

Benchmark Gate status: `go`.

This synthetic benchmark supports pipeline and metadata validation only. It does not support model capability, ranking, or production-readiness claims.
