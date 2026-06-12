---
name: codpm-workflow
description: Use this skill when the user says "使用 codpm", "codpm 管理", "Codex 个性化管理", "rule 管理", "skill 管理", "hook 管理", "MCP 管理", "memory 管理", "同步个性化登记表", or explicitly invokes "$codpm-workflow". This skill routes natural language requests to the local codpm CLI at <PROJECT_ROOT>.
---

# codpm Workflow

This skill is a thin natural-language router. The executable logic lives in the local `codpm` CLI, and the CLI must inspect real Codex personalization surfaces instead of treating a registry entry as an active Codex rule.

## Absolute Invocation

Run all local commands from the project root:

```bash
cd <PROJECT_ROOT> && python -B -m codpm.cli <command>
```

Use `python -B` to avoid routine `__pycache__` writes. Do not use relative paths such as `cd codpm`.

## Source-Of-Truth Boundary

- Codex behavior source of truth means actual loaded or loadable surfaces such as `$CODEX_HOME/AGENTS.md`, project `AGENTS.md`, `$CODEX_HOME/rules/*.rules`, `.codex/config.toml`, hooks, skills, MCP config, and memory files.
- `codpm/registry/*.json` is governance metadata. It can describe, check, and render personalization entries, but it does not by itself prove Codex will obey a behavior.
- `$CODEX_HOME/rules/*.rules` is an execpolicy command-approval surface, not a natural-language behavior-instruction surface.
- If an operation cannot be executed against a real surface or real external service, report it as blocked. Do not call dry-run, mock, or generated text a completed sync.

## Natural Language Routing

### Workflow Router

When the user gives a natural-language codpm request and the target command is not obvious, first route it deterministically:

```bash
cd <PROJECT_ROOT> && python -B -m codpm.cli workflow route --text "<user request>"
```

Use the returned command as the next `codpm.cli` invocation. The router is only a deterministic bridge from `$codpm-workflow` language to CLI commands; it does not replace real surface inspection.

### Current Inventory

User asks for current personalization state, all config, or a general scan.

Run:

```bash
cd <PROJECT_ROOT> && python -B -m codpm.cli scan
```

Use `inventory --json` only when structured details are needed:

```bash
cd <PROJECT_ROOT> && python -B -m codpm.cli inventory --json
```

### Rules

User asks to list or display rule content.

Run:

```bash
cd <PROJECT_ROOT> && python -B -m codpm.cli rule list
```

For global/system Codex rules, run:

```bash
cd <PROJECT_ROOT> && python -B -m codpm.cli rule list --scope global
```

For one project, run:

```bash
cd <PROJECT_ROOT> && python -B -m codpm.cli rule list --scope project --project <project>
```

For a concrete file path, run:

```bash
cd <PROJECT_ROOT> && python -B -m codpm.cli rule list --path <path>
```

User asks for rule locations, missing rule files, or whether a rule surface exists.

Run:

```bash
cd <PROJECT_ROOT> && python -B -m codpm.cli list-rules
```

Answer by separating:

- `AGENTS.md` and instruction files: behavior instructions.
- `.rules` files: execpolicy command approval rules.
- registry entries: management metadata only.

### Skills

User asks for skills or skill management.

Run:

```bash
cd <PROJECT_ROOT> && python -B -m codpm.cli skill list
```

For one skill, run:

```bash
cd <PROJECT_ROOT> && python -B -m codpm.cli skill show <name-or-path>
```

Skill maintenance is currently an interface boundary only. Do not represent display output as an install, update, or sync.

If the user asks to maintain a skill, run the explicit interface command and report the blocked result:

```bash
cd <PROJECT_ROOT> && python -B -m codpm.cli skill maintain --name <skill> --action <install|update|remove>
```

### Hooks

User asks for hooks or hook status.

Run:

```bash
cd <PROJECT_ROOT> && python -B -m codpm.cli hook list
```

Hook maintenance is currently an explicit interface boundary:

```bash
cd <PROJECT_ROOT> && python -B -m codpm.cli hook maintain --action <add|update|remove>
```

### Config, MCP, Personality

User asks for config, MCP, model, marketplace, personality, or similar Codex settings.

Run:

```bash
cd <PROJECT_ROOT> && python -B -m codpm.cli config show
```

For MCP-only questions, run:

```bash
cd <PROJECT_ROOT> && python -B -m codpm.cli mcp show
```

Config and MCP maintenance are currently explicit interface boundaries:

```bash
cd <PROJECT_ROOT> && python -B -m codpm.cli config maintain --key <key> --action <set|unset>
cd <PROJECT_ROOT> && python -B -m codpm.cli mcp maintain --name <server> --action <add|update|remove>
```

### Memory

User asks about Codex memory or persistent personal context.

Run:

```bash
cd <PROJECT_ROOT> && python -B -m codpm.cli memory boundary
```

Explain memory as advisory unless the CLI output proves a stronger load/enforcement mechanism.

### Registry

User asks for governance registry entries or registered personalization items.

Run:

```bash
cd <PROJECT_ROOT> && python -B -m codpm.cli registry list
```

Use `registry list --json` if evidence details are needed. Do not call registry entries "real Codex rules" unless their declared surfaces point to actual Codex rule/instruction files and `check` verifies them.

### Explain

User asks what codpm knows overall.

Run:

```bash
cd <PROJECT_ROOT> && python -B -m codpm.cli explain current
```

User asks to explain a concrete file path or surface id.

Run:

```bash
cd <PROJECT_ROOT> && python -B -m codpm.cli explain surface <id-or-path>
```

User asks to explain a governance registry entry id.

Run:

```bash
cd <PROJECT_ROOT> && python -B -m codpm.cli explain registry <entry-id>
```

### Check

User asks whether entries are valid, active, missing, or registry-only.

Run:

```bash
cd <PROJECT_ROOT> && python -B -m codpm.cli check
```

Use `check --json` when exact status and evidence are needed.

### Render

User asks to update the personalization registry document or Feishu-ready content.

Run:

```bash
cd <PROJECT_ROOT> && python -B -m codpm.cli render
```

The generated documents are:

- `<PROJECT_ROOT>/generated/codex-personalization-registry.md`
- `<FORGE_ROOT>/docs/codex-personalization-registry.md`

### Feishu Sync

User asks to preview Feishu sync.

Run:

```bash
cd <PROJECT_ROOT> && python -B -m codpm.cli sync feishu
```

User explicitly asks to write or execute Feishu sync.

Run:

```bash
cd <PROJECT_ROOT> && python -B -m codpm.cli sync feishu --execute
```

If credentials, Nexus, permissions, or the concrete Feishu target are missing, report the command's blocked reason. Do not represent dry-run as a successful write.

### Watcher

User asks to watch personalization changes once, refresh if changed, or check whether the registry document is stale.

Run:

```bash
cd <PROJECT_ROOT> && python -B -m codpm.cli watch --once
```

User explicitly asks to continuously watch.

Run with an explicit interval:

```bash
cd <PROJECT_ROOT> && python -B -m codpm.cli watch --interval 5
```

Do not start continuous polling unless the user explicitly asks for it.

## Editing Boundary

The CLI can write behavior rules only by editing real `AGENTS.md` source-of-truth files. It does not silently edit global Codex files.

If the user asks to modify a real Codex behavior rule:

1. Locate the correct target with `list-rules`, `list-configs`, `list-hooks`, or `list-skills`.
2. Use `rule add-behavior` for new behavior instructions when the target is `AGENTS.md`.
3. For global `$CODEX_HOME/AGENTS.md`, use `--allow-global` only after the user explicitly asks for a global write and Codex grants host permission.
4. Run the relevant list command, then `check`, then `render`.

Add a forge-level behavior rule:

```bash
cd <PROJECT_ROOT> && python -B -m codpm.cli rule add-behavior --scope forge --title "<title>" --body "<body>"
```

Add a project-level behavior rule:

```bash
cd <PROJECT_ROOT> && python -B -m codpm.cli rule add-behavior --scope project --project "<project>" --title "<title>" --body "<body>"
```

Add a global behavior rule only with explicit permission:

```bash
cd <PROJECT_ROOT> && python -B -m codpm.cli rule add-behavior --scope global --allow-global --title "<title>" --body "<body>"
```

If the user asks to modify registry metadata only:

1. Edit `<PROJECT_ROOT>/registry/entries.json`.
2. Run `check`.
3. Run `render`.
4. Say clearly that registry metadata is not itself an active Codex rule.

## Output Style

Answer in Chinese by default for Chinese user requests. Include the command result that matters, the real source-of-truth path when relevant, and whether the item is an actual Codex surface, registry metadata, or generated/synced artifact.
