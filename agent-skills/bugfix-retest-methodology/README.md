# bugfix-retest-methodology

Bug 修复复测方法论（代码确认/部署确认/行为验证/基线残留陷阱/多环境交叉）。

## 安装与接入

### 目录约定

本 skill 目录可放置于任意 agent 的 skills 目录，例如：

- `~/.agents/skills/bugfix-retest-methodology/`（用户级，OpenCode/Hermes 等）
- 仓库级 `.agents/skills/bugfix-retest-methodology/`
- 框架共享目录（如 `<framework-root>\agent-skills\`）

只需保证目录内 `SKILL.md` 完整，agent 按 frontmatter 的 `name/description` 路由加载。

### 触发方式

当任务涉及以下关键词时加载本 skill：

- 复测 / 修复验证 / Bug 已修复 / 回归验证
- 重新验证 / 修复复现 / 部署后验证

### 配套运行时资源（使用前确认）

| 资源 | 用途 |
|---|---|
| 被测环境地址 + 已授权 credential_ref | 行为验证 |
| 代码仓库只读访问 | fetch + 修复提交 diff 确认 |
| 日志访问途径 | 500 异常定位 |
| 验证对象的当前基线 | 快照与恢复 |

## 与其他 skill 的关系

- `giteerepo-testing`：GiteeRepo 测试执行知识库（环境/登录/API 总纲）
- `one-notification-testing`：One 通知专项（其"错误与异常处理"引用了本方法论的判定规则）

## 版本

- 1.1：接入框架工作区、环境规则与证据位置；保留原有复测判定方法。
