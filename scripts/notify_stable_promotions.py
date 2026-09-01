#!/usr/bin/env python3
"""Generate Slack payloads for manifest stable-section promotions."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import PurePosixPath

import yaml


EMPTY_GIT_SHA = "0" * 40
YAML_SUFFIXES = {".yaml", ".yml"}
VENDOR_NAMES = {
    "ibm": "IBM",
    "redhat": "RedHat",
}


def git(*args: str) -> str:
    """Run git and return standard output as text."""
    return subprocess.check_output(["git", *args], text=True)


def recipe_at_revision(revision: str, path: str) -> dict:
    """Load one manifest recipe, returning an empty map when it is new."""
    try:
        content = git("show", f"{revision}:{path}")
    except subprocess.CalledProcessError:
        return {}
    return yaml.safe_load(content) or {}


def changed_yaml_files(before: str, after: str) -> list[str]:
    """Return added or modified YAML recipes between two revisions."""
    changed_files = git(
        "diff",
        "--name-only",
        "--diff-filter=AM",
        before,
        after,
        "--",
    ).splitlines()
    return [
        path
        for path in changed_files
        if PurePosixPath(path).suffix.lower() in YAML_SUFFIXES
    ]


def promotion_payloads(
    before: str, after: str, promotion_comment: str = ""
) -> list[dict[str, str]]:
    """Build a Slack payload for every recipe whose stable section changed."""
    if before == EMPTY_GIT_SHA:
        # The first commit of a new branch has no meaningful baseline.
        return []

    payloads = []
    for path in changed_yaml_files(before, after):
        previous_stable = recipe_at_revision(before, path).get("stable")
        current_stable = recipe_at_revision(after, path).get("stable")

        if not current_stable or previous_stable == current_stable:
            continue

        build_version = current_stable.get("version")
        if not build_version:
            raise ValueError(f"Stable section in {path} has no version value")

        path_parts = PurePosixPath(path).parts
        vendor = VENDOR_NAMES.get(path_parts[0].lower(), "")
        ceph_version = PurePosixPath(path).stem
        vendor_prefix = f"{vendor} " if vendor else ""
        message = (
            f"{vendor_prefix}Ceph {ceph_version} build {build_version} has been promoted to stable "
            "and available for QA regression testing"
        )
        if promotion_comment.strip():
            message += f"\nPromotion PR comment: {promotion_comment.strip()}"
        payloads.append({"text": message})

    return payloads


def main() -> None:
    if len(sys.argv) not in (3, 4):
        raise SystemExit(
            "Usage: notify_stable_promotions.py BEFORE_SHA AFTER_SHA [PROMOTION_COMMENT]"
        )

    promotion_comment = sys.argv[3] if len(sys.argv) == 4 else ""
    print(json.dumps(promotion_payloads(sys.argv[1], sys.argv[2], promotion_comment)))


if __name__ == "__main__":
    main()
