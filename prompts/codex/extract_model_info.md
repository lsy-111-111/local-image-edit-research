# Evidence Extraction Prompt

Extract only facts explicitly supported by the provided page text.

Return JSONL records with:

- `candidate_id`
- `candidate_name`
- `candidate_label`
- `record_type`
- `source_url`
- `evidence_quote`
- `evidence_level`
- `last_verified_date`
- `review_status`
- `notes`

Rules:

1. Do not infer capabilities from titles, company names, or model names.
2. Do not guess mask support.
3. Do not fill `source_url` unless it is present in the input page record.
4. If evidence is insufficient, use `candidate_label: "X"` and `review_status: "needs_review"`.
