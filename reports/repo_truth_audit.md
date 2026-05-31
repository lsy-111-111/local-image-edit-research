# Repo Truth Audit

repo_truth_decision: no_go

blocking_reasons:
- mock adapter records cannot unlock real pilot/core

warnings:
- adapter registry/pilot is mock-only; real adapter pilot is still required

record_counts:
  pilot_RUN_001: 700
  benchmark_cases: 112
  extracted_evidence_entries: 15
  model_registry_records: 15

claim_conflicts:
- none

jsonl_parse_errors:
- none
