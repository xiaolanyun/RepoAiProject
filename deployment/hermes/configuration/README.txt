用途：存放不含真实凭据的 Hermes 配置模板。

`.env` 与 `config.yaml` 保留运行时原始文件名，但当前内容仅为占位符。
真实供应商凭据必须通过受控的本机密钥存储或部署系统注入，不得写入 Git。
模板允许访问已登记的内网测试服务；Agent 仍须从 `environment_rule/config/`
解析目标，按 `environment_rule/docs/UNATTENDED-SAFETY.md` 做主机校验、
L0～L4 判定和审计。`approvals.deny` 仅保留系统级危险命令，任务内可恢复的
清理依 L3 规则执行。实际 Hermes 运行配置需由部署过程应用本模板。

Purpose: non-secret Hermes configuration templates.

`.env` and `config.yaml` retain the original runtime filenames so that the
directory layout matches a deployment. Their current contents are placeholders,
not live configuration. Do not replace placeholders with real credentials in
the version-controlled working tree; inject them from the approved local secret
store or deployment system.
Private URL access in this template supports registered internal test services;
it does not authorize unregistered targets. Apply the environment inventory,
host verification, L0-L4 boundary, and audit for every action. The live Hermes
configuration must be updated through the deployment process to take effect.
