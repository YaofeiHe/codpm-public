from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .checker import check
from .editor import add_behavior_rule
from .explainer import explain_current, explain_registry, explain_surface
from .parser import parse_surface
from .personalization import list_personalization, maintenance_interface, route_workflow
from .registry import registry_entries
from .render import render
from .scanner import inventory_payload, scan_surfaces
from .syncer import sync_feishu, sync_status
from .watcher import watch_loop, watch_once


def _print_json(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _print_scan(payload: dict[str, Any]) -> None:
    print("Codex personalization inventory")
    print(f"- Codex home: {payload['codex_home']}")
    print(f"- Forge root: {payload['forge_root']}")
    print(f"- Surfaces: {payload['summary']['total']} total, {payload['summary']['existing']} existing")
    for key, value in payload["summary"]["by_type"].items():
        print(f"- {key}: {value}")


def _print_surfaces(surface_type: str | None = None) -> None:
    surfaces = [surface for surface in scan_surfaces(include_missing=True) if surface_type is None or surface.type == surface_type]
    for surface in surfaces:
        status = "present" if surface.exists else "missing"
        project = f" [{surface.project}]" if surface.project else ""
        print(f"{surface.scope}{project} {surface.type} {status}: {surface.path}")


def _print_check(payload: dict[str, Any]) -> None:
    print(f"Check: {'ok' if payload['ok'] else 'blocked'}")
    for item in payload["errors"]:
        print(f"ERROR: {item}")
    for item in payload["warnings"]:
        print(f"WARNING: {item}")
    for entry in payload["registry"]:
        print(f"- registry {entry['id']}: {entry['activation_status']}")


def _print_registry_list(payload: dict[str, Any]) -> None:
    entries = payload["entries"]
    if not entries:
        print("No registry entries.")
        return
    for entry in entries:
        entry_type = entry.get("type", "unknown")
        title = entry.get("title") or entry.get("name") or ""
        suffix = f" - {title}" if title else ""
        print(f"{entry.get('id', '<missing-id>')} ({entry_type}){suffix}")


def _print_mcp() -> None:
    found = False
    for surface in scan_surfaces(include_missing=True):
        if surface.type == "codex_config":
            parsed = parse_surface(surface)
            if "mcp_servers" in parsed.get("keys", []):
                found = True
                status = "present" if surface.exists else "missing"
                project = f" [{surface.project}]" if surface.project else ""
                print(f"{surface.scope}{project} codex_config {status}: {surface.path}")
        elif surface.type == "tool":
            found = True
            status = "present" if surface.exists else "missing"
            print(f"{surface.scope} tool {status}: {surface.path}")
    if not found:
        print("No MCP/tool related surfaces found.")


def _print_sync(payload: dict[str, Any]) -> None:
    print(f"Feishu sync: {payload['status']}")
    if payload.get("reason"):
        print(f"Reason: {payload['reason']}")
    if payload.get("message"):
        print(f"Message: {payload['message']}")
    if payload.get("command"):
        print("Command: " + " ".join(payload["command"]))
    for step in payload.get("next_steps", []):
        print(f"Next: {step}")


def _print_update(payload: dict[str, Any]) -> None:
    print(f"Rule update: {payload['status']}")
    if payload.get("reason"):
        print(f"Reason: {payload['reason']}")
    if payload.get("message"):
        print(f"Message: {payload['message']}")
    if payload.get("path"):
        print(f"Path: {payload['path']}")
    if payload.get("marker_id"):
        print(f"Marker: {payload['marker_id']}")


def _print_blocked(payload: dict[str, Any]) -> None:
    print(f"{payload.get('surface_kind', 'maintenance')} maintenance: {payload['status']}")
    print(f"Reason: {payload['reason']}")
    print(f"Message: {payload['message']}")


def _print_personalization(payload: dict[str, Any]) -> None:
    print(f"Personalization surfaces: {payload['surface_kind']}")
    for surface in payload["surfaces"]:
        project = f" [{surface['project']}]" if surface.get("project") else ""
        print(f"{surface['scope']}{project} {surface['type']} {surface['status']}: {surface['path']}")
        parsed = surface.get("parsed", {})
        for block in parsed.get("rule_blocks", []):
            print(f"- {block['title']}")
            for item in block.get("items", []):
                print(f"  - {item}")
        if surface["type"] == "skill":
            if parsed.get("name"):
                print(f"- name: {parsed['name']}")
            if parsed.get("description"):
                print(f"- description: {parsed['description']}")
            for heading in parsed.get("headings", [])[:8]:
                print(f"  - {heading['text']}")
        elif surface["type"] == "codex_memory":
            print(f"- boundary: {parsed.get('boundary')}")
        elif not parsed.get("rule_blocks"):
            for item in parsed.get("items", [])[:12]:
                if "text" in item:
                    print(f"- {item['text']}")
                elif "key" in item:
                    print(f"- {item['key']}: {item.get('type', '')}")
                else:
                    print(f"- {item}")
    print(f"Registry: {payload['registry_note']}")


def _add_scope_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--scope", choices=["global", "forge", "project"], default="")
    parser.add_argument("--project", default="")
    parser.add_argument("--path", default="")
    parser.add_argument("--json", action="store_true")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Codex Personalization Manager")
    sub = parser.add_subparsers(dest="command", required=True)

    scan_parser = sub.add_parser("scan", help="Scan real Codex personalization surfaces")
    scan_parser.add_argument("--json", action="store_true")

    inventory_parser = sub.add_parser("inventory", help="Print real personalization inventory")
    inventory_parser.add_argument("--json", action="store_true")

    sub.add_parser("list-rules", help="List real Codex rule/instruction surfaces")
    sub.add_parser("list-skills", help="List real skill surfaces")
    sub.add_parser("list-hooks", help="List hook surfaces")
    sub.add_parser("list-configs", help="List config surfaces")
    sub.add_parser("list-mcp", help="List MCP/tool related surfaces")
    sub.add_parser("list-memory", help="List memory surfaces")

    personalization_parser = sub.add_parser("personalization", help="Display personalization surfaces")
    personalization_sub = personalization_parser.add_subparsers(dest="personalization_command", required=True)
    personalization_list = personalization_sub.add_parser("list")
    personalization_list.add_argument("--type", choices=["rule", "execpolicy", "skill", "hook", "config", "mcp", "memory"], default="")
    _add_scope_args(personalization_list)

    rule_parser = sub.add_parser("rule", help="Write real Codex rule surfaces")
    rule_sub = rule_parser.add_subparsers(dest="rule_command", required=True)
    rule_list = rule_sub.add_parser("list", help="List Codex behavior rules with content")
    _add_scope_args(rule_list)
    add_behavior = rule_sub.add_parser("add-behavior", help="Append or replace a behavior rule in AGENTS.md")
    add_behavior.add_argument("--scope", choices=["global", "forge", "project"], required=True)
    add_behavior.add_argument("--project", default="")
    add_behavior.add_argument("--title", required=True)
    add_behavior.add_argument("--body", required=True)
    add_behavior.add_argument("--allow-global", action="store_true")
    add_behavior.add_argument("--replace", action="store_true")
    add_behavior.add_argument("--json", action="store_true")

    registry_parser = sub.add_parser("registry", help="Registry metadata commands")
    registry_sub = registry_parser.add_subparsers(dest="registry_command", required=True)
    registry_list = registry_sub.add_parser("list")
    registry_list.add_argument("--json", action="store_true")

    explain_parser = sub.add_parser("explain", help="Explain current state, surface, or registry entry")
    explain_sub = explain_parser.add_subparsers(dest="explain_command", required=True)
    explain_sub.add_parser("current")
    surface_parser = explain_sub.add_parser("surface")
    surface_parser.add_argument("id_or_path")
    registry_explain = explain_sub.add_parser("registry")
    registry_explain.add_argument("entry_id")

    check_parser = sub.add_parser("check", help="Check registry activation against real surfaces")
    check_parser.add_argument("--json", action="store_true")

    render_parser = sub.add_parser("render", help="Render dynamic personalization registry docs")
    render_parser.add_argument("--json", action="store_true")

    sync_parser = sub.add_parser("sync", help="Sync rendered docs to external systems")
    sync_sub = sync_parser.add_subparsers(dest="sync_command", required=True)
    feishu = sync_sub.add_parser("feishu")
    feishu.add_argument("--execute", action="store_true")
    feishu.add_argument("--json", action="store_true")
    status = sync_sub.add_parser("status")
    status.add_argument("--json", action="store_true")

    watch_parser = sub.add_parser("watch", help="Poll real personalization inventory and render on change")
    watch_parser.add_argument("--once", action="store_true")
    watch_parser.add_argument("--interval", type=float, default=0)
    watch_parser.add_argument("--max-iterations", type=int, default=0)
    watch_parser.add_argument("--json", action="store_true")

    skill_parser = sub.add_parser("skill", help="Display skill surfaces")
    skill_sub = skill_parser.add_subparsers(dest="skill_command", required=True)
    skill_list = skill_sub.add_parser("list")
    _add_scope_args(skill_list)
    skill_show = skill_sub.add_parser("show")
    skill_show.add_argument("path_or_name")
    skill_show.add_argument("--json", action="store_true")
    skill_maintain = skill_sub.add_parser("maintain")
    skill_maintain.add_argument("--name", required=True)
    skill_maintain.add_argument("--action", choices=["install", "update", "remove"], required=True)
    skill_maintain.add_argument("--json", action="store_true")

    hook_parser = sub.add_parser("hook", help="Display hook surfaces")
    hook_sub = hook_parser.add_subparsers(dest="hook_command", required=True)
    hook_list = hook_sub.add_parser("list")
    _add_scope_args(hook_list)
    hook_maintain = hook_sub.add_parser("maintain")
    hook_maintain.add_argument("--action", choices=["add", "update", "remove"], required=True)
    _add_scope_args(hook_maintain)

    config_parser = sub.add_parser("config", help="Display Codex config surfaces")
    config_sub = config_parser.add_subparsers(dest="config_command", required=True)
    config_show = config_sub.add_parser("show")
    _add_scope_args(config_show)
    config_maintain = config_sub.add_parser("maintain")
    config_maintain.add_argument("--key", required=True)
    config_maintain.add_argument("--action", choices=["set", "unset"], required=True)
    config_maintain.add_argument("--json", action="store_true")

    mcp_parser = sub.add_parser("mcp", help="Display MCP/tool surfaces")
    mcp_sub = mcp_parser.add_subparsers(dest="mcp_command", required=True)
    mcp_show = mcp_sub.add_parser("show")
    _add_scope_args(mcp_show)
    mcp_maintain = mcp_sub.add_parser("maintain")
    mcp_maintain.add_argument("--name", required=True)
    mcp_maintain.add_argument("--action", choices=["add", "update", "remove"], required=True)
    mcp_maintain.add_argument("--json", action="store_true")

    memory_parser = sub.add_parser("memory", help="Display memory boundary")
    memory_sub = memory_parser.add_subparsers(dest="memory_command", required=True)
    memory_boundary = memory_sub.add_parser("boundary")
    _add_scope_args(memory_boundary)

    workflow_parser = sub.add_parser("workflow", help="Route natural-language workflow requests")
    workflow_sub = workflow_parser.add_subparsers(dest="workflow_command", required=True)
    workflow_route = workflow_sub.add_parser("route")
    workflow_route.add_argument("--text", required=True)
    workflow_route.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)

    if args.command in {"scan", "inventory"}:
        payload = inventory_payload(include_missing=True)
        _print_json(payload) if args.json else _print_scan(payload)
        return 0
    if args.command == "list-rules":
        _print_surfaces("codex_instruction")
        _print_surfaces("codex_instruction_override")
        _print_surfaces("execpolicy_rule")
        return 0
    if args.command == "list-skills":
        _print_surfaces("skill")
        return 0
    if args.command == "list-hooks":
        _print_surfaces("codex_hook")
        return 0
    if args.command == "list-configs":
        _print_surfaces("codex_config")
        return 0
    if args.command == "list-mcp":
        _print_mcp()
        return 0
    if args.command == "list-memory":
        _print_surfaces("codex_memory")
        return 0
    if args.command == "personalization" and args.personalization_command == "list":
        payload = list_personalization(
            surface_kind=args.type,
            scope=args.scope,
            project=args.project,
            path=args.path,
        )
        _print_json(payload) if args.json else _print_personalization(payload)
        return 0
    if args.command == "rule" and args.rule_command == "list":
        payload = list_personalization(
            surface_kind="rule",
            scope=args.scope,
            project=args.project,
            path=args.path,
        )
        _print_json(payload) if args.json else _print_personalization(payload)
        return 0
    if args.command == "rule" and args.rule_command == "add-behavior":
        payload = add_behavior_rule(
            scope=args.scope,
            project=args.project,
            title=args.title,
            body=args.body,
            allow_global=args.allow_global,
            replace=args.replace,
        )
        _print_json(payload) if args.json else _print_update(payload)
        return 0 if payload.get("ok") else 1
    if args.command == "registry" and args.registry_command == "list":
        payload = {"schema": "codpm.registry_list.v1", "entries": registry_entries()}
        _print_json(payload) if args.json else _print_registry_list(payload)
        return 0
    if args.command == "explain":
        if args.explain_command == "current":
            _print_json(explain_current())
            return 0
        if args.explain_command == "surface":
            payload = explain_surface(args.id_or_path)
            _print_json(payload)
            return 0 if payload.get("reason") != "surface_not_found" else 1
        if args.explain_command == "registry":
            payload = explain_registry(args.entry_id)
            _print_json(payload)
            return 0 if payload.get("reason") != "registry_entry_not_found" else 1
    if args.command == "check":
        payload = check()
        _print_json(payload) if args.json else _print_check(payload)
        return 0 if payload["ok"] else 1
    if args.command == "render":
        payload = render()
        _print_json(payload) if args.json else print(f"Rendered: {payload['forge_path']}")
        return 0
    if args.command == "sync" and args.sync_command == "feishu":
        payload = sync_feishu(execute=args.execute)
        _print_json(payload) if args.json else _print_sync(payload)
        return 0 if payload.get("ok") else 1
    if args.command == "sync" and args.sync_command == "status":
        payload = sync_status()
        _print_json(payload) if args.json else print(payload.get("status", "unknown"))
        return 0 if payload.get("ok") else 1
    if args.command == "watch":
        if args.once or args.interval <= 0:
            payload = watch_once()
        else:
            max_iterations = args.max_iterations if args.max_iterations > 0 else None
            payload = watch_loop(interval=args.interval, max_iterations=max_iterations)
        _print_json(payload) if args.json else print(f"Watch: {payload['status']}")
        return 0 if payload.get("ok") else 1
    if args.command == "skill" and args.skill_command == "list":
        payload = list_personalization(surface_kind="skill", scope=args.scope, project=args.project, path=args.path)
        _print_json(payload) if args.json else _print_personalization(payload)
        return 0
    if args.command == "skill" and args.skill_command == "show":
        payload = list_personalization(surface_kind="skill", path=args.path_or_name)
        if not payload["surfaces"]:
            payload = _find_skill_by_name(args.path_or_name)
        _print_json(payload) if args.json else _print_personalization(payload)
        return 0 if payload["surfaces"] else 1
    if args.command == "skill" and args.skill_command == "maintain":
        payload = maintenance_interface(surface_kind="skill", action=args.action, target=args.name)
        _print_json(payload) if args.json else _print_blocked(payload)
        return 1
    if args.command == "hook" and args.hook_command == "list":
        payload = list_personalization(surface_kind="hook", scope=args.scope, project=args.project, path=args.path)
        _print_json(payload) if args.json else _print_personalization(payload)
        return 0
    if args.command == "hook" and args.hook_command == "maintain":
        target = args.path or args.project or args.scope
        payload = maintenance_interface(surface_kind="hook", action=args.action, target=target)
        _print_json(payload) if args.json else _print_blocked(payload)
        return 1
    if args.command == "config" and args.config_command == "show":
        payload = list_personalization(surface_kind="config", scope=args.scope, project=args.project, path=args.path)
        _print_json(payload) if args.json else _print_personalization(payload)
        return 0
    if args.command == "config" and args.config_command == "maintain":
        payload = maintenance_interface(surface_kind="config", action=args.action, target=args.key)
        _print_json(payload) if args.json else _print_blocked(payload)
        return 1
    if args.command == "mcp" and args.mcp_command == "show":
        payload = list_personalization(surface_kind="mcp", scope=args.scope, project=args.project, path=args.path)
        _print_json(payload) if args.json else _print_personalization(payload)
        return 0
    if args.command == "mcp" and args.mcp_command == "maintain":
        payload = maintenance_interface(surface_kind="mcp", action=args.action, target=args.name)
        _print_json(payload) if args.json else _print_blocked(payload)
        return 1
    if args.command == "memory" and args.memory_command == "boundary":
        payload = list_personalization(surface_kind="memory", scope=args.scope, project=args.project, path=args.path)
        _print_json(payload) if args.json else _print_personalization(payload)
        return 0
    if args.command == "workflow" and args.workflow_command == "route":
        payload = route_workflow(args.text)
        _print_json(payload) if args.json else print(" ".join(["python", "-B", "-m", "codpm.cli", *payload["command"]]))
        return 0
    return 1


def _find_skill_by_name(name: str) -> dict[str, Any]:
    payload = list_personalization(surface_kind="skill")
    matches = []
    for surface in payload["surfaces"]:
        parsed = surface.get("parsed", {})
        if parsed.get("name") == name or Path(surface["path"]).parent.name == name:
            matches.append(surface)
    payload["surfaces"] = matches
    return payload


if __name__ == "__main__":
    raise SystemExit(main())
