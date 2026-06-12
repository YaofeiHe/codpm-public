from __future__ import annotations

from pathlib import Path
from typing import Any

from .checker import check
from .parser import parse_surface
from .registry import find_entry
from .scanner import scan_surfaces


def explain_current() -> dict[str, Any]:
    surfaces = [surface for surface in scan_surfaces(include_missing=True) if surface.exists]
    by_scope: dict[str, list[dict[str, Any]]] = {}
    for surface in surfaces:
        by_scope.setdefault(surface.scope, []).append(
            {
                "id": surface.id,
                "type": surface.type,
                "project": surface.project,
                "path": surface.path,
                "summary": parse_surface(surface).get("summary", surface.summary),
            }
        )
    return {
        "schema": "codpm.explain_current.v1",
        "summary": "Current personalization state is derived from real Codex surfaces, not registry entries.",
        "by_scope": by_scope,
        "check": check(),
    }


def explain_surface(surface_id_or_path: str) -> dict[str, Any]:
    surfaces = scan_surfaces(include_missing=True)
    for surface in surfaces:
        if surface.id == surface_id_or_path or surface.path == surface_id_or_path:
            return {
                "schema": "codpm.explain_surface.v1",
                "surface": surface.to_dict(),
                "parsed": parse_surface(surface),
            }
    path = Path(surface_id_or_path).expanduser()
    for surface in surfaces:
        if Path(surface.path).expanduser() == path:
            return {
                "schema": "codpm.explain_surface.v1",
                "surface": surface.to_dict(),
                "parsed": parse_surface(surface),
            }
    return {"schema": "codpm.explain_surface.v1", "ok": False, "reason": "surface_not_found"}


def explain_registry(entry_id: str) -> dict[str, Any]:
    entry = find_entry(entry_id)
    if not entry:
        return {"schema": "codpm.explain_registry.v1", "ok": False, "reason": "registry_entry_not_found"}
    check_payload = check()
    status = next((item for item in check_payload["registry"] if item.get("id") == entry_id), None)
    return {
        "schema": "codpm.explain_registry.v1",
        "entry": entry,
        "activation": status,
        "conclusion": _activation_conclusion(status),
    }


def _activation_conclusion(status: dict[str, Any] | None) -> str:
    if not status:
        return "No activation status is available."
    activation = status.get("activation_status")
    if activation == "active":
        return "This registry entry is backed by real surfaces and can be treated as active for its declared scope."
    if activation == "partial":
        return "This registry entry has some real surface evidence but is not fully active."
    if activation == "missing":
        return "This registry entry requires a surface that is missing; it is not active."
    return "This registry entry is metadata only and must not be described as an active Codex rule."

