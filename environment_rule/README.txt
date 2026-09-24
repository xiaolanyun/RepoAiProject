用途：GiteeRepo 团队测试环境的统一规则目录。

本目录集中维护环境主机、服务、协议、SSH 主机身份校验、远程操作安全规则和
校验工具，供团队成员按同一套环境定义接入与执行。`credentials.env` 仅保留
凭据字段和占位符；真实值必须从受控本机密钥存储或部署系统取得。

新增测试环境时：维护 config 中的主机与服务条目，登记 credential_ref，向
受控密钥存储添加实际值，核验 SSH 指纹并更新 known_hosts，最后运行配置校验。
向 AI 提出新增环境任务时，应提供环境用途、测试属性、服务地址、SSH 信息、
执行主机、credential_ref 和已验证的 SSH 指纹；不要在对话中粘贴密码或私钥。

Purpose: the team-maintained GiteeRepo environment rule set.

This directory is the operational source for environment inventory, services,
protocol configuration, SSH host verification, remote-operation safety rules,
and validation utilities. It intentionally keeps these related materials in
one place so members can onboard consistently.

Contents:
- config/: registered test hosts, services, protocols, and execution policy.
- docs/: unattended-operation safety boundary.
- bin/: configuration query and validation helpers.
- ssh/config and ssh/known_hosts: SSH client settings and verified host identities.
- credentials.env: the required credential variable names only; values are
  placeholders.

Local-only files, never committed:
- real credential values: supplied through the approved local secret store or
  deployment system, not saved to this version-controlled file.
- ssh/hermes_ed25519 and any private-key material.

Adding a test environment manually:
1. Add the host entry to config/inventory.yaml.
2. Add its service and credential_ref mapping to config/services.yaml.
3. Add credential values only through the approved local secret store.
4. Add the verified public host key to ssh/known_hosts and the SSH alias to ssh/config.
5. Run bin/validate-config.py. Use StrictHostKeyChecking when testing access.

To delegate this to AI, provide the environment purpose, test/non-production
designation, service URL, SSH host/port/user, execution host, credential_ref,
and the verified SSH host fingerprint. Do not paste passwords or private keys
into an AI prompt; provide them only through the approved local secret store.
