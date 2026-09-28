# Team Test Run Framework

# 团队测试执行工作区

本目录是标准任务工作区，结构参考 `D:\opencode\repo\test_run`。

- `config/`：不含密钥的运行配置。
- `data/`：参数化测试数据及获批的测试样本。
- `evidence/`：截图和其他执行证据。
- `pages/`：UI 自动化页面对象。
- `results/`：结构化执行结果及报告。
- `state/`：本地运行状态，不得提交认证信息或令牌。
- `tests/`：pytest 测试套件。
- `utils/`：可复用测试辅助代码。
- `archive/`：已淘汰脚本及历史任务产物。
- `_scripts/`：按生命周期分类的任务操作脚本。

并行任务需要隔离时，在各输出目录下建立任务专属子目录。任何提交的脚本或结果都不得包含密码、令牌、Cookie 或私钥。

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
