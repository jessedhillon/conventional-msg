from __future__ import annotations

from pathlib import Path
import subprocess
import tomllib
import typing as t

import pydantic as p


DefaultTypes = {
    "chore",
    "docs",
    "feat",
    "fix",
    "revise",
    "wip",
}
DefaultAreas = {
    "all",  # rare
    "cli",
    "config",
    "core",
    "dev",  # developer tooling
    "lib",
    "model",
    "migrations",
    "tests",
    "typings",
}
DefaultTags = {
    "tests-failing",
}
DefaultArealess = {
    "docs",
    "wip",
}


def find_repo_root() -> Path:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
        if out:
            return Path(out)
        raise RuntimeError("Did not locate git toplevel")
    except Exception as ex:
        raise RuntimeError("Are we even in a git repo?") from ex


def load_pyproject_config(repo_root: Path, tool_key: str) -> dict[str, t.Any]:
    pp = repo_root / "pyproject.toml"
    if not pp.exists():
        return {}
    data = tomllib.loads(pp.read_text("utf-8"))
    return (data.get("tool") or {}).get(tool_key) or {}


class MessageRules(p.BaseModel):
    model_config = {
        "extra": "forbid",
    }
    min_len: int = p.Field(default=8)
    areas: set[str] | None = p.Field(default=None)
    types: set[str] = p.Field(default_factory=DefaultTypes.copy)
    tags: set[str] = p.Field(default_factory=DefaultTags.copy)
    branch: str = p.Field(default="master")
    revise_name: str = p.Field(default="revise")
    allow_omit_area: set[str] = p.Field(default_factory=DefaultArealess.copy)

    @property
    def validate_areas(self) -> bool:
        return self.areas is not None

    @classmethod
    def from_pyproject(cls, repo_root: Path, key: str = "conventional-msg") -> MessageRules:
        raw = load_pyproject_config(repo_root, "conventional-msg")
        return cls.model_validate(raw)
