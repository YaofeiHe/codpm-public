# codpm 项目说明

- 更新时间：`2026-06-07T19:37:30Z`
- 项目路径：`<PROJECT_ROOT>`
- GitHub private：`<PRIVATE_REPO>` (enabled)
- GitHub public：`YaofeiHe/codpm-public`
- Feishu 长期文档同步：`enabled`

## 项目定位

`codpm` 是 Codex Personalization Manager。它负责把 forge 工作区里的真实 Codex 个性化 surface 盘点清楚、解释清楚、检查清楚，并输出可同步的治理文档。

## 项目命名说明

- 项目当前使用名称 `codpm`。
- 含义：`Codex Personalization Manager`。
- 这个名字强调它管理的是个性化治理层，而不是某一条规则或某一个外部集成。

## 文档体系

- `docs/intent/original-requirement.md`：原始需求归档。
- `docs/intent/normalized-requirement.md`：完整规范化需求主文档。
- `docs/project-overview.md`：项目说明文档。
- `docs/operation-guide.md`：操作指南。
- `docs/feishu-records.md`：飞书同步记录。

## 当前目录结构摘要

- `README.md`
- `docs/`
- `tests/`
- `.nexus/`
- `.data/`
- `codpm/`
- `generated/`
- `registry/`
- `skills/`
- `pyproject.toml`

## 核心模块

- `codpm/scanner.py`：扫描 global、forge、project、external 四层真实 surface。
- `codpm/parser.py`：解析 Markdown、TOML、JSON、rules 和 skill 内容。
- `codpm/personalization.py`：把真实 surface 解析成面向 workflow 的内容级展示，并提供自然语言到 CLI 的确定性路由。
- `codpm/checker.py`：对 registry 元数据与真实 surface 做一致性检查。
- `codpm/explainer.py`：解释当前状态、单个 surface 和 registry 项。
- `codpm/render.py`：渲染动态登记表并写入本地 artifact。
- `codpm/syncer.py`：通过 Nexus CLI 编排 Feishu dry-run/execute。
- `codpm/watcher.py`：基于 inventory hash 轮询变更并按需 render。
- `codpm/editor.py`：向真实 `AGENTS.md` 写入项目或范围级行为规则。

## 关键运行与同步约束

- 真实 surface 是 source of truth；registry 只做治理元数据。
- `personalization list`、`rule list`、`skill list/show`、`hook list`、`config show`、`mcp show` 和 `memory boundary` 是面向 `$codpm-workflow` 的展示入口。
- `workflow route --text` 只做确定性路由说明；实际读取和展示仍由对应 surface 命令完成。
- 长期文档默认同步到飞书，并复用已有线上文档绑定。
- GitHub private 是默认同步能力；GitHub public 仍需要显式确认。
- 缺少项目级 Feishu 配置时，`sync feishu --execute` 必须 blocked，而不是假装外部写入成功。
- public clone 默认把 `render`、`watch` 和 `sync feishu` 产生的 `.data/`、`generated/`、`docs/codex-personalization-registry.md`、构建缓存和认证/runtime 文件留在本地忽略状态；只有显式设置 `CODPM_FORGE_ROOT` 时才写 forge 级 docs。
- GitHub public staging 必须携带 `.gitignore` 并通过 secret/metadata scan、安装、import、CLI smoke、测试和 fresh-clone validation 后才能 push。
