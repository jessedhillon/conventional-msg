from __future__ import annotations

from pathlib import Path
import pytest

import pydantic as p

from conventional_msg.config import MessageRules, DefaultAreas, DefaultTypes, DefaultTags, DefaultArealess


def write_pyproject(tmp: Path, body: str) -> None:
    (tmp / "pyproject.toml").write_text(body, encoding="utf-8")


def test_defaults_when_no_pyproject(tmp_path: Path):
    rules = MessageRules.from_pyproject(tmp_path)
    assert rules.min_len == 8
    assert rules.areas == set(DefaultAreas)
    assert rules.types == set(DefaultTypes)
    assert rules.tags == set(DefaultTags)
    assert rules.allow_omit_area == set(DefaultArealess)
    assert rules.branch == "master"
    assert rules.revise_name == "revise"


def test_partial_override(tmp_path: Path):
    write_pyproject(
        tmp_path,
        """
[tool.conventional-msg]
min_len = 12
branch = "main"
types = ["feat", "fix"]
""",
    )
    rules = MessageRules.from_pyproject(tmp_path)
    assert rules.min_len == 12
    assert rules.branch == "main"
    assert rules.types == {"feat", "fix"}
    assert rules.areas == set(DefaultAreas)


def test_set_fields_are_deduped(tmp_path: Path):
    write_pyproject(
        tmp_path,
        """
[tool.conventional-msg]
types = ["feat", "feat", "fix"]
""",
    )
    rules = MessageRules.from_pyproject(tmp_path)
    assert rules.types == {"feat", "fix"}


def test_invalid_type_for_min_len(tmp_path: Path):
    write_pyproject(
        tmp_path,
        """
[tool.conventional-msg]
min_len = "eight"
""",
    )
    with pytest.raises(p.ValidationError):
        MessageRules.from_pyproject(tmp_path)


def test_unknown_keys_policy(tmp_path: Path):
    write_pyproject(
        tmp_path,
        """
[tool.conventional-msg]
lol = 123
""",
    )
    with pytest.raises(p.ValidationError):
        MessageRules.from_pyproject(tmp_path)
