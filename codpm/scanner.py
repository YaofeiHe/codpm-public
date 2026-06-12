from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable

from .io import mtime_iso, now_iso, sha256_file
from .model import Surface, stable_id
from .paths import FORGE_ROOT, codex_home


def _surface(
    path: Path,
    *,
    surface_type: str,
    scope: str,
    project: str = "",
    source_of_truth: bool = True,
    loaded_by_codex: str = "unknown",
    summary: str = "",
    risk: str = "low",
    metadata: dict | None = None,
) -> Surface:
    exists = path.exists()
    return Surface(
        id=stable_id(surface_type, scope, path, project),
        type=surface_type,
        scope=scope,
        project=project,
        path=str(path),
        exists=exists,
        source_of_truth=source_of_truth,
        loaded_by_codex=loaded_by_codex,
        content_hash=sha256_file(path) if exists and path.is_file() else "",
        last_modified=mtime_iso(path) if exists else "",
        summary=summary,
        risk=risk,
        evidence=[str(path)] if exists else [],
        metadata=metadata or {},
    )


def _files(base: Path, pattern: str) -> list[Path]:
    if not base.exists():
        return []
    return sorted(path for path in base.glob(pattern) if path.is_file())


def _skill_files(base: Path) -> list[Path]:
    return _files(base, "*/SKILL.md")


def _project_dirs() -> list[Path]:
    if not FORGE_ROOT.exists():
        return []
    return sorted(path for path in FORGE_ROOT.iterdir() if path.is_dir() and not path.name.startswith("."))


def _global_surfaces() -> list[Surface]:
    home = codex_home()
    surfaces = [
        _surface(
            home / "AGENTS.md",
            surface_type="codex_instruction",
            scope="global",
            loaded_by_codex="yes",
            summary="Global Codex behavior instructions.",
        ),
        _surface(
            home / "AGENTS.override.md",
            surface_type="codex_instruction_override",
            scope="global",
            loaded_by_codex="unknown",
            summary="Potential global instruction override.",
        ),
        _surface(
            home / "config.toml",
            surface_type="codex_config",
            scope="global",
            loaded_by_codex="yes",
            summary="Global Codex CLI configuration.",
        ),
        _surface(
            home / "hooks.json",
            surface_type="codex_hook",
            scope="global",
            loaded_by_codex="yes",
            summary="Global Codex hook configuration.",
        ),
        _surface(
            home / "memories",
            surface_type="codex_memory",
            scope="global",
            source_of_truth=False,
            loaded_by_codex="unknown",
            summary="Global Codex memory directory.",
            risk="medium",
        ),
        _surface(
            home / "memories_1.sqlite",
            surface_type="codex_memory",
            scope="global",
            source_of_truth=False,
            loaded_by_codex="unknown",
            summary="Global Codex memory database.",
            risk="medium",
        ),
    ]
    for path in _files(home / "rules", "*.rules"):
        surfaces.append(
            _surface(
                path,
                surface_type="execpolicy_rule",
                scope="global",
                loaded_by_codex="yes",
                summary="Codex execpolicy command rule file.",
            )
        )
    for path in _skill_files(home / "skills"):
        surfaces.append(
            _surface(
                path,
                surface_type="skill",
                scope="global",
                loaded_by_codex="yes",
                summary="Global Codex skill.",
            )
        )
    for path in _skill_files(Path.home() / ".agents" / "skills"):
        surfaces.append(
            _surface(
                path,
                surface_type="skill",
                scope="global",
                loaded_by_codex="unknown",
                summary="Agent skill visible from ~/.agents.",
            )
        )
    return surfaces


def _forge_surfaces() -> list[Surface]:
    surfaces = [
        _surface(
            FORGE_ROOT / "AGENTS.md",
            surface_type="codex_instruction",
            scope="forge",
            project=FORGE_ROOT.name,
            loaded_by_codex="yes",
            summary="Forge-level Codex behavior instructions.",
        ),
        _surface(
            FORGE_ROOT / ".codex" / "config.toml",
            surface_type="codex_config",
            scope="forge",
            project=FORGE_ROOT.name,
            loaded_by_codex="yes",
            summary="Forge-level Codex configuration.",
        ),
        _surface(
            FORGE_ROOT / ".codex" / "hooks.json",
            surface_type="codex_hook",
            scope="forge",
            project=FORGE_ROOT.name,
            loaded_by_codex="yes",
            summary="Forge-level Codex hooks.",
        ),
    ]
    for path in _files(FORGE_ROOT / ".codex" / "rules", "*.rules"):
        surfaces.append(
            _surface(
                path,
                surface_type="execpolicy_rule",
                scope="forge",
                project=FORGE_ROOT.name,
                loaded_by_codex="yes",
                summary="Forge-level execpolicy rule file.",
            )
        )
    for path in _skill_files(FORGE_ROOT / ".agents" / "skills"):
        surfaces.append(
            _surface(
                path,
                surface_type="skill",
                scope="forge",
                project=FORGE_ROOT.name,
                loaded_by_codex="unknown",
                summary="Forge-level agent skill.",
            )
        )
    return surfaces


def _project_surfaces(project_dir: Path) -> list[Surface]:
    name = project_dir.name
    surfaces = [
        _surface(
            project_dir / "AGENTS.md",
            surface_type="codex_instruction",
            scope="project",
            project=name,
            loaded_by_codex="yes",
            summary=f"Project-level Codex behavior instructions for {name}.",
        ),
        _surface(
            project_dir / ".codex" / "config.toml",
            surface_type="codex_config",
            scope="project",
            project=name,
            loaded_by_codex="yes",
            summary=f"Project-level Codex configuration for {name}.",
        ),
        _surface(
            project_dir / ".codex" / "hooks.json",
            surface_type="codex_hook",
            scope="project",
            project=name,
            loaded_by_codex="yes",
            summary=f"Project-level Codex hooks for {name}.",
        ),
        _surface(
            project_dir / ".nexus",
            surface_type="nexus_project",
            scope="project",
            project=name,
            source_of_truth=True,
            loaded_by_codex="no",
            summary=f"Nexus project state for {name}.",
        ),
    ]
    for path in _files(project_dir / ".codex" / "rules", "*.rules"):
        surfaces.append(
            _surface(
                path,
                surface_type="execpolicy_rule",
                scope="project",
                project=name,
                loaded_by_codex="yes",
                summary=f"Project-level execpolicy rule file for {name}.",
            )
        )
    for path in _skill_files(project_dir / ".agents" / "skills"):
        surfaces.append(
            _surface(
                path,
                surface_type="skill",
                scope="project",
                project=name,
                loaded_by_codex="unknown",
                summary=f"Project-level agent skill for {name}.",
            )
        )
    return surfaces


def _tool_surfaces() -> list[Surface]:
    tools = ["codex", "dotagents", "agent-rules-sync", "python"]
    surfaces: list[Surface] = []
    for tool in tools:
        found = shutil.which(tool)
        path = Path(found) if found else Path(f"tool://{tool}")
        surfaces.append(
            Surface(
                id=f"tool:external:{tool}",
                type="tool",
                scope="external",
                project="",
                path=str(path),
                exists=bool(found),
                source_of_truth=False,
                loaded_by_codex="no",
                summary=f"External tool availability: {tool}.",
                risk="medium" if not found else "low",
                evidence=[found] if found else [],
                metadata={"command": tool},
            )
        )
    return surfaces


def scan_surfaces(*, include_missing: bool = True) -> list[Surface]:
    surfaces: list[Surface] = []
    surfaces.extend(_global_surfaces())
    surfaces.extend(_forge_surfaces())
    for project in _project_dirs():
        surfaces.extend(_project_surfaces(project))
    surfaces.extend(_tool_surfaces())
    if include_missing:
        return surfaces
    return [surface for surface in surfaces if surface.exists]


def inventory_payload(*, include_missing: bool = True) -> dict:
    surfaces = scan_surfaces(include_missing=include_missing)
    return {
        "schema": "codpm.inventory.v1",
        "generated_at": now_iso(),
        "codex_home": str(codex_home()),
        "forge_root": str(FORGE_ROOT),
        "surfaces": [surface.to_dict() for surface in surfaces],
        "summary": summarize_surfaces(surfaces),
    }


def summarize_surfaces(surfaces: Iterable[Surface]) -> dict:
    by_type: dict[str, int] = {}
    by_scope: dict[str, int] = {}
    existing = 0
    for surface in surfaces:
        by_type[surface.type] = by_type.get(surface.type, 0) + 1
        by_scope[surface.scope] = by_scope.get(surface.scope, 0) + 1
        existing += 1 if surface.exists else 0
    return {
        "total": sum(by_type.values()),
        "existing": existing,
        "by_type": dict(sorted(by_type.items())),
        "by_scope": dict(sorted(by_scope.items())),
    }

