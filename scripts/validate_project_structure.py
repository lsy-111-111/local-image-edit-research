from __future__ import annotations

from pathlib import Path

from scripts.common import fail_with_errors, project_root


REQUIRED_DIRS = [
    "data/raw",
    "data/evidence",
    "data/registry",
    "data/benchmark",
    "data/runs",
    "data/eval",
    "outputs",
    "prompts/codex",
    "scripts",
    "scripts/adapters",
    "tests",
    "reports",
    "docs",
    ".agents/skills/local-image-edit-research/references",
    ".github/workflows",
]

REQUIRED_FILES = [
    "AGENTS.md",
    "Makefile",
    "README.md",
    ".github/workflows/ci.yml",
    ".agents/skills/local-image-edit-research/SKILL.md",
    "docs/project_rules.md",
    "docs/data_contract.md",
    "docs/taxonomy.md",
    "docs/decision_log.md",
    "data/raw/query_bank.csv",
    "data/raw/pages.schema.json",
    "data/evidence/extracted_entries.schema.json",
    "data/registry/raw_entries.csv",
    "data/registry/model_family.csv",
    "data/registry/model_version.csv",
    "data/registry/implementation.csv",
    "data/registry/company_product_api.csv",
    "data/registry/company_product_api.schema.json",
    "data/registry/experiment_run.csv",
    "data/registry/model_registry.jsonl",
    "data/registry/uncertain_cases.csv",
    "data/registry/architecture_labels.schema.json",
    "data/registry/architecture_labels.jsonl",
    "data/benchmark/benchmark_cases.schema.json",
    "data/benchmark/benchmark_cases.csv",
    "data/runs/run_metadata.schema.json",
    "prompts/codex/extract_model_info.md",
    "scripts/validate_raw_entries.py",
    "scripts/validate_registry_consistency.py",
    "scripts/audit_evidence.py",
    "scripts/audit_report_claims.py",
    "scripts/gpt_batch.py",
    "scripts/merge_extracted_entries.py",
    "scripts/export_needs_review.py",
    "scripts/dedupe_candidates.py",
    "scripts/build_family_tree.py",
    "scripts/build_registry_from_evidence.py",
    "scripts/validate_architecture_labels.py",
    "scripts/export_architecture_review_queue.py",
    "scripts/hash_assets.py",
    "scripts/build_benchmark_cases.py",
    "scripts/validate_benchmark_cases.py",
    "scripts/adapters/base.py",
    "scripts/adapters/mock_adapter.py",
    "scripts/run_generation.py",
    "scripts/audit_run_metadata.py",
    "scripts/select_pilot_models.py",
    "scripts/summarize_pilot.py",
    "scripts/export_failure_cases.py",
    "scripts/pilot_gate_decision.py",
    "scripts/compute_metrics.py",
    "scripts/sample_for_human_eval.py",
    "scripts/merge_human_eval.py",
    "scripts/audit_eval_coverage.py",
    "scripts/summarize_failure_tags.py",
    "scripts/validate_company_product_api.py",
    "scripts/export_company_review_queue.py",
    "scripts/monthly_company_reverify.py",
    "scripts/select_core_candidates.py",
    "scripts/core_gate_decision.py",
    "scripts/block_core_without_pilot.py",
    "scripts/render_report.py",
    "outputs/.gitkeep",
    "data/benchmark/source_images/.gitkeep",
    "data/benchmark/masks/.gitkeep",
]


def main() -> None:
    root = project_root()
    errors: list[str] = []
    for rel in REQUIRED_DIRS:
        path = root / rel
        if not path.is_dir():
            errors.append(f"missing directory: {rel}")
    for rel in REQUIRED_FILES:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing file: {rel}")
    fail_with_errors(errors)


if __name__ == "__main__":
    main()
