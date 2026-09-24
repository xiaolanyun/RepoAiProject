用途：存放不含真实凭据的 Hermes 配置模板。

`.env` 与 `config.yaml` 保留运行时原始文件名，但当前内容仅为占位符。
真实供应商凭据必须通过受控的本机密钥存储或部署系统注入，不得写入 Git。

Purpose: non-secret Hermes configuration templates.

`.env` and `config.yaml` retain the original runtime filenames so that the
directory layout matches a deployment. Their current contents are placeholders,
not live configuration. Do not replace placeholders with real credentials in
the version-controlled working tree; inject them from the approved local secret
store or deployment system.
