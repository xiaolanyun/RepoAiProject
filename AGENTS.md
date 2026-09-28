# Team AI Framework Entry Rules

Apply these rules before handling work in this repository.

## Mandatory discovery order

1. Read this file and the root `README.md`.
2. For requirements, test analysis, test-case design, test execution, or test
   reporting, read `agent-skills/giteerepo-test-delivery/SKILL.md`.
   For a developer-provided bug fix, also read
   `agent-skills/bugfix-retest-methodology/SKILL.md`; for Repo-to-One
   notification work, also read `agent-skills/one-notification-testing/SKILL.md`.
   For adding or changing a GiteeRepo test environment, read
   `agent-skills/giteerepo-environment-onboarding/SKILL.md` before editing
   environment files.
3. Identify the task's product, version, requirement, and delivery type before
   reading additional material. Do not load unrelated historical files.
4. When approved local product documents are available, search
   `company-docs/gitee-docs/` by requirement keywords to find basic
   functionality and interface information. For protocol work, also search
   `company-docs/protocol-guides/`. The public distribution intentionally
   excludes proprietary documents; if they are absent, record that limitation
   rather than inventing product facts.
5. Read only the requirement, test case, and report materials relevant to the
   requested version under `workspace/`.
6. For environment access or execution, read `environment_rule/README.txt`,
   then the locally provisioned relevant files under `environment_rule/config/`,
   `environment_rule/docs/`, and `environment_rule/bin/`. The public edition
   excludes site-specific inventory and service definitions; missing local
   configuration blocks environment actions and must not be guessed.

When running inside the Hermes container, resolve framework paths as follows:
`environment_rule/` = `/workspace/envs/giteerepo/`, `agent-skills/` =
`/workspace/agent-skills/`, `company-docs/` = `/workspace/company-docs/`, and
`workspace/` = `/workspace/work/`. If the container layout differs, inspect
the actual mounts before concluding that a rule or configuration is missing.

## Operating boundaries

- Treat `environment_rule/config/` as the current environment definition and
  `environment_rule/docs/UNATTENDED-SAFETY.md` as the execution safety boundary.
- Choose SSH, HTTP, kubectl, database, protocol client, or a task script from
  the resolved target and task needs. No unified runner or runner-policy file is
  required. Apply the same L0-L4 boundary and command audit to every method:
  L0-L3 proceed within scope; L4 is blocked and recorded.
- Use credential references from configuration. Never place real passwords,
  API keys, tokens, cookies, or private keys in a report, script, test case,
  or Git change.
- Read the local credential mechanism only when the task needs it; do not dump
  unrelated credentials. If required credentials are unavailable, report the
  missing credential reference and request the authorized setup owner to supply
  it through the approved local secret store.
- Before modifying a test environment, state the target, action, risk, restore
  plan, and evidence location. Follow the environment safety rules.
- Treat `company-docs/` as read-only reference material. It may be searched for
  functionality and API facts but must never be edited by an Agent.
- `environment/`, `test/`, and `tools/` are retired empty legacy directories;
  never use them for new work. Use `environment_rule/` and `test_run/`.
- Do not use `archive/` or historical task artifacts as current facts.

## Required deliverables

Choose only the deliverables requested by the user: clarified requirements and
open questions, test cases, test points, an execution plan, evidence, and/or a
test report. Use the test-delivery Skill's format rules whenever generating or
changing test cases or test points.
