PYTHON ?= python

.PHONY: check structure truth test

check: structure truth test

structure:
	$(PYTHON) scripts/validate_project_structure.py

truth:
	$(PYTHON) scripts/audit_repo_truth.py --pilot-metadata data/runs/pilot_RUN_001.jsonl --pilot-gate reports/pilot_RUN_001_gate.md --claim-manifest reports/claim_manifest.csv --benchmark data/benchmark/benchmark_cases.csv --evidence data/evidence/extracted_entries.jsonl --registry data/registry/model_registry.jsonl --final-report reports/final_report_draft.md --output reports/repo_truth_audit.md --root . --allow-no-go

test:
	$(PYTHON) -m pytest
