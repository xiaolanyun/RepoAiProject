# GiteeRepo 无人值守自动化安全操作边界

本文件是 Hermes 与 Codex 共用的正式安全规则。

核心原则：

- 执行方式由 Agent 自主选择；
- 不强制使用 `Invoke-RemoteRunner.ps1` 或 `remote_runner.sh`；
- L0～L3 不需要人工审核；
- L4 直接熔断；
- 更换执行工具不得绕过安全边界；
- 单个工具或包装脚本故障不得阻断全部任务。

---

## 1. 可选执行方式

Agent 可以根据环境和任务选择：

```text
直接 SSH
SSH 配置别名
docker exec hermes 后直接 SSH
HTTP 客户端
kubectl
Docker CLI
数据库客户端
协议客户端
项目脚本
Invoke-RemoteRunner.ps1（可选）
remote_runner.sh（可选）
policy_check.py（可选预检）
```

优先级不是固定的。Agent 应选择当前最可靠、最简单、可验证的方式。

统一脚本存在以下问题时，可以立即切换：

- 参数不兼容；
- 引号或编码问题；
- 依赖缺失；
- 脚本自身 Bug；
- 容器挂载问题；
- 审计目录故障；
- 不支持当前协议或任务。

---

## 2. 不可放宽的统一要求

无论采用哪种方式，都必须：

1. 从 `inventory.yaml` 解析 SSH 主机。
2. 从 `services.yaml` 解析服务、K8s 和数据库。
3. 从 `protocols.yaml` 解析协议环境。
4. 仅按 `credential_ref` 读取当前任务所需凭据。
5. 使用 `known_hosts` 严格校验主机身份。
6. 执行前完成 L0～L4 风险判断。
7. 保存命令、目标、时间、stdout、stderr 和返回码。
8. L2、L3 写入高风险审计。
9. L4 写入熔断记录。
10. 不得因为改用直接 SSH 而扩大权限或操作范围。

---

## 3. 风险级别

| 级别  | 含义                 | 处理        |
| --- | ------------------ | --------- |
| L0  | 普通只读和健康检查          | 自动执行      |
| L1  | 当前任务范围内写入          | 自动执行      |
| L2  | 可恢复的测试环境变更         | 自动执行并审计   |
| L3  | 当前任务范围内的破坏性操作      | 自动执行并重点审计 |
| L4  | 系统级、越界、范围不明或不可恢复操作 | 直接熔断      |

L0～L3 不等待用户确认。L4 不询问是否放行。

---

## 4. L0：普通只读操作

自动执行：

- 主机、CPU、内存、磁盘、进程和网络检查；
- 查看文件、目录、服务状态和日志；
- `docker ps`、`inspect`、`logs`；
- `kubectl get`、`describe`、`logs`；
- HTTP GET、HEAD 和健康检查；
- 数据库连接检查和只读查询；
- 下载日志和测试结果。

---

## 5. L1：当前任务范围内写入

自动执行：

- 创建任务目录；
- 创建脚本、报告、日志、证据和测试数据；
- 覆盖当前任务自己生成的文件；
- 更新进度和结果；
- 清理当前任务临时文件。

允许范围：

```text
/workspace/work/projects/{project_name}/runs/{task_id}/
<framework-root>\workspace\{project_name}\runs\{task_id}\
/root/yfdata/hermes-tests/{task_id}/
```

不得覆盖其他项目或其他任务的文件。

---

## 6. L2：可恢复的测试环境变更

自动执行并审计：

- HTTP POST、PUT、PATCH、DELETE；
- 上传、发布、下载和拉取测试制品；
- 创建测试仓库、项目、账号和配置；
- `docker exec`；
- 重启明确登记的测试容器或服务；
- `kubectl exec`、`cp`、`port-forward`；
- `kubectl rollout restart`；
- 在测试 Namespace 中 apply 或 patch；
- 安装测试依赖；
- 启停当前任务创建的测试进程。

要求：

1. 目标来自统一配置。
2. 目标属于测试环境。
3. 范围明确。
4. 失败不得扩大范围。
5. 记录完整审计。

---

## 6.1 受控测试环境登记（L2）

当用户明确要求登记或更新一个指定的测试环境时，Agent 可自动执行并审计：

- 新增或更新 `config/inventory.yaml`、`config/services.yaml`、`config/protocols.yaml`、`ssh/config` 与 `ssh/known_hosts` 中属于该环境的条目；
- 在 `credentials.env` 新增该环境专属的凭据键；
- 仅更新当前任务明确指定的 `credential_ref`；
- 为新增 SSH 主机添加经可信指纹核验后的 `known_hosts` 条目；
- 对已登记的新测试 SSH 主机，可向指定用户的 `~/.ssh/authorized_keys` 安装受控公钥，并使用 `StrictHostKeyChecking=yes` 完成复验；
- 执行 `validate-config.py`、`render-docs.py` 与 `sync-runtime.ps1`；
- 保存变更前备份、统一 diff、校验输出与回滚说明。

前提：

1. 环境必须明确标记为测试环境，不能是生产或环境性质不明的目标。
2. 用户必须提供目标地址、测试环境属性、用途和初始认证信息。对于普通 SSH 服务，Agent 可将该主机登记为 execution_host，并完成连通性与工作目录验证；对于 K8s 服务，用户仍须提供 execution_host、kubeconfig 和 namespace。
3. 凭据不得写入源码、共享脚本、报告或聊天回复。
4. 只能影响当前环境条目；不得删除其他环境、其他凭据或共享配置。
5. 修改失败时仅回滚本任务产生的精确 diff。

## 7. L3：当前任务范围内的破坏性操作

自动执行并重点审计：

- 清理当前 task_id 目录；
- 删除当前任务创建的临时容器；
- 删除当前任务创建的 K8s 资源；
- 删除当前任务创建的测试制品、仓库、项目或账号；
- 测试数据库 INSERT、UPDATE、带 WHERE 的 DELETE；
- 测试前置和后置清理。

必须满足：

1. 对象能够证明属于当前任务。
2. 路径、资源名或标签包含 task_id，或使用允许的自动化前缀。
3. 路径必须明确，不含 `..` 或通配符。
4. 不作用于共享数据。
5. 删除失败不得扩大范围。
6. 保存重点审计。

无法证明范围时按 L4 处理。

---

## 8. L4：永久熔断

直接拒绝：

- reboot、shutdown、poweroff、halt；
- mkfs、wipefs、fdisk、parted；
- 删除系统目录；
- `rm -rf /`；
- 删除 `/etc`、`/usr`、`/root`、`/home`、`/opt`、`/var`；
- 删除 `/var/lib/docker`；
- Docker prune；
- `docker compose down -v`；
- 删除 Namespace、CRD、PV、共享 PVC；
- 修改 RBAC 或 kubeconfig；
- DROP DATABASE、DROP SCHEMA、DROP TABLE；
- 共享表 TRUNCATE；
- 无 WHERE 的 DELETE；
- 修改数据库用户或权限；
- 修改私钥、证书、CA 信任链或任何未明确指定的凭据；
- 删除凭据键，或修改当前任务未明确指定的 credential_ref；
- 自动修改 remote-runner-policy、安全策略、RBAC、kubeconfig 或全局执行工具；
- 删除或覆盖其他环境的 inventory、services、protocols 条目；
- 其他任务、其他项目或共享数据的删除；
- 任何范围不明的破坏性命令。

不得通过 Shell 包装、编码、脚本或更换客户端绕过 L4。

#

L4 操作仍由 Agent 永久熔断，Agent 不得通过 SSH、Docker、HTTP、
脚本或其他执行通道运行该操作。

当用户明确要求“仅提供人工执行命令”时，Agent 可以输出标注为
`MANUAL-ONLY` 的运行手册，供具备环境管理权限的人员自行执行。

运行手册必须：

1. 基于已完成的只读盘点；
2. 指定精确主机、容器、文件或镜像 ID；
3. 写明预计释放空间、影响范围与回滚限制；
4. 禁止通配范围删除、`docker system prune`、卷清理及制品库 filestore 清理；
5. 明确 Agent 不会执行其中任何命令。

---

## 9. 直接执行审计

不使用 `remote_runner` 时，Agent 应在当前任务目录创建：

```text
audit/commands.log
audit/stdout/
audit/stderr/
audit/high_risk_operations.md
audit/critical_blocks.md
audit/summary.md
```

`commands.log` 至少包含：

```text
时间
task_id
主机或服务别名
解析出的目标
执行方式
命令
风险级别
返回码
stdout 文件
stderr 文件
```

### 9.1 测试证据不脱敏模式

本项目默认启用测试证据不脱敏模式：

1. 当前任务目录中的命令、stdout、stderr、HTTP 请求与响应、Cargo/协议客户端日志、服务端日志、配置文件和测试报告，可以完整保留运行时用户名、密码、Token、Cookie、Authorization、ACCESSTOKEN、JSESSIONID 和其他诊断值。
2. 不得调用 `redact`、`mask`、`sanitize` 等逻辑主动替换、截断或删除当前任务的原始测试证据。
3. “凭据安全检查”只检查正式源码、Skill、模板、共享配置和可复用脚本中是否硬编码真实凭据；不检查当前测试运行证据是否包含凭据。
4. 原始证据只能保存在当前任务的受控目录，不得提交 Git、上传公共仓库或用于对外发布。
5. 若 Codex、聊天界面或其他上层平台规则不允许直接展示完整凭据，Agent 必须把原始值完整写入本地任务证据文件，并在回复中给出文件路径；不得因此修改本地原始证据。
6. SSH 私钥、长期主密钥和生产凭据仍不得复制到普通源码或公共报告；测试环境运行时实际使用的凭据可按本节完整留证。

---

## 10. SSH 安全

### Hermes 容器

源私钥是 Windows 只读挂载时，先复制到 `/tmp` 并设置 `600`，再执行 SSH。

### Codex / Windows

可以使用：

- Windows OpenSSH；
- 已配置 SSH Agent；
- 用户 SSH 配置；
- `docker exec hermes` 后从容器内直接 SSH；
- 可选 `Invoke-RemoteRunner.ps1`。

某一种方式发生密钥 ACL、引号或兼容性问题时，可以切换其他方式。

始终启用：

```text
StrictHostKeyChecking=yes
BatchMode=yes
连接超时
命令超时
```

---

## 11. K8s、数据库和协议任务

### K8s

服务端点不等于 SSH 主机。根据 `services.yaml` 中的 `execution_host`、`kubeconfig` 和 `namespace` 自主选择执行方式。

### 数据库

登记的测试数据库允许 L0～L3。DELETE 必须带 WHERE；L4 数据库命令直接熔断。

### 协议环境

可以直接 `docker exec` 协议容器，也可使用可选执行器。当前 task_id 范围内清理按 L3 执行。

---

## 12. 失败与降级

1. 相同方式最多重试一次。
2. 可从包装脚本切换到直接 SSH。
3. 可从宿主机工具切换到 Hermes 容器工具。
4. 可从直连切换到 execution_host。
5. 单个失败继续其他独立任务。
6. L4 熔断后继续其他安全任务。
7. 不得通过降级扩大权限或范围。

---

## 13. 可选工具定位

以下文件保留，但不再是强制入口：

```text
<framework-root>\environment_rule\bin\Invoke-RemoteRunner.ps1
<framework-root>\environment_rule\bin\remote_runner.sh
<framework-root>\environment_rule\bin\policy_check.py
<framework-root>\environment_rule\config\remote-runner-policy.yaml
```

作用：

- 提供别名解析；
- 提供统一日志；
- 提供安全预检；
- 处理 Hermes 容器私钥权限；
- 在适合的场景下快速复用。

这些工具故障时，不得阻断 Agent 使用其他符合本规则的方式执行。
