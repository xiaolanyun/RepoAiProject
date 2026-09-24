# Team AI Framework

Reusable framework for operating an AI-enabled delivery team. It versions agent
entry rules, skills, Hermes deployment definitions, standard test workspaces,
and safe local-environment templates together. Runtime data and real secrets
are always kept outside Git.

## Layout

- `deployment/hermes/` — Hermes container, configuration, and governance assets.
- `environment_rule/` — environment onboarding rules, safety controls, and
  secret-free templates.
- `agent-skills/` — reusable workflows and output templates for agents.
- `company-docs/` — local, read-only product/API documents; proprietary sources
  are intentionally not distributed in this public repository.
- `workspace/` — project workspace structure for requirements, test cases, and reports.
- `test_run/` — standard test workspace and task-operation script lifecycle.

## Before use

1. Create local runtime configuration from the templates under deployment.
2. Fill `environment_rule/credentials.env` through an approved local secret
   store or deployment system; never commit real values.
3. Create your own environment inventory, service definitions, SSH configuration,
   and host fingerprints locally.
4. Place approved SSH private keys in the ignored `environment_rule/ssh/` folder.
5. Review `environment_rule/docs/UNATTENDED-SAFETY.md` before remote execution.
6. Run Hermes from `deployment/hermes/container/docker-compose.yml`; consult the
   adjacent Chinese mount-rule document before changing volumes or permissions.
