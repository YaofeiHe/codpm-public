# codpm

`codpm` is the Codex Personalization Manager for this forge workspace.

Its source of truth is the real Codex personalization surface: `AGENTS.md`, `.rules`, skills, config, hooks, MCP/tool configuration, memory files, and project-level instruction files. The registry is metadata for governance and audit only; it is not proof that a rule is active.

## Quick Start

```bash
python -B -m codpm.cli scan
python -B -m codpm.cli inventory --json
python -B -m codpm.cli list-rules
python -B -m codpm.cli rule list --scope global
python -B -m codpm.cli skill list
python -B -m codpm.cli hook list
python -B -m codpm.cli config show
python -B -m codpm.cli mcp show
python -B -m codpm.cli memory boundary
python -B -m codpm.cli workflow route --text "列表展示规则"
python -B -m codpm.cli skill maintain --name codpm-workflow --action update
python -B -m codpm.cli explain current
python -B -m codpm.cli check
python -B -m codpm.cli render
python -B -m codpm.cli sync feishu
python -B -m codpm.cli watch --once
```

Use `sync feishu --execute` only when real Feishu/Nexus configuration is present and you intend to write externally.

`watch --once` checks the real inventory hash and renders only when the inventory changed. Continuous polling is explicit:

```bash
python -B -m codpm.cli watch --interval 5
```

## Public Clone Hygiene

The public repository is intended to run from any clone directory. Generated runtime files stay local and are ignored by git:

- `.data/`
- `generated/`
- `build/`, `dist/`, `*.egg-info/`
- `.pytest_cache/`, `__pycache__/`
- `.github/nexus-auth/`, `.nexus/runtime/`, `.nexus/private/`

By default `render` writes both generated and docs outputs inside the current codpm project root. Set `CODPM_FORGE_ROOT` only when intentionally writing a forge-level docs copy.

## Real Rule Writes

Behavior rules are written to real `AGENTS.md` files. Registry entries are not treated as active Codex behavior. Use `rule list` to display rule content; `list-rules` remains a low-level surface location inventory.

```bash
python -B -m codpm.cli rule add-behavior --scope forge --title "Rule title" --body "Rule body"
python -B -m codpm.cli rule add-behavior --scope project --project nexus-lab --title "Rule title" --body "Rule body"
```

Global writes target `$CODEX_HOME/AGENTS.md` and are blocked unless explicitly allowed:

```bash
python -B -m codpm.cli rule add-behavior --scope global --allow-global --title "Rule title" --body "Rule body"
```

After a write, run:

```bash
python -B -m codpm.cli list-rules
python -B -m codpm.cli check
python -B -m codpm.cli render
```

<!-- nexus:public-install -->
## Public Install

Install the public package from GitHub:

```bash
python -m pip install git+https://github.com/YaofeiHe/codpm-public.git
```

Smoke test the installed command:

```bash
codpm --help
```

Codex workflow/skill install:

```bash
tmp="$(mktemp -d)" && git clone --depth 1 https://github.com/YaofeiHe/codpm-public.git "$tmp/repo" && mkdir -p "$HOME/.agents/skills" && for skill in skills/codpm-workflow; do cp -R "$tmp/repo/$skill" "$HOME/.agents/skills/"; done
```

This installs the workflow skill directly from the repository files into `$HOME/.agents/skills`.

Private runtime files, credentials, `.env`, tokens, cookies, browser profiles, `.data/`, `.nexus/private/`, and local host paths are not part of the public release.
