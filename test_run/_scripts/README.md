# Task Operation Scripts

# 任务操作脚本

执行任务所需的脚本放在此处，不放在测试工作区根目录。文件名应包含简短动作和任务标识，例如 `preflight_repo-44.py` 或 `restore_sync-policy-46.ps1`。

按下方生命周期目录分类。会改变共享测试环境的脚本，必须在 `recovery/` 下配套恢复脚本，并将执行证据记录到该任务的 `results/` 或 `evidence/` 目录。

Store scripts needed to operate a task here instead of placing them at the test
workspace root. Name files with a concise action and a task identifier, for
example `preflight_repo-44.py` or `restore_sync-policy-46.ps1`.

Use the lifecycle folders below. A script that changes a shared test environment
must have a paired restore script under `recovery/` and record its evidence in
the task's `results/` or `evidence/` directory.
