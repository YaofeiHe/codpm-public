from __future__ import annotations

import subprocess
from pathlib import Path

from .io import load_json, now_iso, write_json
from .paths import FORGE_ROOT, PROJECT_ROOT, data_dir
from .render import render


def sync_feishu(*, execute: bool = False) -> dict:
    render_payload = render()
    doc_path = Path(render_payload["forge_path"])
    sync_state_path = data_dir() / "sync" / ("feishu.json" if execute else "feishu.dry_run.json")

    project_root = PROJECT_ROOT
    nexus_root = FORGE_ROOT / "nexus"
    project_config = project_root / ".nexus" / "feishu.json"
    command = _feishu_command(project_root, doc_path) if nexus_root.exists() else []

    if not execute:
        payload = {
            "ok": True,
            "status": "dry_run",
            "reason": "" if command else "nexus_missing",
            "render": render_payload,
            "command": command,
            "requires_existing_config": str(project_config),
            "nexus_root": str(nexus_root),
        }
        write_json(sync_state_path, payload)
        return payload

    if not nexus_root.exists():
        payload = _blocked("nexus_missing", "Nexus project is required for Feishu sync.", render_payload, command=command)
        write_json(sync_state_path, payload)
        return payload

    if not project_config.exists():
        payload = _blocked(
            "feishu_config_missing",
            f"Missing Feishu project config: {project_config}",
            render_payload,
            command=command,
        )
        write_json(sync_state_path, payload)
        return payload

    completed = subprocess.run(command, cwd=str(nexus_root), text=True, capture_output=True, check=False)
    payload = {
        "ok": completed.returncode == 0,
        "status": "completed" if completed.returncode == 0 else "blocked",
        "reason": "" if completed.returncode == 0 else "feishu_command_failed",
        "render": render_payload,
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "synced_at": now_iso() if completed.returncode == 0 else "",
    }
    write_json(sync_state_path, payload)
    return payload


def _feishu_command(project_root: Path, doc_path: Path) -> list[str]:
    return [
        "python",
        "-m",
        "nexus.cli",
        "feishu",
        "record",
        "--project-path",
        str(project_root),
        "--title",
        "Codex 个性化管理登记表",
        "--file",
        str(doc_path),
    ]


def sync_status() -> dict:
    real_path = data_dir() / "sync" / "feishu.json"
    dry_run_path = data_dir() / "sync" / "feishu.dry_run.json"
    real = load_json(real_path, {"ok": False, "status": "missing", "path": str(real_path)})
    dry_run = load_json(dry_run_path, {"ok": False, "status": "missing", "path": str(dry_run_path)})
    return {
        "ok": real.get("ok", False),
        "status": real.get("status", "missing"),
        "real_sync": real,
        "dry_run": dry_run,
    }


def _blocked(reason: str, message: str, render_payload: dict, command: list[str] | None = None) -> dict:
    return {
        "ok": False,
        "status": "blocked",
        "reason": reason,
        "message": message,
        "render": render_payload,
        "command": command or [],
        "next_steps": [
            "Configure real Nexus/Feishu credentials.",
            "Run codpm sync feishu --execute again.",
        ],
    }
