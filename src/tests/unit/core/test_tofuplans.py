# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

import fcntl
import hashlib
import json
import logging
import os
import re
import shutil
import stat
import subprocess
import sys
import textwrap
import time
from unittest import mock
import zipfile

import pytest

import debops.core.runner as runner_base_module
import debops.core.tofu.binary as binary_module
import debops.core.tofu.runner as runner_module
from debops.core.tofu import plans as plans_module
from debops.core.tofu.plans import plan_rows, resolve_plan_file
from debops.core.tofu.runner import TofuRunner
from debops.core.tofu.rekey import rekey_view
from debops.core.tofu.view import create_view, reconcile_view
from debops.core.tofu.providers import resolve_providers
from debops.core.tofu.modules import resolve_modules
from debops.core.secrets import SecretManager


def test_resolve_plan_file_by_the_sequence(tofu_project):
    """An integer id resolves against the parsed sequences of the
    saved plan files."""
    project = tofu_project(project_type="modern")
    plans_dir = os.path.join(project.path, "tofu", "views",
                             project.view, "plans")
    os.makedirs(plans_dir)
    for name in ("debops-1-20240101T000000.tfplan",
                 "debops-2-20240102T000000.tfplan"):
        with open(os.path.join(plans_dir, name), "w") as handle:
            handle.write("plan")

    assert resolve_plan_file(
        os.path.join(project.path, "tofu", "views", project.view),
        "2") == os.path.join(
        "plans", "debops-2-20240102T000000.tfplan")
    assert [row[0] for row in plan_rows(
        os.path.join(project.path, "tofu", "views",
                     project.view))] == [1, 2]


def test_resolve_plan_file_by_the_prefix(tofu_project):
    """A non-integer id resolves by the unique prefix of the file
    names: the operator's own '-out' plans and the pre-sequence
    DebOps ones carry stamp-only names."""
    project = tofu_project(project_type="modern")
    plans_dir = os.path.join(project.path, "tofu", "views",
                             project.view, "plans")
    os.makedirs(plans_dir)
    for name in ("manual.tfplan", "debops-20240101T000000.tfplan"):
        with open(os.path.join(plans_dir, name), "w") as handle:
            handle.write("plan")
    view_root = os.path.join(project.path, "tofu", "views",
                             project.view)

    assert resolve_plan_file(view_root, "manual") == \
        os.path.join("plans", "manual.tfplan")


def test_resolve_plan_file_refuses_the_collisions(tofu_project):
    """An id which matches several files -- a duplicated sequence,
    an ambiguous prefix -- and an id which matches none refuse with
    the names the view holds."""
    project = tofu_project(project_type="modern")
    plans_dir = os.path.join(project.path, "tofu", "views",
                             project.view, "plans")
    os.makedirs(plans_dir)
    for name in ("debops-3-20240101T000000.tfplan",
                 "debops-3-20240102T000000.tfplan"):
        with open(os.path.join(plans_dir, name), "w") as handle:
            handle.write("plan")
    view_root = os.path.join(project.path, "tofu", "views",
                             project.view)

    with pytest.raises(ValueError, match="not unique"):
        resolve_plan_file(view_root, "3")
    with pytest.raises(ValueError, match="ambiguous"):
        resolve_plan_file(view_root, "debops-3")
    with pytest.raises(ValueError, match="No saved plan"):
        resolve_plan_file(view_root, "7")
