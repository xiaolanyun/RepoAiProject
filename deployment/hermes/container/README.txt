用途：存放 Hermes 容器镜像与服务启动定义。

Dockerfile.feishu 用于在 Hermes 基础镜像中安装飞书 SDK；docker-compose.yml
用于定义服务启动方式。部署时按目标环境调整镜像名和本机运行目录挂载路径。

Purpose: Docker image and service startup definitions for Hermes.

Dockerfile.feishu extends the Hermes base image with the Feishu SDK.
docker-compose.yml is a portable service definition; adjust image names and
local runtime mount paths for the target deployment.

挂载规则：`company-docs`、`environment_rule` 与 `agent-skills` 在容器中均为
只读；`workspace` 和 `deployment/hermes/runtime` 为可写任务与运行状态目录。
环境规则中若存在本机凭据或私钥，容器只能读取，不能修改；任何环境登记修改都在
受控的主机工作区完成并经配置校验后生效。
