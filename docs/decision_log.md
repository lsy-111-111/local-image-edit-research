# Decision Log

No factual model inclusion or exclusion decisions have been made by Codex.

## Step 2 Evidence Pilot Engineering Note

- Date: 2026-05-31
- Actor: Codex as Research DevOps Agent
- Decision: Evidence sources were collected only from official docs, official model cards, official API docs, or paper pages.
- Constraint: All extracted entries are marked `needs_review`; Codex did not make final factual judgments.
- Next human review: Confirm candidate labels, model family/version boundaries, and product/API wrapper exclusions before registry promotion.

## Step 3 Registry Draft Engineering Note

- Date: 2026-05-31
- Actor: Codex as Research DevOps Agent
- Decision: Registry draft was generated from `data/evidence/extracted_entries.jsonl` only.
- Constraint: Product features, API wrappers, demos, and implementations are not promoted to independent model families.
- Next human review: Resolve all rows in `data/registry/uncertain_cases.csv` before using registry rows as factual conclusions.
