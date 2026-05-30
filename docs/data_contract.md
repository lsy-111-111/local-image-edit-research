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
