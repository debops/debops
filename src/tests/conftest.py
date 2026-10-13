# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Shared fixtures for the DebOps test suite.

The suite is split in two:

* ``src/tests/unit`` isolates a single component and replaces the tools it
  would otherwise call. These tests run everywhere.
* ``src/tests/integration`` drives several real components with the real
  tools installed on the machine, skipping when one is missing.
"""

import os
import subprocess
import sys

import pytest


# ``conftest.py`` lives in ``<repo>/src/tests``, so the repository root is
# three directories up. The importable package is ``src/debops``.
SOURCE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "src")


@pytest.fixture
def debops_source_dir():
    """Path to the ``src`` directory which holds the importable package."""
    return SOURCE_DIR


@pytest.fixture
def run_debops(debops_source_dir):
    """Run the DebOps command line in a subprocess.

    The command is launched as ``python -m debops`` with ``src`` on
    ``PYTHONPATH``, which is how the package behaves before installation and
    keeps the real ``sys.exit`` codes observable.
    """
    def _run(*args, cwd=None, env=None, check=False):
        run_env = os.environ.copy()
        run_env["PYTHONPATH"] = os.pathsep.join(
            [debops_source_dir, run_env.get("PYTHONPATH", "")]).rstrip(os.pathsep)
        if env:
            run_env.update(env)

        return subprocess.run(
            [sys.executable, "-m", "debops", *args],
            cwd=cwd, env=run_env, check=check,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return _run
