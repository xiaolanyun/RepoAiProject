用途：存放环境恢复与任务范围清理脚本。

凡是修改共享测试设置的脚本，必须有对应的恢复脚本，并通过回读证明环境已经恢复。

Purpose: restoration and task-scoped cleanup scripts.

Every script that changes a shared test setting must document its matching
recovery script. Recovery must prove the post-restore state with a read-back.
