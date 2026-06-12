from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys

from codpm.checker import check
from codpm.cli import main
from codpm.editor import add_behavior_rule
from codpm.explainer import explain_current, explain_surface
from codpm.personalization import list_personalization, maintenance_interface, route_workflow
from codpm.render import render
from codpm.scanner import inventory_payload, scan_surfaces
from codpm.syncer import sync_feishu
from codpm.watcher import watch_once


def test_scan_surfaces_finds_real_codex_entries() -> None:
    surfaces = scan_surfaces(include_missing=True)
    assert surfaces
    assert any(surface.type == "execpolicy_rule" for surface in surfaces)
    assert any(surface.type == "codex_instruction" for surface in surfaces)


def test_inventory_payload_has_summary() -> None:
    payload = inventory_payload(include_missing=True)
    assert payload["schema"] == "codpm.inventory.v1"
    assert payload["summary"]["total"] >= payload["summary"]["existing"]


def test_explain_current_uses_real_surfaces() -> None:
    payload = explain_current()
    assert payload["schema"] == "codpm.explain_current.v1"
    assert "by_scope" in payload


def test_explain_surface_by_path() -> None:
    payload = inventory_payload(include_missing=True)
    existing = next(surface for surface in payload["surfaces"] if surface["exists"] and surface["type"] == "execpolicy_rule")
    explained = explain_surface(existing["path"])
    assert explained["schema"] == "codpm.explain_surface.v1"
    assert explained["surface"]["path"] == existing["path"]


def test_check_with_empty_registry_is_ok() -> None:
    payload = check()
    assert payload["schema"] == "codpm.check.v1"
    assert payload["ok"]


def test_render_writes_forge_doc(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("codpm.render.generated_dir", lambda: tmp_path / "generated")
    monkeypatch.setattr("codpm.render.forge_docs_dir", lambda: tmp_path / "docs")
    monkeypatch.setattr("codpm.render.data_dir", lambda: tmp_path / ".data")

    payload = render()
    assert payload["ok"]
    assert Path(payload["forge_path"]).exists()
    text = Path(payload["forge_path"]).read_text(encoding="utf-8")
    assert "Real Codex surfaces are the source of truth" in text


def test_feishu_dry_run_does_not_execute_external_write(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("codpm.syncer.data_dir", lambda: tmp_path / ".data")
    monkeypatch.setattr(
        "codpm.syncer.render",
        lambda: {
            "ok": True,
            "forge_path": str(tmp_path / "docs" / "codex-personalization-registry.md"),
        },
    )

    payload = sync_feishu(execute=False)
    assert payload["ok"]
    assert payload["status"] == "dry_run"
    assert "command" in payload


def test_cli_list_rules(capsys) -> None:
    code = main(["list-rules"])
    captured = capsys.readouterr()
    assert code == 0
    assert "codex_instruction" in captured.out or "execpolicy_rule" in captured.out


def test_rule_list_expands_behavior_blocks(capsys) -> None:
    code = main(["rule", "list", "--scope", "global"])
    captured = capsys.readouterr()
    assert code == 0
    assert "Personalization surfaces: rule" in captured.out
    assert "端到端实现与如实协作边界" in captured.out


def test_skill_list_displays_skill_metadata() -> None:
    payload = list_personalization(surface_kind="skill")
    assert payload["schema"] == "codpm.personalization_list.v1"
    assert any(
        surface["parsed"].get("name") == "codpm-workflow"
        for surface in payload["surfaces"]
    )


def test_mcp_listing_includes_config_or_tools() -> None:
    payload = list_personalization(surface_kind="mcp")
    assert payload["surfaces"]
    assert all(surface["type"] in {"codex_config", "tool"} for surface in payload["surfaces"])


def test_memory_boundary_does_not_expose_contents() -> None:
    payload = list_personalization(surface_kind="memory")
    assert payload["surfaces"]
    assert all("boundary" in surface["parsed"] for surface in payload["surfaces"])


def test_workflow_route_maps_rule_listing_to_rule_list() -> None:
    class FakeSurface:
        scope = "project"
        project = "codpm"

    from codpm import personalization

    original_scan_surfaces = personalization.scan_surfaces
    personalization.scan_surfaces = lambda include_missing=True: [FakeSurface()]
    try:
        payload = route_workflow("列表展示 codpm 项目规则")
    finally:
        personalization.scan_surfaces = original_scan_surfaces

    assert payload["command"] == ["rule", "list", "--scope", "project", "--project", "codpm"]
    assert "registry" in payload["registry_role"]


def test_skill_maintenance_is_explicitly_blocked() -> None:
    payload = maintenance_interface(surface_kind="skill", action="update", target="codpm-workflow")
    assert not payload["ok"]
    assert payload["reason"] == "maintenance_interface_only"


def test_cli_check(capsys) -> None:
    code = main(["check"])
    captured = capsys.readouterr()
    assert code == 0
    assert "Check:" in captured.out


def test_add_project_behavior_rule_writes_real_agents_md(tmp_path, monkeypatch) -> None:
    project = tmp_path / "sample"
    project.mkdir()
    monkeypatch.setattr("codpm.editor.FORGE_ROOT", tmp_path)

    payload = add_behavior_rule(
        scope="project",
        project="sample",
        title="Use real surfaces",
        body="Treat AGENTS.md as the behavior source of truth.",
    )

    assert payload["ok"]
    agents = project / "AGENTS.md"
    assert agents.exists()
    text = agents.read_text(encoding="utf-8")
    assert "<!-- codpm:begin use-real-surfaces -->" in text
    assert "Treat AGENTS.md as the behavior source of truth." in text


def test_watch_once_records_inventory_state(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("codpm.watcher.data_dir", lambda: tmp_path)
    monkeypatch.setattr("codpm.watcher.render", lambda: {"ok": True, "forge_path": str(tmp_path / "rendered.md")})
    payload = watch_once()
    assert payload["ok"]
    assert payload["status"] in {"changed", "unchanged"}
    assert (tmp_path / "watch" / "state.json").exists()
    second = watch_once()
    assert second["ok"]
    assert second["status"] == "unchanged"


def test_render_in_arbitrary_clone_writes_inside_clone(tmp_path: Path) -> None:
    clone = tmp_path / "codpm-public"
    shutil.copytree(Path(__file__).resolve().parents[1] / "codpm", clone / "codpm")
    shutil.copy2(Path(__file__).resolve().parents[1] / "pyproject.toml", clone / "pyproject.toml")
    env = {**os.environ, "PYTHONPATH": str(clone)}

    completed = subprocess.run(
        [sys.executable, "-B", "-m", "codpm.cli", "render"],
        cwd=clone,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert (clone / "generated" / "codex-personalization-registry.md").exists()
    assert (clone / "docs" / "codex-personalization-registry.md").exists()
    assert not (tmp_path / "docs" / "codex-personalization-registry.md").exists()


def test_sync_feishu_dry_run_uses_project_root_not_parent_codpm(tmp_path: Path) -> None:
    clone = tmp_path / "codpm-public"
    shutil.copytree(Path(__file__).resolve().parents[1] / "codpm", clone / "codpm")
    shutil.copy2(Path(__file__).resolve().parents[1] / "pyproject.toml", clone / "pyproject.toml")
    env = {**os.environ, "PYTHONPATH": str(clone)}

    completed = subprocess.run(
        [sys.executable, "-B", "-m", "codpm.cli", "sync", "feishu", "--json"],
        cwd=clone,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert str(tmp_path / "codpm" / ".nexus" / "feishu.json") not in completed.stdout
    assert str(clone / ".nexus" / "feishu.json") in completed.stdout


def test_gitignore_covers_public_runtime_outputs() -> None:
    text = (Path(__file__).resolve().parents[1] / ".gitignore").read_text(encoding="utf-8")

    for pattern in [".data/", "generated/", "docs/codex-personalization-registry.md", "build/", "dist/", "*.egg-info/", ".github/nexus-auth/", ".nexus/runtime/", "__pycache__/", ".pytest_cache/"]:
        assert pattern in text
