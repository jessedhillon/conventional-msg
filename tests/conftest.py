from __future__ import annotations

import pytest

from conventional_msg.config import MessageRules


@pytest.fixture
def warn_collector():
    msgs: list[str] = []

    def warn(s: str) -> None:
        msgs.append(str(s))

    return warn, msgs


@pytest.fixture
def default_config():
    return MessageRules()


def make_msg(headline: str, body: str = "") -> str:
    return headline + ("\n\n" + body if body else "")
