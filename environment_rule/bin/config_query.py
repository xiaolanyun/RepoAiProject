#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shlex
import sys
from pathlib import Path

import yaml


def load_yaml(path: str) -> dict:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return data


def emit(name: str, value: object) -> None:
    text = "" if value is None else str(value)
    print(f"{name}={shlex.quote(text)}")


def resolve_host(inventory_path: str, target: str) -> int:
    data = load_yaml(inventory_path)
    hosts = data.get("hosts") or {}
    selected_name = None
    selected = None

    if target in hosts:
        selected_name = target
        selected = hosts[target]
    else:
        for name, cfg in hosts.items():
            if str(cfg.get("ip", "")) == target or str(cfg.get("ssh_alias", "")) == target:
                selected_name = name
                selected = cfg
                break

    if selected is None:
        print(f"Unknown or non-SSH target: {target}", file=sys.stderr)
        return 3

    if not bool(selected.get("enabled", False)):
        print(f"Host is disabled: {selected_name}", file=sys.stderr)
        return 4

    if not bool(selected.get("allow_remote_runner", False)):
        print(f"Host is not allowed for remote_runner: {selected_name}", file=sys.stderr)
        return 5

    emit("TARGET_ALIAS", selected_name)
    emit("TARGET_HOST", selected.get("ip"))
    emit("TARGET_USER", selected.get("ssh_user", "root"))
    emit("TARGET_PORT", selected.get("ssh_port", 22))
    emit("TARGET_WORKDIR", selected.get("remote_workdir", "/root/yfdata/hermes-tests"))
    emit("TARGET_AUTH_MODE", selected.get("auth_mode", "ssh-key"))
    return 0


def resolve_policy(policy_path: str) -> int:
    data = load_yaml(policy_path)
    defaults = data.get("defaults") or {}
    sandbox = data.get("sandbox") or {}
    cleanup = sandbox.get("cleanup") or {}

    emit("POLICY_TIMEOUT", defaults.get("timeout_seconds", 300))
    emit("AUDIT_BASE_DIR", defaults.get("audit_base_dir", "/workspace/work/behavior/remote-runner"))
    emit("CONTROL_DIR", defaults.get("control_dir", "/workspace/work/behavior/control"))
    emit("KEY_PATH", defaults.get("ssh_key"))
    emit("SSH_CONFIG", defaults.get("ssh_config"))
    emit("KNOWN_HOSTS", defaults.get("known_hosts"))
    emit("SANDBOX_HOST_ALIAS", sandbox.get("execution_host", "testenv-25"))
    emit("SANDBOX_CONTAINERS", ",".join(str(item) for item in (sandbox.get("containers") or [])))
    emit("SANDBOX_CLEANUP_PATH", cleanup.get("allowed_path", "/root/yfdata/hermes-tests"))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    host_parser = sub.add_parser("resolve-host")
    host_parser.add_argument("inventory")
    host_parser.add_argument("target")

    policy_parser = sub.add_parser("resolve-policy")
    policy_parser.add_argument("policy")

    args = parser.parse_args()

    try:
        if args.command == "resolve-host":
            return resolve_host(args.inventory, args.target)
        if args.command == "resolve-policy":
            return resolve_policy(args.policy)
    except Exception as exc:
        print(f"Configuration query failed: {exc}", file=sys.stderr)
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
