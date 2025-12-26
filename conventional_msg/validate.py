import re as regex
import subprocess
import typing as t

from .config import MessageRules


def validate_headline(msg: str, warn: t.Callable[[str], t.Any], rules: MessageRules) -> bool:
    """
    Validates commit message against modified conventional commit criteria:
        type(area[,...])[!]: [{tag}] message
    """

    if len(msg) < 1:
        warn(f"empty or unparsable message: {msg.strip()!r}")
        return False
    headline = msg.splitlines().pop(0)

    pattern = regex.compile(
        r'^(?P<type>[\w-]+)'
        r'(?:\((?P<area>[\w-]+(?:,[\w-]+)*)\))?'
        r'(?:!: \{(?P<tag>[\w-]+)\}|: )'
        r'(?P<message>.+)$'
    )
    match = pattern.match(headline)
    if not match:
        warn(
            f"""
message:
    {msg.strip()}

does not obey conventional commit format:
    type(area[,...])[!]: {{tag}} message
"""
        )
        return False

    type_: str = match.group("type")
    areas: str | None = match.group("area")
    tag: str | None = match.group("tag")
    message: str = match.group("message").strip()

    if type_ not in rules.types:
        warn(f"{type_!r} is not a valid type: {rules.types!r}")
        return False

    # check revision
    is_revision = (type_ == rules.revise_name)
    if is_revision:
        if not check_revision(areas, warn):
            return False
    else:
        if areas is None and type_ not in rules.allow_no_area:
            warn(f"area is required for {type_!r} type")
            return False
        elif areas is not None:
            ls_areas = areas.split(",")
            for area in ls_areas:
                if area not in rules.areas:
                    warn(f"{area!r} is not a valid area: {rules.areas!r}")
                    return False
            if ls_areas != sorted(ls_areas):
                warn("areas must be alphabetically sorted")
                return False

    if tag is not None and tag not in rules.tags:
        warn(f"{tag!r} is not a valid tag: {rules.tags!r}")
        return False

    if len(message) < rules.min_len:
        warn(f"message must be at least {rules.min_len} characters")
        return False

    return True


def check_revision(rev: str | None, warn: t.Callable[[str], t.Any]) -> bool:
    if rev is None:
        # omitting rev is only permitted if we were 1+ commits from master
        # already, meaning we are revising on a feature branch and this
        # will get squashed anyhow
        current_branch: str = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                stderr=subprocess.DEVNULL).strip().decode()

        merge_base: str = subprocess.check_output(
                ["git", "merge-base", "HEAD", "master"],
                stderr=subprocess.DEVNULL).strip().decode()
        if not merge_base:
            warn("could not locate merge base in master")
            return False

        commit_count: str = subprocess.check_output(
                ["git", "rev-list", "--count", "HEAD", f"^{merge_base}"],
                stderr=subprocess.DEVNULL).strip().decode()
        if int(commit_count) == 0 or current_branch == "master":
            warn("a hash in master must be specified for revision:\n\n\trevise(<commit>): ...\n")
            return False
        return True
    else:
        # if we are on master or authoring the first commit on a branch
        # we must indicate which commit in master is being revised
        if regex.search(r'^[a-f0-9]{6,}$', rev):
            try:
                commit_type: str = subprocess.check_output(
                    ["git", "cat-file", "-t", rev],
                    stderr=subprocess.DEVNULL).strip().decode()
                if commit_type != "commit":
                    warn(f"{rev!r} is not a commit")
                    return False
            except subprocess.CalledProcessError:
                warn(f"{rev!r} does not exist in this repository")
                return False

            if subprocess.call(["git", "merge-base", "--is-ancestor", rev, "HEAD"]) != 0:
                warn(f"{rev!r} is not an ancestor of HEAD")
                return False
        else:
            warn(f"{rev!r} is not a valid revision")
            return False
    return True
