# Codex 研究修复与深化落地执行文档

> 项目：`local-image-edit-research`  
> 角色定位：Codex = Research DevOps Agent；人工 / ChatGPT = 研究裁判  
> 当前结论：**No-Go for research completion. Go for scaffold hardening and evidence pilot.**  
> 本文目的：先修复当前仓库中已经暴露的事实一致性、gate、claim、benchmark、adapter 问题，再按 Evidence → Registry → Benchmark → Adapter → Pilot → Evaluation → Report 的顺序深化研究。

---

## 0. 总控原则

Codex 必须把自己限定为工程执行代理，不得替代研究裁判。

### 0.1 绝对禁止

1. 不新增任何未经证据支持的模型事实。
2. 不编造模型能力、版本、API、价格、license、论文结论。
3. 不把 `API_wrapper`、`product_feature`、`demo`、`implementation` 算作独立 `model_family`。
4. 不跳过 Pilot 直接跑 Core。
5. 不在报告中输出未经 `claim_manifest.csv` 放行的强结论。
6. 不用 mock adapter 结果支持任何真实模型能力结论。
7. 不用重复 row 凑 benchmark / pilot 样本规模。
8. 不把空 metadata、空 benchmark 或 scaffold output 说成研究完成。

### 0.2 所有真实模型判断必须具备

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

### 0.3 强制执行顺序

```text
Step 00 Truth Reconciliation
  ↓
Step 01 Engineering Gate Hardening
  ↓
Step 02 Evidence Pilot
  ↓
Step 03 Registry From Evidence
  ↓
Step 04 Architecture Label Review
  ↓
Step 05 Benchmark Data Pilot
  ↓
Step 06 Single Real Adapter Pilot
  ↓
Step 07 Formal Pilot
  ↓
Step 08 Task-level Evaluation + Blind Human Review
  ↓
Step 09 Core Smoke Gate
  ↓
Step 10 Claim-manifest Report Gate
```

---

## 1. 当前必须修复的问题清单

以下问题必须作为 `Step 00` 优先修复。不要先接模型，不要跑实验。

| ID | 问题 | 严重性 | 修复目标 |
|---|---|---:|---|
| P0-1 | `README.md` 写 No-Go，但 `reports/pilot_RUN_001_gate.md` 显示 `gate_decision: go` | 阻断 | gate 必须由 metadata 生成；空 metadata 必须 no_go |
| P0-2 | `reports/claim_manifest.csv` 声称 pilot 有 700 records，但 `data/runs/pilot_RUN_001.jsonl` 当前为空或需本地复核 | 阻断 | claim manifest 必须与实际 record count 一致 |
| P0-3 | `data/benchmark/benchmark_cases.csv` 当前为空或不足 80 cases | 阻断 | benchmark 不足时不能 pilot/core |
| P0-4 | adapter registry 当前为空或只有 mock adapter | 阻断 | mock 只能验证 pipeline，不能支撑模型结论 |
| P0-5 | JSONL 可能不是一行一个 JSON object | 高 | 增加 JSONL parse gate |
| P0-6 | project structure validator 可能引用缺失文件 | 高 | clean clone 必须可复现通过 |
| P0-7 | 报告审计可能允许未登记强结论绕过 | 高 | 报告必须 claim_manifest 驱动 |

---

## 2. 每个 Step 的通用 Codex 工作流

每步必须独立分支，不允许一次性执行全计划。

```bash
git status
git checkout -b step-{NN}-{short-name}
```

执行 Codex 后必须运行：

```bash
python scripts/validate_project_structure.py
pytest
git diff --stat
git status
```

通过人工审查后再提交：

```bash
git add .
git commit -m "step {NN}: {short description}"
```

Codex 每步必须输出：

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

## 3. 统一 Codex 提示词模板

后续每个 Step 均使用本模板。

```text
Use the local-image-edit-research skill.

你是本仓库的 Research DevOps Agent，不是事实裁判。

当前阶段：{STEP_NAME}
输入文件：{INPUT_FILES}
目标产物：{OUTPUT_FILES}

硬规则：
1. 不新增任何真实模型能力、版本、API、价格、license 或论文结论。
2. 所有真实模型判断必须保留 source_url、evidence_quote、evidence_level、last_verified_date。
3. 证据不足写 unknown 或 needs_review。
4. wrapper/product/demo/implementation 不得算作独立 model family。
5. 不得跳过 pilot、smoke test、metadata audit。
6. 修改前先读 AGENTS.md、docs/project_rules.md、docs/data_contract.md。
7. 修改后运行相关 validator 和 pytest。
8. 输出 changed_files、commands_run、tests_passed、risks、requires_human_review。

请执行：
{TASK}
```

---

# Step 00：Truth Reconciliation，一致性修复

## 00.1 目标

把仓库恢复到可信、保守、可复现的状态。

当前阶段不接模型、不跑 benchmark、不生成研究结论。只修复事实冲突和 gate 漏洞。

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
- reports/pilot_RUN_001_gate.md 更新
- reports/claim_manifest.csv 更新
- reports/missing_evidence_claims.csv 更新
- reports/report_evidence_audit.csv 更新
- reports/repo_truth_audit.md

任务：
1. 新增 scripts/audit_repo_truth.py，用于审计仓库状态是否与 claim/gate 一致。
2. audit_repo_truth.py 至少检查：
   - data/runs/pilot_RUN_001.jsonl 是否为空。
   - reports/pilot_RUN_001_gate.md 的 gate_decision 是否与 pilot metadata record count 一致。
   - reports/claim_manifest.csv 中所有 metadata count claim 是否与实际 JSONL 行数一致。
   - data/benchmark/benchmark_cases.csv 是否为空或不足 80 条有效 case。
   - 所有 *.jsonl 是否为合法 JSONL：一行一个 JSON object。
   - mock adapter 输出不得支持任何真实模型 capability claim。
3. 如果 pilot_RUN_001.jsonl 为空，则 pilot_RUN_001_gate.md 必须改为：
   gate_decision: no_go
   blocking_reasons:
   - no pilot metadata records
4. 如果 claim_manifest.csv 包含“700 records”或“pilot gate go”但 metadata 不支持，必须：
   - 删除该 claim；或
   - allowed_in_report=no；并写 invalid_reason。
5. final_report_draft.md 不得保留任何真实模型优劣、pilot 成功、core 可运行的结论。
6. 新增测试，确保：
   - 空 metadata 不能产生 gate_decision: go。
   - claim_manifest 的 record count claim 必须等于实际 JSONL record count。
   - benchmark <80 valid cases 时 Benchmark Gate no_go。
   - JSONL 非法格式会失败。

禁止：
- 不得新增真实模型数据。
- 不得新增模型能力判断。
- 不得把 mock pilot 写成真实 pilot。
```

## 00.3 必须实现的 `audit_repo_truth.py` 行为

建议 CLI：

```bash
python scripts/audit_repo_truth.py \
  --pilot-metadata data/runs/pilot_RUN_001.jsonl \
  --pilot-gate reports/pilot_RUN_001_gate.md \
  --claim-manifest reports/claim_manifest.csv \
  --benchmark data/benchmark/benchmark_cases.csv \
  --output reports/repo_truth_audit.md
```

必须输出：

```text
repo_truth_decision: go | no_go
blocking_reasons:
- ...
warnings:
- ...
record_counts:
  pilot_RUN_001: <int>
  benchmark_cases: <int>
claim_conflicts:
- claim_id: ...
  reason: ...
```

## 00.4 本地验收命令

```bash
python scripts/audit_repo_truth.py \
  --pilot-metadata data/runs/pilot_RUN_001.jsonl \
  --pilot-gate reports/pilot_RUN_001_gate.md \
  --claim-manifest reports/claim_manifest.csv \
  --benchmark data/benchmark/benchmark_cases.csv \
  --output reports/repo_truth_audit.md

python scripts/audit_report_claims.py \
  --report reports/final_report_draft.md \
  --claim-manifest reports/claim_manifest.csv \
  --output reports/report_evidence_audit.csv \
  --missing reports/missing_evidence_claims.csv

python scripts/validate_project_structure.py
pytest
```

## 00.5 通过标准

- 空 pilot metadata 时，pilot gate 必须是 `no_go`。
- `claim_manifest.csv` 不得再允许与实际 metadata 冲突的 claim。
- benchmark 不足 80 条时，不得进入 pilot/core。
- JSONL 全部可逐行 parse。
- README、gate、claim manifest、final report 状态一致。

---

# Step 01：Engineering Gate Hardening

## 01.1 目标

让 clean clone 后结构验证、pytest、core 阻断、report audit 均可复现。

## 01.2 Codex 提示词

```text
Use the local-image-edit-research skill.

当前阶段：Step 01 engineering gate hardening
输入文件：现有仓库全部文件
目标产物：
- Makefile
- README.md 更新
- .github/workflows/ci.yml
- outputs/.gitkeep
- data/benchmark/source_images/.gitkeep
- data/benchmark/masks/.gitkeep
- data/registry/uncertain_cases.csv
- scripts/validate_project_structure.py 更新
- scripts/run_generation.py 更新
- scripts/block_core_without_pilot.py 更新或新增
- scripts/audit_report_claims.py 更新
- tests/test_core_blocking_in_run_generation.py
- tests/test_report_claim_audit_coverage.py

任务：
1. clean clone 后 python scripts/validate_project_structure.py 必须通过。
2. Makefile 必须提供 make check，等价于结构验证 + pytest。
3. run_generation.py 必须显式支持 --phase：pilot / core_smoke / core_full。
4. phase=core_smoke 或 core_full 时，必须要求 --pilot-gate 且 gate_decision: go。
5. phase=core_full 时，必须额外要求 --core-smoke-gate 且 gate_decision: go。
6. audit_report_claims.py 不得只依赖 CLAIM: 前缀，必须自动扫描强结论词：best, better, outperform, supports, recommend, conclusion, rank, leaderboard, 最好, 优于, 推荐, 排名, 结论。
7. 无 claim_manifest.csv 或 allowed_in_report != yes 的 claim 不得进入 final_report_draft.md。
8. 所有新增 gate 必须有测试。

禁止：
- 不新增真实模型事实。
- 不新增真实模型能力判断。
```

## 01.3 验收命令

```bash
make check

python scripts/block_core_without_pilot.py \
  --pilot-gate reports/pilot_RUN_001_gate.md

python scripts/run_generation.py \
  --phase core_smoke \
  --cases data/benchmark/core_cases_smoke_100.csv \
  --models data/registry/core_models_batch_01.csv \
  --output-dir outputs/core_SMOKE_TEST \
  --metadata data/runs/core_SMOKE_TEST.jsonl \
  --pilot-gate reports/pilot_RUN_001_gate.md
```

预期：当前 pilot gate 不满足时，core_smoke 必须失败或拒绝运行。

---

# Step 02：Evidence Pilot，不直接填模型榜

## 02.1 目标

建立第一版 evidence pipeline 的真实可审计样本。只做 20–30 页高质量来源，不追求模型数量。

## 02.2 输入来源规则

只允许以下来源进入第一轮：

```text
official documentation
official model card
official API documentation
paper / arXiv / conference paper
official GitHub repository README / release note
```

不允许以下来源支持强结论：

```text
SEO blog
third-party leaderboard
marketing copy without technical details
social media post
uncited claim
```

## 02.3 Codex 提示词

```text
Use the local-image-edit-research skill.

当前阶段：Step 02 evidence pilot
输入文件：
- data/raw/pages.jsonl
- data/raw/query_bank.csv
- prompts/codex/extract_model_info.md
- scripts/gpt_batch.py
- scripts/audit_evidence.py
- scripts/export_needs_review.py

目标产物：
- data/raw/pages.jsonl 更新或校验
- data/evidence/extracted_entries.jsonl
- data/evidence/needs_review.csv
- docs/decision_log.md 更新
- reports/evidence_pilot_summary.md
- tests/test_evidence_source_requirements.py

任务：
1. 不新增模型事实；只实现 pipeline 和 gate。
2. 确保 pages.jsonl 每条记录包含：source_url, retrieved_at, source_type, text 或 saved_path。
3. 确保 extracted_entries.jsonl 所有 A0/A1/A2 记录都有：source_url, evidence_quote, evidence_level, last_verified_date。
4. candidate_label 只能是：A0/A1/A2/B/C/D/X。
5. evidence_level 为 E4/E5 的记录不得进入 strong claim。
6. 证据不足的条目写入 needs_review.csv。
7. 输出 evidence_pilot_summary.md，总结：source count、source types、valid entries、blocked entries、needs_review count。
8. 不得根据网页标题推断模型能力。
9. 不得根据模型名猜 mask_support。
10. 不得自动补 source_url。

不要添加真实模型能力结论；只做 evidence pipeline 和 gate 层面的落地。
```

## 02.4 运行命令

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

## 02.5 通过标准

- `data/raw/pages.jsonl` 非空。
- 每条 page 有 `source_url`、`retrieved_at`、`source_type`、`text` 或 `saved_path`。
- `data/evidence/extracted_entries.jsonl` 非空。
- 所有 A0/A1/A2 都有 `source_url/evidence_quote/evidence_level/last_verified_date`。
- E4/E5 没有进入强结论。
- `needs_review.csv` 可以非空；非空说明 gate 工作正常。

---

# Step 03：Registry From Evidence

## 03.1 目标

从 evidence 生成最小 registry。不得手工猜 family，不得根据名字相似自动合并。

## 03.2 Codex 提示词

```text
Use the local-image-edit-research skill.

当前阶段：Step 03 registry from evidence
输入文件：
- data/evidence/extracted_entries.jsonl
- scripts/dedupe_candidates.py
- scripts/build_family_tree.py
- scripts/validate_registry_consistency.py

目标产物：
- data/registry/dedup_suggestions.jsonl
- data/registry/model_registry.jsonl
- data/registry/model_family.csv
- data/registry/model_version.csv
- data/registry/implementation.csv
- data/registry/uncertain_cases.csv
- docs/family_tree.md
- docs/decision_log.md 更新
- tests/test_registry_no_wrapper_family.py
- tests/test_registry_decision_reason_required.py

任务：
1. 从 extracted_entries.jsonl 生成 registry 草案。
2. 每个合并或不合并决定必须写 duplicate_reason 或 decision_reason。
3. wrapper/product/demo 不得注册为独立 model_family。
4. LoRA、quantized、fork、checkpoint 必须挂父模型，除非证据证明是独立 family。
5. 证据不足写 needs_review 并进入 uncertain_cases.csv。
6. family_tree.md 必须区分 family、version、implementation、wrapper、product、demo。
7. validate_registry_consistency.py 必须通过。

不要新增 evidence 中不存在的模型事实。
```

## 03.3 运行命令

```bash
python scripts/dedupe_candidates.py \
  --input data/evidence/extracted_entries.jsonl \
  --output data/registry/dedup_suggestions.jsonl

python scripts/build_family_tree.py \
  --input data/registry/dedup_suggestions.jsonl \
  --out-md docs/family_tree.md

python scripts/validate_registry_consistency.py
pytest
```

## 03.4 通过标准

- `model_registry.jsonl` 非空。
- wrapper/product/demo 没有进入 independent model family。
- 每个合并或不合并都有 `decision_reason`。
- 证据不足条目进入 `uncertain_cases.csv`。
- `docs/decision_log.md` 记录人工裁判待办。

---

# Step 04：Architecture Label Review

## 04.1 目标

建立架构标签表，但不允许猜测。未知就是 `unknown`。

## 04.2 Codex 提示词

```text
Use the local-image-edit-research skill.

当前阶段：Step 04 architecture label review
输入文件：
- data/registry/model_registry.jsonl
- data/evidence/extracted_entries.jsonl
- docs/taxonomy.md
- data/registry/architecture_labels.jsonl

目标产物：
- docs/taxonomy.md 更新
- data/registry/architecture_labels.schema.json
- data/registry/architecture_labels.jsonl
- data/registry/architecture_needs_review.csv
- scripts/validate_architecture_labels.py 更新
- scripts/export_architecture_review_queue.py 更新
- tests/test_architecture_unknown_rules.py

任务：
1. 非 unknown 架构标签必须有 evidence_quote。
2. 闭源模型 architecture_public 只能是 public / partial / unknown。
3. 不得根据公司名、模型名、营销文案猜测架构。
4. 标签集合必须包括：
   - base_architecture: G0-G9 或 unknown
   - control_mechanism: C_mask, C_auto_mask, C_box, C_scribble, C_reference, C_text_edit, C_multiturn, unknown
   - training_or_inference: T_finetuned, T_instruction, T_inversion, T_training_free, T_composite, T_closed, unknown
   - deployment: D_local, D_weights, D_api, D_web, D_seed, D_no_seed, D_versioned, D_unversioned, unknown
5. 证据不足写入 architecture_needs_review.csv。
```

## 04.3 运行命令

```bash
python scripts/validate_architecture_labels.py data/registry/architecture_labels.jsonl

python scripts/export_architecture_review_queue.py \
  --input data/registry/architecture_labels.jsonl \
  --output data/registry/architecture_needs_review.csv

pytest
```

---

# Step 05：Benchmark Data Pilot，80 cases

## 05.1 目标

建立最小可用 benchmark data pilot。此阶段不跑模型，不跑 core。

## 05.2 数据规模

| 项目 | 要求 |
|---|---:|
| 任务类型 | T01–T16 全覆盖 |
| 每任务 case | 至少 5 |
| 总 cases | 至少 80 |
| 图片来源 | 合成 / 自制 / 明确授权 |
| mask | 覆盖 high / medium / rough / none |
| prompt | 每 case 中英双语 |
| 版权 | `copyright_status != unknown` |
| 验收 | hash、prompt、preserve requirements 全部通过 |

## 05.3 任务类型

```text
T01 object replacement / 对象替换
T02 object removal / 对象删除
T03 object insertion / 对象新增
T04 color editing / 颜色修改
T05 material editing / 材质修改
T06 local style editing / 局部风格修改
T07 background replacement / 背景替换
T08 lighting editing / 光照修改
T09 expression or pose micro-edit / 表情姿态微调
T10 clothing edit / 服装编辑
T11 product image edit / 商品图编辑
T12 text-in-image edit / 图中文字编辑
T13 reference-guided insertion / 参考图插入
T14 multi-turn edit / 多轮编辑
T15 small object fine edit / 小物体精细编辑
T16 occlusion/reflection complex edit / 复杂遮挡反射编辑
```

## 05.4 Codex 提示词

```text
Use the local-image-edit-research skill.

当前阶段：Step 05 benchmark data pilot
输入文件：
- data/benchmark/source_images/
- data/benchmark/masks/
- data/benchmark/task_prompts.csv
- scripts/hash_assets.py
- scripts/build_benchmark_cases.py
- scripts/validate_benchmark_cases.py

目标产物：
- data/benchmark/image_hashes.csv
- data/benchmark/benchmark_cases.csv
- data/benchmark/core_cases_smoke_100.csv 仅从合格 cases 中抽样；不足 100 时不得伪造
- reports/benchmark_data_pilot_summary.md
- tests/test_benchmark_minimum_coverage.py
- tests/test_benchmark_no_duplicate_case_inflation.py

任务：
1. 建立 80-case benchmark data pilot。
2. 覆盖 T01–T16，每个 task 至少 5 个 case。
3. 所有图片必须是合成、自制或明确授权。
4. copyright_status 不能是 unknown。
5. 每个 case 必须有 expected_change 和 preserve_requirements。
6. 每个 image_sha256 和 mask_sha256 必须可复算。
7. mask_path 为空时，mask_sha256 应为空，mask_quality 必须为 none。
8. 禁止重复 row 凑样本规模。
9. 生成 benchmark_data_pilot_summary.md，列出 task 覆盖、mask 覆盖、语言覆盖、版权状态、重复检查结果。

不要跑模型，不要生成模型结论。
```

## 05.5 运行命令

```bash
python scripts/hash_assets.py \
  --root data/benchmark/source_images \
  --output data/benchmark/image_hashes.csv

python scripts/build_benchmark_cases.py \
  --images data/benchmark/source_images \
  --masks data/benchmark/masks \
  --prompts data/benchmark/task_prompts.csv \
  --output data/benchmark/benchmark_cases.csv

python scripts/validate_benchmark_cases.py data/benchmark/benchmark_cases.csv
pytest
```

## 05.6 通过标准

- `benchmark_cases.csv` 有至少 80 条有效 case。
- T01–T16 全覆盖。
- 所有图片 hash 可复算。
- `copyright_status != unknown`。
- 每个 case 有 `expected_change` 和 `preserve_requirements`。
- 不存在重复 row 扩样本。

---

# Step 06：Single Real Adapter Pilot

## 06.1 目标

只接入 1 个真实 adapter，用于验证 adapter contract，不做模型排名。

## 06.2 Codex 提示词

```text
Use the local-image-edit-research skill.

当前阶段：Step 06 single real adapter pilot
输入文件：
- scripts/adapters/base.py
- scripts/adapters/mock_adapter.py
- scripts/adapters/registry.py
- scripts/run_generation.py
- data/runs/run_metadata.schema.json
- scripts/audit_run_metadata.py
- tests/test_adapter_contract.py
- tests/test_run_generation_resume.py
- tests/test_metadata_integrity.py

目标产物：
- scripts/adapters/{adapter_name}_adapter.py
- scripts/adapters/registry.py 更新
- tests/test_{adapter_name}_adapter_contract.py
- reports/adapter_pilot_summary.md

任务：
1. 只接入 1 个 adapter。
2. 不新增任何模型能力判断。
3. adapter 必须支持 dry-run、resume、不覆盖、稳定 output path。
4. run_generation.py 必须通过 --adapter 显式选择 adapter。
5. metadata 必须包含：
   - source_image_sha256
   - mask_sha256
   - seed_requested
   - seed_effective
   - runtime_seconds
   - cost_usd
   - raw_response_path
   - status
   - adapter_name
   - model_id
   - version_lock 或 D_unversioned
   - version_risk
6. 失败状态必须结构化：failed / filtered / timeout / rate_limited / invalid_input。
7. 若版本不可锁定，必须写 D_unversioned 和 version_risk。
8. 输出 adapter_pilot_summary.md，说明支持项、缺口、风险。

不要跑 core，不要跑 full benchmark。
```

## 06.3 前置 gate

```bash
python scripts/validate_registry_consistency.py
python scripts/validate_architecture_labels.py data/registry/architecture_labels.jsonl
python scripts/validate_benchmark_cases.py data/benchmark/benchmark_cases.csv
pytest
```

## 06.4 dry-run 命令

```bash
python scripts/run_generation.py \
  --phase pilot \
  --adapter {adapter_name} \
  --cases data/benchmark/benchmark_cases.csv \
  --models data/registry/pilot_models.csv \
  --output-dir outputs/adapter_DRYRUN_001 \
  --metadata data/runs/adapter_DRYRUN_001.jsonl \
  --dry-run \
  --resume

python scripts/audit_run_metadata.py data/runs/adapter_DRYRUN_001.jsonl
pytest
```

## 06.5 通过标准

- adapter dry-run 通过。
- metadata audit 通过。
- resume 不重复生成、不覆盖已有结果。
- raw response path 稳定存在。
- 失败状态结构化。
- 没有新增未经证据支持的模型能力判断。

---

# Step 07：Formal Pilot，5–8 个模型

## 07.1 目标

正式 Pilot 的目标是发现 pipeline、prompt、mask、adapter、metadata、成本和版本风险，不是排名。

## 07.2 Codex 提示词

```text
Use the local-image-edit-research skill.

当前阶段：Step 07 formal pilot
输入文件：
- data/registry/model_registry.jsonl
- data/registry/architecture_labels.jsonl
- data/benchmark/benchmark_cases.csv
- scripts/select_pilot_models.py
- scripts/run_generation.py
- scripts/audit_run_metadata.py
- scripts/summarize_pilot.py
- scripts/export_failure_cases.py
- scripts/pilot_gate_decision.py

目标产物：
- data/registry/pilot_models.csv
- outputs/pilot_RUN_001/
- data/runs/pilot_RUN_001.jsonl
- data/runs/pilot_RUN_001_failures.csv
- reports/pilot_RUN_001_summary.md
- reports/pilot_RUN_001_gate.md

任务：
1. 只选择 5–8 个模型。
2. 不选择同一 family 的多个 wrapper。
3. 每模型只跑 100–300 cases。
4. 所有 run metadata 必须可审计。
5. failure_rate >40% 标记 core_candidate_no。
6. 缺 metadata 标记 blocked_from_core。
7. 输出 pilot summary 和 pilot gate。
8. gate 只能基于 metadata、failure_rate、cost、version_risk、coverage，不允许主观排名。
9. 不得从 mock adapter 结果写真实模型能力结论。

不要跑 core。
```

## 07.3 运行命令

```bash
python scripts/select_pilot_models.py \
  --registry data/registry/model_registry.jsonl \
  --architecture data/registry/architecture_labels.jsonl \
  --output data/registry/pilot_models.csv

python scripts/run_generation.py \
  --phase pilot \
  --adapter {adapter_name} \
  --cases data/benchmark/benchmark_cases.csv \
  --models data/registry/pilot_models.csv \
  --output-dir outputs/pilot_RUN_001 \
  --metadata data/runs/pilot_RUN_001.jsonl \
  --max-retries 3 \
  --resume \
  --cost-limit-usd 50

python scripts/audit_run_metadata.py data/runs/pilot_RUN_001.jsonl

python scripts/export_failure_cases.py \
  --metadata data/runs/pilot_RUN_001.jsonl \
  --output data/runs/pilot_RUN_001_failures.csv

python scripts/summarize_pilot.py \
  --metadata data/runs/pilot_RUN_001.jsonl \
  --output reports/pilot_RUN_001_summary.md

python scripts/pilot_gate_decision.py \
  --metadata data/runs/pilot_RUN_001.jsonl \
  --output reports/pilot_RUN_001_gate.md

pytest
```

## 07.4 通过标准

- `pilot_models.csv` 有 5–8 个模型。
- 没有同 family wrapper 重复进入 pilot。
- `pilot_RUN_001.jsonl` 非空。
- 所有成功/失败都有 metadata。
- 失败率、成本、版本风险写入 summary。
- `pilot_RUN_001_gate.md` 明确 `go` 或 `no_go`，且有原因。

---

# Step 08：Task-level Evaluation + Blind Human Review

## 08.1 目标

先做 task-level 分析和失败标签，不做总榜。

## 08.2 失败标签 taxonomy

建议字段：

```csv
failure_tag,definition,applies_to_task_ids,severity,example_case_id,review_notes
```

最低失败类型：

```text
model_failure
adapter_failure
prompt_failure
mask_failure
metadata_failure
safety_filter
version_drift
cost_or_timeout
locality_failure
preservation_failure
instruction_failure
visual_artifact
```

## 08.3 人工盲评字段

盲评表不得含 `model_name` 或 `model_id`。

```csv
blind_id,case_id,task_id,output_path,prompt,status,
instruction_following_score,locality_score,preservation_score,
visual_quality_score,artifact_score,safety_issue,failure_tags,
reviewer_id,reviewer_notes
```

私有 mapping 单独保存：

```text
data/eval/blind_mapping_private.csv
```

## 08.4 Codex 提示词

```text
Use the local-image-edit-research skill.

当前阶段：Step 08 evaluation without leaderboard
输入文件：
- data/runs/pilot_RUN_001.jsonl
- data/benchmark/benchmark_cases.csv
- scripts/compute_metrics.py
- scripts/sample_for_human_eval.py
- scripts/merge_human_eval.py
- scripts/audit_eval_coverage.py
- scripts/summarize_failure_tags.py

目标产物：
- data/eval/pilot_metrics.csv
- data/eval/human_eval_batch_001.csv
- data/eval/blind_mapping_private.csv
- data/eval/failure_tag_taxonomy.csv
- reports/pilot_eval_task_level_summary.md
- reports/pilot_failure_tags_summary.md
- tests/test_human_eval_blinding.py
- tests/test_no_leaderboard_on_coverage_mismatch.py

任务：
1. 不生成总榜。
2. 只生成 task_id 级别指标和覆盖情况。
3. 盲评表不得包含 model_name 或 model_id。
4. 如果自动指标和人工评估覆盖不一致，必须阻止 leaderboard。
5. failure tags 必须区分模型失败、adapter 失败、prompt 失败、mask 失败、metadata 失败。
6. OCR 指标只用于文字任务。
7. face identity 指标只用于授权或合成数据。
8. 输出 task-level summary 和 failure tags summary。

不要根据 pilot 结果写“某模型最好”。
```

## 08.5 运行命令

```bash
python scripts/compute_metrics.py \
  --metadata data/runs/pilot_RUN_001.jsonl \
  --output data/eval/pilot_metrics.csv

python scripts/sample_for_human_eval.py \
  --metadata data/runs/pilot_RUN_001.jsonl \
  --sample-per-task 30 \
  --blind \
  --output data/eval/human_eval_batch_001.csv \
  --mapping data/eval/blind_mapping_private.csv

python scripts/audit_eval_coverage.py \
  --metrics data/eval/pilot_metrics.csv \
  --human data/eval/human_eval_batch_001.csv

python scripts/summarize_failure_tags.py \
  --input data/eval/human_eval_batch_001.csv \
  --output reports/pilot_failure_tags_summary.md

pytest
```

---

# Step 09：Core Smoke Gate

## 09.1 目标

只让 formal pilot 通过者进入 core smoke。先 100 cases；不允许直接 1000–3000。

## 09.2 Codex 提示词

```text
Use the local-image-edit-research skill.

当前阶段：Step 09 core smoke gate
输入文件：
- reports/pilot_RUN_001_gate.md
- data/runs/pilot_RUN_001.jsonl
- data/registry/core_models_batch_01.csv
- data/benchmark/core_cases_smoke_100.csv
- scripts/select_core_candidates.py
- scripts/run_generation.py
- scripts/audit_run_metadata.py
- scripts/core_gate_decision.py

目标产物：
- data/registry/core_models_batch_01.csv
- outputs/core_SMOKE_001/
- data/runs/core_SMOKE_001.jsonl
- reports/core_SMOKE_001_gate.md
- tests/test_core_requires_pilot_go.py
- tests/test_core_full_requires_smoke_go.py

任务：
1. 无 pilot gate 或 pilot gate != go 时，禁止 core_smoke。
2. core_smoke 只跑 100 cases。
3. 无 core_smoke gate go 时，禁止 core_full。
4. 每 500 张 metadata audit 的逻辑必须为后续 core_full 预留。
5. version_unlocked、cost_over_limit、failure_rate_high、metadata_missing 必须单独标记。
6. 不得基于 smoke 直接生成总榜。
```

## 09.3 运行命令

```bash
python scripts/select_core_candidates.py \
  --pilot-gate reports/pilot_RUN_001_gate.md \
  --pilot-summary reports/pilot_RUN_001_summary.md \
  --output data/registry/core_models_batch_01.csv

python scripts/run_generation.py \
  --phase core_smoke \
  --adapter {adapter_name} \
  --cases data/benchmark/core_cases_smoke_100.csv \
  --models data/registry/core_models_batch_01.csv \
  --output-dir outputs/core_SMOKE_001 \
  --metadata data/runs/core_SMOKE_001.jsonl \
  --pilot-gate reports/pilot_RUN_001_gate.md \
  --max-retries 3 \
  --resume \
  --cost-limit-usd 50

python scripts/audit_run_metadata.py data/runs/core_SMOKE_001.jsonl

python scripts/core_gate_decision.py \
  --metadata data/runs/core_SMOKE_001.jsonl \
  --output reports/core_SMOKE_001_gate.md

pytest
```

---

# Step 10：Claim-manifest Report Gate

## 10.1 目标

报告可以自动生成，但结论不能自动放行。报告必须由 `claim_manifest.csv` 驱动。

## 10.2 claim_manifest 字段

```csv
claim_id,
claim_text,
claim_type,
strength,
source_type,
source_path,
source_url,
evidence_quote,
evidence_level,
run_metadata_ref,
eval_metadata_ref,
allowed_in_report,
invalid_reason,
reviewer,
review_status
```

## 10.3 Codex 提示词

```text
Use the local-image-edit-research skill.

当前阶段：Step 10 claim manifest report gate
输入文件：
- reports/final_report_draft.md
- reports/claim_manifest.csv
- scripts/render_report.py
- scripts/audit_report_claims.py
- data/evidence/extracted_entries.jsonl
- data/runs/pilot_RUN_001.jsonl
- data/eval/pilot_metrics.csv
- data/eval/human_eval_batch_001.csv

目标产物：
- reports/claim_manifest.csv 更新
- reports/final_report_draft.md 更新
- reports/report_evidence_audit.csv
- reports/missing_evidence_claims.csv
- tests/test_claim_manifest_gate.py
- tests/test_report_no_unmanifested_strong_claims.py

任务：
1. 没有 claim_manifest.csv，不生成 final_report_draft.md。
2. final_report_draft.md 中的关键结论必须来自 claim_manifest.csv。
3. claim_manifest 中 allowed_in_report != yes 的 claim 不得进入报告。
4. 每个 claim 必须能追溯到 evidence 或 run/eval metadata。
5. E4/E5 不得生成强结论。
6. product/API 结果不得和底层模型结果混榜。
7. 如果 metrics coverage 不一致，不生成总榜。
8. 报告必须包含：失败率、成本、版本风险、人工盲评覆盖、证据审计。
9. 如果 pilot/core 仍是 mock 或 metadata 不足，报告只能写 scaffold/no-go 状态。

不要新增数据表中不存在的结论。
```

## 10.4 运行命令

```bash
python scripts/render_report.py \
  --claim-manifest reports/claim_manifest.csv \
  --output reports/final_report_draft.md

python scripts/audit_report_claims.py \
  --report reports/final_report_draft.md \
  --claim-manifest reports/claim_manifest.csv \
  --output reports/report_evidence_audit.csv \
  --missing reports/missing_evidence_claims.csv

pytest
```

## 10.5 通过标准

- 没有 claim manifest 时报告生成失败。
- 每个结论都能追到 evidence 或 run/eval metadata。
- E4/E5 没有生成强结论。
- product/API 结果没有和底层模型结果混榜。
- metrics coverage 不一致时不生成总榜。
- 报告包含失败率、成本、版本风险、人工盲评覆盖、证据审计。

---

# 4. 给 Codex 的第一条任务：立即执行

把下面整段直接交给 Codex。

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
- reports/pilot_RUN_001_gate.md 更新
- reports/claim_manifest.csv 更新
- reports/missing_evidence_claims.csv 更新
- reports/report_evidence_audit.csv 更新
- reports/repo_truth_audit.md

硬规则：
1. 不新增任何真实模型能力、版本、API、价格、license 或论文结论。
2. 不新增任何真实模型数据。
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
3. 如果 data/runs/pilot_RUN_001.jsonl 为空或无有效记录，把 reports/pilot_RUN_001_gate.md 改为 no_go。
4. 如果 reports/claim_manifest.csv 里有与实际 metadata 冲突的 claim，把 allowed_in_report 改为 no，并写 invalid_reason；不得删除证据审计痕迹。
5. 重新运行 scripts/audit_report_claims.py。
6. 输出 changed_files、commands_run、tests_passed、risks、requires_human_review、next_recommended_step。
```

---

# 5. 人工审查清单

| Step | 人工审查重点 | Go 条件 |
|---|---|---|
| 00 | README、gate、claim、metadata 是否一致 | 无冲突 claim；空 metadata no_go |
| 01 | gate 是否不可绕过 | core 无法绕过 pilot/smoke |
| 02 | evidence 是否可追溯 | A0/A1/A2 全有 source_url/evidence_quote/evidence_level/last_verified_date |
| 03 | registry 是否去重正确 | wrapper/product/demo 不进 independent family |
| 04 | 架构标签是否猜测 | 非 unknown 必须有 evidence_quote |
| 05 | benchmark 是否真实 80 cases | T01–T16 覆盖，hash 可复算，版权明确 |
| 06 | adapter contract 是否可靠 | dry-run/resume/raw_response/cost/runtime/status 全通过 |
| 07 | pilot 是否小规模且可审计 | 5–8 模型，每模型 100–300 cases，metadata 完整 |
| 08 | 评估是否避免虚假总榜 | task-level summary；盲评真盲 |
| 09 | core 是否被 gate 控制 | pilot go 才 smoke；smoke go 才 full |
| 10 | 报告是否 claim-driven | 无未登记强结论；证据/metadata 可追溯 |

---

# 6. 最终控制线

当前研究不能被描述为“已完成”。在以下条件全部满足前，只能描述为：

```text
Engineering scaffold / evidence pilot in progress.
No-Go for research completion.
```

进入“研究结果可报告”的最低条件：

1. Step 00–05 全部通过。
2. 至少一个真实 adapter dry-run 和 metadata audit 通过。
3. Formal Pilot 真实运行且 metadata 非空。
4. Evaluation 有 task-level 指标和盲评覆盖。
5. Claim Manifest 中每个结论都有 evidence 或 run/eval metadata 支撑。
6. 报告审计没有 missing evidence claims。

任何一条不满足，报告只能输出 scaffold / no-go / needs_review 状态。
