from __future__ import annotations

import hashlib
from pathlib import Path

from .checker import check
from .io import now_iso, write_json
from .parser import parse_surface
from .paths import data_dir, forge_docs_dir, generated_dir
from .registry import registry_entries
from .model import Surface
from .scanner import inventory_payload, scan_surfaces


def inventory_hash_for_surfaces(surfaces: list[Surface]) -> str:
    payload = [(s.id, s.content_hash, s.exists, s.last_modified) for s in surfaces]
    return hashlib.sha256(repr(payload).encode("utf-8")).hexdigest()


def render() -> dict:
    inventory = inventory_payload(include_missing=True)
    surfaces = scan_surfaces(include_missing=True)
    check_payload = check()
    inventory_hash = inventory_hash_for_surfaces(surfaces)

    lines = [
        "# Codex Personalization Registry",
        "",
        f"- Generated at: `{now_iso()}`",
        f"- Inventory hash: `{inventory_hash}`",
        f"- Codex home: `{inventory['codex_home']}`",
        f"- Forge root: `{inventory['forge_root']}`",
        f"- Check status: `{'ok' if check_payload['ok'] else 'blocked'}`",
        "",
        "## Ground Rule",
        "",
        "Real Codex surfaces are the source of truth. Registry entries are governance metadata only.",
        "",
        "## Inventory Summary",
        "",
    ]
    for key, value in inventory["summary"]["by_type"].items():
        lines.append(f"- `{key}`: {value}")

    lines.extend(["", "## Real Surfaces", ""])
    for surface in sorted(surfaces, key=lambda item: (item.scope, item.project, item.type, item.path)):
        parsed = parse_surface(surface)
        status = "present" if surface.exists else "missing"
        lines.extend(
            [
                f"### {surface.id}",
                "",
                f"- Type: `{surface.type}`",
                f"- Scope: `{surface.scope}`",
                f"- Project: `{surface.project or '-'}`",
                f"- Status: `{status}`",
                f"- Loaded by Codex: `{surface.loaded_by_codex}`",
                f"- Source of truth: `{surface.source_of_truth}`",
                f"- Path: `{surface.path}`",
                f"- Summary: {parsed.get('summary', surface.summary)}",
                "",
            ]
        )

    lines.extend(["## Registry Entries", ""])
    if not registry_entries():
        lines.append("- No registry entries yet.")
    for result in check_payload["registry"]:
        lines.extend(
            [
                f"### {result['id']}",
                "",
                f"- Activation status: `{result['activation_status']}`",
            ]
        )
        for surface in result["surfaces"]:
            lines.append(
                f"- Surface: `{surface['path']}` exists=`{surface['exists']}` evidence_match=`{surface['evidence_match']}`"
            )
        lines.append("")

    lines.extend(["", "## Check Findings", ""])
    if check_payload["errors"]:
        lines.extend(f"- ERROR: {item}" for item in check_payload["errors"])
    if check_payload["warnings"]:
        lines.extend(f"- WARNING: {item}" for item in check_payload["warnings"])
    if not check_payload["errors"] and not check_payload["warnings"]:
        lines.append("- No blocking findings.")

    content = "\n".join(lines) + "\n"
    generated_dir().mkdir(parents=True, exist_ok=True)
    forge_docs_dir().mkdir(parents=True, exist_ok=True)
    generated_path = generated_dir() / "codex-personalization-registry.md"
    forge_path = forge_docs_dir() / "codex-personalization-registry.md"
    generated_path.write_text(content, encoding="utf-8")
    forge_path.write_text(content, encoding="utf-8")

    inventory_path = data_dir() / "inventory" / "latest.json"
    write_json(inventory_path, inventory)

    return {
        "ok": True,
        "generated_path": str(generated_path),
        "forge_path": str(forge_path),
        "inventory_path": str(inventory_path),
        "inventory_hash": inventory_hash,
    }
