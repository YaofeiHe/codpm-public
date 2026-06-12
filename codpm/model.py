from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Surface:
    id: str
    type: str
    scope: str
    path: str
    exists: bool
    source_of_truth: bool
    loaded_by_codex: str
    project: str = ""
    content_hash: str = ""
    last_modified: str = ""
    summary: str = ""
    risk: str = "low"
    evidence: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def stable_id(surface_type: str, scope: str, path: Path, project: str = "") -> str:
    text = str(path).replace("/", "_").replace(" ", "_")
    bits = [surface_type, scope]
    if project:
        bits.append(project)
    bits.append(text)
    return ":".join(bits)

