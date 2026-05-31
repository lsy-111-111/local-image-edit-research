# local-image-edit-research

Engineering scaffold for evidence-based local image editing model research.

This repository is not a completed research result. Current data files may be empty scaffold outputs, and no model capability, API, price, license, or ranking claim is valid unless it is backed by repository evidence and passes the implemented gates.

## Role Split

- Codex acts as the Research DevOps Agent.
- Human reviewers act as factual judges.
- Evidence-bearing model records must preserve `source_type`, `source_url`, `evidence_quote`, `evidence_level`, and `last_verified_date`.
- `API_wrapper`, `product_feature`, `demo`, and `implementation` must not be counted as independent `model_family` records.

## Required Order

Run phases in order and do not jump directly to Core:

```text
Schema Gate -> Evidence Gate -> Registry Gate -> Architecture Gate -> Benchmark Gate -> Adapter Gate -> Pilot Gate -> Evaluation -> Company/API Review -> Core Gate -> Report Gate
```

Core smoke requires a `gate_decision: go` pilot gate. Core full requires both a `gate_decision: go` pilot gate and a `gate_decision: go` core smoke gate.
Mock-only metadata never unlocks real pilot, core smoke, or core full.

## Local Checks

```bash
python scripts/validate_project_structure.py
python scripts/audit_repo_truth.py --pilot-metadata data/runs/pilot_RUN_001.jsonl --pilot-gate reports/pilot_RUN_001_gate.md --claim-manifest reports/claim_manifest.csv --benchmark data/benchmark/benchmark_cases.csv --evidence data/evidence/extracted_entries.jsonl --registry data/registry/model_registry.jsonl --final-report reports/final_report_draft.md --output reports/repo_truth_audit.md --root . --allow-no-go
pytest
```

or:

```bash
make check
```

## Current Status

No-Go for research completion. Go for scaffold hardening and evidence pilot only.

Current implementation includes OpenAI Images and Replicate adapter contracts with dry-run support. Live adapter execution remains blocked until `OPENAI_API_KEY` and `REPLICATE_API_TOKEN` are configured and the provider model map receives human review.
