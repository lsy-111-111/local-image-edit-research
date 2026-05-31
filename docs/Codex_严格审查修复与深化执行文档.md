# Codex 严格审查修复与深化执行文档

> 项目：`local-image-edit-research`  
> 当前判定：**No-Go for research completion. Go only for Truth Reconciliation + Engineering Gate Hardening.**  
> 角色边界：Codex 是 Research DevOps Agent，不是事实裁判。Codex 不得新增、猜测、合成任何真实模型能力、版本、API、价格、license 或论文结论。

---

## 0. 立即停止线

在完成本文件 Step 00–03 之前：

1. 不接真实 adapter。
2. 不跑 pilot。
3. 不跑 core smoke。
4. 不跑 core full。
5. 不生成模型优劣、排名、推荐、leaderboard 或 capability conclusion。
6. 不允许 mock adapter 输出支撑任何真实模型能力结论。
7. 不允许空 metadata、空 benchmark、空 evidence 被报告成“研究完成”。

所有真实模型判断必须具备：

```text
source_url
evidence_quote
evidence_level
last_verified_date
review_status
```

证据不足时只能写：

```text
unknown
needs_review
blocked
```

---

## 1. 当前必须修复的事实冲突

Codex 必须先修复以下冲突，不得跳过：

| ID | 阻断问题 | 必须修复成什么 |
|---|---|---|
| B0-1 | `data/runs/pilot_RUN_001.jsonl` 为空，但 `reports/claim_manifest.csv` 仍允许“700 records” claim | 该 claim 必须 `allowed_in_report=no`，写明 `invalid_reason=actual pilot metadata has 0 records` |
| B0-2 | `reports/pilot_RUN_001_gate.md` 为 `no_go`，但 `claim_manifest.csv` 和 `final_report_draft.md` 仍允许/输出 “pilot gate go” | 该 claim 必须禁用；final report 不得包含该句 |
| B0-3 | `data/benchmark/benchmark_cases.csv` 只有表头，不满足 80 valid cases | benchmark gate 必须 `no_go`；不得进入 pilot/core |
| B0-4 | `data/evidence/extracted_entries.jsonl` 为空 | 不得生成 registry、architecture claim、model capability claim |
| B0-5 | `data/registry/model_registry.jsonl` 为空，`pilot_models.csv` 只有表头 | 不得选择 pilot 模型，不得声称 5–8 模型 pilot 已完成 |
| B0-6 | `run_generation.py` 只固定使用 mock adapter，且没有 `--phase / --adapter / --pilot-gate / --core-smoke-gate` | 必须增加 phase gate 和 adapter registry；core 路径必须被 gate 控制 |
| B0-7 | 缺少 `scripts/audit_repo_truth.py`、`reports/repo_truth_audit.md`、truth reconciliation tests | 必须新增并作为 `make check` 的一部分 |

---

## 2. Git 工作流

每个 Step 单独分支，不允许一次性做完所有任务。

```bash
git status
git checkout -b step-00-truth-reconciliation
```

每次改动后必须运行：

```bash
python scripts/validate_project_structure.py
pytest
git diff --stat
git status
```

Codex 完成后必须输出：

```text
changed_files:
- ...

commands_run:
- ...

tests_passed:
- ...

risks:
- ...

requires_human_review:
- ...

next_recommended_step:
- ...
```

---

# Step 00：Truth Reconciliation

## 00.1 目标

让 README、gate、claim_manifest、final_report、metadata、benchmark 状态一致。当前阶段只做事实一致性和 gate 修复，不接模型、不跑实验。

## 00.2 Codex 提示词

```text
Use the local-image-edit-research skill.

当前阶段：Step 00 truth reconciliation
输入文件：现有仓库全部文件
目标产物：
- scripts/audit_repo_truth.py
- tests/test_truth_reconciliation.py
- tests/test_pilot_gate_empty_metadata_no_go.py
- tests/test_claim_manifest_record_counts.py
- tests/test_jsonl_integrity.py
- tests/test_benchmark_minimum_coverage.py
- reports/repo_truth_audit.md
- reports/claim_manifest.csv 更新
- reports/final_report_draft.md 更新
- reports/report_evidence_audit.csv 更新
- reports/missing_evidence_claims.csv 更新

硬规则：
1. 不新增任何真实模型能力、版本、API、价格、license 或论文结论。
2. 不新增真实模型数据。
3. 不跑真实 adapter。
4. 不跑 pilot。
5. 不跑 core。
6. 空 metadata 不得产生 gate_decision: go。
7. claim_manifest 中任何 record count claim 必须等于实际 JSONL record count。
8. benchmark <80 valid cases 时必须 benchmark_gate=no_go。
9. mock adapter 结果不得支持真实模型 capability claim。
10. final_report_draft.md 只能输出 scaffold/no-go/needs_review 状态。

请执行：
1. 新增 scripts/audit_repo_truth.py。
2. 审计 data/runs/pilot_RUN_001.jsonl：逐行 JSONL parse，统计有效 records。
3. 审计 reports/pilot_RUN_001_gate.md：如果 metadata records=0，则 gate_decision 必须是 no_go。
4. 审计 reports/claim_manifest.csv：
   - 凡 claim_text 包含 700 records、pilot gate go、core 可运行、pilot 成功等与实际 metadata/gate 冲突的 claim，设置 allowed_in_report=no。
   - 写入 invalid_reason。
   - 不删除冲突记录，保留审计痕迹。
5. 审计 data/benchmark/benchmark_cases.csv：有效 case <80 时写入 blocking_reasons。
6. 审计所有 *.jsonl：必须是一行一个 JSON object；空文件允许但不得支持任何完成性 claim。
7. 生成 reports/repo_truth_audit.md，必须包含：
   - repo_truth_decision: go | no_go
   - blocking_reasons
   - warnings
   - record_counts
   - claim_conflicts
8. 重新生成/审计 final_report_draft.md：不得包含无 metadata 支撑的 700 records、pilot go、模型表、排行榜或模型能力结论。
9. 新增测试覆盖上述全部阻断逻辑。
```

## 00.3 `audit_repo_truth.py` CLI

必须支持：

```bash
python scripts/audit_repo_truth.py \
  --pilot-metadata data/runs/pilot_RUN_001.jsonl \
  --pilot-gate reports/pilot_RUN_001_gate.md \
  --claim-manifest reports/claim_manifest.csv \
  --benchmark data/benchmark/benchmark_cases.csv \
  --final-report reports/final_report_draft.md \
  --output reports/repo_truth_audit.md
```

## 00.4 `repo_truth_audit.md` 最低格式

```text
repo_truth_decision: no_go

blocking_reasons:
- no pilot metadata records
- claim_manifest contains claims inconsistent with actual metadata
- benchmark has fewer than 80 valid cases
- evidence registry is empty

record_counts:
  pilot_RUN_001: 0
  benchmark_cases_valid: 0
  extracted_entries: 0
  model_registry: 0

claim_conflicts:
- claim_id: c002
  reason: claims 700 pilot records but actual count is 0
  required_action: allowed_in_report=no
- claim_id: c003
  reason: claims pilot gate go but gate file says no_go
  required_action: allowed_in_report=no
```

## 00.5 验收命令

```bash
python scripts/audit_repo_truth.py \
  --pilot-metadata data/runs/pilot_RUN_001.jsonl \
  --pilot-gate reports/pilot_RUN_001_gate.md \
  --claim-manifest reports/claim_manifest.csv \
  --benchmark data/benchmark/benchmark_cases.csv \
  --final-report reports/final_report_draft.md \
  --output reports/repo_truth_audit.md

python scripts/audit_report_claims.py \
  --report reports/final_report_draft.md \
  --claim-manifest reports/claim_manifest.csv \
  --output reports/report_evidence_audit.csv \
  --missing reports/missing_evidence_claims.csv

python scripts/validate_project_structure.py
pytest
```

## 00.6 Go 条件

- `reports/repo_truth_audit.md` 明确 `repo_truth_decision: no_go`，且列出阻断原因。
- `claim_manifest.csv` 中 c002/c003 或等价冲突 claim 为 `allowed_in_report=no`。
- `final_report_draft.md` 不再包含 “700 records”“pilot gate go”“7 draft model entries” 等冲突 claim。
- 空 pilot metadata 对应 `pilot_RUN_001_gate.md = no_go`。
- benchmark <80 时不能进入 pilot/core。
- JSONL parse gate 有测试。

---

# Step 01：Clean Clone + Engineering Gate Hardening

## 01.1 目标

让 clean clone 后结构验证、pytest、report audit、core blocking 可复现。

## 01.2 Codex 提示词

```text
Use the local-image-edit-research skill.

当前阶段：Step 01 engineering gate hardening
输入文件：现有仓库全部文件
目标产物：
- Makefile 更新或新增
- .github/workflows/ci.yml 更新或新增
- scripts/validate_project_structure.py 修正
- scripts/run_generation.py 更新
- scripts/block_core_without_pilot.py 更新
- scripts/audit_report_claims.py 更新
- tests/test_core_blocking_in_run_generation.py
- tests/test_core_full_requires_smoke_go.py
- tests/test_report_claim_audit_coverage.py

任务：
1. 修复 scripts/validate_project_structure.py，确保 required files 与仓库真实目标一致；不要要求不存在的未来脚本，除非本 Step 同时创建可测试 stub。
2. Makefile 必须提供 make check，等价于：
   - python scripts/validate_project_structure.py
   - python scripts/audit_repo_truth.py ...
   - pytest
3. run_generation.py 必须显式支持：
   - --phase pilot | core_smoke | core_full
   - --adapter mock | <real_adapter_name>
   - --pilot-gate
   - --core-smoke-gate
4. phase=core_smoke 或 core_full 时，必须要求 --pilot-gate 且精确解析 gate_decision: go。
5. phase=core_full 时，必须额外要求 --core-smoke-gate 且精确解析 gate_decision: go。
6. block_core_without_pilot.py 不能用简单 substring 判断；必须按行解析 gate_decision 字段。
7. audit_report_claims.py 必须扫描中英文强结论词：
   - best, better, outperform, supports, recommend, conclusion, rank, leaderboard
   - 最好, 优于, 推荐, 排名, 榜单, 结论, 支持, 胜过
8. 无 claim_manifest.csv 或 allowed_in_report != yes 的 claim 不得进入 final_report_draft.md。
9. 所有新增 gate 必须有测试。

禁止：
- 不新增真实模型事实。
- 不新增真实模型能力判断。
```

## 01.3 验收命令

```bash
make check

python scripts/run_generation.py \
  --phase core_smoke \
  --adapter mock \
  --cases data/benchmark/core_cases_smoke_100.csv \
  --models data/registry/core_models_batch_01.csv \
  --output-dir outputs/core_SMOKE_TEST \
  --metadata data/runs/core_SMOKE_TEST.jsonl \
  --pilot-gate reports/pilot_RUN_001_gate.md
```

预期：当前 pilot gate 为 no_go 时，上述 core_smoke 命令必须失败，且不得写 output/metadata。

---

# Step 02：Benchmark Gate 修复，不创建假数据

## 02.1 目标

先把 benchmark validator 修对。当前只有表头时必须明确 no_go。

## 02.2 Codex 提示词

```text
Use the local-image-edit-research skill.

当前阶段：Step 02 benchmark gate hardening
输入文件：
- data/benchmark/benchmark_cases.csv
- scripts/validate_benchmark_cases.py
- tests/test_benchmark_schema.py

目标产物：
- scripts/validate_benchmark_cases.py 更新
- tests/test_benchmark_minimum_coverage.py
- tests/test_benchmark_no_duplicate_case_inflation.py
- reports/benchmark_gate.md

任务：
1. benchmark_cases.csv 有效 case <80 时必须失败或输出 no_go。
2. T01–T16 每个 task 至少 5 个有效 case；不足时 no_go。
3. 禁止重复 row 凑样本规模：至少检查 case_id 唯一，以及 image_path+mask_path+prompt_en+prompt_zh+task_id 组合重复。
4. copyright_status 不能是 unknown。
5. mask_path 为空时 mask_sha256 必须为空，mask_quality 必须为 none。
6. mask_path 非空时 mask_sha256 必须非空且可复算。
7. 每个 case 必须有 expected_change 和 preserve_requirements。
8. 生成 reports/benchmark_gate.md，包含：
   - benchmark_gate: go | no_go
   - valid_case_count
   - task_coverage
   - mask_coverage
   - duplicate_count
   - blocking_reasons

禁止：
- 不自动生成 80 rows。
- 不复制重复 row 充数。
- 不使用未授权图片。
```

## 02.3 验收命令

```bash
python scripts/validate_benchmark_cases.py data/benchmark/benchmark_cases.csv
pytest tests/test_benchmark_minimum_coverage.py tests/test_benchmark_no_duplicate_case_inflation.py
```

当前数据状态下，validator 应该返回失败或 no_go，因为没有 80 个有效 case。

---

# Step 03：Evidence Pilot 准备，只做 pipeline，不写模型结论

## 03.1 目标

准备 20–30 个高质量来源的 evidence pilot。Codex 不得自行判断模型真实能力，只能抽取并标记 needs_review。

## 03.2 Codex 提示词

```text
Use the local-image-edit-research skill.

当前阶段：Step 03 evidence pilot readiness
输入文件：
- data/raw/pages.jsonl
- data/raw/query_bank.csv
- prompts/codex/extract_model_info.md
- scripts/gpt_batch.py
- scripts/audit_evidence.py
- scripts/export_needs_review.py

目标产物：
- data/raw/pages.schema.json 更新
- data/evidence/extracted_entries.schema.json 更新
- tests/test_evidence_source_requirements.py
- reports/evidence_pilot_readiness.md

任务：
1. pages.jsonl 每条记录必须包含：source_url, retrieved_at, source_type, text 或 saved_path。
2. source_type 只允许：official_docs, official_model_card, official_api_docs, paper, official_github, release_note。
3. extracted_entries.jsonl 的 A0/A1/A2 记录必须有 source_url, evidence_quote, evidence_level, last_verified_date。
4. candidate_label 只能是 A0/A1/A2/B/C/D/X。
5. evidence_level 为 E4/E5 的记录不得进入 strong claim。
6. 证据不足写 needs_review.csv。
7. 输出 reports/evidence_pilot_readiness.md：只报告 pipeline readiness，不报告模型能力。

禁止：
- 不根据网页标题推断模型能力。
- 不根据模型名猜 mask_support。
- 不自动补 source_url。
- 不从 SEO blog 或第三方榜单生成强结论。
```

## 03.3 验收命令

```bash
python scripts/gpt_batch.py \
  --input data/raw/pages.jsonl \
  --prompt prompts/codex/extract_model_info.md \
  --output data/evidence/extracted_entries.jsonl \
  --dry-run

python scripts/audit_evidence.py data/evidence/extracted_entries.jsonl
python scripts/export_needs_review.py \
  --input data/evidence/extracted_entries.jsonl \
  --output data/evidence/needs_review.csv
pytest
```

---

# Step 04：后续深化顺序

只有 Step 00–03 全部通过后，才允许继续：

```text
Step 04：人工填入 20–30 个 official/paper/GitHub evidence pages
  ↓
Step 05：从 evidence 生成最小 registry，不允许猜 family
  ↓
Step 06：架构标签 review，unknown 优先，非 unknown 必须有 evidence_quote
  ↓
Step 07：构造 80-case benchmark data pilot，T01–T16 每类 ≥5
  ↓
Step 08：只接 1 个真实 adapter dry-run，验证 metadata/resume/cost/runtime/raw_response
  ↓
Step 09：Formal Pilot，5–8 模型，每模型 100–300 cases，不排名
  ↓
Step 10：Task-level Evaluation + Blind Human Review，不生成总榜
  ↓
Step 11：Core Smoke Gate，pilot go 后只跑 100 cases
  ↓
Step 12：Claim-manifest Report Gate，所有结论可追溯
```

---

# Step 05：最终 Stop Conditions

任何一条不满足，都必须输出 no_go / needs_review，而不是继续：

1. `data/runs/pilot_RUN_001.jsonl` 为空。
2. `benchmark_cases.csv` 有效 case <80。
3. `extracted_entries.jsonl` 为空。
4. `model_registry.jsonl` 为空。
5. `pilot_models.csv` 少于 5 个模型或多于 8 个模型。
6. run_generation 使用 mock adapter 却生成真实模型能力结论。
7. final_report_draft 包含未在 claim_manifest 中 `allowed_in_report=yes` 的强结论。
8. human_eval_batch 包含 model_id/model_name 或缺少评分字段。
9. 自动指标与人工评估覆盖不一致却生成 leaderboard。
10. product/API wrapper 与底层模型混入同一榜单。

---

# 给 Codex 的第一条立即执行指令

把下面整段直接交给 Codex：

```text
Use the local-image-edit-research skill.

当前阶段：Step 00 truth reconciliation
输入文件：现有仓库全部文件
目标产物：
- scripts/audit_repo_truth.py
- tests/test_truth_reconciliation.py
- tests/test_pilot_gate_empty_metadata_no_go.py
- tests/test_claim_manifest_record_counts.py
- tests/test_jsonl_integrity.py
- tests/test_benchmark_minimum_coverage.py
- reports/repo_truth_audit.md
- reports/claim_manifest.csv 更新
- reports/final_report_draft.md 更新
- reports/report_evidence_audit.csv 更新
- reports/missing_evidence_claims.csv 更新

硬规则：
1. 不新增任何真实模型能力、版本、API、价格、license 或论文结论。
2. 不新增真实模型数据。
3. 不跑真实 adapter。
4. 不跑 pilot。
5. 不跑 core。
6. 空 metadata 不得产生 gate_decision: go。
7. claim_manifest 中任何 record count claim 必须等于实际 JSONL record count。
8. benchmark <80 valid cases 时必须 no_go。
9. mock adapter 结果不得支持真实模型 capability claim。
10. 修改后运行 python scripts/validate_project_structure.py 和 pytest。

请执行：
1. 新增 scripts/audit_repo_truth.py。
2. 新增测试覆盖 pilot gate、claim_manifest record count、JSONL integrity、benchmark minimum count。
3. 如果 data/runs/pilot_RUN_001.jsonl 为空或无有效记录，把 reports/pilot_RUN_001_gate.md 保持/改为 no_go。
4. 如果 reports/claim_manifest.csv 里有与实际 metadata 或 gate 冲突的 claim，把 allowed_in_report 改为 no，并写 invalid_reason；不得删除证据审计痕迹。
5. 从 final_report_draft.md 删除或屏蔽 700 records、pilot gate go、7 draft model entries 等冲突 claim。
6. 生成 reports/repo_truth_audit.md。
7. 重新运行 scripts/audit_report_claims.py。
8. 输出 changed_files、commands_run、tests_passed、risks、requires_human_review、next_recommended_step。
```
