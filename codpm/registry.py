from __future__ import annotations

from typing import Any

from .io import load_json, write_json
from .paths import registry_dir


DEFAULT_REGISTRY = {
    "schema": "codpm.registry.v1",
    "entries": [],
}


def registry_path():
    return registry_dir() / "entries.json"


def load_registry() -> dict[str, Any]:
    return load_json(registry_path(), DEFAULT_REGISTRY.copy())


def save_registry(payload: dict[str, Any]) -> None:
    write_json(registry_path(), payload)


def registry_entries() -> list[dict[str, Any]]:
    payload = load_registry()
    entries = payload.get("entries", [])
    return entries if isinstance(entries, list) else []


def find_entry(entry_id: str) -> dict[str, Any] | None:
    for entry in registry_entries():
        if entry.get("id") == entry_id:
            return entry
    return None


def ensure_registry() -> None:
    if not registry_path().exists():
        save_registry(DEFAULT_REGISTRY.copy())

