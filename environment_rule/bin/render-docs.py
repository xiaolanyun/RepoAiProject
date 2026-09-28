#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path

import yaml


ROOT = Path(os.environ.get("GITEEREPO_CONFIG_ROOT", Path(__file__).resolve().parents[1]))
CONFIG = ROOT / "config"
GENERATED = ROOT / "generated"


def load(name: str) -> dict:
    with (CONFIG / name).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def write(name: str, text: str) -> None:
    GENERATED.mkdir(parents=True, exist_ok=True)
    (GENERATED / name).write_text(text.rstrip() + "\n", encoding="utf-8")


def main() -> int:
    inventory = load("inventory.yaml")
    services = load("services.yaml")
    protocols = load("protocols.yaml")
    hermes_api = load("hermes-api.yaml")

    host_lines = ["# Server Inventory / 服务器清单", ""]
    for name, host in (inventory.get("hosts") or {}).items():
        host_lines.extend([
            f"## {name}",
            "",
            f"- IP: `{host.get('ip')}`",
            f"- SSH user / SSH 用户: `{host.get('ssh_user')}`",
            f"- SSH port / SSH 端口: `{host.get('ssh_port')}`",
            f"- Remote workdir / 远程工作目录: `{host.get('remote_workdir')}`",
            f"- Roles / 角色: `{', '.join(host.get('roles') or [])}`",
            "",
        ])
    write("server-inventory.md", "\n".join(host_lines))

    service_lines = ["# GiteeRepo Environments / GiteeRepo 环境", ""]
    for name, service in (services.get("services") or {}).items():
        service_lines.extend([
            f"## {name}",
            "",
            f"- Type / 类型: `{service.get('type')}`",
            f"- URL: `{service.get('url')}`",
            f"- Execution host / 执行主机: `{service.get('execution_host')}`",
            f"- Credential reference / 凭据引用: `{service.get('credential_ref')}`",
            "",
        ])

    service_lines.extend(["# Protocol Containers / 协议容器", ""])
    for name, cfg in (protocols.get("containers") or {}).items():
        service_lines.extend([
            f"## {name}",
            "",
            f"- Protocols / 协议: `{', '.join(cfg.get('protocols') or [])}`",
            f"- AMD64 image / AMD64 镜像: `{(cfg.get('images') or {}).get('amd64')}`",
            f"- ARM64 image / ARM64 镜像: `{(cfg.get('images') or {}).get('arm64')}`",
            "",
        ])
    write("giteerepo-environments.md", "\n".join(service_lines))

    api_lines = [
        "# Hermes Call Information / Hermes 调用信息",
        "",
        f"- Container / 容器: `{hermes_api.get('container')}`",
        f"- Base URL: `{hermes_api.get('base_url')}`",
        f"- Health URL: `{hermes_api.get('health_url')}`",
        f"- Models URL: `{hermes_api.get('models_url')}`",
        f"- Dashboard URL: `{hermes_api.get('dashboard_url')}`",
        f"- API key variable / API 密钥环境变量: `{hermes_api.get('api_key_env')}`",
        "",
        "```powershell",
        '$key = (Get-Content "$env:LOCAL_SECRET_FILE" | '
        'Where-Object { $_ -like "HERMES_API_KEY=*" }) -replace "^HERMES_API_KEY=", ""',
        'curl.exe -H "Authorization: Bearer $key" http://127.0.0.1:8642/health',
        "```",
    ]
    write("hermes-call-info.md", "\n".join(api_lines))
    print("Generated documentation refreshed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
