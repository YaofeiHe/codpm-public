from __future__ import annotations

from pathlib import Path
from typing import Any

from .parser import parse_surface
from .registry import registry_entries
from .scanner import scan_surfaces


SURFACE_TYPES = {
    "rule": {"codex_instruction", "codex_instruction_override"},
    "execpolicy": {"execpolicy_rule"},
    "skill": {"skill"},
    "hook": {"codex_hook"},
    "config": {"codex_config"},
    "mcp": {"codex_config", "tool"},
    "memory": {"codex_memory"},
}


def list_personalization(
    *,
    surface_kind: str = "",
    scope: str = "",
    project: str = "",
    path: str = "",
) -> dict[str, Any]:
    surfaces = _filter_surfaces(
        surface_kind=surface_kind,
        scope=scope,
        project=project,
        path=path,
    )
    return {
        "schema": "codpm.personalization_list.v1",
        "surface_kind": surface_kind or "all",
        "scope": scope or "all",
        "project": project,
        "path": path,
        "surfaces": [_surface_payload(surface) for surface in surfaces],
        "registry_note": _registry_note(),
    }


def route_workflow(text: str) -> dict[str, Any]:
    normalized = text.strip().lower()
    command = ["personalization", "list"]
    reason = "general_personalization_inventory"

    if _contains_any(normalized, ["规则", "rule", "agents.md"]):
        command = ["rule", "list"]
        reason = "rule_content_listing"
    elif _contains_any(normalized, ["skill", "技能"]):
        command = ["skill", "list"]
        reason = "skill_listing"
    elif _contains_any(normalized, ["hook", "钩子"]):
        command = ["hook", "list"]
        reason = "hook_listing"
    elif _contains_any(normalized, ["mcp"]):
        command = ["mcp", "show"]
        reason = "mcp_listing"
    elif _contains_any(normalized, ["config", "配置", "personality", "model", "模型"]):
        command = ["config", "show"]
        reason = "config_listing"
    elif _contains_any(normalized, ["memory", "记忆", "memories"]):
        command = ["memory", "boundary"]
        reason = "memory_boundary"

    scope = _scope_from_text(normalized)
    if scope:
        command.extend(["--scope", scope])
    project = _project_from_text(normalized)
    if project and "--project" not in command:
        command.extend(["--scope", "project", "--project", project])

    return {
        "schema": "codpm.workflow_route.v1",
        "text": text,
        "command": command,
        "reason": reason,
        "source_of_truth": "real Codex personalization surfaces",
        "registry_role": _registry_note(),
    }


def maintenance_interface(*, surface_kind: str, action: str, target: str = "") -> dict[str, Any]:
    return {
        "schema": "codpm.maintenance_interface.v1",
        "ok": False,
        "status": "blocked",
        "reason": "maintenance_interface_only",
        "surface_kind": surface_kind,
        "action": action,
        "target": target,
        "message": (
            f"{surface_kind} maintenance is exposed as an interface boundary only. "
            "A real write command must define schema validation, target resolution, permissions, and verification first."
        ),
        "source_of_truth": "real Codex personalization surfaces",
    }


def _filter_surfaces(*, surface_kind: str, scope: str, project: str, path: str):
    requested_path = Path(path).expanduser() if path else None
    allowed_types = SURFACE_TYPES.get(surface_kind, set())
    surfaces = []
    for surface in scan_surfaces(include_missing=True):
        if allowed_types and surface.type not in allowed_types:
            continue
        if surface_kind == "mcp" and surface.type == "codex_config":
            parsed = parse_surface(surface)
            if "mcp_servers" not in parsed.get("keys", []):
                continue
        if scope and surface.scope != scope:
            continue
        if project and surface.project != project:
            continue
        if requested_path and Path(surface.path).expanduser() != requested_path:
            continue
        surfaces.append(surface)
    return surfaces


def _surface_payload(surface) -> dict[str, Any]:
    parsed = parse_surface(surface)
    return {
        "id": surface.id,
        "type": surface.type,
        "scope": surface.scope,
        "project": surface.project,
        "path": surface.path,
        "status": "present" if surface.exists else "missing",
        "source_of_truth": surface.source_of_truth,
        "loaded_by_codex": surface.loaded_by_codex,
        "summary": parsed.get("summary", surface.summary),
        "parsed": _display_parsed(surface.type, parsed),
    }


def _display_parsed(surface_type: str, parsed: dict[str, Any]) -> dict[str, Any]:
    if surface_type in {"codex_instruction", "codex_instruction_override"}:
        return {"rule_blocks": parsed.get("rule_blocks", []), "items": parsed.get("items", [])}
    if surface_type == "skill":
        return {
            "name": parsed.get("name", ""),
            "description": parsed.get("description", ""),
            "headings": parsed.get("items", []),
            "frontmatter": parsed.get("frontmatter", {}),
        }
    if surface_type == "codex_memory":
        return {
            "boundary": "Memory is advisory; codpm reports existence and risk, not private memory contents.",
            "items": [],
        }
    return {"items": parsed.get("items", []), "keys": parsed.get("keys", [])}


def _registry_note() -> str:
    count = len(registry_entries())
    if count == 0:
        return "registry/entries.json has no entries and is not used as a rule source."
    return f"registry/entries.json has {count} governance entries; it is metadata, not the active behavior source."


def _contains_any(text: str, needles: list[str]) -> bool:
    return any(needle in text for needle in needles)


def _scope_from_text(text: str) -> str:
    if _contains_any(text, ["系统级", "全局", "global", "codex系统"]):
        return "global"
    if _contains_any(text, ["forge级", "forge 层", "forge根", "forge root"]):
        return "forge"
    return ""


def _project_from_text(text: str) -> str:
    for surface in scan_surfaces(include_missing=True):
        if surface.scope == "project" and surface.project and surface.project.lower() in text:
            return surface.project
    return ""
