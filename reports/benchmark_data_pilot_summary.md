# Benchmark Data Pilot Summary

Step 4 generated a synthetic 80-case benchmark data pilot.

## Coverage

- Task coverage: T01-T16, 5 cases each.
- Mask coverage: high 32, medium 16, rough 16, none 16.
- Language coverage: every case includes English and Chinese prompts.
- Copyright status: `synthetic_codex_generated` for every case.
- Image format: self-generated SVG source assets and SVG masks.

## Outputs

- `data/benchmark/source_images/`: 16 synthetic source SVG files.
- `data/benchmark/masks/`: 48 synthetic mask SVG files.
- `data/benchmark/task_prompts.csv`: 80 prompt rows.
- `data/benchmark/benchmark_cases.csv`: 80 validated case rows.
- `data/benchmark/image_hashes.csv`: 16 source image hashes.
- `data/benchmark/core_cases_smoke_100.csv`: header-only placeholder.

## Decision

Benchmark Gate status: `go_for_adapter_pilot`.

Core smoke remains blocked until 100 validated cases are available and pilot gate passes.
