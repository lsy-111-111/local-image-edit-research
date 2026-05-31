# Final Report Draft

This draft is generated from repository data only. It releases no strong model capability statements without human approval.

## Approved Claims

CLAIM: The Step 6 pilot used mock adapter outputs only and does not support any model capability conclusion.
CLAIM: Pilot metadata includes 700 records across 7 draft model entries, all retained as mock scaffold metadata only.
CLAIM: No aggregate leaderboard is generated from the mock pilot.
CLAIM: Human evaluation rows are blind and model mapping is stored separately.
CLAIM: Current research status is scaffold/no-go/needs_review until a real adapter pilot passes metadata and claim gates.

## Evidence Status

- Strong model capability claims released: 0
- Missing-evidence strong claims: 0
- Company/API rows present: 0
- Report mode: scaffold/no-go/needs_review unless pilot and core gates are go with real adapter metadata.

## Gate Status

- pilot: no_go
- core_smoke: no_go

## Pilot Metadata Summary

mock_only_no_model_capability_claim: yes

| model_id | adapter | cases | failures | failure_rate | cost_usd | cost_status | version_risk_records |
|---|---|---:|---:|---:|---:|---|---:|
| flux-1-fill-dev | mock | 100 | 0 | 0.000 | 0.0000 | legacy_or_unknown | 100 |
| flux-1-kontext-dev | mock | 100 | 0 | 0.000 | 0.0000 | legacy_or_unknown | 100 |
| gpt-image-1 | mock | 100 | 0 | 0.000 | 0.0000 | legacy_or_unknown | 100 |
| qwen-image-edit | mock | 100 | 0 | 0.000 | 0.0000 | legacy_or_unknown | 100 |
| seededit | mock | 100 | 0 | 0.000 | 0.0000 | legacy_or_unknown | 100 |
| stable-diffusion-2-inpainting | mock | 100 | 0 | 0.000 | 0.0000 | legacy_or_unknown | 100 |
| stable-diffusion-xl-base-1-0 | mock | 100 | 0 | 0.000 | 0.0000 | legacy_or_unknown | 100 |

## Core Smoke Metadata Summary

No run metadata is available.

## Required Risk Sections

- Failure rate: reported only from run metadata tables above.
- Cost: reported only from run metadata `cost_usd`; rows with `dry_run`, `legacy_or_unknown`, or `no_pricing_applied` cost status are not real cost conclusions.
- Version risk: `D_unversioned` records require human review.
- Blind human review: no aggregate comparison table is released unless coverage audit passes.
- Evidence audit: see `reports/report_evidence_audit.csv` and `reports/missing_evidence_claims.csv`.
