from __future__ import annotations

import time
from typing import Any

from .io import load_json, now_iso, write_json
from .paths import data_dir
from .render import render
from .scanner import scan_surfaces


def watch_once() -> dict[str, Any]:
    state_path = data_dir() / "watch" / "state.json"
    from .render import inventory_hash_for_surfaces

    surfaces = scan_surfaces(include_missing=True)
    inventory_hash = inventory_hash_for_surfaces(surfaces)
    previous = load_json(state_path, {})
    changed = previous.get("inventory_hash") != inventory_hash
    render_payload = render() if changed else None
    payload = {
        "ok": True,
        "status": "changed" if changed else "unchanged",
        "inventory_hash": inventory_hash,
        "previous_hash": previous.get("inventory_hash", ""),
        "checked_at": now_iso(),
        "render": render_payload,
    }
    write_json(state_path, payload)
    return payload


def watch_loop(*, interval: float, max_iterations: int | None = None) -> dict[str, Any]:
    iterations = 0
    last: dict[str, Any] = {}
    while max_iterations is None or iterations < max_iterations:
        last = watch_once()
        iterations += 1
        if max_iterations is not None and iterations >= max_iterations:
            break
        time.sleep(interval)
    return {"ok": True, "status": "stopped", "iterations": iterations, "last": last}
