---
name: giteerepo-environment-onboarding
description: Register or update a declared GiteeRepo test environment using the team environment rule, credential references, verified SSH host identity, and configuration validation. Use only for explicit environment onboarding or change requests.
---

# GiteeRepo Test Environment Onboarding

Use this skill only when the user explicitly asks to add or change a named test
environment. Read `environment_rule/README.txt`, `config/inventory.yaml`,
`config/services.yaml`, `config/remote-runner-policy.yaml`, and
`docs/UNATTENDED-SAFETY.md` before editing anything.

## Framework boundary

Resolve all paths from the framework root containing `AGENTS.md`. The only
current environment source is `environment_rule/`; never use the retired
`environment/`, `tools/`, or archived files as a substitute. Before changing a
test environment, record the named target, intended files, risk level, restore
plan, and evidence location in the current task workspace. Use
`test_run/_scripts/` for any repeatable preflight, update, verification, or
recovery script; keep its evidence and result in task-specific directories under
`test_run/evidence/` and `test_run/results/`.

## Required input

Collect or identify: environment name and test/non-production designation,
purpose, SSH host/port/user, service URL, execution host, credential reference,
and verified SSH host fingerprint. For Kubernetes services also require the
execution host, kubeconfig, and namespace.

Do not infer a production/test classification, an SSH target, or a host key. If
information is missing, report the exact missing field rather than inventing it.

## Controlled update

1. Add or update only the specified host in `config/inventory.yaml`.
2. Add or update only the related service in `config/services.yaml`; reference
   credentials by `credential_ref`, never by literal value.
3. Add the verified SSH alias to `ssh/config` and host identity to
   `ssh/known_hosts`.
4. Add credential values only through the approved local secret store; do not
   write them into Git-tracked files, a report, or an AI message.
5. Run `bin/validate-config.py`. If relevant, regenerate local derived
   documentation using `bin/render-docs.py` without treating generated output
   as the source of truth.
6. Record target, files changed, validation result, and any remaining access
   verification. Follow L0-L4 and strict host verification for any connection.
   If validation, host verification, or the permitted credential reference is
   unavailable, stop with the exact missing item; do not guess or add a
   placeholder host identity.

## Completion criteria

The environment is ready only when configuration validation passes, the
credential reference exists in the authorized local secret store, and the SSH
host identity is verified. A failed or unavailable service must be reported as
an environment condition, not fixed by guessing or bypassing safety rules.
