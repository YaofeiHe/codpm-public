# codpm 整体操作指南

目标类型：`project`

## 定位

`codpm` 是由 Nexus 管理或初始化的项目，应拥有可运行代码、git 基线、GitHub private 默认同步和整体操作指南。

## 项目意图说明

- 原始意图需求固定存放于 `docs/intent/original-requirement.md`。
- 完整规范化需求主文档固定存放于 `docs/intent/normalized-requirement.md`。
- 项目说明文档固定存放于 `docs/project-overview.md`。
- 整体操作指南固定存放于 `docs/operation-guide.md`。
- 机器可读索引固定存放于 `.nexus/project-intent.json`。

### 原始意图摘录

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

### 规范化意图摘录

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
- public clone 必须能在任意目录运行基础 CLI、测试、render 和 watch；运行后产生的 `.data/`、`generated/`、`docs/codex-personalization-registry.md`、构建缓存和认证/runtime 文件必须被 `.gitig

...（已截断，完整内容见对应意图文档）

### 项目说明摘录

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
- `workflow route --text` 只做确定性路由说明；实际读取和展示仍由对应 su

...（已截断，完整内容见对应意图文档）

## Skill 入口

```text
$nexus-workflow 为项目 <PROJECT_ROOT> 生成整体操作指南
$nexus-workflow 同步项目 <PROJECT_ROOT> 的整体操作指南到飞书
$nexus-workflow 将项目 <PROJECT_ROOT> 同步到 GitHub public，确认 public 发布
```

## 初始化与日常更新

- 新项目初始化应创建真实项目目录，并在默认情况下初始化 git。
- GitHub private 同步是默认能力；只有指令显式写“不同步 GitHub”、“跳过 GitHub 同步”、`no-github-sync`，或 CLI 使用 `--no-github-sync` 时才跳过。
- Feishu 是操作指南、说明文档和初始化/更新记录的发布通道；初始化项目时默认写入 `docs/feishu-records.md` 并同步到飞书，只有指令显式写“不同步飞书”、“跳过飞书”、`no-feishu-sync`，或 CLI 使用 `--no-feishu-sync` 时才跳过。
- 激活 `$nexus-workflow` 后，每次对项目内容产生更新，都应默认触发飞书自动同步：优先更新已有线上文档，没有对应绑定时才新建，不能把同一份说明拆成多份重复文件。
- 如果飞书配置不可用，应 blocked 到 setup/doctor，不应假装写入成功；本地记录和本地指南仍需保留为 artifact。
- GitHub public 发布永远需要显式确认，不能跟随 private 自动发布。

## GitHub 同步

private 仓库：`<PRIVATE_REPO>`

public 仓库：`YaofeiHe/codpm-public`

GitHub CLI 未认证或 token 失效时，workflow 使用原生 GitHub CLI 浏览器登录：

```bash
gh auth login --web --clipboard --skip-ssh-key --git-protocol https --hostname github.com
```

用户手动完成邮箱、密码、2FA、CAPTCHA 和授权确认。workflow 不读取本地邮箱、密码、token、cookie、浏览器 profile、SSH key、`.env` 或 2FA/CAPTCHA 内容。

### GitHub 登录与同步经验

- 如果 `gh auth login --web` 在 `https://github.com/login/device/code` 阶段返回 EOF，不要立即让用户重复登录；workflow 应先复查 `gh auth status --hostname github.com`，因为设备授权可能已经成功写入 GitHub CLI 状态。
- 如果登录启动失败包含代理、`127.0.0.1`、`operation not permitted`、`dial tcp` 或 EOF，优先复用 recovery playbook 的 `retry_without_proxy_and_debug_api` 方向：绕开代理并开启 `GH_DEBUG=api` 后再次发起 GitHub CLI 官方 web/device 登录。
- 如果 GitHub 仓库创建失败，先检查是否为同名 private/public 仓库已存在；若 `gh repo view` 可访问，应复用现有仓库、补齐 remote，并重试原 bootstrap/sync，不要默认更换仓库名。
- 如果 `git push` 看似卡住或失败，先收口检查本地 commit、remote、GitHub 仓库可访问性和 `gh auth setup-git --hostname github.com`；确认凭证桥接可用后再重试原 private/public sync。
- GitHub 登录、建仓、凭证桥接、push、public staging/secret scan 任一环节失败时，应先查项目 `.nexus/recovery-playbook.json` 和内置经验；命中经验先按对应方向尝试或发起提权，仍失败才调用高精度恢复模块。
- 如果没有精确命中的经验，高精度恢复模块应读取相关经验库条款和历史操作结果作为参考证据，先判断经验是否与当前情景有关、是否仍有效、是否值得尝试；经验无关时应直接丢弃并自主规划新路线，不能被经验库限制住。

public 发布必须先生成 staging，并通过 secret scan。`.env`、token、key、cookie、apikey、本地运行数据、`.data`、`.codex`、`.agents` 等不能进入 public。

## Feishu 同步

- 本指南的主文件是 `docs/operation-guide.md`。
- 同步到飞书时，应优先把本地 Markdown 文件上传并通过 Drive import task 导入为飞书云文档，以保留 Markdown 标题、列表、代码块等结构。
- Markdown 导入需要 folder_token 作为目标文件夹；仅配置 doc_token 时不能保真导入 `.md`。
- 飞书同步应维护 `.nexus/feishu-documents.json`，按本地 Markdown 路径绑定线上 docx；有效绑定存在时更新同一文档，不重复创建。
- 初始化和日常更新记录统一写入 `docs/feishu-records.md`，不应为每一次记录生成一份独立飞书文档。
- 如果绑定文档已删除、失效或资源不可访问，且 folder_token 可用，workflow 应在同一条同步指令内自动标记旧绑定为 stale、重新导入新文档并更新绑定。
- 只有缺凭证、缺 folder_token、缺 API 权限、缺资源权限或网络不可用等真实外部条件时才 blocked；blocked 的下一步提示必须指向真实缺口，并回到原同步指令重试。
- 缺少 `.nexus/feishu.json`、app_id/app_secret、folder_token、`docs:document.media:upload`/Drive 导入上传权限或文件夹资源权限时，应返回明确 blocked reason。
- Feishu 配置和权限问题由 `feishu setup` / `feishu doctor` 处理，不使用 mock 替代。

## 验收边界

- GitHub private/bootstrap/auth/secret scan 已作为基础能力验证；日常变更不重复跑完整 GitHub private E2E。
- Nexus 自身指南同步飞书可以作为本机真实 Feishu 自同步测试。
- Verix 飞书同步、Nexus 初始化新项目后的飞书同步、public 发布由后续 `$` 指令验收。

## 机器可读上下文

```json
{
  "schema": "nexus.operation_guide_context.v1",
  "project": "codpm",
  "target": "project",
  "private_repo": "<PRIVATE_REPO>",
  "public_repo": "YaofeiHe/codpm-public",
  "updated_at": "2026-06-12T08:11:24.592404+00:00"
}
```
