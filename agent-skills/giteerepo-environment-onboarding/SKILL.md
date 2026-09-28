---
name: giteerepo-environment-onboarding
description: Register or update a declared GiteeRepo test environment using the team environment rule, credential references, verified SSH host identity, and configuration validation. Use only for explicit environment onboarding or change requests.
---

# GiteeRepo Test Environment Onboarding

## 中文说明

仅当用户明确要求新增或修改指定测试环境时使用本技能。编辑前阅读 `environment_rule/README.txt`、`config/inventory.yaml`、`config/services.yaml`、`docs/UNATTENDED-SAFETY.md`；涉及协议资源时再读 `config/protocols.yaml`。环境接入不依赖统一执行器或其策略文件。公开版的具体环境文件需由使用者在本地提供，缺失时不能推测。

框架根目录以 `AGENTS.md` 所在目录为准。唯一有效的环境来源是 `environment_rule/`，不得用废弃的 `environment/`、`tools/` 或归档文件替代。修改前在当前任务工作区记录目标、拟修改文件、风险等级、恢复方案和证据位置。可重复操作脚本放入 `test_run/_scripts/`，证据与结果分别保存在 `test_run/evidence/`、`test_run/results/` 的任务专属目录。

必需信息包括环境名称、测试或非生产属性、用途、SSH 主机/端口/用户、服务 URL、执行主机、凭据引用和已验证的 SSH 主机指纹。Kubernetes 服务还需要执行主机、kubeconfig 和 namespace。不得猜测环境属性、SSH 目标或主机密钥；缺少信息时报告确切字段。

受控更新步骤：

1. 仅在 `config/inventory.yaml` 新增或更新指定主机。
2. 仅在 `config/services.yaml` 新增或更新相关服务；凭据使用 `credential_ref` 引用，不写明文。
3. 将已验证的 SSH 别名写入 `ssh/config`、主机身份写入 `ssh/known_hosts`。
4. 凭据值只能通过获批的本地密钥存储添加，不得写入 Git 跟踪文件、报告或 AI 消息。
5. 运行 `bin/validate-config.py`；必要时用 `bin/render-docs.py` 更新本地派生文档，不能把生成结果当作事实来源。
6. 记录目标、修改文件、校验结果和待完成的访问验证。连接时遵守 L0～L4 及严格主机校验；若配置校验、主机身份验证或获批的凭据引用缺失，报告缺项并停止，不得猜测或添加占位主机身份。

只有配置校验通过、授权本地密钥存储中存在对应凭据引用且 SSH 主机身份已验证，才可称环境就绪。服务故障或不可用应报告为环境状态，不得靠猜测或绕过安全规则“修复”。

Use this skill only when the user explicitly asks to add or change a named test
environment. Read `environment_rule/README.txt`, `config/inventory.yaml`,
`config/services.yaml`, and `docs/UNATTENDED-SAFETY.md` before editing anything.
Read `config/protocols.yaml` when onboarding protocol resources. The unified
runner and its policy file are not required for environment registration.

## Framework boundary

Resolve all paths from the framework root containing `AGENTS.md`. The only
current environment source is `environment_rule/`; never use the retired
`environment/`, `tools/`, or archived files as a substitute. Before changing a
test environment, record the named target, intended files, risk level, restore
plan, and evidence location in the current task workspace. Use
`test_run/_scripts/` for any repeatable preflight, update, verification, or
recovery script; keep its evidence and result in task-specific directories under
`test_run/evidence/` and `test_run/results/`.

## Required input

Collect or identify: environment name and test/non-production designation,
purpose, SSH host/port/user, service URL, execution host, credential reference,
and verified SSH host fingerprint. For Kubernetes services also require the
execution host, kubeconfig, and namespace.

Do not infer a production/test classification, an SSH target, or a host key. If
information is missing, report the exact missing field rather than inventing it.

## Controlled update

1. Add or update only the specified host in `config/inventory.yaml`.
2. Add or update only the related service in `config/services.yaml`; reference
   credentials by `credential_ref`, never by literal value.
3. Add the verified SSH alias to `ssh/config` and host identity to
   `ssh/known_hosts`.
4. Add credential values only through the approved local secret store; do not
   write them into Git-tracked files, a report, or an AI message.
5. Run `bin/validate-config.py`. If relevant, regenerate local derived
   documentation using `bin/render-docs.py` without treating generated output
   as the source of truth.
6. Record target, files changed, validation result, and any remaining access
   verification. Follow L0-L4 and strict host verification for any connection.
   If validation, host verification, or the permitted credential reference is
   unavailable, stop with the exact missing item; do not guess or add a
   placeholder host identity.

## Completion criteria

The environment is ready only when configuration validation passes, the
credential reference exists in the authorized local secret store, and the SSH
host identity is verified. A failed or unavailable service must be reported as
an environment condition, not fixed by guessing or bypassing safety rules.
