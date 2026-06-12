from __future__ import annotations

import re
from pathlib import Path

from .io import now_iso, read_text
from .paths import FORGE_ROOT, codex_home


def add_behavior_rule(
    *,
    scope: str,
    title: str,
    body: str,
    project: str = "",
    allow_global: bool = False,
    replace: bool = False,
) -> dict:
    target_result = _behavior_target(scope=scope, project=project, allow_global=allow_global)
    if not target_result["ok"]:
        return target_result

    target = Path(target_result["path"])
    marker_id = _marker_id(title)
    start = f"<!-- codpm:begin {marker_id} -->"
    end = f"<!-- codpm:end {marker_id} -->"
    block = f"{start}\n## {title.strip()}\n\n{body.strip()}\n{end}\n"

    current = read_text(target) if target.exists() else ""
    if start in current and not replace:
        return _blocked(
            "behavior_rule_already_exists",
            f"Behavior rule already exists in {target}: {marker_id}",
            path=target,
        )

    if start in current and replace:
        pattern = re.compile(re.escape(start) + r".*?" + re.escape(end) + r"\n?", re.DOTALL)
        updated = pattern.sub(block, current)
    else:
        prefix = current.rstrip() + "\n\n" if current.strip() else ""
        updated = prefix + block

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(updated, encoding="utf-8")
    return {
        "ok": True,
        "status": "updated",
        "scope": scope,
        "project": project,
        "path": str(target),
        "marker_id": marker_id,
        "source_of_truth": True,
        "updated_at": now_iso(),
    }


def _behavior_target(*, scope: str, project: str, allow_global: bool) -> dict:
    if scope == "global":
        target = codex_home() / "AGENTS.md"
        if not allow_global:
            return _blocked(
                "global_write_requires_allow_global",
                "Global Codex behavior writes require --allow-global and host permission when run inside Codex.",
                path=target,
            )
        return {"ok": True, "path": str(target)}
    if scope == "forge":
        return {"ok": True, "path": str(FORGE_ROOT / "AGENTS.md")}
    if scope == "project":
        if not project:
            return _blocked("project_required", "Project scope requires --project.", path=FORGE_ROOT)
        project_root = FORGE_ROOT / project
        if not project_root.exists():
            return _blocked("project_missing", f"Project does not exist: {project_root}", path=project_root)
        return {"ok": True, "path": str(project_root / "AGENTS.md")}
    return _blocked("invalid_scope", "Scope must be one of: global, forge, project.", path=FORGE_ROOT)


def _marker_id(title: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "-", title.strip()).strip("-").lower()
    return value or "untitled"


def _blocked(reason: str, message: str, *, path: Path) -> dict:
    return {
        "ok": False,
        "status": "blocked",
        "reason": reason,
        "message": message,
        "path": str(path),
    }
