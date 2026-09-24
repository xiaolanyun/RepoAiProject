# 安全边界 / Security Boundary

版本库可以保存环境定义、SSH 公钥主机指纹、凭据字段名和占位符，但不能保存真实
密码、API Key、Token、Cookie 或私钥。真实值只能通过获授权的本机密钥存储或部署
系统提供。

提交前必须特别检查 `environment_rule/credentials.env`、
`deployment/hermes/configuration/.env` 和测试执行产物。`company-docs/` 为已有的
只读参考资料；其中存在历史认证示例，未经资料所有者确认不得修改或上传到外部仓库。

---

The repository may retain environment definitions, verified SSH host identities,
credential variable names, and placeholders. It must not retain live passwords,
API keys, tokens, cookies, or private keys. Supply live values only from an
authorized local secret store or deployment system.

Review `environment_rule/credentials.env`,
`deployment/hermes/configuration/.env`, and test-run artifacts before every
commit. `company-docs/` is inherited read-only reference material; it contains
historic authentication examples and must not be modified or uploaded to an
external repository without the owner's confirmation.
