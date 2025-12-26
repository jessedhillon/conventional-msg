from __future__ import annotations

import subprocess
import pytest

from conventional_msg.validate import validate_headline
from conventional_msg.config import DefaultAreas, MessageRules
from tests.conftest import make_msg


def test_valid_basic(warn_collector, default_config):
    warn, msgs = warn_collector
    msg = make_msg("feat(core): add widgets support")
    assert validate_headline(msg, warn, default_config) is True
    assert msgs == []


@pytest.mark.parametrize(
    "headline",
    [
        "feat core: missing parens",
        "feat(core) add missing colon",
        "feat(core):",  # empty message
        "feat(core): yo",  # too short (min_len=8)
    ],
)
def test_invalid_format_or_too_short(headline, warn_collector, default_config):
    warn, msgs = warn_collector
    msg = make_msg(headline)
    assert validate_headline(msg, warn, default_config) is False
    assert msgs  # at least one warning


def test_invalid_type(warn_collector, default_config):
    warn, msgs = warn_collector
    msg = make_msg("banana(core): add widgets support")
    assert validate_headline(msg, warn, default_config) is False
    assert any("not a valid type" in m for m in msgs)


def test_area_required_for_feat(warn_collector, default_config):
    warn, msgs = warn_collector
    msg = make_msg("feat: add widgets support")
    # NOTE: your current code *warns* but does not return False.
    # This test encodes current behavior; change it if you later make it strict.
    assert validate_headline(msg, warn, default_config) is True
    assert any("area is required" in m for m in msgs)


def test_invalid_area(warn_collector, default_config):
    warn, msgs = warn_collector
    msg = make_msg("feat(nope): add widgets support")
    assert validate_headline(msg, warn, default_config) is False
    assert any("not a valid area" in m for m in msgs)


def test_areas_must_be_sorted(warn_collector):
    warn, msgs = warn_collector
    config = MessageRules(areas=DefaultAreas | {"web"})
    msg = make_msg("feat(web,cli): add widgets support")
    assert validate_headline(msg, warn, config) is False
    assert any("alphabetically sorted" in m for m in msgs)


def test_tag_valid(warn_collector, default_config):
    warn, msgs = warn_collector
    msg = make_msg("fix(core)!: [tests-failing] handle edge-case properly")
    assert validate_headline(msg, warn, default_config) is True
    assert msgs == []


def test_tag_invalid(warn_collector, default_config):
    warn, msgs = warn_collector
    msg = make_msg("fix(core)!: [lol] handle edge-case properly")
    assert validate_headline(msg, warn, default_config) is False
    assert any("not a valid tag" in m for m in msgs)


# ---------------------------
# revise(...) behavior tests
# ---------------------------

def test_revise_with_valid_hash_that_is_ancestor(monkeypatch, warn_collector, default_config):
    warn, msgs = warn_collector

    # validate_headline calls:
    # - git cat-file -t <rev>  (check_output)
    # - git merge-base --is-ancestor <rev> HEAD  (call)
    def fake_check_output(cmd, stderr=None):
        if cmd[:3] == ["git", "cat-file", "-t"]:
            return b"commit\n"
        raise AssertionError(f"unexpected check_output: {cmd}")

    def fake_call(cmd, **kwargs):
        if cmd[:4] == ["git", "merge-base", "--is-ancestor", "abc123"]:
            return 0
        raise AssertionError(f"unexpected call: {cmd}")

    monkeypatch.setattr(subprocess, "check_output", fake_check_output)
    monkeypatch.setattr(subprocess, "call", fake_call)

    msg = make_msg("revise(abc123): fix regression in parser")
    assert validate_headline(msg, warn, default_config) is True
    assert msgs == []


def test_revise_with_hash_that_is_not_ancestor(monkeypatch, warn_collector, default_config):
    warn, msgs = warn_collector

    def fake_check_output(cmd, stderr=None):
        if cmd[:3] == ["git", "cat-file", "-t"]:
            return b"commit\n"
        raise AssertionError(f"unexpected check_output: {cmd}")

    def fake_call(cmd, **kwargs):
        if cmd[:4] == ["git", "merge-base", "--is-ancestor", "abc123"]:
            return 1
        raise AssertionError(f"unexpected call: {cmd}")

    monkeypatch.setattr(subprocess, "check_output", fake_check_output)
    monkeypatch.setattr(subprocess, "call", fake_call)

    msg = make_msg("revise(abc123): fix regression in parser")
    assert validate_headline(msg, warn, default_config) is False
    assert any("not an ancestor" in m for m in msgs)


def test_revise_with_nonhex_revision_is_rejected(warn_collector, default_config):
    warn, msgs = warn_collector
    msg = make_msg("revise(main): fix regression in parser")
    assert validate_headline(msg, warn, default_config) is False
    assert any("not a valid revision" in m for m in msgs)


def test_revise_without_hash_on_master_is_rejected(monkeypatch, warn_collector, default_config):
    warn, msgs = warn_collector

    # revise with no (...) area triggers:
    # - git rev-parse --abbrev-ref HEAD
    # - git merge-base HEAD master
    # - git rev-list --count HEAD ^<merge_base>
    def fake_check_output(cmd, stderr=None):
        if cmd[:3] == ["git", "rev-parse", "--abbrev-ref"]:
            return b"master\n"
        if cmd[:3] == ["git", "merge-base", "HEAD"]:
            return b"deadbeef\n"
        if cmd[:4] == ["git", "rev-list", "--count", "HEAD"]:
            return b"0\n"
        raise AssertionError(f"unexpected check_output: {cmd}")

    monkeypatch.setattr(subprocess, "check_output", fake_check_output)

    msg = make_msg("revise: fix regression in parser")
    assert validate_headline(msg, warn, default_config) is False
    assert any("must be specified for revision" in m for m in msgs)
