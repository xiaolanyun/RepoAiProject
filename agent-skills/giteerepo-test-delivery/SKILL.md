---
name: giteerepo-test-delivery
description: Analyze GiteeRepo requirements, design import-ready test cases and OPML test points, execute scoped tests, and produce evidence-based reports. Use for Repo test design, execution, or reporting; not for unrelated software work.
---

# GiteeRepo Test Delivery

Use this skill after the repository entry rules in `AGENTS.md` have routed the
task to the relevant requirement, product documentation, and environment files.

## Framework locations

Treat the directory containing `AGENTS.md` as the framework root. Requirements,
test cases, test points, and delivery reports belong under the relevant version
in `workspace/`. Put execution scripts in `test_run/_scripts/`, evidence in a
task-specific directory under `test_run/evidence/`, and structured results or
execution reports under `test_run/results/`.

`company-docs/` is read-only background material, not an environment source.
For any environment access or mutation, use `environment_rule/` and its safety
rule; never fall back to the retired `environment/`, `test/`, `tools/`, or
historical archive directories.

## Workflow

1. Establish the requirement facts: product, version, requirement ID, stated
   behavior, exclusions, and acceptance criteria. Search product and API
   documentation only with task-specific keywords.
2. Identify expectation-changing ambiguities before generating tests. Reuse a
   user-confirmed decision in later work; do not ask it again. Mark unspecified
   assumptions as unresolved rather than presenting them as facts.
3. When asked for test cases or test points, read
   [test-case-and-point-output.md](references/test-case-and-point-output.md).
4. Before execution, perform a task-scoped preflight: confirm the test target,
   authenticated identity, access scope, baseline state, evidence path, and
   restoration method. State the intended target, action, risk, restore plan,
   and evidence location before any environment mutation.
5. Execute only the authorized, feasible subset. Separate configuration review,
   observed runtime behavior, and test-framework readiness in the conclusion.
6. Produce an evidence-based report: scope, environment, method, results,
   defects or risks, restoration result, and unresolved items. Never include
   secrets in a deliverable.

## Script workspace

Put task-operation scripts in `test_run/_scripts/` by lifecycle:

- `preflight/` for read-only readiness and baseline capture;
- `execution/` for task-scoped operations;
- `verification/` for independent read-back and assertions;
- `recovery/` for restoration and cleanup;
- `utilities/` for reusable helpers.

An environment-changing script requires a paired recovery step, recorded
post-restore verification, and no embedded credential value.

## Deliverable boundaries

- Do not invent API capabilities, requirements, expected results, or test data.
- Explain when an item is blocked by missing authority, environment access, or
  an unresolved expectation.
- Keep test points concise: they say what to test, while test cases carry full
  conditions, steps, data, and expected results.
