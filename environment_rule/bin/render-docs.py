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

    host_lines = ["# Server Inventory", ""]
    for name, host in (inventory.get("hosts") or {}).items():
        host_lines.extend([
            f"## {name}",
            "",
            f"- IP: `{host.get('ip')}`",
            f"- SSH user: `{host.get('ssh_user')}`",
            f"- SSH port: `{host.get('ssh_port')}`",
            f"- Remote workdir: `{host.get('remote_workdir')}`",
            f"- remote_runner enabled: `{host.get('allow_remote_runner')}`",
            f"- Roles: `{', '.join(host.get('roles') or [])}`",
            "",
        ])
    write("server-inventory.md", "\n".join(host_lines))

    service_lines = ["# GiteeRepo Environments", ""]
    for name, service in (services.get("services") or {}).items():
        service_lines.extend([
            f"## {name}",
            "",
            f"- Type: `{service.get('type')}`",
            f"- URL: `{service.get('url')}`",
            f"- Execution host: `{service.get('execution_host')}`",
            f"- Credential reference: `{service.get('credential_ref')}`",
            "",
        ])

    service_lines.extend(["# Protocol Containers", ""])
    for name, cfg in (protocols.get("containers") or {}).items():
        service_lines.extend([
            f"## {name}",
            "",
            f"- Protocols: `{', '.join(cfg.get('protocols') or [])}`",
            f"- AMD64 image: `{(cfg.get('images') or {}).get('amd64')}`",
            f"- ARM64 image: `{(cfg.get('images') or {}).get('arm64')}`",
            "",
        ])
    write("giteerepo-environments.md", "\n".join(service_lines))

    api_lines = [
        "# Hermes Call Information",
        "",
        f"- Container: `{hermes_api.get('container')}`",
        f"- Base URL: `{hermes_api.get('base_url')}`",
        f"- Health URL: `{hermes_api.get('health_url')}`",
        f"- Models URL: `{hermes_api.get('models_url')}`",
        f"- Dashboard URL: `{hermes_api.get('dashboard_url')}`",
        f"- API key variable: `{hermes_api.get('api_key_env')}`",
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
