---
name: one-notification-testing
description: "Test Repo↔One notification integration: channel control, support-channel verification, cache behavior, aggregated sending, tenant isolation, and fallback. Use only when the current Repo version integrates with One; verify version-specific routes, configuration, and behavior before asserting them."
metadata:
  version: "1.1"
---

# One 消息通知集成测试执行

测试 Repo 业务事件 → One 渠道获取（support-channel）→ 本地缓存 → 聚合发送 → 站内信到达的完整链路，以及渠道启停/降级/多租户隔离行为。

## 何时使用

- 测试 Repo 与 One 的通知集成功能（渠道获取/缓存/聚合发送/降级）
- 验证通知相关 Bug 修复（support-channel 路由/渠道分类/租户限速）
- 配置或验证 One 通知渠道（启停/新建/通知对象）

## 框架接入与版本确认

先遵循框架根目录的 `AGENTS.md`，再读取
`giteerepo-test-delivery/SKILL.md`；通知修复复测还要读取
`bugfix-retest-methodology/SKILL.md`。需求、测试用例、测试点和报告放在当前
版本的 `workspace/` 目录；可复用操作脚本、执行证据和结果分别放在
`test_run/_scripts/`、`test_run/evidence/` 和 `test_run/results/` 的任务专属目录。

从 `environment_rule/` 解析当前测试环境、credential_ref、执行主机和安全边界。
不得使用旧 `environment/`、`tools/` 或历史归档推断 One 地址、租户、认证方式、
Pod 或接口。渠道开关、通知对象或测试数据的改动必须先记录目标、基线、风险、恢复
步骤和证据位置，并在结束时回读恢复。

## 版本基线：先核验，后断言

下表是此前一个版本的已观测实现，用于提出检查项和定位线索，不是本框架对所有
Repo↔One 集成版本的默认预期。先从当前需求、产品资料、代码版本、运行配置或日志
确认路由、TTL、渠道结构、角色映射和 fallback 配置；未确认的项目必须标为待澄清
或探索性验证，而不是写入预期结果。

| 概念 | 说明 |
|---|---|
| support-channel | 确认当前服务是否通过此类接口获取已启用渠道，以及返回字段和语义 |
| 渠道启停控制点 | 确认当前 UI/API 中真正控制渠道启停的层级；不要把名称相近的企业设置当作同一控制点 |
| 渠道缓存 | 确认缓存 key、TTL、过期策略与多 Pod 是否各自持有本地缓存；此前基线为按租户缓存、TTL 约 300 秒 |
| 聚合发送 | 确认发送路由、HTTP 方法、messageType 组成和 Body 字段；以实际请求或代码为准 |
| 渠道分类 | 确认 channelCode 到消息结构的当前映射，且字段名大小写和 HTML 字段均以实现为准 |
| 降级 fallback | 确认失败条件、默认渠道和失败结果是否缓存；此前默认渠道仅是历史基线 |
| 接收人三方交集 | 确认 Repo 候选用户/角色、One 渠道通知对象及其交集的当前规则 |
| messageType | 从当前 eventKey 映射或实际请求确认，不因历史事件名自动推断 |

## 输入参数（运行时确认，不写死）

- One 平台地址与企业标识（从当前环境定义解析）
- 登录身份的 credential_ref（只在获授权的本地机制中使用，**不写入任何产出物**）
- 目标租户（当前企业 + 对照租户）
- k8s 访问配置（观察 Pod 日志用）
- 被测 Repo 的通知事件入口

## 执行流程

### 1. 登录与环境确认

- 先确认当前版本的认证方式；若使用 Keycloak SSO，可采用获授权的 UI 会话复用方式，不把该方式假定为所有环境通用
- 用当前环境的会话失效信号判断是否重新认证，不把单一 HTTP 状态作为通用证据
- 确认 Repo 页脚版本号与修复部署状态（多副本时注意 Pod 启动时间，滚动期请求可能命中新旧不同实例）

### 2. 渠道配置与验证

```
平台通知方式配置页（渠道启停/新建/删除；isEnable 控制）
  └─ 典型路径：平台管理 → 通知配置 → 通知方式（行开关 + 新建通知方式按钮 + 行操作下拉菜单）
企业通知设置页（通知场景/通知对象：用户/角色；不改 isEnable）
  └─ 典型路径：企业设置 → 通知与公告 → 通知设置（email/internal 页签）
```

在确认当前管理入口、网关路由和字段语义后，可按“切换开关 → 回读渠道状态 →
触发通知 → 观察聚合发送”闭环验证。

### 3. 事件触发（选择立即可执行的事件源）

| 事件 | 触发方式 | 特性 |
|---|---|---|
| 备份策略 | API：创建备份配置 + 运行接口 | **同 key 有约 5 分钟执行间隔**——不适合连续验证 |
| 垃圾回收 | API：执行定时任务接口（任务名=垃圾清理类任务） | 立即执行，可连续触发——**验证缓存/渠道的首选** |
| 平台存储告警 | 通用设置开启配额+低阈值+等待定时检查 | 触发延迟不可控 |
| 扫描漏洞通知 | 需扫描命中安全策略违规（策略+制品+扫描） | 配置复杂；受制品大小上传限制 |

### 4. 日志观测（按当前版本确认）

先从当前代码、日志样本或可观测性配置确定日志关键字和字段。下表为既有版本的
排查线索，不是缺失即失败的固定断言。

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
2. **TTL 内**（T0+当前配置 TTL 前）再触发 → SC 调用=0 且渠道集合不变（缓存命中）
3. TTL 内修改 One 渠道配置再触发 → 渠道集合仍为旧值（用旧缓存）
4. TTL 过期后（T0+当前配置 TTL 后）触发 → SC 调用重新出现且渠道反映新配置

**多 Pod 注意**：本地缓存按 Pod 独立。跨 Pod 验证时表现为"改配置立即生效"——这是另一 Pod 无缓存回源，非缓存失效。同 Pod 验证需连续多次触发提高命中同 Pod 概率。

### 6. 多租户对照

- 切换企业：直接访问目标企业路径（`/{企业标识}/_detail`）→ 若无权限页提示则点"切换并访问" → 会话进入目标租户
- 租户上下文由会话决定（API 路径不带租户前缀）
- 验证断言：发送 URL 的 company、SC 回源 URL 的租户段、通知正文链接前缀均为目标租户标识；两租户渠道配置互不影响

### 7. 到达验证

站内信收件箱 API（当前用户收件列表）核对消息内容/时间/链接与聚合 Body 的 internal 字段一致。

## 校验清单

- [ ] 当前渠道查询路由、返回码和字段符合已确认的接口契约
- [ ] 渠道启停后，回读状态与聚合请求中的渠道字段按当前实现同步变化
- [ ] 缓存验证三态齐备：回源/命中/过期刷新（TTL 取当前配置）
- [ ] 聚合请求方法、messageType、租户和 Body 结构符合当前映射
- [ ] 自定义渠道分类、字段名和内容结构符合当前实现
- [ ] 降级场景有已确认的日志或请求证据，且降级集合符合当前配置
- [ ] 站内信实际到达且内容与 Body 一致
- [ ] 通知渠道/策略/场景配置测试后已恢复并回读确认

## 错误与异常处理（经验性排查线索）

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
- 将实际脚本、命令输出和截图保存至当前任务的 `test_run/` 目录；报告只引用必要证据，不含凭据或认证头

## 示例

**场景：验证"禁用邮件渠道后聚合发送不含 email 字段"**

1. 平台通知方式页关闭 email 行开关（截图）
2. Pod 内 curl 网关 support-channel → 确认 email isEnable=0
3. API 触发垃圾回收事件
4. 逐 Pod 拉日志：聚合 Body 含 internal/workWeiXin 等启用渠道字段、无 email=、messageType=repo-cleanupTask
5. 恢复 email 开关并回读确认

**边界：全部渠道禁用**

若当前版本配置了 fallback，期望以已确认的降级日志或请求为证；随后可能因降级渠道在 One 无有效接收人而不发送，是否合理应由当前接收人规则判断。

## 禁止事项

- 禁止把企业级"邮件服务配置"开关当作渠道 isEnable 控制点
- 禁止使用触发间隔或调度窗口会掩盖当前 TTL 的事件验证缓存
- 禁止以"回读值非空"判断写入是否发生（须对比传入值与基线值，参见 bugfix-retest-methodology skill）
- 禁止跳过环境恢复直接结束
- 禁止把历史版本的 TTL、接口路径、默认渠道、角色或日志文本直接写成当前需求事实
