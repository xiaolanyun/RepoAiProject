#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import shlex
from pathlib import Path, PurePosixPath

import yaml


def load_yaml(path: str) -> dict:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError("Policy root must be a mapping")
    return data


def emit(name: str, value: object) -> None:
    print(f"{name}={shlex.quote(str(value))}")


def decision(name: str, risk: str, reason: str, code: int) -> int:
    emit("DECISION", name)
    emit("RISK_LEVEL", risk)
    emit("REASON", reason)
    emit("POLICY_EXIT_CODE", code)
    return 0


def first_match(text: str, patterns: list[str]) -> str | None:
    lowered = text.lower()
    for pattern in patterns:
        if str(pattern).lower() in lowered:
            return str(pattern)
    return None


def normalize_path(value: str) -> str:
    return os.path.normpath(value.strip())


def is_safe_task_path(path_value: str, allowed_root: str, task_id: str) -> bool:
    if not path_value or not path_value.startswith("/"):
        return False
    if any(ch in path_value for ch in ("*", "?", "[", "]", "{", "}")):
        return False
    if ".." in PurePosixPath(path_value).parts:
        return False

    normalized = normalize_path(path_value)
    root = normalize_path(allowed_root)
    task_root = normalize_path(f"{root}/{task_id}")

    return normalized == task_root or normalized.startswith(task_root + "/")


def extract_simple_delete_target(command: str) -> tuple[str, str] | None:
    try:
        tokens = shlex.split(command)
    except ValueError:
        return None

    if not tokens:
        return None

    if tokens[0] == "rm":
        flags = [token for token in tokens[1:] if token.startswith("-")]
        targets = [token for token in tokens[1:] if not token.startswith("-")]
        if len(targets) == 1 and any(flag in {"-rf", "-fr", "-r", "-f"} for flag in flags):
            return ("rm", targets[0])

    if tokens[0] in {"rmdir", "unlink"}:
        targets = [token for token in tokens[1:] if not token.startswith("-")]
        if len(targets) == 1:
            return (tokens[0], targets[0])

    return None


def has_explicit_namespace(command: str) -> bool:
    return bool(re.search(r"(?:^|\s)(?:-n|--namespace)(?:=|\s+)[A-Za-z0-9._-]+", command))


def has_task_marker(command: str, task_id: str, prefixes: list[str]) -> bool:
    lowered = command.lower()
    if task_id and task_id.lower() in lowered:
        return True
    return any(prefix.lower() in lowered for prefix in prefixes)


def sql_delete_is_safe(command: str) -> bool:
    lowered = command.lower()
    if "delete from" not in lowered:
        return False
    return bool(re.search(r"\bwhere\b", lowered))


def docker_delete_is_scoped(command: str, task_id: str, prefixes: list[str]) -> bool:
    try:
        tokens = shlex.split(command)
    except ValueError:
        return False

    try:
        docker_index = tokens.index("docker")
    except ValueError:
        return False

    if len(tokens) <= docker_index + 2 or tokens[docker_index + 1] != "rm":
        return False

    targets = [token for token in tokens[docker_index + 2:] if not token.startswith("-")]
    if not targets:
        return False

    markers = [task_id.lower()] + [prefix.lower() for prefix in prefixes]
    return all(any(marker and marker in target.lower() for marker in markers) for target in targets)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", required=True)
    parser.add_argument("--scope", required=True, choices=["host", "sandbox-container"])
    parser.add_argument("--container", default="")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--target-workdir", required=True)
    parser.add_argument("--cleanup-sandbox", action="store_true")
    parser.add_argument("--cleanup-task", action="store_true")
    parser.add_argument("--command", required=True)
    args = parser.parse_args()

    policy = load_yaml(args.policy)
    command = args.command
    lowered = command.lower()

    always_block = [str(v) for v in policy.get("always_block_patterns", [])]
    l1_patterns = [str(v) for v in policy.get("l1_task_write_patterns", [])]
    l2_patterns = [str(v) for v in policy.get("l2_audit_patterns", [])]
    l3_db_patterns = [str(v) for v in policy.get("l3_database_patterns", [])]

    task_scope = policy.get("task_scope") or {}
    prefixes = [str(v) for v in task_scope.get("allowed_resource_prefixes", [])]
    remote_root = str(task_scope.get("remote_root", args.target_workdir)).rstrip("/")

    sandbox = policy.get("sandbox") or {}
    cleanup = sandbox.get("cleanup") or {}
    allowed_containers = {str(v) for v in sandbox.get("containers", [])}
    sandbox_root = str(cleanup.get("allowed_path", remote_root)).rstrip("/")

    hit = first_match(lowered, always_block)
    if hit:
        return decision("BLOCK", "L4", f"permanent block pattern matched: {hit}", 100)

    simple_delete = extract_simple_delete_target(command)
    if simple_delete:
        delete_kind, target = simple_delete

        if args.scope == "sandbox-container":
            allowed = (
                args.cleanup_sandbox
                and args.container in allowed_containers
                and is_safe_task_path(target, sandbox_root, args.task_id)
            )
        else:
            allowed = (
                args.cleanup_task
                and is_safe_task_path(target, args.target_workdir or remote_root, args.task_id)
            )

        if allowed:
            return decision(
                "ALLOW_WITH_AUDIT",
                "L3",
                f"task-scoped {delete_kind} cleanup allowed: {target}",
                0,
            )

        return decision(
            "BLOCK",
            "L4",
            f"delete path is not explicitly task-scoped or cleanup flag is missing: {target}",
            100,
        )

    if "delete from" in lowered:
        if not sql_delete_is_safe(command):
            return decision("BLOCK", "L4", "SQL DELETE without WHERE is blocked", 100)
        return decision("ALLOW_WITH_AUDIT", "L3", "SQL DELETE with WHERE allowed in registered test database", 0)

    if "kubectl delete" in lowered:
        if "--all" in lowered:
            return decision("BLOCK", "L4", "kubectl delete --all is blocked", 100)
        if not has_explicit_namespace(command):
            return decision("BLOCK", "L4", "kubectl delete requires an explicit namespace", 100)
        if not has_task_marker(command, args.task_id, prefixes):
            return decision("BLOCK", "L4", "kubectl delete requires task_id or an allowed automation prefix", 100)
        return decision("ALLOW_WITH_AUDIT", "L3", "task-scoped Kubernetes resource deletion allowed", 0)

    if "docker rmi" in lowered:
        return decision("BLOCK", "L4", "docker rmi is blocked for unattended tasks", 100)

    if "docker rm" in lowered:
        if docker_delete_is_scoped(command, args.task_id, prefixes):
            return decision("ALLOW_WITH_AUDIT", "L3", "task-scoped Docker container deletion allowed", 0)
        return decision("BLOCK", "L4", "docker rm requires task_id or an allowed automation prefix in every target", 100)

    if "helm uninstall" in lowered:
        if not has_explicit_namespace(command):
            return decision("BLOCK", "L4", "helm uninstall requires an explicit namespace", 100)
        if not has_task_marker(command, args.task_id, prefixes):
            return decision("BLOCK", "L4", "helm uninstall requires task_id or an allowed automation prefix", 100)
        return decision("ALLOW_WITH_AUDIT", "L3", "task-scoped Helm uninstall allowed", 0)

    db_hit = first_match(lowered, l3_db_patterns)
    if db_hit:
        return decision("ALLOW_WITH_AUDIT", "L3", f"database write operation matched: {db_hit}", 0)

    task_path = f"{args.target_workdir.rstrip('/')}/{args.task_id}"
    l1_hit = first_match(lowered, l1_patterns)
    if l1_hit and task_path in command:
        return decision("ALLOW", "L1", f"task-scoped write operation matched: {l1_hit}", 0)

    l2_hit = first_match(lowered, l2_patterns)
    if l2_hit:
        return decision("ALLOW_WITH_AUDIT", "L2", f"audited test operation matched: {l2_hit}", 0)

    return decision("ALLOW", "L0", "ordinary read-only or low-risk operation", 0)


if __name__ == "__main__":
    raise SystemExit(main())
