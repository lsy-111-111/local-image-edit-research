# Final Report Draft

This draft is generated from repository data only. It releases no strong model capability conclusions without human approval.

## Approved Claims

CLAIM: The Step 6 pilot used mock adapter outputs only and does not support any model capability conclusion.
CLAIM: Pilot metadata includes 700 records across 7 draft model entries.
CLAIM: Pilot gate decision is go for the implemented engineering metadata gate.
CLAIM: No aggregate leaderboard is generated from the mock pilot.
CLAIM: Human evaluation rows are blind and model mapping is stored separately.

## Evidence Status

- Strong model capability claims released: 0
- Missing-evidence strong claims: 0
- Company/API rows present: 0

## Pilot Metadata Summary

| model_id | cases | failures | failure_rate | cost_usd |
|---|---:|---:|---:|---:|
| flux-1-fill-dev | 100 | 0 | 0.000 | 0.0000 |
| flux-1-kontext-dev | 100 | 0 | 0.000 | 0.0000 |
| gpt-image-1 | 100 | 0 | 0.000 | 0.0000 |
| qwen-image-edit | 100 | 0 | 0.000 | 0.0000 |
| seededit | 100 | 0 | 0.000 | 0.0000 |
| stable-diffusion-2-inpainting | 100 | 0 | 0.000 | 0.0000 |
| stable-diffusion-xl-base-1-0 | 100 | 0 | 0.000 | 0.0000 |

## Core Smoke Metadata Summary

No run metadata is available.

## Required Risk Sections

- Failure rate: reported only from run metadata tables above.
- Cost: reported only from run metadata `cost_usd`.
- Version risk: `D_unversioned` records require human review.
- Blind human review: no aggregate leaderboard is released unless coverage audit passes.
- Evidence audit: see `reports/report_evidence_audit.csv` and `reports/missing_evidence_claims.csv`.
