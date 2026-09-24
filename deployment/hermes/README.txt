用途：Hermes 部署资产总说明。

本目录按职责分为三类：container 存放镜像与启动定义，configuration
存放非敏感运行配置模板，governance 存放团队行为与操作规范。真实 .env、
访问令牌、运行数据库、日志和会话记录均不得提交 Git。

Hermes deployment assets are grouped by responsibility:

- container: image build files and Docker Compose definitions.
- configuration: non-secret runtime configuration templates.
- governance: team behavior, operating conventions, and agent rules.

Copy configuration templates locally before editing them. Do not add live .env
files, access tokens, runtime databases, logs, or session records to Git.
