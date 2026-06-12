from __future__ import annotations

from pathlib import Path
from typing import Any

from .parser import content_contains
from .paths import resolve_vars
from .registry import registry_entries
from .scanner import inventory_payload, scan_surfaces


def check() -> dict[str, Any]:
    surfaces = scan_surfaces(include_missing=True)
    surface_by_path = {surface.path: surface for surface in surfaces}
    registry_results = []
    errors: list[str] = []
    warnings: list[str] = []

    for entry in registry_entries():
        result = _check_registry_entry(entry, surface_by_path)
        registry_results.append(result)
        if result["activation_status"] in {"missing"}:
            errors.append(f"registry entry missing required surface: {entry.get('id')}")
        elif result["activation_status"] in {"partial", "registry_only"}:
            warnings.append(f"registry entry not fully active: {entry.get('id')} ({result['activation_status']})")

    inventory = inventory_payload(include_missing=True)
    return {
        "schema": "codpm.check.v1",
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "registry": registry_results,
        "inventory_summary": inventory["summary"],
    }


def _check_registry_entry(entry: dict[str, Any], surface_by_path: dict[str, Any]) -> dict[str, Any]:
    surfaces = entry.get("actual_surfaces")
    if not isinstance(surfaces, list) or not surfaces:
        return {
            "id": entry.get("id", ""),
            "activation_status": "registry_only",
            "surfaces": [],
            "findings": ["No actual_surfaces declared."],
        }

    surface_results = []
    required_missing = False
    matched = 0
    existing = 0

    for item in surfaces:
        raw_path = str(item.get("path") or "")
        required = bool(item.get("required", True))
        query = str(item.get("evidence_query") or "")
        path = resolve_vars(raw_path)
        surface = surface_by_path.get(str(path))
        exists = path.exists()
        if exists:
            existing += 1
        evidence_match = False
        if surface and query:
            evidence_match = content_contains(surface, query)
        elif exists:
            evidence_match = True
        if evidence_match:
            matched += 1
        if required and not exists:
            required_missing = True
        surface_results.append(
            {
                "path": str(path),
                "declared_path": raw_path,
                "required": required,
                "exists": exists,
                "evidence_query": query,
                "evidence_match": evidence_match,
                "type": item.get("type", ""),
            }
        )

    if required_missing:
        status = "missing"
    elif matched == len(surface_results):
        status = "active"
    elif existing:
        status = "partial"
    else:
        status = "registry_only"

    return {
        "id": entry.get("id", ""),
        "title": entry.get("title", ""),
        "activation_status": status,
        "surfaces": surface_results,
        "findings": [],
    }


def stale_doc(render_path: Path, inventory_hash: str) -> bool:
    if not render_path.exists():
        return True
    return inventory_hash not in render_path.read_text(encoding="utf-8", errors="replace")

