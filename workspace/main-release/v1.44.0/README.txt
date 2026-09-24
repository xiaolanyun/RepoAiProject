用途：v1.44.0 主版本任务的示例工作区。

- `requirements/`：该版本的需求说明、澄清记录和需求 ID。
- `testcase/`：测试用例、测试点 OPML/Markdown 和导入文件。
- `report/`：测试计划、执行报告、缺陷复现和交付总结。

后续版本按同一结构在 `workspace/main-release/` 下创建独立版本目录。任务执行的
脚本、状态、证据和结构化结果应放在根 `test_run/`，而不是本版本目录中。
