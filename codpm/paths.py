from __future__ import annotations

import os
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def _looks_like_codpm_root(path: Path) -> bool:
    return (path / "codpm").is_dir() and (path / "pyproject.toml").exists()


def _detect_project_root() -> Path:
    configured = os.environ.get("CODPM_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    cwd = Path.cwd().resolve()
    candidates = [cwd, *cwd.parents]
    for candidate in candidates:
        if _looks_like_codpm_root(candidate):
            return candidate
    return PACKAGE_ROOT


def _detect_forge_root(project_root: Path) -> Path:
    configured = os.environ.get("CODPM_FORGE_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    if project_root.name == "codpm":
        return project_root.parent
    return project_root


PROJECT_ROOT = _detect_project_root()
FORGE_ROOT = _detect_forge_root(PROJECT_ROOT)


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()


def generated_dir() -> Path:
    return PROJECT_ROOT / "generated"


def data_dir() -> Path:
    return PROJECT_ROOT / ".data"


def registry_dir() -> Path:
    return PROJECT_ROOT / "registry"


def forge_docs_dir() -> Path:
    configured = os.environ.get("CODPM_FORGE_ROOT")
    if configured:
        return Path(configured).expanduser().resolve() / "docs"
    return PROJECT_ROOT / "docs"


def resolve_vars(value: str) -> Path:
    expanded = value.replace("$CODEX_HOME", str(codex_home()))
    expanded = expanded.replace("$FORGE_ROOT", str(FORGE_ROOT))
    expanded = expanded.replace("$CODPM_ROOT", str(PROJECT_ROOT))
    return Path(expanded).expanduser()
