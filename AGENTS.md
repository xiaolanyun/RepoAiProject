# Team AI Framework Entry Rules

# 团队 AI 框架入口规则

处理本仓库任务前，先遵守以下规则。

## 必读顺序（中文）

1. 阅读本文件和根目录 `README.md`。
2. 需求、测试分析、用例、执行或报告任务读取 `agent-skills/giteerepo-test-delivery/SKILL.md`；开发者声称修复 Bug 后的复测另读 `agent-skills/bugfix-retest-methodology/SKILL.md`；Repo 到 One 通知任务另读 `agent-skills/one-notification-testing/SKILL.md`；新增或修改 GiteeRepo 测试环境先读 `agent-skills/giteerepo-environment-onboarding/SKILL.md`。
3. 先确定产品、版本、需求和交付类型，只读取相关资料，不加载无关历史文件。
4. 若本地提供了获批的产品文档，以需求关键词检索 `company-docs/gitee-docs/` 中的功能与接口资料；协议任务还应检索 `company-docs/protocol-guides/`。公开版不包含企业内部文档，缺失时记录限制，不能编造产品事实。仅读取 `workspace/` 中当前版本的需求、用例和报告。
5. 访问或操作环境时，先读 `environment_rule/README.txt`，再读本地配置的 `environment_rule/config/`、`environment_rule/docs/`、`environment_rule/bin/` 中的相关文件。公开版不包含具体环境清单及服务定义；若本地未配置，不得猜测目标或执行环境操作。

在 Hermes 容器中，`environment_rule/` 对应 `/workspace/envs/giteerepo/`，`agent-skills/` 对应 `/workspace/agent-skills/`，`company-docs/` 对应 `/workspace/company-docs/`，`workspace/` 对应 `/workspace/work/`；若实际布局不同，应先检查挂载，不能直接判定规则或配置缺失。

## 操作边界（中文）

- `environment_rule/config/` 是当前环境定义，`environment_rule/docs/UNATTENDED-SAFETY.md` 是执行安全边界。按任务与解析出的目标选择 SSH、HTTP、kubectl、数据库、协议客户端或脚本；不强制统一执行器。所有方式均遵守 L0～L4 与命令审计：L0～L3 在授权范围内执行，L4 阻断并记录。
- 配置中仅引用凭据；真实密码、API Key、令牌、Cookie 和私钥不得写入报告、脚本、用例或 Git。仅在任务需要时读取本地凭据机制，不输出无关凭据；若缺失，报告具体引用并请授权负责人通过获批的本地密钥存储提供。
- 修改测试环境前说明目标、操作、风险、恢复方案和证据位置，并遵守环境安全规则。
- `company-docs/` 仅供只读检索，Agent 不得修改。`environment/`、`test/`、`tools/` 是废弃目录，不用于新任务；改用 `environment_rule/` 和 `test_run/`。不得把 `archive/` 或历史任务产物当作当前事实。

## 交付边界（中文）

仅提供用户要求的交付物，例如澄清后的需求与疑问、测试用例、测试点、执行计划、证据或测试报告。生成或修改用例及测试点时，遵守测试交付 Skill 的格式规则。

Apply these rules before handling work in this repository.

## Mandatory discovery order

1. Read this file and the root `README.md`.
2. For requirements, test analysis, test-case design, test execution, or test
   reporting, read `agent-skills/giteerepo-test-delivery/SKILL.md`.
   For a developer-provided bug fix, also read
   `agent-skills/bugfix-retest-methodology/SKILL.md`; for Repo-to-One
   notification work, also read `agent-skills/one-notification-testing/SKILL.md`.
   For adding or changing a GiteeRepo test environment, read
   `agent-skills/giteerepo-environment-onboarding/SKILL.md` before editing
   environment files.
3. Identify the task's product, version, requirement, and delivery type before
   reading additional material. Do not load unrelated historical files.
4. When approved local product documents are available, search
   `company-docs/gitee-docs/` by requirement keywords to find basic
   functionality and interface information. For protocol work, also search
   `company-docs/protocol-guides/`. The public distribution intentionally
   excludes proprietary documents; if they are absent, record that limitation
   rather than inventing product facts.
5. Read only the requirement, test case, and report materials relevant to the
   requested version under `workspace/`.
6. For environment access or execution, read `environment_rule/README.txt`,
   then the locally provisioned relevant files under `environment_rule/config/`,
   `environment_rule/docs/`, and `environment_rule/bin/`. The public edition
   excludes site-specific inventory and service definitions; missing local
   configuration blocks environment actions and must not be guessed.

When running inside the Hermes container, resolve framework paths as follows:
`environment_rule/` = `/workspace/envs/giteerepo/`, `agent-skills/` =
`/workspace/agent-skills/`, `company-docs/` = `/workspace/company-docs/`, and
`workspace/` = `/workspace/work/`. If the container layout differs, inspect
the actual mounts before concluding that a rule or configuration is missing.

## Operating boundaries

- Treat `environment_rule/config/` as the current environment definition and
  `environment_rule/docs/UNATTENDED-SAFETY.md` as the execution safety boundary.
- Choose SSH, HTTP, kubectl, database, protocol client, or a task script from
  the resolved target and task needs. No unified runner or runner-policy file is
  required. Apply the same L0-L4 boundary and command audit to every method:
  L0-L3 proceed within scope; L4 is blocked and recorded.
- Use credential references from configuration. Never place real passwords,
  API keys, tokens, cookies, or private keys in a report, script, test case,
  or Git change.
- Read the local credential mechanism only when the task needs it; do not dump
  unrelated credentials. If required credentials are unavailable, report the
  missing credential reference and request the authorized setup owner to supply
  it through the approved local secret store.
- Before modifying a test environment, state the target, action, risk, restore
  plan, and evidence location. Follow the environment safety rules.
- Treat `company-docs/` as read-only reference material. It may be searched for
  functionality and API facts but must never be edited by an Agent.
- `environment/`, `test/`, and `tools/` are retired empty legacy directories;
  never use them for new work. Use `environment_rule/` and `test_run/`.
- Do not use `archive/` or historical task artifacts as current facts.

## Required deliverables

Choose only the deliverables requested by the user: clarified requirements and
open questions, test cases, test points, an execution plan, evidence, and/or a
test report. Use the test-delivery Skill's format rules whenever generating or
changing test cases or test points.
