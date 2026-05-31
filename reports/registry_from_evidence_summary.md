# Registry From Evidence Summary

Step 3 generated a registry draft from Step 2 evidence only.

## Outputs

- `data/registry/model_registry.jsonl`: 13 draft records.
- `data/registry/model_family.csv`: 7 draft family rows.
- `data/registry/model_version.csv`: 6 draft version rows.
- `data/registry/implementation.csv`: header-only because no implementation record was promoted.
- `data/registry/uncertain_cases.csv`: 13 review rows.
- `data/registry/provider_model_map.csv`: 6 provider routing rows for OpenAI/Replicate dry-run/live adapter planning.
- `data/registry/pilot_models.csv`: 6 provider-mapped pilot candidates; all require human review before live formal pilot.
- `docs/family_tree.md`: family/review notes generated from dedupe suggestions.

## Gate Rules Applied

- No name-similarity merge was treated as factual.
- `API_wrapper`, `product_feature`, `demo`, and `implementation` records were blocked from independent model-family status.
- All rows remain human-review gated.
- Provider mappings are routing hints only until exact hosted endpoint/version review passes.
- No model ranking or capability comparison was produced.

## Decision

Registry Gate status: `go_for_benchmark_data_pilot_after_human_review`.
