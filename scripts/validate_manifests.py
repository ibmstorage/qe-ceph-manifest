#!/usr/bin/env python3
"""Validate qe-ceph-manifest YAML files for syntax and common promotion errors."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_DIRS = ("ibm", "redhat", "ceph")
SECTION_CHILDREN = ("version", "repositories", "images", "repo_ids")

errors: list[str] = []


def validate_file(path: Path) -> None:
    rel = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8")

    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        errors.append(f"{rel}: YAML parse error: {exc}")
        return

    if not isinstance(data, dict):
        errors.append(f"{rel}: root must be a mapping")
        return

    for line_no, line in enumerate(text.splitlines(), start=1):
        if "\t" in line:
            errors.append(f"{rel}:{line_no}: tabs are not allowed")

        # Recurring promotion typo: 3-space indent for section-level keys.
        for key in SECTION_CHILDREN:
            if line == f"   {key}:" or line.startswith(f"   {key}: "):
                errors.append(
                    f"{rel}:{line_no}: '{key}' must use 2 spaces under a build section, not 3"
                )

    for section, body in data.items():
        if not isinstance(body, dict):
            errors.append(f"{rel}: section '{section}' must be a mapping")


def main() -> int:
    manifest_files: list[Path] = []
    for subdir in MANIFEST_DIRS:
        manifest_dir = ROOT / subdir
        if not manifest_dir.is_dir():
            errors.append(f"missing manifest directory: {subdir}/")
            continue
        manifest_files.extend(sorted(manifest_dir.glob("*.yaml")))

    if not manifest_files:
        print("No manifest YAML files found.", file=sys.stderr)
        return 1

    for path in manifest_files:
        validate_file(path)

    if errors:
        print("Manifest validation failed:\n")
        print("\n".join(errors))
        return 1

    print(f"All {len(manifest_files)} manifest YAML files are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
