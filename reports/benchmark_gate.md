# Benchmark Gate

benchmark_gate_decision: go

summary:
- cases: 112
- pilot_cases: 100
- core_cases: 100
- provenance_manifest: data/benchmark/provenance_manifest.csv
- task_count: 16
- min_cases_required: 80
- require_api_assets: false
- scope: data readiness only; this gate does not support model ranking or capability claims

blocking_reasons:
- none
