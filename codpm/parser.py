from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore

from .io import read_text
from .model import Surface


def parse_surface(surface: Surface) -> dict[str, Any]:
    if not surface.exists:
        return {"status": "missing", "summary": surface.summary, "items": []}
    path = Path(surface.path)
    if surface.type in {"codex_instruction", "codex_instruction_override"}:
        return parse_markdown_instruction(path)
    if surface.type == "execpolicy_rule":
        return parse_execpolicy(path)
    if surface.type == "skill":
        return parse_skill(path)
    if surface.type == "codex_config":
        return parse_toml(path)
    if surface.type == "codex_hook":
        return parse_json(path)
    if surface.type == "codex_memory":
        return {"status": "present", "summary": "Memory exists; treat as advisory, not a hard rule.", "items": []}
    if surface.type == "nexus_project":
        return {"status": "present", "summary": "Nexus project state exists; active only through Nexus workflows.", "items": []}
    return {"status": "present", "summary": surface.summary, "items": []}


def parse_markdown_instruction(path: Path) -> dict[str, Any]:
    text = read_text(path)
    lines = text.splitlines()
    headings = []
    bullets = []
    for lineno, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            headings.append({"line": lineno, "text": stripped})
        elif stripped.startswith(("-", "*")):
            bullets.append({"line": lineno, "text": stripped})
    empty = not text.strip()
    return {
        "status": "empty" if empty else "present",
        "summary": "Empty instruction file." if empty else f"{len(headings)} headings, {len(bullets)} bullets.",
        "items": headings[:20] + bullets[:30],
        "rule_blocks": parse_markdown_rule_blocks(text),
    }


def parse_markdown_rule_blocks(text: str) -> list[dict[str, Any]]:
    blocks = _codpm_rule_blocks(text)
    if blocks:
        return blocks
    return _heading_rule_blocks(text)


def _codpm_rule_blocks(text: str) -> list[dict[str, Any]]:
    pattern = re.compile(
        r"<!--\s*codpm:begin\s+(?P<marker>.*?)\s*-->(?P<body>.*?)<!--\s*codpm:end\s+(?P=marker)\s*-->",
        re.DOTALL,
    )
    blocks = []
    for match in pattern.finditer(text):
        body = match.group("body").strip()
        title = _first_heading(body) or match.group("marker").strip()
        blocks.append(
            {
                "title": title,
                "marker_id": match.group("marker").strip(),
                "line": text[: match.start()].count("\n") + 1,
                "managed_by": "codpm",
                "items": _body_items(body),
            }
        )
    return blocks


def _heading_rule_blocks(text: str) -> list[dict[str, Any]]:
    lines = text.splitlines()
    heading_indexes = [
        index
        for index, line in enumerate(lines)
        if line.startswith("## ") and not line.startswith("### ")
    ]
    blocks = []
    for pos, start in enumerate(heading_indexes):
        end = heading_indexes[pos + 1] if pos + 1 < len(heading_indexes) else len(lines)
        body = "\n".join(lines[start:end]).strip()
        title = lines[start].lstrip("#").strip()
        blocks.append(
            {
                "title": title,
                "marker_id": "",
                "line": start + 1,
                "managed_by": "markdown",
                "items": _body_items(body),
            }
        )
    return blocks


def _first_heading(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return ""


def _body_items(text: str) -> list[str]:
    items = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("<!--") or stripped.startswith("#"):
            continue
        if stripped.startswith(("-", "*")):
            stripped = stripped[1:].strip()
        items.append(stripped)
        if len(items) >= 12:
            break
    return items


def parse_execpolicy(path: Path) -> dict[str, Any]:
    text = read_text(path)
    rules = []
    for lineno, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        rules.append({"line": lineno, "text": stripped, "kind": _execpolicy_kind(stripped)})
    return {"status": "present", "summary": f"{len(rules)} execpolicy statements.", "items": rules}


def _execpolicy_kind(line: str) -> str:
    match = re.match(r"([a-zA-Z_][a-zA-Z0-9_]*)\(", line)
    return match.group(1) if match else "unknown"


def parse_skill(path: Path) -> dict[str, Any]:
    text = read_text(path)
    frontmatter: dict[str, str] = {}
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    frontmatter[key.strip()] = value.strip()
    headings = [
        {"line": lineno, "text": line.strip()}
        for lineno, line in enumerate(text.splitlines(), 1)
        if line.strip().startswith("#")
    ]
    return {
        "status": "present",
        "summary": f"Skill {frontmatter.get('name', path.parent.name)}.",
        "items": headings[:30],
        "frontmatter": frontmatter,
        "name": frontmatter.get("name", path.parent.name),
        "description": frontmatter.get("description", ""),
    }


def parse_toml(path: Path) -> dict[str, Any]:
    try:
        payload = tomllib.loads(read_text(path))
    except Exception as exc:
        return {"status": "parse_error", "summary": str(exc), "items": []}
    keys = sorted(payload.keys())
    return {
        "status": "present",
        "summary": f"TOML keys: {', '.join(keys)}",
        "keys": keys,
        "items": [{"key": key, "type": type(value).__name__} for key, value in sorted(payload.items())],
    }


def parse_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(read_text(path))
    except Exception as exc:
        return {"status": "parse_error", "summary": str(exc), "items": []}
    if isinstance(payload, dict):
        items = [{"key": key, "type": type(value).__name__} for key, value in sorted(payload.items())]
        summary = f"JSON object keys: {', '.join(sorted(payload.keys()))}"
    else:
        items = [{"type": type(payload).__name__}]
        summary = f"JSON {type(payload).__name__}"
    return {"status": "present", "summary": summary, "items": items}


def content_contains(surface: Surface, query: str) -> bool:
    if not surface.exists or not query:
        return False
    path = Path(surface.path)
    if not path.is_file():
        return False
    return query in read_text(path)
