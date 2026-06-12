# codpm 原始意图需求

- 记录时间：`2026-06-07T19:37:30Z`
- 来源 run：`<NEXUS_RUN_ID>`
- 外部意图来源：`<PROJECT_ROOT>/README.md`

## 原始输入

基于现存仓库 README、当前 CLI 入口、历史 Nexus GitHub/Feishu artifact 还原出的 `codpm` 原始项目意图如下：

- 将 `codpm` 作为 forge 工作区的 Codex Personalization Manager，而不是某一条规则本身。
- 真实 Codex 个性化 surface 才是 source of truth；registry 只做治理和审计元数据。
- 提供面向真实 surface 的扫描、inventory、解释、检查、渲染、watch 和 Feishu 同步入口。
- 复用 Nexus、Codex、Feishu 和其他已有工具，不重复造同步器、提权系统或外部客户端。
- 项目初始化后应补齐项目意图持久化、整体操作指南、GitHub private/public 同步配置、Feishu 记录和项目级行为说明。

## 归档职责

- 本文件只负责保留项目原始意图和追溯来源。
- 对意图的结构化解释、边界、同步策略和更新约束统一写入 `docs/intent/normalized-requirement.md`。
