#!/usr/bin/env python3
"""Generate Slack payloads for manifest stable-section promotions."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import PurePosixPath

import yaml


EMPTY_GIT_SHA = "0" * 40
YAML_SUFFIXES = {".yaml", ".yml"}
VENDOR_NAMES = {
    "ibm": "IBM",
    "redhat": "RedHat",
    "ceph": "Ceph",
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
    # Manifests are expected to live at <vendor>/<ceph-version>.yaml
    # (e.g. ibm/9.2.yaml, redhat/9.2.yaml, ceph/squid.yaml).
    # Files at the repo root or in unrelated directories (e.g. .github/) are
    # skipped because they cannot carry a meaningful stable section.
    for path in changed_yaml_files(before, after):
        p = PurePosixPath(path)
        if p.parent == PurePosixPath("."):
            # Root-level YAML file — not a manifest recipe; skip.
            continue

        previous_stable = recipe_at_revision(before, path).get("stable")
        current_stable = recipe_at_revision(after, path).get("stable")

        if not current_stable or previous_stable == current_stable:
            continue

        build_version = current_stable.get("version")
        if not build_version:
            raise ValueError(f"Stable section in {path} has no version value")

        path_parts = p.parts
        vendor = VENDOR_NAMES.get(path_parts[0].lower(), "")
        # The filename stem is used directly as the Ceph version label.
        # Expected convention: <vendor>/<ceph-version>.yaml (e.g. ibm/9.2.yaml,
        # redhat/9.2.yaml, ceph/squid.yaml).  An unconventionally named file such
        # as ibm/ibm-ceph-9.2.yaml would produce a misleading label; rename it to
        # follow the convention before adding a stable section.
        ceph_version = p.stem
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
    before = os.environ.get("BEFORE_SHA", "").strip()
    after = os.environ.get("AFTER_SHA", "").strip()
    if not before or not after:
        raise SystemExit(
            "BEFORE_SHA and AFTER_SHA environment variables are required."
        )
    promotion_comment = os.environ.get("PROMOTION_COMMENT", "")
    try:
        print(json.dumps(promotion_payloads(before, after, promotion_comment)))
    except subprocess.CalledProcessError as exc:
        raise SystemExit(
            f"ERROR: git command failed (exit {exc.returncode}): {exc.cmd}"
        ) from exc
    except ValueError as exc:
        raise SystemExit(f"ERROR: {exc}") from exc


if __name__ == "__main__":
    main()
