#!/usr/bin/env python3

# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Render the DebOps CI role manifest into a GitHub Actions job matrix.

The manifest (:file:`roles.yml` in this directory) lists the DebOps
playbooks tested by the 'DebOps CI Pipeline' GitHub Actions workflow,
along with the roles excluded from CI and the reason for the exclusion.
This script turns the manifest into a JSON document consumed by the
workflow's ``strategy`` section.

On pull requests the job matrix is filtered by changed paths: only the
entries whose ``role`` matches a changed role tree are tested, while the
entries marked as ``always`` (the base playbooks) run on every CI
invocation. Changes that affect the whole pipeline - shared plumbing, or
a role without its own test entry - select the full matrix, since such
a role can be a dependency of any playbook.

The script never emits more than the 256 jobs that GitHub Actions allows
in a strategy matrix; the workflow itself sets the ``fail-fast`` and
``max-parallel`` strategy options.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

MANIFEST_PATH = Path(__file__).parent / "roles.yml"

# Changes under these paths affect every playbook, so the full matrix is
# selected. Role trees are matched separately.
SHARED_PATH_PREFIXES = (
    "ansible/",
    "requirements-integration.txt",
)

ROLE_PATH_RE = re.compile(r"ansible/roles/([^/]+)/")

DEFAULT_RUNNER = "ubuntu-24.04"
DEFAULT_TIMEOUT = 30

# GitHub Actions allows at most 256 jobs in a strategy matrix.
MATRIX_MAX_JOBS = 256

DEFAULT_FIELDS: dict[str, Any] = {
    "always": False,
    "excluded": False,
    "groups": [],
    "idempotency": "strict",
    "inventoryspec": {},
    "packages": [],
    "playbook": None,
    "post_script": "",
    "pre_script": "",
    "reason": "",
    "role": None,
    "runner": DEFAULT_RUNNER,
    "timeout": DEFAULT_TIMEOUT,
    "vars": {},
}

# Keys of an inventory specification document, rejected early so that
# manifest typos surface before the CI run. The 'debops' CLI validates the
# rest of the document when it applies it.
INVENTORY_SPEC_KEYS = frozenset({"version", "files", "keep"})


def load_manifest(path: Path) -> list[dict[str, Any]]:
    """Load and validate the role manifest, applying field defaults."""
    try:
        entries = yaml.safe_load(path.read_text())
    except FileNotFoundError:
        raise SystemExit(f"Error: manifest not found: {path}")
    except yaml.YAMLError as errmsg:
        raise SystemExit(f"Error: cannot parse manifest {path}: {errmsg}")

    if not isinstance(entries, list) or not entries:
        raise SystemExit(f"Error: manifest {path} contains no entries")

    manifest: list[dict[str, Any]] = []
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict) or "name" not in entry:
            raise SystemExit(
                f"Error: manifest {path} contains an entry without a 'name'"
            )
        name = entry["name"]
        if name in seen:
            raise SystemExit(f"Error: duplicate manifest entry: {name}")
        seen.add(name)

        fields = {**DEFAULT_FIELDS, **entry}
        fields["role"] = fields["role"] or name

        # The 'playbook' field accepts a single playbook or a list of
        # playbooks to apply in order on the same host.
        if fields["playbook"] is None:
            playbooks = [name]
        elif isinstance(fields["playbook"], str):
            playbooks = [fields["playbook"]]
        elif isinstance(fields["playbook"], list):
            playbooks = fields["playbook"]
        else:
            raise SystemExit(
                f"Error: entry '{name}' field 'playbook' must be a string "
                f"or a list of strings"
            )
        if not playbooks or \
                not all(isinstance(item, str) and item for item in playbooks):
            raise SystemExit(
                f"Error: entry '{name}' field 'playbook' contains no "
                f"playbooks to apply"
            )
        fields["playbooks"] = playbooks
        del fields["playbook"]

        if fields["idempotency"] not in ("strict", "advisory"):
            raise SystemExit(
                f"Error: entry '{name}' has invalid 'idempotency' field, "
                f"expected 'strict' or 'advisory'"
            )
        if not isinstance(fields["groups"], list) or \
                not all(isinstance(item, str) for item in fields["groups"]):
            raise SystemExit(
                f"Error: entry '{name}' field 'groups' must be a list "
                f"of strings"
            )
        if not isinstance(fields["packages"], list) or \
                not all(isinstance(item, str) for item in fields["packages"]):
            raise SystemExit(
                f"Error: entry '{name}' field 'packages' must be a list "
                f"of strings"
            )
        if not isinstance(fields["role"], str):
            raise SystemExit(
                f"Error: entry '{name}' field 'role' must be a string with "
                f"the name of the role that the entry tests"
            )
        if not isinstance(fields["post_script"], str):
            raise SystemExit(
                f"Error: entry '{name}' field 'post_script' must be a "
                f"string with the shell commands to test the service"
            )
        if not isinstance(fields["inventoryspec"], dict):
            raise SystemExit(
                f"Error: entry '{name}' field 'inventoryspec' must be an "
                f"inventory specification dictionary"
            )
        if fields["inventoryspec"]:
            if not fields["inventoryspec"].keys() <= INVENTORY_SPEC_KEYS:
                raise SystemExit(
                    f"Error: entry '{name}' field 'inventoryspec' contains "
                    f"unknown keys: {', '.join(fields['inventoryspec'])}"
                )
            if "files" not in fields["inventoryspec"]:
                raise SystemExit(
                    f"Error: entry '{name}' field 'inventoryspec' has no "
                    f"'files' key"
                )
        # The workflow applies the specification through 'debops project
        # refresh --template -', which reads a YAML document from standard
        # input, so the specification is serialized here and the workflow
        # entry carries it as a string.
        fields["inventoryspec"] = (
            yaml.safe_dump(fields["inventoryspec"], default_flow_style=False,
                           sort_keys=False, width=4096)
            if fields["inventoryspec"] else ""
        )
        if fields["vars"]:
            # Reserved for per-entry variable overrides, not consumed by the
            # workflow yet.
            raise SystemExit(
                f"Error: entry '{name}' uses the reserved 'vars' field"
            )
        if fields["excluded"] and not fields["reason"]:
            raise SystemExit(
                f"Error: excluded entry '{name}' needs a 'reason'"
            )
        manifest.append(fields)
    return manifest


def select_entries(
    entries: list[dict[str, Any]],
    changed_files: list[str] | None,
) -> tuple[list[dict[str, Any]], bool]:
    """Select the manifest entries to run.

    Returns the selected entries and a flag that tells whether the full
    matrix was selected because the changes could affect any playbook.
    """
    if changed_files is None:
        return [entry for entry in entries if not entry["excluded"]], True

    roles = {entry["role"] for entry in entries if not entry["excluded"]}
    selected_roles: set[str] = set()
    run_all = False

    for path in changed_files:
        match = ROLE_PATH_RE.match(path)
        if match:
            # A role without its own test entry can be a dependency of any
            # playbook, so its changes select the full matrix.
            if match.group(1) not in roles:
                run_all = True
                break
            selected_roles.add(match.group(1))
        elif path.startswith(SHARED_PATH_PREFIXES):
            run_all = True
            break

    if run_all:
        return [entry for entry in entries if not entry["excluded"]], True

    picked = [entry for entry in entries
              if entry["always"] or entry["role"] in selected_roles]
    return picked, False


def build_matrix(
    entries: list[dict[str, Any]],
    run_all: bool,
) -> dict[str, Any]:
    """Build the GitHub Actions strategy matrix from the selected entries."""
    include = [
        {
            "name": entry["name"],
            "playbooks": " ".join(entry["playbooks"]),
            "groups": ",".join(entry["groups"]),
            "packages": " ".join(entry["packages"]),
            "inventoryspec": entry["inventoryspec"],
            "post_script": entry["post_script"],
            "pre_script": entry["pre_script"],
            "runner": entry["runner"],
            "timeout": entry["timeout"],
            "idempotency": entry["idempotency"],
        }
        for entry in entries
    ]
    if not include:
        raise SystemExit("Error: job matrix is empty, check the manifest")
    if len(include) > MATRIX_MAX_JOBS:
        raise SystemExit(
            f"Error: job matrix has {len(include)} entries, GitHub Actions "
            f"supports at most {MATRIX_MAX_JOBS}"
        )
    # The 'matrix' section of the strategy is the only part that has to be
    # dynamic; 'fail-fast' and 'max-parallel' are set by the workflow.
    return {
        "include": include,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render the DebOps CI role manifest into a GitHub "
                    "Actions job matrix"
    )
    parser.add_argument(
        "--manifest", type=Path, default=MANIFEST_PATH,
        help="path to the role manifest "
             "(default: roles.yml next to this script)"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--all", action="store_true",
        help="run the full matrix, regardless of changed paths"
    )
    group.add_argument(
        "--changed-files", type=Path, metavar="PATH",
        help="file with newline-separated, repository-relative paths of "
             "changed files to filter the matrix by"
    )
    parser.add_argument(
        "--output", type=Path, metavar="PATH",
        help="write the matrix to this file instead of standard output"
    )
    args = parser.parse_args()

    entries = load_manifest(args.manifest)

    changed_files: list[str] | None = None
    if args.changed_files:
        try:
            content = args.changed_files.read_text()
        except FileNotFoundError:
            raise SystemExit(
                f"Error: changed files list not found: {args.changed_files}"
            )
        changed_files = [line for line in content.splitlines() if line]

    picked, run_all = select_entries(entries, changed_files)
    matrix = build_matrix(picked, run_all)

    print(
        f"Job matrix: {len(matrix['include'])} entries, "
        f"run_all={run_all}",
        file=sys.stderr,
    )
    output = json.dumps(matrix, indent=2) + "\n"
    if args.output:
        args.output.write_text(output)
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
