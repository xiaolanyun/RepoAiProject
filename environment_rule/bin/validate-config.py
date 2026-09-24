#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path

import yaml


ROOT = Path(os.environ.get("GITEEREPO_CONFIG_ROOT", Path(__file__).resolve().parents[1]))
CONFIG_DIR = ROOT / "config"


def load(name: str) -> dict:
    path = CONFIG_DIR / name
    if not path.exists():
        raise RuntimeError(f"Missing file: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise RuntimeError(f"YAML root must be a mapping: {path}")
    return data


def main() -> int:
    inventory = load("inventory.yaml")
    services = load("services.yaml")
    protocols = load("protocols.yaml")
    policy = load("remote-runner-policy.yaml")
    hermes_api = load("hermes-api.yaml")

    hosts = inventory.get("hosts") or {}
    if not hosts:
        raise RuntimeError("inventory.yaml has no hosts")

    seen_ips: dict[str, str] = {}
    for name, host in hosts.items():
        ip = str(host.get("ip", "")).strip()
        if not ip:
            raise RuntimeError(f"Host has no IP: {name}")
        if ip in seen_ips:
            raise RuntimeError(f"Duplicate IP {ip}: {seen_ips[ip]} and {name}")
        seen_ips[ip] = name

        if host.get("allow_remote_runner") and not host.get("remote_workdir"):
            raise RuntimeError(f"remote_workdir is missing for {name}")

    endpoints = inventory.get("service_endpoints") or {}
    for name, endpoint in endpoints.items():
        if endpoint.get("ssh_enabled") is True:
            raise RuntimeError(f"Service endpoint must not enable SSH: {name}")

    credential_refs = services.get("credentials") or {}

    for name, service in (services.get("services") or {}).items():
        execution_host = service.get("execution_host")
        if execution_host and execution_host not in hosts:
            raise RuntimeError(f"Unknown execution_host for service {name}: {execution_host}")

        credential_ref = service.get("credential_ref")
        if credential_ref and credential_ref not in credential_refs:
            raise RuntimeError(
                f"Unknown credential_ref for service {name}: {credential_ref}"
            )

    protocol_host = protocols.get("execution_host")
    if protocol_host not in hosts:
        raise RuntimeError(f"Unknown protocol execution host: {protocol_host}")

    sandbox = policy.get("sandbox") or {}
    if sandbox.get("execution_host") not in hosts:
        raise RuntimeError("Policy sandbox execution host is not in inventory")

    if not hermes_api.get("base_url"):
        raise RuntimeError("Hermes API base_url is missing")

    required_runtime_files = [
        ROOT / "ssh" / "config",
        ROOT / "ssh" / "known_hosts",
        ROOT / "bin" / "remote_runner.sh",
        ROOT / "bin" / "config_query.py",
        ROOT / "bin" / "policy_check.py",
    ]
    for path in required_runtime_files:
        if not path.exists():
            raise RuntimeError(f"Missing runtime file: {path}")

    print("Configuration validation passed.")
    print(f"Hosts: {len(hosts)}")
    print(f"Services: {len(services.get('services') or {})}")
    print(f"Protocol containers: {len(protocols.get('containers') or {})}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Configuration validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
