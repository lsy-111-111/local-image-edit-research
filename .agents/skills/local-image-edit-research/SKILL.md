---
name: local-image-edit-research
description: Use for evidence-based local image editing model research. Enforces registry evidence, model family separation, pilot-first experiments, metadata audits, and report claim checks.
---

Use this skill when working in the local image editing model research repo.

Non-negotiable gates:
1. Schema Gate: required files and fields must exist.
2. Evidence Gate: A0/A1/A2 records require source_url, evidence_quote, evidence_level, last_verified_date.
3. Registry Gate: wrapper/product/demo must not be counted as independent model families.
4. Architecture Gate: non-unknown G/C/T/D labels require evidence_quote.
5. Benchmark Gate: every case needs image hash, mask hash if applicable, prompt, expected_change, preserve_requirements, copyright_status.
6. Adapter Gate: dry-run, resume, stable output paths, cost, runtime, seed, status, raw_response_path.
7. Pilot Gate: 5-8 models, 100-300 cases per model, no direct core.
8. Core Gate: 100-case smoke test first, then expand only if metadata/cost/failure/version checks pass.
9. Report Gate: every key claim must trace to table fields or evidence_quote.
