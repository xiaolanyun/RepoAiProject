# Team Test Run Framework

This is the standard task workspace, based on `D:\opencode\repo\test_run`.

- `config/` — non-secret runtime settings.
- `data/` — parameterized test data and approved fixtures.
- `evidence/` — screenshots and other execution evidence.
- `pages/` — page-object models for UI automation.
- `results/` — structured run results and reports.
- `state/` — local runtime state; never commit authentication or tokens.
- `tests/` — pytest test suites.
- `utils/` — reusable test helpers.
- `archive/` — superseded scripts and historic task artifacts.
- `_scripts/` — task-operation scripts, grouped by lifecycle.

Create a task-specific subdirectory below each output folder when concurrent
tasks need isolation. Do not put passwords, tokens, cookies, or private keys in
any committed script or result.
