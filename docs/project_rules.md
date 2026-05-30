# Project Rules

This repository implements the engineering side of an evidence-based research workflow for local image editing models. Codex is only the Research DevOps Agent. It must not act as the factual judge.

## Hard Rules

1. Do not invent model capabilities, versions, APIs, pricing, licenses, or paper conclusions.
2. Any model judgment labeled `A0`, `A1`, or `A2` must keep `source_url`, `evidence_quote`, `evidence_level`, and `last_verified_date`.
3. If evidence is insufficient, write `unknown` or `needs_review`.
4. Do not count `API_wrapper`, `product_feature`, `demo`, or `implementation` as independent `model_family`.
5. Do not run Core Benchmark before Pilot Gate and Core Smoke Gate pass.
6. Reports must include failure rate, cost, version risk, blind human review status, and evidence audit status.
7. E4/E5 evidence cannot support strong claims.
8. Web product results and underlying model results must not be mixed into one leaderboard.

## Phase Order

The phase order is mandatory:

```text
Schema Gate -> Evidence Gate -> Registry Gate -> Architecture Gate -> Benchmark Gate -> Adapter Gate -> Pilot Gate -> Evaluation -> Company/API Review -> Core Gate -> Report Gate
```

Every phase must pass its validators and tests before the next phase is executed.
