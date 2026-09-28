---
name: giteerepo-test-delivery
description: Analyze GiteeRepo requirements, design import-ready test cases and OPML test points, execute scoped tests, and produce evidence-based reports. Use for Repo test design, execution, or reporting; not for unrelated software work.
---

# GiteeRepo Test Delivery

## 中文说明

先按仓库 `AGENTS.md` 的入口规则定位任务对应的需求、产品资料和环境文件，再使用本技能。`AGENTS.md` 所在目录即框架根目录。需求、用例、测试点与交付报告放在 `workspace/` 的对应版本下；执行脚本放在 `test_run/_scripts/`，证据和结构化结果分别放在 `test_run/evidence/`、`test_run/results/` 的任务专属目录。

`company-docs/` 仅是只读背景资料，不能当作环境来源。公开版不包含企业内部文档及具体环境配置，缺失时必须说明限制，不得猜测。访问或修改环境时使用 `environment_rule/` 及其安全规则，不得回退到废弃的 `environment/`、`test/`、`tools/` 或历史归档目录。

工作流程：

1. 确认产品、版本、需求 ID、已明确的行为、排除项和验收标准；仅用任务关键词检索产品与接口资料。
2. 生成测试内容前识别会改变预期的歧义；已获用户确认的口径复用，不重复询问。未说明的假设标记为待确认，不写成事实。
3. 生成或修改测试用例、测试点时阅读 [测试用例与测试点输出规范](references/test-case-and-point-output.md)。
4. 执行前按任务核对目标、认证身份、访问范围、基线状态、证据路径和恢复方法。修改环境前说明目标、动作、风险、恢复方案和证据位置。
5. 仅执行已获授权且可行的范围；结论分开描述配置核查、实际运行行为和测试框架就绪程度。
6. 报告需有证据支撑，包含范围、环境、方法、结果、缺陷或风险、恢复结果和未解决事项；不得包含密钥。

任务操作脚本按生命周期分类：`preflight/` 负责只读就绪检查与基线记录，`execution/` 负责任务范围内的操作，`verification/` 负责独立回读和断言，`recovery/` 负责恢复清理，`utilities/` 存放复用工具。改变环境的脚本需配套恢复步骤、记录恢复后验证结果，且不得内嵌凭据。

不得编造接口能力、需求、预期结果或测试数据。因权限、环境访问或预期歧义无法推进时说明具体阻塞。测试点只写“测什么”；完整前置条件、步骤、数据和预期放在测试用例中。

Use this skill after the repository entry rules in `AGENTS.md` have routed the
task to the relevant requirement, product documentation, and environment files.

## Framework locations

Treat the directory containing `AGENTS.md` as the framework root. Requirements,
test cases, test points, and delivery reports belong under the relevant version
in `workspace/`. Put execution scripts in `test_run/_scripts/`, evidence in a
task-specific directory under `test_run/evidence/`, and structured results or
execution reports under `test_run/results/`.

`company-docs/` is read-only background material, not an environment source.
For any environment access or mutation, use `environment_rule/` and its safety
rule; never fall back to the retired `environment/`, `test/`, `tools/`, or
historical archive directories.

## Workflow

1. Establish the requirement facts: product, version, requirement ID, stated
   behavior, exclusions, and acceptance criteria. Search product and API
   documentation only with task-specific keywords.
2. Identify expectation-changing ambiguities before generating tests. Reuse a
   user-confirmed decision in later work; do not ask it again. Mark unspecified
   assumptions as unresolved rather than presenting them as facts.
3. When asked for test cases or test points, read
   [test-case-and-point-output.md](references/test-case-and-point-output.md).
4. Before execution, perform a task-scoped preflight: confirm the test target,
   authenticated identity, access scope, baseline state, evidence path, and
   restoration method. State the intended target, action, risk, restore plan,
   and evidence location before any environment mutation.
5. Execute only the authorized, feasible subset. Separate configuration review,
   observed runtime behavior, and test-framework readiness in the conclusion.
6. Produce an evidence-based report: scope, environment, method, results,
   defects or risks, restoration result, and unresolved items. Never include
   secrets in a deliverable.

## Script workspace

Put task-operation scripts in `test_run/_scripts/` by lifecycle:

- `preflight/` for read-only readiness and baseline capture;
- `execution/` for task-scoped operations;
- `verification/` for independent read-back and assertions;
- `recovery/` for restoration and cleanup;
- `utilities/` for reusable helpers.

An environment-changing script requires a paired recovery step, recorded
post-restore verification, and no embedded credential value.

## Deliverable boundaries

- Do not invent API capabilities, requirements, expected results, or test data.
- Explain when an item is blocked by missing authority, environment access, or
  an unresolved expectation.
- Keep test points concise: they say what to test, while test cases carry full
  conditions, steps, data, and expected results.
