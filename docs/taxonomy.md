# Architecture Taxonomy

Architecture labels are conservative. Unknown is acceptable; guessing is not.

## Base Architecture

- `G0` through `G9`: reserved architecture buckets.
- `unknown`: insufficient evidence.

## Control Mechanism

- `C_mask`
- `C_auto_mask`
- `C_box`
- `C_scribble`
- `C_reference`
- `C_text_edit`
- `C_multiturn`
- `unknown`

## Training Or Inference

- `T_finetuned`
- `T_instruction`
- `T_inversion`
- `T_training_free`
- `T_composite`
- `T_closed`
- `unknown`

## Deployment

- `D_local`
- `D_weights`
- `D_api`
- `D_web`
- `D_seed`
- `D_no_seed`
- `D_versioned`
- `D_unversioned`
- `unknown`

Any non-`unknown` label must cite an `evidence_quote`.
