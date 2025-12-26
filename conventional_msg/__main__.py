import functools
import sys
import textwrap
import typing as t

from .validate import validate_headline
from .config import MessageRules, find_repo_root


def main():
    rules = MessageRules.from_pyproject(find_repo_root())
    error = functools.partial(print, "\033[31mERROR\033[0m")

    if len(sys.argv) == 2:
        fn = sys.argv[1]
        with open(fn, "r") as f:
            msg = f.read().strip()
    else:
        if sys.stdin.isatty():
            print(textwrap.dedent(t.cast(str, validate_headline.__doc__)))  # noqa: T201
            tab = "  "
            print(f"""
Types:
{tab}- {f"\n{tab}- ".join(sorted(rules.types))}

Areas:
{tab}- {f"\n{tab}- ".join(sorted(rules.areas))}

Tags:
{tab}- {f"\n{tab}- ".join(sorted(rules.tags))}
      """)  # noqa: T201
            sys.exit(1)
        else:
            msg = sys.stdin.read()

    sys.exit(0 if validate_headline(msg, error, rules) else 1)
