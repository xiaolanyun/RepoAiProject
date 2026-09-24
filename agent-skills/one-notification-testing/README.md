# one-notification-testing

Repo↔One 消息通知集成测试执行知识库。

## 安装与接入

### 目录约定

本 skill 目录可放置于任意 agent 的 skills 目录，例如：

- `~/.agents/skills/one-notification-testing/`（用户级，OpenCode/Hermes 等）
- 仓库级 `.agents/skills/one-notification-testing/`
- 框架共享目录（如 `<framework-root>\agent-skills\`）

只需保证目录内 `SKILL.md` 完整，agent 按 frontmatter 的 `name/description` 路由加载。

### 触发方式

当任务涉及以下关键词时加载本 skill：

- One 通知 / 消息通知 / 通知渠道 / support-channel
- 通知降级 / 通知缓存 / 聚合发送 / messageType
- 通知方式配置 / 通知场景 / 通知对象

### 配套运行时资源（使用前向用户或环境确认）

| 资源 | 用途 |
|---|---|
| One 门户地址 + credential_ref | 获授权的认证与会话建立 |
| k8s 访问配置 | Pod 日志观测 |
| 应用认证头（App-Id/App-Secret/Username） | Pod 内 curl support-channel 验证 |
| Repo 事件触发入口 | 备份/垃圾回收等事件源 |

## 版本

- 1.1：将 46 版本经验改为待核验基线，并接入框架环境、脚本、证据与交付物规则。
