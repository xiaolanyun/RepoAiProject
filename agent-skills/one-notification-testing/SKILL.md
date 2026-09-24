---
name: one-notification-testing
description: Test Repo↔One notification integration: channel enable/disable control, support-channel gateway verification, channel cache TTL, aggregated sending observation, multi-tenant isolation, and fallback behavior. Use when testing One notification delivery, verifying notification bugfixes, or configuring notification channels on a GiteeRepo+One platform.
metadata:
  version: "1.0"
  source_task: "46版本-对接One获取消息通知方式接口"
---

# One 消息通知集成测试执行

测试 Repo 业务事件 → One 渠道获取（support-channel）→ 本地缓存 → 聚合发送 → 站内信到达的完整链路，以及渠道启停/降级/多租户隔离行为。

## 何时使用

- 测试 Repo 与 One 的通知集成功能（渠道获取/缓存/聚合发送/降级）
- 验证通知相关 Bug 修复（support-channel 路由/渠道分类/租户限速）
- 配置或验证 One 通知渠道（启停/新建/通知对象）

## 核心业务概念

| 概念 | 说明 |
|---|---|
| support-channel | Repo 调 One 获取租户启用通知渠道的接口；返回 channelCode/isEnable/effectiveFrom(GLOBAL/LOCAL/NONE) |
| 渠道启停控制点 | **平台级**通知方式配置页的行开关控制 isEnable；企业级"邮件服务配置"开关**不改变** isEnable |
| 渠道缓存 | Guava 本地缓存，key=租户 tenantKey；TTL 默认 300s（expireAfterWrite 读不续期）；**多 Pod 部署时各 Pod 独立** |
| 聚合发送 | 单次 POST `/api/rest/v1/companies/{tenant}/notifications/send?messageType=repo-{eventKey}`；Body 含 userIds/notifyRole/各启用渠道字段 |
| 渠道分类 | internal→INTERNAL{isHtml,content,url}；channelCode contains("email")忽略大小写→EMAIL{theme,content}；其余→默认文本（WECHAT）；Body 字段名=channelCode 原样 |
| 降级 fallback | 渠道获取失败（code≠0/payload null/空启用集合/超时/连接异常）→ 默认降级渠道（channelFallback 配置，默认 internal,workWeiXin,email）；**失败结果不缓存** |
| 接收人三方交集 | Repo 侧 userIds + notifyRole（事件类型决定：备份类=RepoCompanyManager，配额类=RepoProjectManager）+ One 侧渠道通知配置用户 |
| messageType | `repo-` + eventKey（backupTask/cleanupTask/storageTask/projectStorageQuota/scanCronTask/clearDimensionTask/repoAsyncTask 等） |

## 输入参数（运行时确认，不写死）

- One 平台地址与企业标识（如测试环境门户域名）
- 登录账号凭证（从用户提供或凭证库获取，**不写入任何产出物**）
- 目标租户（当前企业 + 对照租户）
- k8s 访问配置（观察 Pod 日志用）
- 被测 Repo 的通知事件入口

## 执行流程

### 1. 登录与环境确认

- One 门户为 Keycloak SSO 登录（UI 表单登录后保存 storage_state 复用会话；API 直调登录不可行）
- 会话过期特征：Repo UI API 返回 401 → 重新 UI 登录刷新 state
- 确认 Repo 页脚版本号与修复部署状态（多副本时注意 Pod 启动时间，滚动期请求可能命中新旧不同实例）

### 2. 渠道配置与验证

```
平台通知方式配置页（渠道启停/新建/删除；isEnable 控制）
  └─ 典型路径：平台管理 → 通知配置 → 通知方式（行开关 + 新建通知方式按钮 + 行操作下拉菜单）
企业通知设置页（通知场景/通知对象：用户/角色；不改 isEnable）
  └─ 典型路径：企业设置 → 通知与公告 → 通知设置（email/internal 页签）
```

**渠道启停验证闭环**：平台页切换开关 → 从 Repo Pod 内 curl 网关 support-channel 接口确认 isEnable 变化 → 触发通知看聚合 Body 渠道字段增减。

### 3. 事件触发（选择立即可执行的事件源）

| 事件 | 触发方式 | 特性 |
|---|---|---|
| 备份策略 | API：创建备份配置 + 运行接口 | **同 key 有约 5 分钟执行间隔**——不适合连续验证 |
| 垃圾回收 | API：执行定时任务接口（任务名=垃圾清理类任务） | 立即执行，可连续触发——**验证缓存/渠道的首选** |
| 平台存储告警 | 通用设置开启配额+低阈值+等待定时检查 | 触发延迟不可控 |
| 扫描漏洞通知 | 需扫描命中安全策略违规（策略+制品+扫描） | 配置复杂；受制品大小上传限制 |

### 4. 日志观测（核心断言手段）

在 Repo 服务 Pod 日志中按以下 INFO 级关键词检索（多副本需逐 Pod 查，通知可能路由到任一副本）：

| 日志关键词 | 含义 |
|---|---|
| `getNotificationSupportChannel request url` | 渠道回源调用（出现=回源；TTL 内不出现=缓存命中） |
| `sendAggregatedMessageToOne request url` | 聚合发送 URL（company/messageType 断言） |
| `sendAggregatedMessageToOne request body` | 聚合 Body（渠道字段/结构/userIds/notifyRole 断言；Body 含真实换行需多行提取） |
| `sendAggregatedMessageToOne result` | One 响应（code=0 成功；count 字段非接收人数） |
| `load enabled notification channels failed, fallback to defaults` | 降级发生（全禁用/接口异常） |
| `No user was matched` | 接收人交集为空→不发送（降级渠道在 One 无有效用户时的合理行为） |

### 5. 缓存 TTL 验证方法

1. 触发事件 A（时刻 T0）→ 日志出现 SC 调用（回源+缓存写入）
2. **TTL 内**（T0+300s 前）再触发 → SC 调用=0 且渠道集合不变（缓存命中）
3. TTL 内修改 One 渠道配置再触发 → 渠道集合仍为旧值（用旧缓存）
4. TTL 过期后（T0+300s 后）触发 → SC 调用重新出现且渠道反映新配置

**多 Pod 注意**：本地缓存按 Pod 独立。跨 Pod 验证时表现为"改配置立即生效"——这是另一 Pod 无缓存回源，非缓存失效。同 Pod 验证需连续多次触发提高命中同 Pod 概率。

### 6. 多租户对照

- 切换企业：直接访问目标企业路径（`/{企业标识}/_detail`）→ 若无权限页提示则点"切换并访问" → 会话进入目标租户
- 租户上下文由会话决定（API 路径不带租户前缀）
- 验证断言：发送 URL 的 company、SC 回源 URL 的租户段、通知正文链接前缀均为目标租户标识；两租户渠道配置互不影响

### 7. 到达验证

站内信收件箱 API（当前用户收件列表）核对消息内容/时间/链接与聚合 Body 的 internal 字段一致。

## 校验清单

- [ ] support-channel 经网关返回 code=0 且渠道数据正确（Pod 内 curl 带应用认证头）
- [ ] 渠道启停后 isEnable 与聚合 Body 渠道字段同步变化
- [ ] 缓存验证三态齐备：回源/命中/过期刷新（TTL 内 SC 调用=0 为命中铁证）
- [ ] 聚合为单次 POST，messageType=repo-{eventKey}，company=当前租户
- [ ] 自定义渠道分类正确（含 email 字符串→EMAIL 结构；其余→文本；字段名=channelCode 原样）
- [ ] 降级场景有日志实锤（fallback 关键词）且降级集合=默认三渠道
- [ ] 站内信实际到达且内容与 Body 一致
- [ ] 通知渠道/策略/场景配置测试后已恢复并回读确认

## 错误与异常处理

| 现象 | 定位 |
|---|---|
| support-channel 返回"接口地址不存在" | 网关未注册该接口路由：先从 Pod curl One 服务直连路径确认接口本身存在，再对照网关路径风格，向研发提供"直连通/网关 404"对照证据 |
| 事件触发后无任何通知日志 | 请求可能路由到另一副本——逐 Pod 拉日志；或触发未真正执行（同 key 间隔限制） |
| 编辑远程仓库返回 500 JsonParseException | 密级校验环节拉取仓库远程 URL 返回 HTML（非 JSON）——该仓库 URL 配置问题，与高优/通知写入逻辑无关，换远程 URL 可达的仓库验证 |
| 渠道启停不生效 | 确认操作的是平台级通知方式页开关（企业级邮件服务开关不控制 isEnable） |
| 401 会话过期 | 重新 UI 登录刷新 storage_state（Keycloak SSO 有时效） |

## 安全边界

- 通知渠道启停/新建/删除测试后**恢复原状**（测试新建的渠道删除，原有开关状态恢复，截图留证）
- 通知场景通知对象配置变更后恢复；用户级配置（收件箱已读状态等）不主动修改
- 凭证（账号/密码/应用 AppSecret）只从运行时获取，不写入 Skill/报告/日志
- Pod 内 curl 的应用认证头属敏感信息，验证命令由用户提供或从环境配置读取，不落盘

## 示例

**场景：验证"禁用邮件渠道后聚合发送不含 email 字段"**

1. 平台通知方式页关闭 email 行开关（截图）
2. Pod 内 curl 网关 support-channel → 确认 email isEnable=0
3. API 触发垃圾回收事件
4. 逐 Pod 拉日志：聚合 Body 含 internal/workWeiXin 等启用渠道字段、无 email=、messageType=repo-cleanupTask
5. 恢复 email 开关并回读确认

**边界：全部渠道禁用**

期望日志出现 `load enabled notification channels failed, fallback to defaults`（降级实锤）；随后可能因降级渠道在 One 无有效接收人出现 `No user was matched` 而不发送——属合理行为，不算降级失败。

## 禁止事项

- 禁止把企业级"邮件服务配置"开关当作渠道 isEnable 控制点
- 禁止用备份事件验证缓存 TTL（执行间隔与 TTL 同量级造成假象）
- 禁止以"回读值非空"判断写入是否发生（须对比传入值与基线值，参见 bugfix-retest-methodology skill）
- 禁止跳过环境恢复直接结束
