# Data Contract

All tabular files use UTF-8 CSV with headers. All JSONL files contain one JSON object per non-empty line.

## Evidence Fields

Records that assert model facts must include:

- `source_url`
- `evidence_quote`
- `evidence_level`
- `last_verified_date`

`last_verified_date` must use `YYYY-MM-DD`.

## Evidence Levels

- `E0`: direct official documentation or model card.
- `E1`: paper, official technical report, or official release note.
- `E2`: first-party API documentation or pricing page.
- `E3`: credible third-party benchmark or reproducible report.
- `E4`: secondary mention or non-authoritative summary.
- `E5`: weak, anecdotal, or unverifiable source.

`E4` and `E5` must never support strong conclusions.

## Candidate Labels

Allowed candidate labels are `A0`, `A1`, `A2`, `B`, `C`, `D`, and `X`.

`A0`, `A1`, and `A2` are evidence-bearing labels and require complete evidence fields.

## Provider Model Map

`data/registry/provider_model_map.csv` records adapter routing only. It must not be treated as evidence of model quality or provider availability until `review_status=approved`.

Required fields:

- `model_id`
- `adapter`
- `provider_model_ref`
- `input_schema_ref`
- `version_lock`
- `source_url`
- `evidence_quote`
- `evidence_level`
- `last_verified_date`
- `review_status`

## Run Metadata

Real or dry-run adapter metadata must include `adapter`, `adapter_name`, `adapter_kind`, `provider_request_id`, `version_risk`, and `cost_estimate_status`. A `cost_usd` value of `0.0` is not a real cost conclusion unless `cost_estimate_status` explicitly states that pricing was applied.
