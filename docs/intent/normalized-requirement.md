# codpm 规范化意图需求

- 记录时间：`2026-06-07T19:37:30Z`
- 来源 run：`<NEXUS_RUN_ID>`
- 项目路径：`<PROJECT_ROOT>`
- GitHub private 默认同步：`enabled`
- GitHub private 仓库：`<PRIVATE_REPO>`
- GitHub public 仓库：`YaofeiHe/codpm-public`
- 飞书文档同步：`enabled`
- 参考意图来源：`<PROJECT_ROOT>/README.md`

## 文档职责

- `docs/intent/original-requirement.md`：原始输入归档，只保留用户原文和引用来源。
- `docs/intent/normalized-requirement.md`：完整规范化需求主文档，需求更新时优先更新这里。
- `docs/project-overview.md`：项目说明文档，随代码结构和模块演进更新。
- `docs/operation-guide.md`：操作指南，随 workflow 入口和实际操作方式更新。
- `docs/feishu-records.md`：飞书同步记录流，不承担长期说明职责。

## 规范化目标

`codpm` 应作为一个由 Nexus 管理的真实项目，负责治理 forge 工作区里的 Codex 个性化表面，并提供可追溯的扫描、解释、检查、渲染和同步入口。

## 项目命名说明

- 项目当前使用名称 `codpm`，因为用户在初始化语义上明确采用该项目名。
- 含义：`codpm` 来自 `Codex Personalization Manager`。
- 记忆点：这个项目管理的是“真实个性化 surface 的登记与治理”，不是单条规则内容。
- 采用理由：名称短、可命令行输入，并且与项目职责直接对应。

## 项目范围

- 扫描 global、forge、project 和 external 四层真实 Codex/Nexus 相关 surface。
- 生成 inventory、explain、check、render、watch 等本地治理能力，并把结果写入稳定 artifact。
- 提供面向自然语言 workflow 的确定性路由，把 `$codpm-workflow` 请求落到规则、skill、hook、config、MCP、memory 等真实 surface 的展示或维护命令。
- 对规则、skill、hook、config、MCP 和 memory 提供内容级展示；规则维护写入真实 `AGENTS.md`，skill 维护暂作为接口边界，hook/config/MCP 维护必须先经过显式写入指令和风险校验。
- 维护 registry 元数据和动态登记表，但不把 registry 当成行为生效依据。
- 通过 Nexus 接入 Feishu 记录和文档同步，通过 GitHub private/public 配置维护项目同步边界。
- 维护 `codpm` 自身的项目初始化文档、项目说明、整体操作指南和同步记录。
- public clone 必须能在任意目录运行基础 CLI、测试、render 和 watch；运行后产生的 `.data/`、`generated/`、`docs/codex-personalization-registry.md`、构建缓存和认证/runtime 文件必须被 `.gitignore` 阻断，避免本机路径或外部同步信息误提交。

## 默认能力边界

- 真实 `AGENTS.md`、rules、skills、hooks、MCP/tool 配置和 memory 文件是行为来源；registry 与渲染文档只是治理层。
- `codpm` 不重写 `dotagents`、`agent-rules-sync`、Nexus Feishu、Codex 官方提权规则或 hooks 已覆盖的能力。
- 默认操作保持本地、只读或 dry-run；真正的外部写入只走显式命令入口。
- “列表展示”类 workflow 必须读取真实 surface 并展开内容摘要，而不是只输出路径；registry 只作为治理状态补充说明。

## 硬安全边界

- 不读取 cookie、token、浏览器 profile、SSH key、`.env`、密码文件或其他凭据内容。
- 不静默安装第三方工具，不静默修改用户全局 Codex 配置，不静默写入飞书或 GitHub。
- GitHub public 发布必须显式确认；GitHub private 和 Feishu 外部写入必须通过 Nexus 能力链路执行。
- GitHub public staging 必须包含 `.gitignore`，并排除动态 registry 文档、runtime 数据、认证状态和本机路径类元数据；public 发布前必须通过 fresh-clone install/import/CLI/test 验证。
- 遇到缺配置、缺权限、认证失效或外部平台阻断时，必须明确写 blocked 结果和下一步提示。

## 默认更新约束

- CLI 能力、真实 surface 扫描口径或同步策略变化时，必须同步刷新 `docs/project-overview.md` 和 `docs/operation-guide.md`。
- 项目定位、范围、同步边界或安全约束变化时，必须优先更新本文件。
- `docs/intent/normalized-requirement.md`、`docs/project-overview.md`、`docs/operation-guide.md` 默认作为长期飞书同步对象维护。
- 若项目初始化产物丢失，应优先恢复 `.nexus/project-intent.json`、Feishu 配置、操作指南和 GitHub sync 配置，再继续外部同步。

## 原始输入摘要

`codpm` 的目标是为 forge 工作区提供一个围绕真实 Codex 个性化 surface 的治理层：既能盘点和解释实际生效位置，也能输出动态登记表，并通过 Nexus 接上 GitHub/Feishu 等外部同步能力；同时保持“已有工具做已有事、`codpm` 只做治理与编排”的边界。
