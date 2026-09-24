# Task Operation Scripts

Store scripts needed to operate a task here instead of placing them at the test
workspace root. Name files with a concise action and a task identifier, for
example `preflight_repo-44.py` or `restore_sync-policy-46.ps1`.

Use the lifecycle folders below. A script that changes a shared test environment
must have a paired restore script under `recovery/` and record its evidence in
the task's `results/` or `evidence/` directory.
