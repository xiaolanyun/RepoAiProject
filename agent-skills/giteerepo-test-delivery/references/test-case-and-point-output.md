# Test Case and Test Point Output Rules

Apply these rules only when generating, supplementing, or modifying test cases
or test points.

## Clarification first

Before generation, analyze whether the requirement contains an ambiguity that
would change an expected result. Reuse an already user-confirmed interpretation
without asking again. If an unresolved detail affects expected behavior, ask or
explicitly mark it as an assumption; never turn experience-based inference into
a requirement fact.

## Test cases

Use the user's most recently provided test-management import template when one
exists. Otherwise use these columns in this exact order:

`所属目录、标题、类型、优先级、前置条件、负责人、步骤、预期结果、数据、所属产品、所属项目、版本、迭代、测试用例标签、所属需求ID`

Default field rules:

- 所属产品: `Repo`.
- 所属项目: leave blank unless explicitly provided.
- 版本: extract from the current requirement.
- 迭代: leave blank unless explicitly provided.
- 所属需求ID: preserve the explicitly stated ID; otherwise leave blank.
- 类型: `测试用例`.
- 负责人: leave blank unless assigned.
- 步骤、预期结果、数据: use consecutive `【1】`, `【2】`, `【3】` numbering.

Only use these test-case labels when supported by the scenario:

`功能、性能、兼容、安全、高可用、UI、国际化翻译`

Prioritize coverage of the main path, data correctness, exceptions, boundaries,
policies, blocking, data isolation, compatibility, and regression. Add
performance, security, high-availability, and UI coverage only when the
requirement actually calls for it. A requirement that says a capability is not
supported, not displayed, or forbidden requires a reverse test that confirms it
cannot take effect.

## Test points

Use this hierarchy:

```text
{版本}-{需求名称}
└─ 测试模块
   └─ 具体测试点
```

Produce OPML first for XMind import, with Markdown as an optional companion for
human review. Test points describe only what is tested; preconditions, steps,
data, and expected results belong in test cases.
